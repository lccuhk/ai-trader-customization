"""
Stock Price Fetcher for Server

US Stock: 从 Alpha Vantage 获取价格
Crypto: 从 Hyperliquid 获取价格（停止使用 Alpha Vantage crypto 端点）
"""

import os
import random
import requests
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Tuple, Any
import re
import time
import json
try:
    from zoneinfo import ZoneInfo
    _ET_ZONEINFO = ZoneInfo("America/New_York")
except ImportError:
    _ET_ZONEINFO = None  # Python < 3.9 fallback: use fixed offset below

# Alpha Vantage API configuration
ALPHA_VANTAGE_API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY", "demo")
BASE_URL = "https://www.alphavantage.co/query"

# Hyperliquid public info endpoint (no API key required for reads)
HYPERLIQUID_API_URL = os.environ.get("HYPERLIQUID_API_URL", "https://api.hyperliquid.xyz/info").strip()

# Polymarket public endpoints (no API key required for reads)
POLYMARKET_GAMMA_BASE_URL = os.environ.get("POLYMARKET_GAMMA_BASE_URL", "https://gamma-api.polymarket.com").strip()
POLYMARKET_CLOB_BASE_URL = os.environ.get("POLYMARKET_CLOB_BASE_URL", "https://clob.polymarket.com").strip()
PRICE_FETCH_TIMEOUT_SECONDS = float(os.environ.get("PRICE_FETCH_TIMEOUT_SECONDS", "10"))
PRICE_FETCH_MAX_RETRIES = max(0, int(os.environ.get("PRICE_FETCH_MAX_RETRIES", "2")))
PRICE_FETCH_BACKOFF_BASE_SECONDS = max(0.0, float(os.environ.get("PRICE_FETCH_BACKOFF_BASE_SECONDS", "0.35")))
PRICE_FETCH_ERROR_COOLDOWN_SECONDS = max(0.0, float(os.environ.get("PRICE_FETCH_ERROR_COOLDOWN_SECONDS", "20")))
PRICE_FETCH_RATE_LIMIT_COOLDOWN_SECONDS = max(0.0, float(os.environ.get("PRICE_FETCH_RATE_LIMIT_COOLDOWN_SECONDS", "60")))
PRICE_FETCH_VERBOSE = os.environ.get("PRICE_FETCH_VERBOSE", "true").strip().lower() not in {"0", "false", "no", "off"}
HYPERLIQUID_SYMBOL_CACHE_TTL_SECONDS = max(60.0, float(os.environ.get("HYPERLIQUID_SYMBOL_CACHE_TTL_SECONDS", "300")))

# 价格缓存配置
_PRICE_CACHE_TTL_SECONDS = max(5, int(os.environ.get("PRICE_CACHE_TTL_SECONDS", "60")))
_PRICE_FAILURE_CACHE_TTL_SECONDS = max(5, int(os.environ.get("PRICE_FAILURE_CACHE_TTL_SECONDS", "30")))

# Redis 配置
_REDIS_ENABLED = os.environ.get("REDIS_ENABLED", "false").strip().lower() in {"1", "true", "yes", "on"}
_REDIS_URL = os.environ.get("REDIS_URL", "").strip()
_REDIS_PREFIX = os.environ.get("REDIS_PREFIX", "ai_trader").strip()

# 本地内存缓存
_local_price_cache: Dict[str, Tuple[Optional[float], float]] = {}

# Redis 客户端（懒加载）
_redis_client = None

# 缓存统计
_cache_stats = {
    "hits": 0,
    "misses": 0,
    "local_hits": 0,
    "redis_hits": 0,
    "api_calls": 0,
    "failures": 0,
    "start_time": time.time()
}

# 缓存访问频率跟踪（用于智能 TTL 调整）
_cache_access_frequency: Dict[str, int] = {}

# 缓存预热配置
_CACHE_WARMUP_ENABLED = os.environ.get("CACHE_WARMUP_ENABLED", "false").strip().lower() in {"1", "true", "yes", "on"}
_CACHE_WARMUP_SYMBOLS = os.environ.get("CACHE_WARMUP_SYMBOLS", "AAPL,MSFT,GOOGL,AMZN,TSLA").split(",")

# 智能 TTL 配置
_SMART_TTL_ENABLED = os.environ.get("SMART_TTL_ENABLED", "false").strip().lower() in {"1", "true", "yes", "on"}
_SMART_TTL_MIN_SECONDS = max(5, int(os.environ.get("SMART_TTL_MIN_SECONDS", "10")))
_SMART_TTL_MAX_SECONDS = max(60, int(os.environ.get("SMART_TTL_MAX_SECONDS", "300")))
_SMART_TTL_HIGH_FREQ_THRESHOLD = int(os.environ.get("SMART_TTL_HIGH_FREQ_THRESHOLD", "10"))


def _get_redis_client():
    """获取 Redis 客户端（懒加载）"""
    global _redis_client
    if _redis_client is not None:
        return _redis_client
    
    if not _REDIS_ENABLED or not _REDIS_URL:
        return None
    
    try:
        import redis
        _redis_client = redis.Redis.from_url(_REDIS_URL, decode_responses=True)
        return _redis_client
    except Exception as e:
        _price_log(f"[Price Cache] Failed to connect to Redis: {e}")
        return None


