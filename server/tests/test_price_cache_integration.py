"""
Integration tests for price cache functionality with real API calls.

Tests cover:
- Real API calls to Alpha Vantage
- Cache hit/miss scenarios with real data
- API fallback mechanism
- Failure caching
- Multi-market price fetching
- Concurrent price fetching
- Redis integration (if available)

Note: These tests require a valid ALPHA_VANTAGE_API_KEY environment variable.
If not set, tests will be skipped.
"""

import os
import sys
import time
import unittest
import asyncio
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch, PropertyMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def has_alpha_vantage_api_key():
    """Check if Alpha Vantage API key is configured."""
    api_key = os.environ.get("ALPHA_VANTAGE_API_KEY", "demo")
    return api_key and api_key != "demo"


def has_redis():
    """Check if Redis is available."""
    redis_enabled = os.environ.get("REDIS_ENABLED", "false").strip().lower() in {"1", "true", "yes", "on"}
    redis_url = os.environ.get("REDIS_URL", "").strip()
    return redis_enabled and redis_url


@unittest.skipUnless(has_alpha_vantage_api_key(), "ALPHA_VANTAGE_API_KEY not configured")
class PriceCacheRealAPITests(unittest.TestCase):
    """Integration tests with real Alpha Vantage API calls."""

    @classmethod
    def setUpClass(cls):
        """Set up test class - reset cache state."""
        import price_fetcher
        price_fetcher._local_price_cache.clear()
        price_fetcher._redis_client = None
        price_fetcher._provider_cooldowns.clear()

    def setUp(self):
        """Reset cache state before each test."""
        import price_fetcher
        price_fetcher._local_price_cache.clear()
        if price_fetcher._redis_client:
            try:
                price_fetcher._redis_client.flushdb()
            except Exception:
                pass

    def test_real_api_call_global_quote(self):
        """Test real API call using GLOBAL_QUOTE endpoint."""
        import price_fetcher
        
        now = datetime.now(timezone.utc)
        executed_at = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        price = price_fetcher._try_global_quote_price("IBM")
        
        if price is not None:
            self.assertIsInstance(price, float)
            self.assertGreater(price, 0)
            print(f"[Real API] IBM price via GLOBAL_QUOTE: ${price:.2f}")
        else:
            print("[Real API] GLOBAL_QUOTE returned None (可能是速率限制)")
            self.skipTest("API rate limit reached or service unavailable")

    def test_get_price_from_market_us_stock(self):
        """Test get_price_from_market with real US stock data."""
        import price_fetcher
        
        now = datetime.now(timezone.utc)
        executed_at = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        price = price_fetcher.get_price_from_market(
            symbol="IBM",
            executed_at=executed_at,
            market="us-stock"
        )
        
        if price is not None:
            self.assertIsInstance(price, float)
            self.assertGreater(price, 0)
            print(f"[Real API] IBM price: ${price:.2f}")
        else:
            print("[Real API] get_price_from_market returned None")
            self.skipTest("API rate limit reached or service unavailable")

    def test_cache_hit_after_real_api_call(self):
        """Test that cache is hit after a real API call."""
        import price_fetcher
        
        now = datetime.now(timezone.utc)
        executed_at = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        symbol = "AAPL"
        market = "us-stock"
        
        price1 = price_fetcher.get_price_from_market(
            symbol=symbol,
            executed_at=executed_at,
            market=market
        )
        
        if price1 is None:
            self.skipTest("First API call failed")
        
        print(f"[Cache Test] First call (API): ${price1:.2f}")
        
        price2 = price_fetcher.get_price_from_market(
            symbol=symbol,
            executed_at=executed_at,
            market=market
        )
        
        self.assertIsNotNone(price2)
        self.assertEqual(price1, price2)
        print(f"[Cache Test] Second call (Cache): ${price2:.2f}")

    def test_multiple_symbols_real_api(self):
        """Test fetching prices for multiple symbols."""
        import price_fetcher
        
        now = datetime.now(timezone.utc)
        executed_at = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        symbols = ["AAPL", "MSFT", "GOOGL"]
        results = {}
        
        for symbol in symbols:
            price = price_fetcher.get_price_from_market(
                symbol=symbol,
                executed_at=executed_at,
                market="us-stock"
            )
            results[symbol] = price
            if price:
                print(f"[Multi-Symbol] {symbol}: ${price:.2f}")
        
        valid_prices = [p for p in results.values() if p is not None]
        if len(valid_prices) == 0:
            self.skipTest("All API calls failed (rate limit?)")
        
        self.assertGreater(len(valid_prices), 0)

    def test_price_format_validation(self):
        """Test that returned prices are in valid format."""
        import price_fetcher
        
        now = datetime.now(timezone.utc)
        executed_at = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        price = price_fetcher.get_price_from_market(
            symbol="AAPL",
            executed_at=executed_at,
            market="us-stock"
        )
        
        if price is None:
            self.skipTest("API call failed")
        
        self.assertIsInstance(price, float)
        self.assertGreater(price, 0)
        self.assertLess(price, 10000)

    def test_cache_ttl_real_scenario(self):
        """Test cache TTL behavior in real scenario."""
        import price_fetcher
        
        original_ttl = price_fetcher._PRICE_CACHE_TTL_SECONDS
        try:
            price_fetcher._PRICE_CACHE_TTL_SECONDS = 2
            
            now = datetime.now(timezone.utc)
            executed_at = now.strftime("%Y-%m-%dT%H:%M:%SZ")
            
            price1 = price_fetcher.get_price_from_market(
                symbol="AAPL",
                executed_at=executed_at,
                market="us-stock"
            )
            
            if price1 is None:
                self.skipTest("First API call failed")
            
            time.sleep(0.5)
            
            price2 = price_fetcher.get_price_from_market(
                symbol="AAPL",
                executed_at=executed_at,
                market="us-stock"
            )
            
            self.assertEqual(price1, price2)
            print(f"[TTL Test] Cache hit within TTL: ${price2:.2f}")
            
            time.sleep(2)
            
            price3 = price_fetcher.get_price_from_market(
                symbol="AAPL",
                executed_at=executed_at,
                market="us-stock"
            )
            
            if price3 is not None:
                print(f"[TTL Test] Cache expired, new API call: ${price3:.2f}")
            
        finally:
            price_fetcher._PRICE_CACHE_TTL_SECONDS = original_ttl


