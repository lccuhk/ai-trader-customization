"""
Unit tests for price cache functionality.

Tests cover:
- Cache key generation
- Local memory cache operations
- Cache TTL behavior
- Redis cache integration (mocked)
- Integration tests for cache behavior
"""

import os
import sys
import time
import unittest
from unittest.mock import MagicMock, patch, PropertyMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class PriceCacheKeyTests(unittest.TestCase):
    """Tests for cache key generation and basic local cache operations."""

    def setUp(self):
        """Reset cache state before each test."""
        import price_fetcher
        price_fetcher._local_price_cache.clear()

    def test_cache_key_generation(self):
        """Test cache key format: price:{market}:{symbol}"""
        import price_fetcher
        
        key = price_fetcher._price_cache_key("AAPL", "us-stock")
        expected_prefix = f"{price_fetcher._REDIS_PREFIX}:price:us-stock:AAPL"
        self.assertEqual(key, expected_prefix)

    def test_cache_key_with_token_id(self):
        """Test cache key with token_id: price:{market}:{symbol}:{token_id}"""
        import price_fetcher
        
        key = price_fetcher._price_cache_key("BTC", "polymarket", "12345")
        expected_prefix = f"{price_fetcher._REDIS_PREFIX}:price:polymarket:BTC:12345"
        self.assertEqual(key, expected_prefix)

    def test_local_cache_hit(self):
        """Test successful cache retrieval after setting."""
        import price_fetcher
        
        price_fetcher._price_cache_set("AAPL", "us-stock", 150.50)
        cached_price = price_fetcher._price_cache_get("AAPL", "us-stock")
        
        self.assertEqual(cached_price, 150.50)

    def test_local_cache_miss(self):
        """Test cache miss returns None."""
        import price_fetcher
        
        cached_price = price_fetcher._price_cache_get("NONEXISTENT", "us-stock")
        self.assertIsNone(cached_price)

    def test_local_cache_expiration(self):
        """Test cache expires after TTL."""
        import price_fetcher
        
        original_ttl = price_fetcher._PRICE_CACHE_TTL_SECONDS
        try:
            price_fetcher._PRICE_CACHE_TTL_SECONDS = 1
            
            price_fetcher._price_cache_set("AAPL", "us-stock", 150.50)
            
            time.sleep(1.1)
            
            cached_price = price_fetcher._price_cache_get("AAPL", "us-stock")
            self.assertIsNone(cached_price)
        finally:
            price_fetcher._PRICE_CACHE_TTL_SECONDS = original_ttl

    def test_failure_cache(self):
        """Test failed price requests are also cached."""
        import price_fetcher
        
        price_fetcher._price_cache_set("INVALID", "us-stock", None)
        cached_price = price_fetcher._price_cache_get("INVALID", "us-stock")
        
        self.assertIsNone(cached_price)

    def test_different_markets(self):
        """Test cache isolation between different markets."""
        import price_fetcher
        
        price_fetcher._price_cache_set("BTC", "crypto", 45000.00)
        price_fetcher._price_cache_set("BTC", "us-stock", 100.00)
        
        crypto_price = price_fetcher._price_cache_get("BTC", "crypto")
        stock_price = price_fetcher._price_cache_get("BTC", "us-stock")
        
        self.assertEqual(crypto_price, 45000.00)
        self.assertEqual(stock_price, 100.00)

    def test_cache_overwrite(self):
        """Test cache can be overwritten with new values."""
        import price_fetcher
        
        price_fetcher._price_cache_set("AAPL", "us-stock", 150.00)
        price_fetcher._price_cache_set("AAPL", "us-stock", 160.00)
        
        cached_price = price_fetcher._price_cache_get("AAPL", "us-stock")
        self.assertEqual(cached_price, 160.00)


class PriceCacheTTLTests(unittest.TestCase):
    """Tests for cache Time-To-Live (TTL) behavior."""

    def test_success_cache_ttl(self):
        """Test successful prices are cached for configured TTL."""
        import price_fetcher
        
        original_ttl = price_fetcher._PRICE_CACHE_TTL_SECONDS
        try:
            price_fetcher._PRICE_CACHE_TTL_SECONDS = 30
            
            price_fetcher._price_cache_set("AAPL", "us-stock", 150.50)
            
            key = price_fetcher._price_cache_key("AAPL", "us-stock")
            cached_value, expires_at = price_fetcher._local_price_cache.get(key, (None, 0))
            
            self.assertEqual(cached_value, 150.50)
            self.assertGreater(expires_at, time.time())
            self.assertLessEqual(expires_at - time.time(), 30)
        finally:
            price_fetcher._PRICE_CACHE_TTL_SECONDS = original_ttl

    def test_failure_cache_ttl(self):
        """Test failed requests are cached for configured TTL."""
        import price_fetcher
        
        original_ttl = price_fetcher._PRICE_FAILURE_CACHE_TTL_SECONDS
        try:
            price_fetcher._PRICE_FAILURE_CACHE_TTL_SECONDS = 15
            
            price_fetcher._price_cache_set("INVALID", "us-stock", None)
            
            key = price_fetcher._price_cache_key("INVALID", "us-stock")
            cached_value, expires_at = price_fetcher._local_price_cache.get(key, (None, 0))
            
            self.assertIsNone(cached_value)
            self.assertGreater(expires_at, time.time())
            self.assertLessEqual(expires_at - time.time(), 15)
        finally:
            price_fetcher._PRICE_FAILURE_CACHE_TTL_SECONDS = original_ttl


