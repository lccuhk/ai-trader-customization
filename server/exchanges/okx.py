"""
OKX Exchange API Integration

Supports spot and derivatives trading on OKX.
"""

import hmac
import hashlib
import base64
import time
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime

from .base import ExchangeAPI


class OKXAPI(ExchangeAPI):
    def _get_base_url(self) -> str:
        if self.is_sandbox:
            return 'https://www.okx.com'
        return 'https://www.okx.com'

    def _generate_signature(self, timestamp: str, method: str, endpoint: str, body: str = '') -> str:
        message = timestamp + method.upper() + endpoint + body
        mac = hmac.new(
            self.api_secret.encode(),
            message.encode(),
            hashlib.sha256
        )
        return base64.b64encode(mac.digest()).decode()

    def _get_passphrase(self) -> str:
        if not self.passphrase:
            raise ValueError('OKX requires passphrase')
        return self.passphrase

    def _request(self, method: str, endpoint: str, params: Dict[str, Any] = None, body: Dict[str, Any] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        timestamp = datetime.utcnow().isoformat(timespec='seconds') + 'Z'

        body_str = ''
        if body:
            import json
            body_str = json.dumps(body)

        signature = self._generate_signature(timestamp, method, endpoint, body_str)

        headers = {
            'OK-ACCESS-KEY': self.api_key,
            'OK-ACCESS-SIGN': signature,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': self._get_passphrase(),
            'Content-Type': 'application/json'
        }

        try:
            if method == 'GET':
                response = requests.get(url, params=params, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=body, params=params, headers=headers, timeout=10)
            else:
                return self._format_response(False, error=f"Unsupported method: {method}")

            data = response.json()
            if data.get('code') == '0':
                return self._format_response(True, data=data.get('data'))
            else:
                return self._format_response(False, error=data.get('msg', 'Unknown error'))

        except Exception as e:
            return self._format_response(False, error=str(e))

    def get_balance(self) -> Dict[str, Any]:
        return self._request('GET', '/api/v5/account/balance')

    def get_price(self, symbol: str) -> Dict[str, Any]:
        symbol = self._parse_symbol(symbol)
        inst_id = f"{symbol}-USDT"
        return self._request('GET', '/api/v5/market/ticker', params={'instId': inst_id})

    def get_orderbook(self, symbol: str, limit: int = 20) -> Dict[str, Any]:
        symbol = self._parse_symbol(symbol)
        inst_id = f"{symbol}-USDT"
        return self._request('GET', '/api/v5/market/books', params={'instId': inst_id, 'sz': limit})

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
        inst_id = f"{symbol}-USDT"

        body = {
            'instId': inst_id,
            'tdMode': 'cash',
            'side': side.lower(),
            'ordType': order_type.lower(),
            'sz': str(quantity)
        }

        if price and order_type.lower() == 'limit':
            body['px'] = str(price)

        return self._request('POST', '/api/v5/trade/order', body=body)

    def cancel_order(self, symbol: str, order_id: str) -> Dict[str, Any]:
        symbol = self._parse_symbol(symbol)
        inst_id = f"{symbol}-USDT"
        body = {'instId': inst_id, 'ordId': order_id}
        return self._request('POST', '/api/v5/trade/cancel-order', body=body)

    def get_order(self, symbol: str, order_id: str) -> Dict[str, Any]:
        symbol = self._parse_symbol(symbol)
        inst_id = f"{symbol}-USDT"
        return self._request('GET', '/api/v5/trade/order', params={'instId': inst_id, 'ordId': order_id})

    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        params = {}
        if symbol:
            params['instId'] = f"{self._parse_symbol(symbol)}-USDT"
        return self._request('GET', '/api/v5/trade/orders-pending', params=params)

    def get_trade_history(self, symbol: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        params = {'limit': limit}
        if symbol:
            params['instId'] = f"{self._parse_symbol(symbol)}-USDT"
        return self._request('GET', '/api/v5/trade/fills', params=params)

    def get_positions(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        params = {}
        if symbol:
            params['instId'] = f"{self._parse_symbol(symbol)}-USDT-SWAP"
        return self._request('GET', '/api/v5/account/positions', params=params)

    def get_kline(
        self,
        symbol: str,
        interval: str = '1h',
        limit: int = 100,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        symbol = self._parse_symbol(symbol)
        inst_id = f"{symbol}-USDT"
        params = {'instId': inst_id, 'bar': interval, 'limit': limit}

        if start_time:
            params['after'] = int(start_time.timestamp() * 1000)
        if end_time:
            params['before'] = int(end_time.timestamp() * 1000)

        response = self._request('GET', '/api/v5/market/candles', params=params)
        if response['success'] and response['data']:
            klines = []
            for k in response['data']:
                klines.append({
                    'open_time': datetime.fromtimestamp(int(k[0]) / 1000).isoformat(),
                    'open': float(k[1]),
                    'high': float(k[2]),
                    'low': float(k[3]),
                    'close': float(k[4]),
                    'volume': float(k[5]),
                    'close_time': datetime.fromtimestamp(int(k[0]) / 1000).isoformat()
                })
            return self._format_response(True, data=klines)
        return response