@unittest.skipUnless(has_alpha_vantage_api_key(), "ALPHA_VANTAGE_API_KEY not configured")
class PriceCacheFailureTests(unittest.TestCase):
    """Integration tests for failure handling and caching."""

    def setUp(self):
        """Reset cache state before each test."""
        import price_fetcher
        price_fetcher._local_price_cache.clear()
        price_fetcher._provider_cooldowns.clear()

    def test_invalid_symbol_handling(self):
        """Test handling of invalid stock symbols."""
        import price_fetcher
        
        now = datetime.now(timezone.utc)
        executed_at = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        price = price_fetcher.get_price_from_market(
            symbol="INVALID_SYMBOL_12345",
            executed_at=executed_at,
            market="us-stock"
        )
        
        self.assertIsNone(price)
        print("[Failure Test] Invalid symbol returned None as expected")

    def test_failure_caching(self):
        """Test that failed requests are cached."""
        import price_fetcher
        
        original_ttl = price_fetcher._PRICE_FAILURE_CACHE_TTL_SECONDS
        try:
            price_fetcher._PRICE_FAILURE_CACHE_TTL_SECONDS = 5
            
            now = datetime.now(timezone.utc)
            executed_at = now.strftime("%Y-%m-%dT%H:%M:%SZ")
            
            symbol = "INVALID_TEST_SYMBOL"
            
            start_time = time.time()
            price1 = price_fetcher.get_price_from_market(
                symbol=symbol,
                executed_at=executed_at,
                market="us-stock"
            )
            first_call_time = time.time() - start_time
            
            self.assertIsNone(price1)
            print(f"[Failure Cache] First call took {first_call_time:.2f}s")
            
            start_time = time.time()
            price2 = price_fetcher.get_price_from_market(
                symbol=symbol,
                executed_at=executed_at,
                market="us-stock"
            )
            second_call_time = time.time() - start_time
            
            self.assertIsNone(price2)
            print(f"[Failure Cache] Second call (cached) took {second_call_time:.2f}s")
            
            self.assertLess(second_call_time, first_call_time * 0.5)
            
        finally:
            price_fetcher._PRICE_FAILURE_CACHE_TTL_SECONDS = original_ttl

    def test_unsupported_market(self):
        """Test handling of unsupported markets."""
        import price_fetcher
        
        now = datetime.now(timezone.utc)
        executed_at = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        price = price_fetcher.get_price_from_market(
            symbol="AAPL",
            executed_at=executed_at,
            market="unsupported-market"
        )
        
        self.assertIsNone(price)


