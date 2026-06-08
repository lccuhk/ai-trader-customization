"""
Base Exchange API Class

Defines the interface for all exchange integrations.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime


class ExchangeAPI(ABC):
    def __init__(self, api_key: str, api_secret: str, **kwargs):
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = kwargs.get('passphrase')
        self.is_sandbox = kwargs.get('is_sandbox', False)
        self.base_url = self._get_base_url()

    @abstractmethod
    def _get_base_url(self) -> str:
        pass

    @abstractmethod
    def get_balance(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_price(self, symbol: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_orderbook(self, symbol: str, limit: int = 20) -> Dict[str, Any]:
        pass

    @abstractmethod
    def create_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    def cancel_order(self, symbol: str, order_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_order(self, symbol: str, order_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_trade_history(self, symbol: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_positions(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_kline(
        self,
        symbol: str,
        interval: str = '1h',
        limit: int = 100,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        pass

    def _parse_symbol(self, symbol: str) -> str:
        return symbol.upper().replace('/', '')

    def _format_response(self, success: bool, data: Any = None, error: str = None) -> Dict[str, Any]:
        return {
            'success': success,
            'data': data,
            'error': error,
            'exchange': self.__class__.__name__,
            'timestamp': datetime.now().isoformat()
        }