class RedisCacheTests(unittest.TestCase):
    """Tests for Redis cache integration."""

    def setUp(self):
        """Reset cache state before each test."""
        import price_fetcher
        price_fetcher._local_price_cache.clear()
        price_fetcher._redis_client = None

    @patch('price_fetcher._get_redis_client')
    def test_redis_cache_hit(self, mock_get_redis):
        """Test Redis cache hit returns cached price."""
        import price_fetcher
        
        mock_redis = MagicMock()
        mock_redis.get.return_value = "150.50"
        mock_redis.ttl.return_value = 25
        mock_get_redis.return_value = mock_redis
        
        cached_price = price_fetcher._price_cache_get("AAPL", "us-stock")
        
        self.assertEqual(cached_price, 150.50)
        mock_redis.get.assert_called_once()

    @patch('price_fetcher._get_redis_client')
    def test_redis_cache_miss(self, mock_get_redis):
        """Test Redis cache miss returns None."""
        import price_fetcher
        
        mock_redis = MagicMock()
        mock_redis.get.return_value = None
        mock_get_redis.return_value = mock_redis
        
        cached_price = price_fetcher._price_cache_get("AAPL", "us-stock")
        
        self.assertIsNone(cached_price)

    @patch('price_fetcher._get_redis_client')
    def test_redis_cache_expired(self, mock_get_redis):
        """Test expired Redis cache returns None."""
        import price_fetcher
        
        mock_redis = MagicMock()
        mock_redis.get.return_value = "150.50"
        mock_redis.ttl.return_value = -1
        mock_get_redis.return_value = mock_redis
        
        cached_price = price_fetcher._price_cache_get("AAPL", "us-stock")
        
        self.assertEqual(cached_price, 150.50)

    @patch('price_fetcher._get_redis_client')
    def test_redis_cache_set(self, mock_get_redis):
        """Test Redis cache is set with correct TTL."""
        import price_fetcher
        
        mock_redis = MagicMock()
        mock_get_redis.return_value = mock_redis
        
        price_fetcher._price_cache_set("AAPL", "us-stock", 150.50)
        
        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args
        self.assertEqual(call_args[0][1], price_fetcher._PRICE_CACHE_TTL_SECONDS)
        self.assertEqual(call_args[0][2], "150.5")


class PriceCacheIntegrationTests(unittest.TestCase):
    """Integration tests for cache behavior."""

    def setUp(self):
        """Reset cache state before each test."""
        import price_fetcher
        price_fetcher._local_price_cache.clear()
        price_fetcher._redis_client = None

    def test_multiple_symbols(self):
        """Test cache works with multiple symbols simultaneously."""
        import price_fetcher
        
        symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
        prices = [150.50, 300.25, 140.75, 175.00, 250.80]
        
        for symbol, price in zip(symbols, prices):
            price_fetcher._price_cache_set(symbol, "us-stock", price)
        
        for symbol, expected_price in zip(symbols, prices):
            cached_price = price_fetcher._price_cache_get(symbol, "us-stock")
            self.assertEqual(cached_price, expected_price)

    def test_cache_local_priority(self):
        """Test local cache takes priority over Redis."""
        import price_fetcher
        
        price_fetcher._price_cache_set("AAPL", "us-stock", 150.50)
        
        with patch('price_fetcher._get_redis_client') as mock_get_redis:
            mock_redis = MagicMock()
            mock_redis.get.return_value = "200.00"
            mock_get_redis.return_value = mock_redis
            
            cached_price = price_fetcher._price_cache_get("AAPL", "us-stock")
            
            self.assertEqual(cached_price, 150.50)
            mock_redis.get.assert_not_called()

    @patch('price_fetcher._get_redis_client')
    def test_redis_to_local_sync(self, mock_get_redis):
        """Test Redis data is synced to local cache."""
        import price_fetcher
        
        mock_redis = MagicMock()
        mock_redis.get.return_value = "150.50"
        mock_redis.ttl.return_value = 25
        mock_get_redis.return_value = mock_redis
        
        price_fetcher._price_cache_get("AAPL", "us-stock")
        
        key = price_fetcher._price_cache_key("AAPL", "us-stock")
        self.assertIn(key, price_fetcher._local_price_cache)
        
        local_value, expires_at = price_fetcher._local_price_cache[key]
        self.assertEqual(local_value, 150.50)


if __name__ == '__main__':
    unittest.main()