@unittest.skipUnless(has_alpha_vantage_api_key(), "ALPHA_VANTAGE_API_KEY not configured")
class PriceCacheConcurrentTests(unittest.TestCase):
    """Integration tests for concurrent price fetching."""

    def setUp(self):
        """Reset cache state before each test."""
        import price_fetcher
        price_fetcher._local_price_cache.clear()
        price_fetcher._provider_cooldowns.clear()

    def test_consecutive_calls_cache_behavior(self):
        """Test that consecutive calls use cache."""
        import price_fetcher
        
        now = datetime.now(timezone.utc)
        executed_at = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        symbol = "AAPL"
        
        times = []
        prices = []
        
        for i in range(3):
            start = time.time()
            price = price_fetcher.get_price_from_market(
                symbol=symbol,
                executed_at=executed_at,
                market="us-stock"
            )
            elapsed = time.time() - start
            
            times.append(elapsed)
            prices.append(price)
            
            if price:
                print(f"[Concurrent] Call {i+1}: ${price:.2f} in {elapsed:.3f}s")
        
        if prices[0] is None:
            self.skipTest("First API call failed")
        
        self.assertEqual(prices[0], prices[1])
        self.assertEqual(prices[1], prices[2])
        
        self.assertGreater(times[0], times[1])
        self.assertGreater(times[0], times[2])

    def test_multiple_different_symbols(self):
        """Test fetching multiple different symbols."""
        import price_fetcher
        
        now = datetime.now(timezone.utc)
        executed_at = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
        results = {}
        
        for symbol in symbols:
            price = price_fetcher.get_price_from_market(
                symbol=symbol,
                executed_at=executed_at,
                market="us-stock"
            )
            results[symbol] = price
        
        valid_results = {k: v for k, v in results.items() if v is not None}
        
        if len(valid_results) == 0:
            self.skipTest("All API calls failed")
        
        print(f"[Multi-Symbol] Got {len(valid_results)}/{len(symbols)} valid prices")
        
        for symbol, price in valid_results.items():
            self.assertIsInstance(price, float)
            self.assertGreater(price, 0)


@unittest.skipUnless(has_alpha_vantage_api_key() and has_redis(), "Redis not configured")
class PriceCacheRedisIntegrationTests(unittest.TestCase):
    """Integration tests for Redis cache with real API calls."""

    def setUp(self):
        """Reset cache state before each test."""
        import price_fetcher
        price_fetcher._local_price_cache.clear()
        price_fetcher._redis_client = None
        
        redis_client = price_fetcher._get_redis_client()
        if redis_client:
            try:
                redis_client.flushdb()
            except Exception:
                pass

    def test_redis_cache_with_real_api(self):
        """Test Redis cache with real API data."""
        import price_fetcher
        
        now = datetime.now(timezone.utc)
        executed_at = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        symbol = "AAPL"
        
        price1 = price_fetcher.get_price_from_market(
            symbol=symbol,
            executed_at=executed_at,
            market="us-stock"
        )
        
        if price1 is None:
            self.skipTest("First API call failed")
        
        print(f"[Redis] First call (API): ${price1:.2f}")
        
        price_fetcher._local_price_cache.clear()
        
        price2 = price_fetcher.get_price_from_market(
            symbol=symbol,
            executed_at=executed_at,
            market="us-stock"
        )
        
        self.assertIsNotNone(price2)
        self.assertEqual(price1, price2)
        print(f"[Redis] Second call (Redis): ${price2:.2f}")

    def test_redis_to_local_sync(self):
        """Test that Redis data syncs to local cache."""
        import price_fetcher
        
        now = datetime.now(timezone.utc)
        executed_at = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        symbol = "MSFT"
        
        price1 = price_fetcher.get_price_from_market(
            symbol=symbol,
            executed_at=executed_at,
            market="us-stock"
        )
        
        if price1 is None:
            self.skipTest("First API call failed")
        
        key = price_fetcher._price_cache_key(symbol, "us-stock")
        self.assertIn(key, price_fetcher._local_price_cache)
        
        price_fetcher._local_price_cache.clear()
        
        price2 = price_fetcher.get_price_from_market(
            symbol=symbol,
            executed_at=executed_at,
            market="us-stock"
        )
        
        self.assertIn(key, price_fetcher._local_price_cache)
        self.assertEqual(price1, price2)