def _price_cache_key(symbol: str, market: str, token_id: Optional[str] = None) -> str:
    """生成缓存键"""
    token_part = f":{token_id}" if token_id else ""
    return f"{_REDIS_PREFIX}:price:{market}:{symbol}{token_part}"


def _price_cache_get(symbol: str, market: str, token_id: Optional[str] = None) -> Optional[float]:
    """从缓存获取价格"""
    cache_key = _price_cache_key(symbol, market, token_id)
    now = time.time()
    
    # 跟踪缓存访问
    _track_cache_access(cache_key)
    
    # 先查本地缓存
    if cache_key in _local_price_cache:
        price, expires_at = _local_price_cache[cache_key]
        if expires_at > now:
            _cache_stats["hits"] += 1
            _cache_stats["local_hits"] += 1
            _price_log(f"[Price Cache] Local cache hit: {cache_key}")
            return price
        else:
            del _local_price_cache[cache_key]
            if cache_key in _cache_access_frequency:
                del _cache_access_frequency[cache_key]
    
    # 再查 Redis 缓存
    redis_client = _get_redis_client()
    if redis_client is not None:
        try:
            cached_value = redis_client.get(cache_key)
            if cached_value is not None:
                # 同步到本地缓存
                try:
                    price = float(cached_value) if cached_value != "null" else None
                    ttl = redis_client.ttl(cache_key)
                    if ttl > 0:
                        _local_price_cache[cache_key] = (price, now + ttl)
                    _cache_stats["hits"] += 1
                    _cache_stats["redis_hits"] += 1
                    _price_log(f"[Price Cache] Redis cache hit: {cache_key}")
                    return price
                except Exception:
                    pass
        except Exception as e:
            _price_log(f"[Price Cache] Redis get error: {e}")
    
    # 缓存未命中
    _cache_stats["misses"] += 1
    return None


def _price_cache_set(symbol: str, market: str, price: Optional[float], token_id: Optional[str] = None) -> None:
    """设置缓存"""
    cache_key = _price_cache_key(symbol, market, token_id)
    now = time.time()
    
    # 使用智能 TTL
    ttl = _get_smart_ttl(cache_key, price)
    expires_at = now + ttl
    
    # 写入本地缓存
    _local_price_cache[cache_key] = (price, expires_at)
    _price_log(f"[Price Cache] Local cache set: {cache_key} (TTL: {ttl}s)")
    
    # 更新统计
    if price is None:
        _cache_stats["failures"] += 1
    else:
        _cache_stats["api_calls"] += 1
    
    # 写入 Redis 缓存
    redis_client = _get_redis_client()
    if redis_client is not None:
        try:
            value = str(price) if price is not None else "null"
            redis_client.setex(cache_key, ttl, value)
            _price_log(f"[Price Cache] Redis cache set: {cache_key} (TTL: {ttl}s)")
        except Exception as e:
            _price_log(f"[Price Cache] Redis set error: {e}")


def _price_cache_clear(symbol: str, market: str, token_id: Optional[str] = None) -> None:
    """清除缓存"""
    cache_key = _price_cache_key(symbol, market, token_id)
    
    # 清除本地缓存
    if cache_key in _local_price_cache:
        del _local_price_cache[cache_key]
    
    # 清除 Redis 缓存
    redis_client = _get_redis_client()
    if redis_client is not None:
        try:
            redis_client.delete(cache_key)
        except Exception:
            pass


def _get_cache_stats() -> Dict[str, Any]:
    """获取缓存统计信息"""
    import time
    
    total_requests = _cache_stats["hits"] + _cache_stats["misses"]
    hit_rate = (_cache_stats["hits"] / total_requests * 100) if total_requests > 0 else 0
    uptime_seconds = time.time() - _cache_stats["start_time"]
    
    return {
        "hits": _cache_stats["hits"],
        "misses": _cache_stats["misses"],
        "local_hits": _cache_stats["local_hits"],
        "redis_hits": _cache_stats["redis_hits"],
        "api_calls": _cache_stats["api_calls"],
        "failures": _cache_stats["failures"],
        "hit_rate": round(hit_rate, 2),
        "total_requests": total_requests,
        "cache_size": len(_local_price_cache),
        "uptime_seconds": round(uptime_seconds, 2),
        "uptime_formatted": _format_uptime(uptime_seconds)
    }


