from __future__ import annotations

from typing import Optional

from fastapi import FastAPI, Header

from market_intel import (
    get_etf_flows_payload,
    get_featured_stock_analysis_payload,
    get_macro_signals_payload,
    get_market_intel_overview,
    get_market_news_payload,
    get_stock_analysis_history_payload,
    get_stock_analysis_latest_payload,
)
from routes_shared import (
    MARKET_INTEL_CACHE_KEY_PREFIX,
    MARKET_INTEL_CACHE_TTL_SECONDS,
    RouteContext,
    attach_experiment_unread_notice,
    get_short_cached_payload,
    set_short_cached_payload,
    utc_now_iso_z,
)
from services import _get_agent_by_token
from tasks import refresh_prices_once
from utils import _extract_token
from price_fetcher import (
    _get_cache_stats,
    _reset_cache_stats,
    _clear_expired_cache,
    _warmup_cache
)


def register_market_routes(app: FastAPI, ctx: RouteContext) -> None:
    def _attach_agent_notice(payload: dict, authorization: str | None, *, surface: str) -> dict:
        token = _extract_token(authorization)
        agent = _get_agent_by_token(token)
        if not agent:
            return payload
        return attach_experiment_unread_notice(dict(payload), agent['id'], surface=surface, ctx=ctx)

    def _cached_market_payload(cache_key: str, builder):
        redis_key = f'{MARKET_INTEL_CACHE_KEY_PREFIX}:{cache_key}'
        cached = get_short_cached_payload(ctx, ctx.market_intel_cache, redis_key, MARKET_INTEL_CACHE_TTL_SECONDS)
        if isinstance(cached, dict):
            return cached
        payload = builder()
        return set_short_cached_payload(
            ctx,
            ctx.market_intel_cache,
            redis_key,
            payload,
            MARKET_INTEL_CACHE_TTL_SECONDS,
        )

    @app.get('/health')
    async def health_check():
        return {'status': 'ok', 'timestamp': utc_now_iso_z()}

    @app.post('/api/refresh-prices')
    async def refresh_prices():
        """手动刷新所有持仓价格"""
        result = await refresh_prices_once()
        return result

    @app.get('/api/cache-stats')
    async def get_cache_statistics():
        """获取价格缓存统计信息"""
        stats = _get_cache_stats()
        return {
            "success": True,
            "data": stats
        }

    @app.post('/api/cache-stats/reset')
    async def reset_cache_statistics():
        """重置价格缓存统计"""
        _reset_cache_stats()
        return {
            "success": True,
            "message": "Cache statistics reset successfully"
        }

    @app.post('/api/cache/cleanup')
    async def cleanup_expired_cache():
        """清除过期的缓存项"""
        cleared_count = _clear_expired_cache()
        return {
            "success": True,
            "cleared_count": cleared_count,
            "message": f"Cleared {cleared_count} expired cache entries"
        }

    @app.post('/api/cache/warmup')
    async def warmup_cache_endpoint(symbols: Optional[str] = None):
        """预热缓存
        
        Args:
            symbols: 可选，逗号分隔的股票符号列表，如 "AAPL,MSFT,GOOGL"
        """
        symbol_list = None
        if symbols:
            symbol_list = [s.strip() for s in symbols.split(",") if s.strip()]
        
        result = _warmup_cache(symbol_list)
        return {
            "success": True,
            "data": result
        }

    @app.get('/api/market-intel/overview')
    async def market_intel_overview(authorization: str = Header(None)):
        payload = _cached_market_payload('overview', get_market_intel_overview)
        return _attach_agent_notice(payload, authorization, surface='market_intel_overview')

    @app.get('/api/market-intel/news')
    async def market_intel_news(
        category: Optional[str] = None,
        limit: int = 5,
        authorization: str = Header(None),
    ):
        safe_limit = max(1, min(limit, 12))
        category_key = (category or 'all').strip() or 'all'
        payload = _cached_market_payload(
            f'news:category={category_key}:limit={safe_limit}',
            lambda: get_market_news_payload(category=category, limit=safe_limit),
        )
        return _attach_agent_notice(payload, authorization, surface='market_intel_news')

    @app.get('/api/market-intel/macro-signals')
    async def market_intel_macro_signals(authorization: str = Header(None)):
        payload = _cached_market_payload('macro_signals', get_macro_signals_payload)
        return _attach_agent_notice(payload, authorization, surface='market_intel_macro_signals')

    @app.get('/api/market-intel/etf-flows')
    async def market_intel_etf_flows(authorization: str = Header(None)):
        payload = _cached_market_payload('etf_flows', get_etf_flows_payload)
        return _attach_agent_notice(payload, authorization, surface='market_intel_etf_flows')

    @app.get('/api/market-intel/stocks/featured')
    async def market_intel_featured_stocks(limit: int = 6, authorization: str = Header(None)):
        safe_limit = max(1, min(limit, 12))
        payload = _cached_market_payload(
            f'stocks_featured:limit={safe_limit}',
            lambda: get_featured_stock_analysis_payload(limit=safe_limit),
        )
        return _attach_agent_notice(payload, authorization, surface='market_intel_stocks_featured')

    @app.get('/api/market-intel/stocks/{symbol}/latest')
    async def market_intel_stock_latest(symbol: str, authorization: str = Header(None)):
        normalized_symbol = (symbol or '').strip().upper()
        payload = _cached_market_payload(
            f'stock_latest:symbol={normalized_symbol}',
            lambda: get_stock_analysis_latest_payload(normalized_symbol),
        )
        return _attach_agent_notice(payload, authorization, surface='market_intel_stock_latest')

    @app.get('/api/market-intel/stocks/{symbol}/history')
    async def market_intel_stock_history(symbol: str, limit: int = 10, authorization: str = Header(None)):
        safe_limit = max(1, min(limit, 50))
        normalized_symbol = (symbol or '').strip().upper()
        payload = _cached_market_payload(
            f'stock_history:symbol={normalized_symbol}:limit={safe_limit}',
            lambda: get_stock_analysis_history_payload(normalized_symbol, limit=safe_limit),
        )
        return _attach_agent_notice(payload, authorization, surface='market_intel_stock_history')