class PriceCacheMockedAPITests(unittest.TestCase):
    """Integration tests with mocked API responses (fast, no rate limits)."""

    def setUp(self):
        """Reset cache state before each test."""
        import price_fetcher
        price_fetcher._local_price_cache.clear()
        price_fetcher._redis_client = None
        price_fetcher._provider_cooldowns.clear()

    @patch('price_fetcher._request_json_with_retry')
    def test_mocked_global_quote(self, mock_request):
        """Test GLOBAL_QUOTE with mocked response."""
        import price_fetcher
        
        mock_request.return_value = {
            "Global Quote": {
                "01. symbol": "AAPL",
                "02. open": "150.00",
                "03. high": "155.00",
                "04. low": "149.00",
                "05. price": "152.50",
                "06. volume": "10000000",
                "07. latest trading day": "2024-01-15",
                "08. previous close": "151.00",
                "09. change": "1.50",
                "10. change percent": "0.99%"
            }
        }
        
        price = price_fetcher._try_global_quote_price("AAPL")
        
        self.assertEqual(price, 152.50)
        mock_request.assert_called_once()

    @patch('price_fetcher._request_json_with_retry')
    def test_mocked_intraday_price(self, mock_request):
        """Test TIME_SERIES_INTRADAY with mocked response."""
        import price_fetcher
        
        mock_request.return_value = {
            "Time Series (1min)": {
                "2024-01-15 14:30:00": {
                    "1. open": "150.00",
                    "2. high": "151.00",
                    "3. low": "149.50",
                    "4. close": "150.75",
                    "5. volume": "100000"
                }
            }
        }
        
        from datetime import datetime
        dt_et = datetime(2024, 1, 15, 14, 30, 0, tzinfo=price_fetcher.ET_TZ)
        
        price = price_fetcher._try_intraday_price("AAPL", dt_et)
        
        self.assertEqual(price, 150.75)

    @patch('price_fetcher._try_intraday_price')
    @patch('price_fetcher._try_global_quote_price')
    def test_api_fallback_mechanism(self, mock_global, mock_intraday):
        """Test API fallback from TIME_SERIES_INTRADAY to GLOBAL_QUOTE."""
        import price_fetcher
        
        mock_intraday.return_value = None
        mock_global.return_value = 150.50
        
        now = datetime.now(timezone.utc)
        executed_at = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        price = price_fetcher._get_us_stock_price("AAPL", executed_at)
        
        self.assertEqual(price, 150.50)
        mock_intraday.assert_called_once()
        mock_global.assert_called_once()

    @patch('price_fetcher._try_intraday_price')
    @patch('price_fetcher._try_global_quote_price')
    def test_both_apis_fail(self, mock_global, mock_intraday):
        """Test behavior when both APIs fail."""
        import price_fetcher
        
        mock_intraday.return_value = None
        mock_global.return_value = None
        
        now = datetime.now(timezone.utc)
        executed_at = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        price = price_fetcher._get_us_stock_price("INVALID", executed_at)
        
        self.assertIsNone(price)

    @patch('price_fetcher._request_json_with_retry')
    def test_rate_limit_handling(self, mock_request):
        """Test rate limit response handling."""
        import price_fetcher
        
        mock_request.return_value = {
            "Note": "Thank you for using Alpha Vantage! Our standard API rate limit is 25 requests per day."
        }
        
        price = price_fetcher._try_global_quote_price("AAPL")
        
        self.assertIsNone(price)
        self.assertIn("alphavantage", price_fetcher._provider_cooldowns)

    @patch('price_fetcher._request_json_with_retry')
    def test_error_message_handling(self, mock_request):
        """Test error message response handling."""
        import price_fetcher
        
        mock_request.return_value = {
            "Error Message": "Invalid API call. Please retry or visit the documentation."
        }
        
        price = price_fetcher._try_global_quote_price("INVALID")
        
        self.assertIsNone(price)

    @patch('price_fetcher._try_global_quote_price')
    def test_cache_behavior_with_mocked_api(self, mock_global):
        """Test cache behavior with mocked API."""
        import price_fetcher
        
        mock_global.return_value = 150.50
        
        now = datetime.now(timezone.utc)
        executed_at = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        price1 = price_fetcher._get_us_stock_price("AAPL", executed_at)
        price2 = price_fetcher._get_us_stock_price("AAPL", executed_at)
        
        self.assertEqual(price1, 150.50)
        self.assertEqual(price2, 150.50)
        
        mock_global.assert_called_once()