def _format_uptime(seconds: float) -> str:
    """格式化运行时间"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def _reset_cache_stats() -> None:
    """重置缓存统计"""
    global _cache_stats
    _cache_stats = {
        "hits": 0,
        "misses": 0,
        "local_hits": 0,
        "redis_hits": 0,
        "api_calls": 0,
        "failures": 0,
        "start_time": time.time()
    }
    _price_log("[Price Cache] Statistics reset")


def _get_smart_ttl(cache_key: str, price: Optional[float]) -> int:
    """获取智能 TTL（根据访问频率动态调整）"""
    if not _SMART_TTL_ENABLED:
        return _PRICE_CACHE_TTL_SECONDS if price is not None else _PRICE_FAILURE_CACHE_TTL_SECONDS
    
    frequency = _cache_access_frequency.get(cache_key, 0)
    
    if price is None:
        return _PRICE_FAILURE_CACHE_TTL_SECONDS
    
    if frequency >= _SMART_TTL_HIGH_FREQ_THRESHOLD:
        ttl = _SMART_TTL_MAX_SECONDS
    elif frequency >= _SMART_TTL_HIGH_FREQ_THRESHOLD // 2:
        ttl = (_SMART_TTL_MIN_SECONDS + _SMART_TTL_MAX_SECONDS) // 2
    else:
        ttl = _SMART_TTL_MIN_SECONDS
    
    _price_log(f"[Price Cache] Smart TTL for {cache_key}: {ttl}s (frequency: {frequency})")
    return ttl


def _track_cache_access(cache_key: str) -> None:
    """跟踪缓存访问频率"""
    _cache_access_frequency[cache_key] = _cache_access_frequency.get(cache_key, 0) + 1
    
    if _cache_access_frequency[cache_key] > _SMART_TTL_HIGH_FREQ_THRESHOLD:
        _cache_access_frequency[cache_key] = _SMART_TTL_HIGH_FREQ_THRESHOLD


def _clear_expired_cache() -> int:
    """清除过期的缓存项，返回清除的数量"""
    now = time.time()
    expired_keys = []
    
    for key, (_, expires_at) in _local_price_cache.items():
        if expires_at <= now:
            expired_keys.append(key)
    
    for key in expired_keys:
        del _local_price_cache[key]
        if key in _cache_access_frequency:
            del _cache_access_frequency[key]
    
    if expired_keys:
        _price_log(f"[Price Cache] Cleared {len(expired_keys)} expired cache entries")
    
    return len(expired_keys)


def _warmup_cache(symbols: list = None) -> Dict[str, Any]:
    """预热缓存"""
    if symbols is None:
        symbols = _CACHE_WARMUP_SYMBOLS
    
    now = datetime.now(timezone.utc)
    executed_at = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    results = {
        "total": len(symbols),
        "success": 0,
        "failed": 0,
        "details": {}
    }
    
    _price_log(f"[Price Cache] Warming up cache for {len(symbols)} symbols...")
    
    for symbol in symbols:
        symbol = symbol.strip()
        if not symbol:
            continue
        
        price = get_price_from_market(
            symbol=symbol,
            executed_at=executed_at,
            market="us-stock"
        )
        
        if price is not None:
            results["success"] += 1
            results["details"][symbol] = price
            _price_log(f"[Price Cache] Warmup: {symbol} = ${price:.2f}")
        else:
            results["failed"] += 1
            results["details"][symbol] = None
            _price_log(f"[Price Cache] Warmup: {symbol} failed")
    
    _price_log(
        f"[Price Cache] Warmup complete: {results['success']}/{results['total']} successful"
    )
    
    return results

# 时区常量
UTC = timezone.utc
# ET_TZ resolves to America/New_York (DST-aware) when zoneinfo is available.
# Falling back to a fixed UTC-5 (EST) offset is conservative — it will be 1 hour
# off during EDT (summer) but at least correct during the longer EST winter period.
# The zoneinfo path is always preferred and available on Python 3.9+.
ET_TZ = _ET_ZONEINFO if _ET_ZONEINFO is not None else timezone(timedelta(hours=-5))

_POLYMARKET_CONDITION_ID_RE = re.compile(r"^0x[a-fA-F0-9]{64}$")
_POLYMARKET_TOKEN_ID_RE = re.compile(r"^\d+$")
_RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
_provider_cooldowns: Dict[str, float] = {}
_price_fetch_logging_enabled: ContextVar[bool] = ContextVar("price_fetch_logging_enabled", default=True)
_hyperliquid_symbol_cache: Tuple[Optional[set[str]], float] = (None, 0.0)


def _price_log(message: str) -> None:
    if PRICE_FETCH_VERBOSE and _price_fetch_logging_enabled.get():
        print(message)


@contextmanager
def price_fetch_logging(enabled: bool):
    token = _price_fetch_logging_enabled.set(enabled)
    try:
        yield
    finally:
        _price_fetch_logging_enabled.reset(token)

# Polymarket outcome prices are probabilities in [0, 1]. Reject values outside to avoid
# token_id/condition_id or other API noise being interpreted as price (e.g. 1.5e+73).
def _polymarket_price_valid(price: float) -> bool:
    if price is None or not isinstance(price, (int, float)):
        return False
    try:
        p = float(price)
        return 0 <= p <= 1
    except (TypeError, ValueError):
        return False

# In-memory cache for Polymarket reference+outcome -> (token_id, expiry_epoch_s)
_polymarket_token_cache: Dict[str, Tuple[str, float]] = {}
_polymarket_market_cache: Dict[str, Tuple[Optional[dict], float]] = {}
_POLYMARKET_TOKEN_CACHE_TTL_S = 300.0
_POLYMARKET_MARKET_CACHE_TTL_S = 300.0


def _provider_cooldown_remaining(provider: str) -> float:
    return max(0.0, _provider_cooldowns.get(provider, 0.0) - time.time())


def _activate_provider_cooldown(provider: str, duration_s: float, reason: str) -> None:
    if duration_s <= 0:
        return
    until = time.time() + duration_s
    previous_until = _provider_cooldowns.get(provider, 0.0)
    _provider_cooldowns[provider] = max(previous_until, until)
    remaining = _provider_cooldown_remaining(provider)
    _price_log(f"[Price API] {provider} cooldown {remaining:.1f}s ({reason})")


def _retry_delay(attempt: int) -> float:
    if PRICE_FETCH_BACKOFF_BASE_SECONDS <= 0:
        return 0.0
    base = PRICE_FETCH_BACKOFF_BASE_SECONDS * (2 ** attempt)
    return base + random.uniform(0.0, base * 0.25)


def _request_json_with_retry(
    provider: str,
    method: str,
    url: str,
    *,
    params: Optional[dict] = None,
    json_payload: Optional[dict] = None,
) -> object:
    remaining = _provider_cooldown_remaining(provider)
    if remaining > 0:
        raise RuntimeError(f"{provider} cooldown active for {remaining:.1f}s")

    last_exc: Optional[Exception] = None
    attempts = PRICE_FETCH_MAX_RETRIES + 1

    for attempt in range(attempts):
        try:
            if method == "POST":
                resp = requests.post(url, json=json_payload, timeout=PRICE_FETCH_TIMEOUT_SECONDS)
            else:
                resp = requests.get(url, params=params, timeout=PRICE_FETCH_TIMEOUT_SECONDS)

            if resp.status_code in _RETRYABLE_STATUS_CODES:
                resp.raise_for_status()

            resp.raise_for_status()
            return resp.json()
        except requests.HTTPError as exc:
            status_code = exc.response.status_code if exc.response is not None else None
            retryable = status_code in _RETRYABLE_STATUS_CODES
            last_exc = exc

            if retryable and attempt < attempts - 1:
                delay = _retry_delay(attempt)
                _price_log(
                    f"[Price API] {provider} retry {attempt + 1}/{attempts - 1} "
                    f"after HTTP {status_code}; sleeping {delay:.2f}s"
                )
                if delay > 0:
                    time.sleep(delay)
                continue

            if status_code == 429:
                _activate_provider_cooldown(
                    provider,
                    PRICE_FETCH_RATE_LIMIT_COOLDOWN_SECONDS,
                    "HTTP 429"
                )
            elif status_code is not None and status_code >= 500:
                _activate_provider_cooldown(
                    provider,
                    PRICE_FETCH_ERROR_COOLDOWN_SECONDS,
                    f"HTTP {status_code}"
                )
            raise
        except (requests.Timeout, requests.ConnectionError) as exc:
            last_exc = exc
            if attempt < attempts - 1:
                delay = _retry_delay(attempt)
                _price_log(
                    f"[Price API] {provider} retry {attempt + 1}/{attempts - 1} "
                    f"after {exc.__class__.__name__}; sleeping {delay:.2f}s"
                )
                if delay > 0:
                    time.sleep(delay)
                continue
            _activate_provider_cooldown(
                provider,
                PRICE_FETCH_ERROR_COOLDOWN_SECONDS,
                exc.__class__.__name__
            )
            raise
        except requests.RequestException as exc:
            last_exc = exc
            raise

    if last_exc is not None:
        raise last_exc
    raise RuntimeError(f"{provider} request failed without response")


def _polymarket_market_title(market: Optional[dict]) -> Optional[str]:
    if not isinstance(market, dict):
        return None
    for key in ("question", "title", "description", "slug"):
        value = market.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def describe_polymarket_contract(reference: str, token_id: Optional[str] = None, outcome: Optional[str] = None) -> Optional[dict]:
    """
    Return human-readable Polymarket metadata for UI/documentation.
    """
    contract = _polymarket_resolve_reference(reference, token_id=token_id, outcome=outcome)
    if not contract:
        return None

    market = contract.get("market")
    resolved_outcome = contract.get("outcome")
    market_title = _polymarket_market_title(market)
    market_slug = market.get("slug") if isinstance(market, dict) else None
    display_title = market_title or market_slug or reference
    if resolved_outcome:
        display_title = f"{display_title} [{resolved_outcome}]"

    return {
        "token_id": contract.get("token_id"),
        "outcome": resolved_outcome,
        "market_title": market_title,
        "market_slug": market_slug,
        "display_title": display_title,
    }

def _parse_executed_at_to_utc(executed_at: str) -> Optional[datetime]:
    """
    Parse executed_at into an aware UTC datetime.
    Accepts:
    - 2026-03-07T14:30:00Z
    - 2026-03-07T14:30:00+00:00
    - 2026-03-07T14:30:00   (treated as UTC)
    """
    try:
        cleaned = executed_at.strip()
        if cleaned.endswith("Z"):
            cleaned = cleaned.replace("Z", "+00:00")
        dt = datetime.fromisoformat(cleaned)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=UTC)
        return dt.astimezone(UTC)
    except Exception:
        return None


def _normalize_hyperliquid_symbol(symbol: str) -> str:
    """
    Best-effort normalization for Hyperliquid 'coin' identifiers.
    Examples:
    - 'btc' -> 'BTC'
    - 'BTC-USD' -> 'BTC'
    - 'BTC/USD' -> 'BTC'
    - 'BTC-PERP' -> 'BTC'
    - 'xyz:NVDA' -> 'xyz:NVDA' (keep dex-prefixed builder listings)
    """
    raw = symbol.strip()
    if ":" in raw:
        return raw  # builder/dex symbols are case sensitive upstream; keep as-is

    s = raw.upper()
    for suffix in ("-PERP", "PERP"):
        if s.endswith(suffix):
            s = s[: -len(suffix)]
            break

    for sep in ("-USD", "/USD"):
        if s.endswith(sep):
            s = s[: -len(sep)]
            break

    for sep in ("-USDT", "/USDT"):
        if s.endswith(sep):
            s = s[: -len(sep)]
            break

    if s.endswith("USDT") and len(s) > len("USDT"):
        s = s[: -len("USDT")]

    return s.strip()


def _hyperliquid_post(payload: dict) -> object:
    if not HYPERLIQUID_API_URL:
        raise RuntimeError("HYPERLIQUID_API_URL is empty")
    return _request_json_with_retry(
        "hyperliquid",
        "POST",
        HYPERLIQUID_API_URL,
        json_payload=payload,
    )


def _get_hyperliquid_available_symbols() -> Optional[set[str]]:
    global _hyperliquid_symbol_cache

    cached_symbols, expires_at = _hyperliquid_symbol_cache
    now = time.time()
    if expires_at > now:
        return cached_symbols

    try:
        data = _hyperliquid_post({"type": "meta"})
    except Exception:
        _hyperliquid_symbol_cache = (None, now + 30.0)
        return None

    symbols: set[str] = set()
    if isinstance(data, dict):
        universe = data.get("universe")
        if isinstance(universe, list):
            for asset in universe:
                if isinstance(asset, dict):
                    name = str(asset.get("name") or "").strip()
                    if name:
                        symbols.add(name)

    _hyperliquid_symbol_cache = (symbols or None, now + HYPERLIQUID_SYMBOL_CACHE_TTL_SECONDS)
    return symbols or None


def _hyperliquid_symbol_available(coin: str) -> bool:
    symbols = _get_hyperliquid_available_symbols()
    if symbols is None:
        return True
    return coin in symbols


def _polymarket_get_json(url: str, params: Optional[dict] = None) -> object:
    return _request_json_with_retry(
        "polymarket",
        "GET",
        url,
        params=params,
    )


def _parse_string_array(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(v).strip() for v in value if isinstance(v, (str, int)) and str(v).strip()]
    if isinstance(value, str) and value.strip().startswith("["):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return [str(v).strip() for v in parsed if isinstance(v, (str, int)) and str(v).strip()]
        except Exception:
            return []
    return []


def _polymarket_fetch_market(reference: str, token_id: Optional[str] = None) -> Optional[dict]:
    if not POLYMARKET_GAMMA_BASE_URL:
        return None

    ref = (reference or "").strip()
    requested_token_id = (token_id or "").strip()
    if not ref and not requested_token_id:
        return None

    cache_key = f"{ref}::{requested_token_id}"
    now = time.time()
    cached = _polymarket_market_cache.get(cache_key)
    if cached and cached[1] > now:
        return cached[0]

    url = f"{POLYMARKET_GAMMA_BASE_URL.rstrip('/')}/markets"
    params = {"limit": "1"}
    if requested_token_id and _POLYMARKET_TOKEN_ID_RE.match(requested_token_id):
        params["clob_token_ids"] = requested_token_id
    elif _POLYMARKET_CONDITION_ID_RE.match(ref):
        params["conditionId"] = ref
    elif _POLYMARKET_TOKEN_ID_RE.match(ref):
        params["clob_token_ids"] = ref
    else:
        params["slug"] = ref

    try:
        raw = _polymarket_get_json(url, params=params)
    except Exception:
        _polymarket_market_cache[cache_key] = (None, now + 60.0)
        return None

    if not isinstance(raw, list) or not raw or not isinstance(raw[0], dict):
        _polymarket_market_cache[cache_key] = (None, now + _POLYMARKET_MARKET_CACHE_TTL_S)
        return None
    market = raw[0]
    _polymarket_market_cache[cache_key] = (market, now + _POLYMARKET_MARKET_CACHE_TTL_S)
    return market


def _polymarket_extract_tokens(market: dict) -> list[dict[str, Optional[str]]]:
    token_ids = _parse_string_array(market.get("clobTokenIds")) or _parse_string_array(market.get("clob_token_ids"))
    outcomes = _parse_string_array(market.get("outcomes"))
    extracted: list[dict[str, Optional[str]]] = []
    for idx, token_id in enumerate(token_ids):
        if token_id and _POLYMARKET_TOKEN_ID_RE.match(token_id):
            extracted.append({
                "token_id": token_id,
                "outcome": outcomes[idx] if idx < len(outcomes) else None,
            })
    return extracted


def _polymarket_resolve_reference(reference: str, token_id: Optional[str] = None, outcome: Optional[str] = None) -> Optional[dict]:
    """
    Resolve a Polymarket reference into an explicit outcome token.

    For ambiguous references (slug/condition with multiple outcomes), caller must provide
    either `token_id` or `outcome`.
    """
    ref = (reference or "").strip()
    if not ref:
        return None

    requested_token_id = (token_id or "").strip()
    requested_outcome = (outcome or "").strip().lower()
    cache_key = f"{ref}::{(token_id or '').strip().lower()}::{(outcome or '').strip().lower()}"
    cached = _polymarket_token_cache.get(cache_key)
    now = time.time()
    if cached and cached[1] > now:
        return {
            "token_id": cached[0],
            "outcome": outcome,
            "market": _polymarket_fetch_market(ref, token_id=requested_token_id),
        }

    market = _polymarket_fetch_market(ref, token_id=requested_token_id)
    if not market:
        return None

    tokens = _polymarket_extract_tokens(market)

    selected = None
    if requested_token_id and _POLYMARKET_TOKEN_ID_RE.match(requested_token_id):
        for candidate in tokens:
            if candidate["token_id"] == requested_token_id:
                selected = candidate
                break
        if selected is None and not tokens:
            selected = {"token_id": requested_token_id, "outcome": outcome}
    if selected is None and _POLYMARKET_TOKEN_ID_RE.match(ref):
        selected = {"token_id": ref, "outcome": outcome}
    if selected is None and requested_outcome:
        for candidate in tokens:
            if (candidate.get("outcome") or "").strip().lower() == requested_outcome:
                selected = candidate
                break
    if selected is None and len(tokens) == 1:
        selected = tokens[0]

    if not selected or not selected.get("token_id"):
        return None

    resolved_token_id = str(selected["token_id"])
    _polymarket_token_cache[cache_key] = (resolved_token_id, now + _POLYMARKET_TOKEN_CACHE_TTL_S)
    return {
        "token_id": resolved_token_id,
        "outcome": selected.get("outcome"),
        "market": market,
    }


def _get_polymarket_mid_price(reference: str, token_id: Optional[str] = None, outcome: Optional[str] = None) -> Optional[float]:
    """
    Fetch a mid price for a Polymarket outcome token.
    Price is derived from best bid/ask in the CLOB orderbook.
    """
    if not POLYMARKET_CLOB_BASE_URL:
        return None

    contract = _polymarket_resolve_reference(reference, token_id=token_id, outcome=outcome)
    if not contract:
        return None
    resolved_token_id = contract["token_id"]

    url = f"{POLYMARKET_CLOB_BASE_URL.rstrip('/')}/book"
    data = None
    try:
        data = _polymarket_get_json(url, params={"token_id": resolved_token_id})
    except Exception:
        data = None

    if isinstance(data, dict):
        bids = data.get("bids") if isinstance(data.get("bids"), list) else []
        asks = data.get("asks") if isinstance(data.get("asks"), list) else []

        def _best_px(levels: list) -> Optional[float]:
            if not levels:
                return None
            first = levels[0]
            if isinstance(first, dict) and "price" in first:
                try:
                    return float(first["price"])
                except Exception:
                    return None
            return None

        best_bid = _best_px(bids)
        best_ask = _best_px(asks)
        if best_bid is not None or best_ask is not None:
            mid = (best_bid + best_ask) / 2 if (best_bid is not None and best_ask is not None) else (best_bid if best_bid is not None else best_ask)
            mid = float(f"{mid:.6f}")
            if _polymarket_price_valid(mid):
                return mid
            return None

    # Fallback: use Gamma market fields when CLOB orderbook is missing.
    market = contract.get("market")
    if not isinstance(market, dict):
        return None
    try:
        outcome_prices = _parse_string_array(market.get("outcomePrices"))
        outcomes = _parse_string_array(market.get("outcomes"))
        target_outcome = (contract.get("outcome") or "").strip().lower()
        if target_outcome and outcome_prices and outcomes:
            for idx, label in enumerate(outcomes):
                if label.strip().lower() == target_outcome and idx < len(outcome_prices):
                    p = float(f"{float(outcome_prices[idx]):.6f}")
                    if _polymarket_price_valid(p):
                        return p
        for key in ("lastTradePrice", "outcomePrice"):
            v = market.get(key)
            if isinstance(v, (int, float)):
                p = float(f"{float(v):.6f}")
                if _polymarket_price_valid(p):
                    return p
            if isinstance(v, str) and v.strip():
                try:
                    p = float(f"{float(v):.6f}")
                    if _polymarket_price_valid(p):
                        return p
                except Exception:
                    pass
    except Exception:
        pass

    return None


def _polymarket_resolve(reference: str, token_id: Optional[str] = None, outcome: Optional[str] = None) -> Optional[dict]:
    """
    Resolve a Polymarket market via Gamma.
    Returns dict: { resolved: bool, outcome: Optional[str], settlementPrice: Optional[float] } or None.
    """
    contract = _polymarket_resolve_reference(reference, token_id=token_id, outcome=outcome)
    if not contract:
        return None
    market = contract.get("market")
    if not isinstance(market, dict):
        return None

    resolved_flag = bool(market.get("resolved"))
    resolved_outcome = market.get("outcome") if isinstance(market.get("outcome"), str) else None
    settlement_raw = market.get("settlementPrice")
    settlement_price = None
    if isinstance(settlement_raw, (int, float)):
        settlement_price = float(settlement_raw)
    elif isinstance(settlement_raw, str) and settlement_raw.strip():
        try:
            settlement_price = float(settlement_raw)
        except Exception:
            settlement_price = None
    if settlement_price is not None and not _polymarket_price_valid(settlement_price):
        settlement_price = None

    return {
        "resolved": resolved_flag,
        "token_id": contract.get("token_id"),
        "outcome": contract.get("outcome"),
        "market_slug": market.get("slug"),
        "resolved_outcome": resolved_outcome,
        "settlementPrice": settlement_price,
    }


def _get_hyperliquid_mid_price(symbol: str) -> Optional[float]:
    """
    Fetch mid price from Hyperliquid L2 book.
    This is used for 'now' style queries.
    """
    coin = _normalize_hyperliquid_symbol(symbol)
    if not _hyperliquid_symbol_available(coin):
        _price_log(f"[Price API] Hyperliquid symbol not listed: {symbol} -> {coin}")
        return None

    data = _hyperliquid_post({"type": "l2Book", "coin": coin})
    if not isinstance(data, dict) or "levels" not in data:
        return None
    levels = data.get("levels")
    if not isinstance(levels, list) or len(levels) < 2:
        return None
    bids = levels[0] if isinstance(levels[0], list) else []
    asks = levels[1] if isinstance(levels[1], list) else []
    best_bid = None
    best_ask = None
    if bids and isinstance(bids[0], dict) and "px" in bids[0]:
        try:
            best_bid = float(bids[0]["px"])
        except Exception:
            best_bid = None
    if asks and isinstance(asks[0], dict) and "px" in asks[0]:
        try:
            best_ask = float(asks[0]["px"])
        except Exception:
            best_ask = None
    if best_bid is None and best_ask is None:
        return None
    if best_bid is not None and best_ask is not None:
        return float(f"{((best_bid + best_ask) / 2):.6f}")
    return float(f"{(best_bid if best_bid is not None else best_ask):.6f}")


def _get_hyperliquid_candle_close(symbol: str, executed_at: str) -> Optional[float]:
    """
    Fetch a 1m candle around executed_at via candleSnapshot and return the closest close.
    This approximates "price at time" without requiring any private keys.
    """
    dt = _parse_executed_at_to_utc(executed_at)
    if not dt:
        return None

    # Query a small window around the target time (±10 minutes)
    target_ms = int(dt.timestamp() * 1000)
    start_ms = target_ms - 10 * 60 * 1000
    end_ms = target_ms + 10 * 60 * 1000

    coin = _normalize_hyperliquid_symbol(symbol)
    if not _hyperliquid_symbol_available(coin):
        _price_log(f"[Price API] Hyperliquid symbol not listed: {symbol} -> {coin}")
        return None

    payload = {
        "type": "candleSnapshot",
        "req": {
            "coin": coin,
            "interval": "1m",
            "startTime": start_ms,
            "endTime": end_ms,
        },
    }
    data = _hyperliquid_post(payload)
    if not isinstance(data, list) or len(data) == 0:
        return None

    closest = None
    closest_ts = None
    for candle in data:
        if not isinstance(candle, dict):
            continue
        t = candle.get("t")
        c = candle.get("c")
        if t is None or c is None:
            continue
        try:
            t_ms = int(float(t))
            close = float(c)
        except Exception:
            continue
        if t_ms > target_ms:
            continue
        if closest_ts is None or t_ms > closest_ts:
            closest_ts = t_ms
            closest = close

    if closest is None:
        return None
    return float(f"{closest:.6f}")


def get_price_from_market(
    symbol: str,
    executed_at: str,
    market: str,
    token_id: Optional[str] = None,
    outcome: Optional[str] = None,
) -> Optional[float]:
    """
    根据市场获取价格

    Args:
        symbol: 股票代码
        executed_at: 执行时间 (ISO 8601 格式)
        market: 市场类型 (us-stock, crypto)

    Returns:
        查询到的价格，如果失败返回 None
    """
    try:
        try:
            from routes_shared import normalize_market

            market = normalize_market(market)
        except Exception:
            market = (market or "").strip().lower()

        if market == "crypto":
            # Crypto pricing now uses Hyperliquid public endpoints.
            # Try historical candle (when executed_at is provided), then fall back to mid price.
            price = _get_hyperliquid_candle_close(symbol, executed_at) or _get_hyperliquid_mid_price(symbol)
        elif market == "polymarket":
            # Polymarket pricing uses public Gamma + CLOB endpoints.
            # We use the current orderbook mid price (paper trading).
            price = _get_polymarket_mid_price(symbol, token_id=token_id, outcome=outcome)
        elif market == "us-stock":
            if not ALPHA_VANTAGE_API_KEY or ALPHA_VANTAGE_API_KEY == "demo":
                _price_log("Warning: ALPHA_VANTAGE_API_KEY not set, using agent-provided price")
                return None
            price = _get_us_stock_price(symbol, executed_at)
        else:
            _price_log(f"[Price API] Unsupported market for server price fetch: {market}")
            return None

        if price is None:
            _price_log(f"[Price API] Failed to fetch {symbol} ({market}) price for time {executed_at}")
        else:
            _price_log(f"[Price API] Successfully fetched {symbol} ({market}): ${price}")

        return price
    except Exception as e:
        _price_log(f"[Price API] Error fetching {symbol} ({market}): {e}")
        return None


def _try_intraday_price(symbol: str, dt_et: datetime) -> Optional[float]:
    """尝试使用 TIME_SERIES_INTRADAY 端点获取价格（高级端点）"""
    month = dt_et.strftime("%Y-%m")

    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": "1min",
        "month": month,
        "outputsize": "compact",
        "entitlement": "realtime",
        "apikey": ALPHA_VANTAGE_API_KEY
    }

    try:
        data = _request_json_with_retry(
            "alphavantage",
            "GET",
            BASE_URL,
            params=params,
        )

        if "Error Message" in data:
            _price_log(f"[Price API] TIME_SERIES_INTRADAY Error: {data.get('Error Message')}")
            return None
        if "Note" in data:
            _activate_provider_cooldown(
                "alphavantage",
                PRICE_FETCH_RATE_LIMIT_COOLDOWN_SECONDS,
                "body rate limit note"
            )
            _price_log(f"[Price API] Rate limit: {data.get('Note')}")
            return None

        time_series_key = "Time Series (1min)"
        if time_series_key not in data:
            _price_log(f"[Price API] No time series data for {symbol}")
            return None

        time_series = data[time_series_key]
        target_datetime = dt_et.strftime("%Y-%m-%d %H:%M:%S")

        if target_datetime in time_series:
            return float(time_series[target_datetime].get("4. close", 0))

        min_diff = float('inf')
        closest_price = None

        for time_key, values in time_series.items():
            time_dt = datetime.strptime(time_key, "%Y-%m-%d %H:%M:%S").replace(tzinfo=ET_TZ)
            if time_dt <= dt_et:
                diff = (dt_et - time_dt).total_seconds()
                if diff < min_diff:
                    min_diff = diff
                    closest_price = float(values.get("4. close", 0))

        if closest_price:
            _price_log(f"[Price API] Found closest price for {symbol}: ${closest_price} ({int(min_diff)}s earlier)")
        return closest_price

    except Exception as e:
        _price_log(f"[Price API] Exception in TIME_SERIES_INTRADAY for {symbol}: {e}")
        return None


def _try_global_quote_price(symbol: str) -> Optional[float]:
    """使用 GLOBAL_QUOTE 端点获取价格（免费端点）"""
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": ALPHA_VANTAGE_API_KEY
    }

    try:
        data = _request_json_with_retry(
            "alphavantage",
            "GET",
            BASE_URL,
            params=params,
        )

        if "Error Message" in data:
            _price_log(f"[Price API] GLOBAL_QUOTE Error: {data.get('Error Message')}")
            return None
        if "Note" in data:
            _activate_provider_cooldown(
                "alphavantage",
                PRICE_FETCH_RATE_LIMIT_COOLDOWN_SECONDS,
                "body rate limit note"
            )
            _price_log(f"[Price API] Rate limit: {data.get('Note')}")
            return None

        global_quote = data.get("Global Quote", {})
        if not isinstance(global_quote, dict):
            return None

        price_str = global_quote.get("05. price")
        if price_str:
            try:
                price = float(price_str)
                _price_log(f"[Price API] GLOBAL_QUOTE price for {symbol}: ${price}")
                return price
            except (ValueError, TypeError):
                pass

        return None

    except Exception as e:
        _price_log(f"[Price API] Exception in GLOBAL_QUOTE for {symbol}: {e}")
        return None


def _get_us_stock_price(symbol: str, executed_at: str) -> Optional[float]:
    """获取美股价格（带缓存和 API 回退）"""
    # 先检查缓存
    cache_key = _price_cache_key(symbol, "us-stock")
    now = time.time()
    
    # 检查本地缓存是否存在（无论值是多少）
    if cache_key in _local_price_cache:
        cached_price, expires_at = _local_price_cache[cache_key]
        if expires_at > now:
            if cached_price is not None:
                _price_log(f"[Price Cache] Using cached price for {symbol}: ${cached_price}")
            else:
                _price_log(f"[Price Cache] Using cached failure for {symbol}")
            return cached_price
        else:
            del _local_price_cache[cache_key]
    
    # 检查 Redis 缓存
    redis_client = _get_redis_client()
    if redis_client is not None:
        try:
            cached_value = redis_client.get(cache_key)
            if cached_value is not None:
                try:
                    cached_price = float(cached_value) if cached_value != "null" else None
                    ttl = redis_client.ttl(cache_key)
                    if ttl > 0:
                        _local_price_cache[cache_key] = (cached_price, now + ttl)
                    if cached_price is not None:
                        _price_log(f"[Price Cache] Redis cache hit for {symbol}: ${cached_price}")
                    else:
                        _price_log(f"[Price Cache] Redis cache hit (failure) for {symbol}")
                    return cached_price
                except Exception:
                    pass
        except Exception as e:
            _price_log(f"[Price Cache] Redis get error: {e}")

    # 解析时间
    try:
        dt_utc = datetime.fromisoformat(executed_at.replace('Z', '')).replace(tzinfo=UTC)
        dt_et = dt_utc.astimezone(ET_TZ)
    except ValueError:
        _price_cache_set(symbol, "us-stock", None)
        return None

    # 先尝试 TIME_SERIES_INTRADAY（高级端点）
    price = _try_intraday_price(symbol, dt_et)
    if price is not None:
        _price_cache_set(symbol, "us-stock", price)
        return price

    # 回退到 GLOBAL_QUOTE（免费端点）
    _price_log(f"[Price API] Falling back to GLOBAL_QUOTE for {symbol}")
    price = _try_global_quote_price(symbol)
    
    # 缓存结果（成功或失败）
    _price_cache_set(symbol, "us-stock", price)
    
    return price


def _get_crypto_price(symbol: str, executed_at: str) -> Optional[float]:
    """
    Backwards-compat shim.
    AI-Trader 已停止使用 Alpha Vantage 的 crypto 端点；此函数保留仅为避免旧代码引用时报错。
    """
    return _get_hyperliquid_candle_close(symbol, executed_at) or _get_hyperliquid_mid_price(symbol)
