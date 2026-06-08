"""
Alpaca Exchange API Integration

Supports stock and crypto trading on Alpaca.
"""

import hmac
import hashlib
import time
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime

from .base import ExchangeAPI


class AlpacaAPI(ExchangeAPI):
    def _get_base_url(self) -> str:
        if self.is_sandbox:
            return 'https://paper-api.alpaca.markets'
        return 'https://api.alpaca.markets'

    def _request(self, method: str, endpoint: str, params: Dict[str, Any] = None, body: Dict[str, Any] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        timestamp = str(int(time.time()))

        body_str = ''
        if body:
            import json
            body_str = json.dumps(body)

        message = timestamp + method.upper() + endpoint + body_str
        signature = hmac.new(
            self.api_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        headers = {
            'APCA-API-KEY-ID': self.api_key,
            'APCA-API-SECRET-KEY': self.api_secret,
            'Content-Type': 'application/json'
        }

        try:
            if method == 'GET':
                response = requests.get(url, params=params, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=body, params=params, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, params=params, headers=headers, timeout=10)
            else:
                return self._format_response(False, error=f"Unsupported method: {method}")

            if response.status_code in [200, 201]:
                return self._format_response(True, data=response.json())
            else:
                return self._format_response(False, error=response.text)

        except Exception as e:
            return self._format_response(False, error=str(e))

    def get_balance(self) -> Dict[str, Any]:
        return self._request('GET', '/v2/account')

    def get_price(self, symbol: str) -> Dict[str, Any]:
        symbol = self._parse_symbol(symbol)
        return self._request('GET', f'/v2/stocks/{symbol}/quotes/latest')

    def get_orderbook(self, symbol: str, limit: int = 20) -> Dict[str, Any]:
        symbol = self._parse_symbol(symbol)
        return self._request('GET', f'/v2/stocks/{symbol}/quotes/latest')

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

        body = {
            'symbol': symbol,
            'side': side.lower(),
            'type': order_type.lower(),
            'qty': quantity,
            'time_in_force': 'gtc'
        }

        if price and order_type.lower() == 'limit':
            body['limit_price'] = price

        if kwargs.get('stop_loss'):
            body['stop_loss'] = {'stop_price': kwargs['stop_loss']}

        if kwargs.get('take_profit'):
            body['take_profit'] = {'limit_price': kwargs['take_profit']}

        return self._request('POST', '/v2/orders', body=body)

    def cancel_order(self, symbol: str, order_id: str) -> Dict[str, Any]:
        return self._request('DELETE', f'/v2/orders/{order_id}')

    def get_order(self, symbol: str, order_id: str) -> Dict[str, Any]:
        return self._request('GET', f'/v2/orders/{order_id}')

    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        params = {'status': 'open'}
        if symbol:
            params['symbols'] = self._parse_symbol(symbol)
        return self._request('GET', '/v2/orders', params=params)

    def get_trade_history(self, symbol: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        return self._request('GET', '/v2/account/activities', params={'activity_types': 'FILL', 'limit': limit})

    def get_positions(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        if symbol:
            symbol = self._parse_symbol(symbol)
            return self._request('GET', f'/v2/positions/{symbol}')
        return self._request('GET', '/v2/positions')

    def get_kline(
        self,
        symbol: str,
        interval: str = '1h',
        limit: int = 100,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        symbol = self._parse_symbol(symbol)

        timeframe_map = {
            '1m': '1Min',
            '5m': '5Min',
            '15m': '15Min',
            '1h': '1Hour',
            '4h': '4Hour',
            '1d': '1Day'
        }

        params = {
            'symbols': symbol,
            'timeframe': timeframe_map.get(interval, '1Hour'),
            'limit': limit
        }

        if start_time:
            params['start'] = start_time.isoformat()
        if end_time:
            params['end'] = end_time.isoformat()

        response = self._request('GET', '/v2/stocks/bars', params=params)
        if response['success'] and response['data'] and symbol in response['data'].get('bars', {}):
            klines = []
            for k in response['data']['bars'][symbol]:
                klines.append({
                    'open_time': k['t'],
                    'open': float(k['o']),
                    'high': float(k['h']),
                    'low': float(k['l']),
                    'close': float(k['c']),
                    'volume': float(k['v']),
                    'close_time': k['t']
                })
            return self._format_response(True, data=klines)
        return response