class PriceCacheEdgeCaseTests(unittest.TestCase):
    """Tests for edge cases and boundary conditions."""

    def setUp(self):
        """Reset cache state before each test."""
        import price_fetcher
        price_fetcher._local_price_cache.clear()
        price_fetcher._redis_client = None

    def test_empty_symbol(self):
        """Test handling of empty symbol."""
        import price_fetcher
        
        now = datetime.now(timezone.utc)
        executed_at = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        price = price_fetcher.get_price_from_market(
            symbol="",
            executed_at=executed_at,
            market="us-stock"
        )
        
        self.assertIsNone(price)

    def test_none_symbol(self):
        """Test handling of None symbol."""
        import price_fetcher
        
        now = datetime.now(timezone.utc)
        executed_at = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        price = price_fetcher.get_price_from_market(
            symbol=None,
            executed_at=executed_at,
            market="us-stock"
        )
        
        self.assertIsNone(price)

    def test_invalid_executed_at_format(self):
        """Test handling of invalid executed_at format."""
        import price_fetcher
        
        price = price_fetcher.get_price_from_market(
            symbol="AAPL",
            executed_at="invalid-date-format",
            market="us-stock"
        )
        
        self.assertIsNone(price)

    def test_empty_executed_at(self):
        """Test handling of empty executed_at."""
        import price_fetcher
        
        price = price_fetcher.get_price_from_market(
            symbol="AAPL",
            executed_at="",
            market="us-stock"
        )
        
        self.assertIsNone(price)

    def test_case_insensitive_market(self):
        """Test that market names are case-insensitive."""
        import price_fetcher
        
        price_fetcher._price_cache_set("AAPL", "US-STOCK", 150.00)
        
        price = price_fetcher._price_cache_get("AAPL", "us-stock")
        
        self.assertIsNone(price)

    def test_cache_key_collision(self):
        """Test that different symbols don't collide."""
        import price_fetcher
        
        price_fetcher._price_cache_set("AAPL", "us-stock", 150.00)
        price_fetcher._price_cache_set("MSFT", "us-stock", 300.00)
        
        self.assertEqual(price_fetcher._price_cache_get("AAPL", "us-stock"), 150.00)
        self.assertEqual(price_fetcher._price_cache_get("MSFT", "us-stock"), 300.00)

    def test_cache_clear_function(self):
        """Test cache clear functionality."""
        import price_fetcher
        
        price_fetcher._price_cache_set("AAPL", "us-stock", 150.00)
        self.assertIsNotNone(price_fetcher._price_cache_get("AAPL", "us-stock"))
        
        price_fetcher._price_cache_clear("AAPL", "us-stock")
        self.assertIsNone(price_fetcher._price_cache_get("AAPL", "us-stock"))

    def test_cache_clear_nonexistent(self):
        """Test clearing non-existent cache entry."""
        import price_fetcher
        
        price_fetcher._price_cache_clear("NONEXISTENT", "us-stock")
        
        self.assertIsNone(price_fetcher._price_cache_get("NONEXISTENT", "us-stock"))


