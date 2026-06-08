"""
Binance Exchange API Integration

Supports spot and futures trading on Binance.
"""

import hmac
import hashlib
import time
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime

from .base import ExchangeAPI


class BinanceAPI(ExchangeAPI):
    def _get_base_url(self) -> str:
        if self.is_sandbox:
            return 'https://testnet.binance.vision/api'
        return 'https://api.binance.com/api'

    def _generate_signature(self, params: Dict[str, Any]) -> str:
        query_string = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
        return hmac.new(
            self.api_secret.encode(),
            query_string.encode(),
            hashlib.sha256
        ).hexdigest()

    def _request(self, method: str, endpoint: str, params: Dict[str, Any] = None, signed: bool = False) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        headers = {
            'X-MBX-APIKEY': self.api_key,
            'Content-Type': 'application/json'
        }

        if params is None:
            params = {}

        if signed:
            params['timestamp'] = int(time.time() * 1000)
            params['signature'] = self._generate_signature(params)

        try:
            if method == 'GET':
                response = requests.get(url, params=params, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, params=params, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, params=params, headers=headers, timeout=10)
            else:
                return self._format_response(False, error=f"Unsupported method: {method}")

            if response.status_code == 200:
                return self._format_response(True, data=response.json())
            else:
                return self._format_response(False, error=response.text)

        except Exception as e:
            return self._format_response(False, error=str(e))

    def get_balance(self) -> Dict[str, Any]:
        return self._request('GET', '/v3/account', signed=True)

    def get_price(self, symbol: str) -> Dict[str, Any]:
        symbol = self._parse_symbol(symbol)
        return self._request('GET', '/v3/ticker/price', params={'symbol': symbol})

    def get_orderbook(self, symbol: str, limit: int = 20) -> Dict[str, Any]:
        symbol = self._parse_symbol(symbol)
        return self._request('GET', '/v3/depth', params={'symbol': symbol, 'limit': limit})

    def create_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        symbol = self._parse_symbol(symbol)
        params = {
            'symbol': symbol,
            'side': side.upper(),
            'type': order_type.upper(),
            'quantity': quantity
        }

        if price and order_type.lower() == 'limit':
            params['price'] = price

        if kwargs.get('stop_loss'):
            params['stopPrice'] = kwargs['stop_loss']

        if kwargs.get('take_profit'):
            params['takeProfit'] = kwargs['take_profit']

        return self._request('POST', '/v3/order', params=params, signed=True)

    def cancel_order(self, symbol: str, order_id: str) -> Dict[str, Any]:
        symbol = self._parse_symbol(symbol)
        return self._request('DELETE', '/v3/order', params={'symbol': symbol, 'orderId': order_id}, signed=True)

    def get_order(self, symbol: str, order_id: str) -> Dict[str, Any]:
        symbol = self._parse_symbol(symbol)
        return self._request('GET', '/v3/order', params={'symbol': symbol, 'orderId': order_id}, signed=True)

    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        params = {}
        if symbol:
            params['symbol'] = self._parse_symbol(symbol)
        return self._request('GET', '/v3/openOrders', params=params, signed=True)

    def get_trade_history(self, symbol: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        if not symbol:
            return self._format_response(False, error='Symbol is required for Binance trade history')
        symbol = self._parse_symbol(symbol)
        return self._request('GET', '/v3/myTrades', params={'symbol': symbol, 'limit': limit}, signed=True)

    def get_positions(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        return self._format_response(True, data=[], error='Positions only available in futures API')

    def get_kline(
        self,
        symbol: str,
        interval: str = '1h',
        limit: int = 100,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        symbol = self._parse_symbol(symbol)
        params = {'symbol': symbol, 'interval': interval, 'limit': limit}

        if start_time:
            params['startTime'] = int(start_time.timestamp() * 1000)
        if end_time:
            params['endTime'] = int(end_time.timestamp() * 1000)

        response = self._request('GET', '/v3/klines', params=params)
        if response['success'] and response['data']:
            klines = []
            for k in response['data']:
                klines.append({
                    'open_time': datetime.fromtimestamp(k[0] / 1000).isoformat(),
                    'open': float(k[1]),
                    'high': float(k[2]),
                    'low': float(k[3]),
                    'close': float(k[4]),
                    'volume': float(k[5]),
                    'close_time': datetime.fromtimestamp(k[6] / 1000).isoformat()
                })
            return self._format_response(True, data=klines)
        return response
