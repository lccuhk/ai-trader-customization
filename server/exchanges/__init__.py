"""
Exchange API Integration Module

Supports multiple cryptocurrency and stock exchanges.
"""

from .base import ExchangeAPI
from .binance import BinanceAPI
from .okx import OKXAPI
from .alpaca import AlpacaAPI

EXCHANGE_CLASSES = {
    'binance': BinanceAPI,
    'okx': OKXAPI,
    'alpaca': AlpacaAPI
}


def get_exchange_api(exchange_name: str, api_key: str, api_secret: str, **kwargs) -> ExchangeAPI:
    exchange_class = EXCHANGE_CLASSES.get(exchange_name.lower())
    if not exchange_class:
        raise ValueError(f"Unsupported exchange: {exchange_name}")
    return exchange_class(api_key, api_secret, **kwargs)


__all__ = ['ExchangeAPI', 'BinanceAPI', 'OKXAPI', 'AlpacaAPI', 'get_exchange_api']