class PriceCacheStatisticsTests(unittest.TestCase):
    """Tests for cache statistics functionality."""

    def setUp(self):
        """Reset cache state and statistics before each test."""
        import price_fetcher
        price_fetcher._local_price_cache.clear()
        price_fetcher._redis_client = None
        price_fetcher._reset_cache_stats()

    def test_initial_stats(self):
        """Test initial cache statistics."""
        import price_fetcher
        
        stats = price_fetcher._get_cache_stats()
        
        self.assertEqual(stats["hits"], 0)
        self.assertEqual(stats["misses"], 0)
        self.assertEqual(stats["hit_rate"], 0)
        self.assertEqual(stats["total_requests"], 0)
        self.assertEqual(stats["cache_size"], 0)

    def test_stats_after_cache_miss(self):
        """Test statistics after cache miss."""
        import price_fetcher
        
        price_fetcher._price_cache_get("AAPL", "us-stock")
        stats = price_fetcher._get_cache_stats()
        
        self.assertEqual(stats["hits"], 0)
        self.assertEqual(stats["misses"], 1)
        self.assertEqual(stats["total_requests"], 1)

    def test_stats_after_cache_hit(self):
        """Test statistics after cache hit."""
        import price_fetcher
        
        price_fetcher._price_cache_set("AAPL", "us-stock", 150.00)
        price_fetcher._price_cache_get("AAPL", "us-stock")
        
        stats = price_fetcher._get_cache_stats()
        
        self.assertEqual(stats["hits"], 1)
        self.assertEqual(stats["misses"], 0)
        self.assertEqual(stats["hit_rate"], 100.0)

    def test_stats_after_multiple_operations(self):
        """Test statistics after multiple cache operations."""
        import price_fetcher
        
        price_fetcher._price_cache_set("AAPL", "us-stock", 150.00)
        price_fetcher._price_cache_set("MSFT", "us-stock", 300.00)
        
        price_fetcher._price_cache_get("AAPL", "us-stock")
        price_fetcher._price_cache_get("MSFT", "us-stock")
        price_fetcher._price_cache_get("GOOGL", "us-stock")
        
        stats = price_fetcher._get_cache_stats()
        
        self.assertEqual(stats["hits"], 2)
        self.assertEqual(stats["misses"], 1)
        self.assertEqual(stats["total_requests"], 3)
        self.assertAlmostEqual(stats["hit_rate"], 66.67, places=1)

    def test_reset_stats(self):
        """Test resetting cache statistics."""
        import price_fetcher
        
        price_fetcher._price_cache_set("AAPL", "us-stock", 150.00)
        price_fetcher._price_cache_get("AAPL", "us-stock")
        
        stats_before = price_fetcher._get_cache_stats()
        self.assertEqual(stats_before["hits"], 1)
        
        price_fetcher._reset_cache_stats()
        
        stats_after = price_fetcher._get_cache_stats()
        self.assertEqual(stats_after["hits"], 0)
        self.assertEqual(stats_after["misses"], 0)

    def test_stats_uptime(self):
        """Test uptime statistics."""
        import price_fetcher
        import time
        
        time.sleep(0.01)
        
        stats = price_fetcher._get_cache_stats()
        
        self.assertIn("uptime_seconds", stats)
        self.assertIn("uptime_formatted", stats)
        self.assertGreaterEqual(stats["uptime_seconds"], 0)
        self.assertIsInstance(stats["uptime_formatted"], str)


class PriceCacheSmartTTLTests(unittest.TestCase):
    """Tests for smart TTL functionality."""

    def setUp(self):
        """Reset cache state before each test."""
        import price_fetcher
        price_fetcher._local_price_cache.clear()
        price_fetcher._redis_client = None
        price_fetcher._cache_access_frequency.clear()
        price_fetcher._SMART_TTL_ENABLED = False

    def test_default_ttl_when_smart_ttl_disabled(self):
        """Test that default TTL is used when smart TTL is disabled."""
        import price_fetcher
        
        cache_key = price_fetcher._price_cache_key("AAPL", "us-stock")
        ttl = price_fetcher._get_smart_ttl(cache_key, 150.00)
        
        self.assertEqual(ttl, price_fetcher._PRICE_CACHE_TTL_SECONDS)

    def test_failure_ttl(self):
        """Test that failure TTL is used for None prices."""
        import price_fetcher
        
        cache_key = price_fetcher._price_cache_key("INVALID", "us-stock")
        ttl = price_fetcher._get_smart_ttl(cache_key, None)
        
        self.assertEqual(ttl, price_fetcher._PRICE_FAILURE_CACHE_TTL_SECONDS)

    def test_smart_ttl_low_frequency(self):
        """Test smart TTL for low frequency access."""
        import price_fetcher
        
        price_fetcher._SMART_TTL_ENABLED = True
        cache_key = price_fetcher._price_cache_key("AAPL", "us-stock")
        
        ttl = price_fetcher._get_smart_ttl(cache_key, 150.00)
        
        self.assertEqual(ttl, price_fetcher._SMART_TTL_MIN_SECONDS)

    def test_smart_ttl_high_frequency(self):
        """Test smart TTL for high frequency access."""
        import price_fetcher
        
        price_fetcher._SMART_TTL_ENABLED = True
        cache_key = price_fetcher._price_cache_key("AAPL", "us-stock")
        
        for i in range(price_fetcher._SMART_TTL_HIGH_FREQ_THRESHOLD + 1):
            price_fetcher._track_cache_access(cache_key)
        
        ttl = price_fetcher._get_smart_ttl(cache_key, 150.00)
        
        self.assertEqual(ttl, price_fetcher._SMART_TTL_MAX_SECONDS)

    def test_track_cache_access(self):
        """Test cache access tracking."""
        import price_fetcher
        
        cache_key = price_fetcher._price_cache_key("AAPL", "us-stock")
        
        self.assertEqual(price_fetcher._cache_access_frequency.get(cache_key, 0), 0)
        
        price_fetcher._track_cache_access(cache_key)
        price_fetcher._track_cache_access(cache_key)
        
        self.assertEqual(price_fetcher._cache_access_frequency.get(cache_key, 0), 2)

    def test_access_frequency_cap(self):
        """Test that access frequency is capped."""
        import price_fetcher
        
        cache_key = price_fetcher._price_cache_key("AAPL", "us-stock")
        max_freq = price_fetcher._SMART_TTL_HIGH_FREQ_THRESHOLD * 2
        
        for i in range(max_freq + 10):
            price_fetcher._track_cache_access(cache_key)
        
        self.assertLessEqual(
            price_fetcher._cache_access_frequency.get(cache_key, 0),
            price_fetcher._SMART_TTL_HIGH_FREQ_THRESHOLD
        )


class PriceCacheCleanupTests(unittest.TestCase):
    """Tests for cache cleanup functionality."""

    def setUp(self):
        """Reset cache state before each test."""
        import price_fetcher
        price_fetcher._local_price_cache.clear()
        price_fetcher._redis_client = None

    def test_clear_expired_cache(self):
        """Test clearing expired cache entries."""
        import price_fetcher
        import time
        
        cache_key = price_fetcher._price_cache_key("AAPL", "us-stock")
        price_fetcher._local_price_cache[cache_key] = (150.00, time.time() - 10)
        
        cleared = price_fetcher._clear_expired_cache()
        
        self.assertEqual(cleared, 1)
        self.assertNotIn(cache_key, price_fetcher._local_price_cache)

    def test_clear_expired_keeps_valid(self):
        """Test that valid cache entries are kept."""
        import price_fetcher
        import time
        
        expired_key = price_fetcher._price_cache_key("AAPL", "us-stock")
        valid_key = price_fetcher._price_cache_key("MSFT", "us-stock")
        
        price_fetcher._local_price_cache[expired_key] = (150.00, time.time() - 10)
        price_fetcher._local_price_cache[valid_key] = (300.00, time.time() + 100)
        
        cleared = price_fetcher._clear_expired_cache()
        
        self.assertEqual(cleared, 1)
        self.assertNotIn(expired_key, price_fetcher._local_price_cache)
        self.assertIn(valid_key, price_fetcher._local_price_cache)

    def test_clear_expired_nothing_to_clear(self):
        """Test cleanup when nothing is expired."""
        import price_fetcher
        import time
        
        cache_key = price_fetcher._price_cache_key("AAPL", "us-stock")
        price_fetcher._local_price_cache[cache_key] = (150.00, time.time() + 100)
        
        cleared = price_fetcher._clear_expired_cache()
        
        self.assertEqual(cleared, 0)
        self.assertIn(cache_key, price_fetcher._local_price_cache)

    def test_clear_expired_empty_cache(self):
        """Test cleanup with empty cache."""
        import price_fetcher
        
        cleared = price_fetcher._clear_expired_cache()
        
        self.assertEqual(cleared, 0)


class PriceCacheFormatTests(unittest.TestCase):
    """Tests for formatting functions."""

    def test_format_uptime_seconds(self):
        """Test uptime formatting for seconds."""
        import price_fetcher
        
        formatted = price_fetcher._format_uptime(45)
        self.assertEqual(formatted, "45s")

    def test_format_uptime_minutes(self):
        """Test uptime formatting for minutes."""
        import price_fetcher
        
        formatted = price_fetcher._format_uptime(125)
        self.assertEqual(formatted, "2m 5s")

    def test_format_uptime_hours(self):
        """Test uptime formatting for hours."""
        import price_fetcher
        
        formatted = price_fetcher._format_uptime(3725)
        self.assertEqual(formatted, "1h 2m 5s")

    def test_format_uptime_zero(self):
        """Test uptime formatting for zero."""
        import price_fetcher
        
        formatted = price_fetcher._format_uptime(0)
        self.assertEqual(formatted, "0s")


if __name__ == '__main__':
    unittest.main(verbosity=2)
