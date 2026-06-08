"""
Price Updater Service

Background service for real-time price updates and PnL calculations.
"""

import random
import time
import threading
from typing import Dict, List, Optional
from datetime import datetime

from .push_service import push_service


class PriceUpdater:
    def __init__(self):
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._prices: Dict[str, Dict[str, float]] = {}
        self._subscribed_symbols: set = set()
        self._update_interval = 5  # seconds
        
        self._default_symbols = [
            'BTC', 'ETH', 'BNB', 'SOL', 'XRP',
            'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA',
            'EUR/USD', 'GBP/USD', 'USD/JPY', 'XAU/USD'
        ]
        
        self._init_prices()

    def _init_prices(self):
        base_prices = {
            'BTC': 65000.0,
            'ETH': 3500.0,
            'BNB': 580.0,
            'SOL': 145.0,
            'XRP': 0.52,
            'AAPL': 185.0,
            'GOOGL': 140.0,
            'MSFT': 378.0,
            'AMZN': 178.0,
            'TSLA': 248.0,
            'EUR/USD': 1.08,
            'GBP/USD': 1.27,
            'USD/JPY': 157.5,
            'XAU/USD': 2320.0
        }
        
        for symbol in self._default_symbols:
            base_price = base_prices.get(symbol, 100.0)
            self._prices[symbol] = {
                'current': base_price,
                'open': base_price,
                'high': base_price,
                'low': base_price,
                'change_24h': 0.0,
                'change_percent_24h': 0.0
            }

    def start(self):
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        print(f"[PriceUpdater] Started with {len(self._default_symbols)} symbols")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
        print("[PriceUpdater] Stopped")

    def _run(self):
        while self._running:
            try:
                self._update_prices()
                self._push_updates()
            except Exception as e:
                print(f"[PriceUpdater] Error: {e}")
            
            time.sleep(self._update_interval)

    def _update_prices(self):
        for symbol in self._default_symbols:
            price_data = self._prices[symbol]
            current_price = price_data['current']
            
            volatility = 0.002  # 0.2% volatility
            change = random.uniform(-volatility, volatility) * current_price
            new_price = max(current_price + change, current_price * 0.5)
            
            price_data['current'] = new_price
            price_data['high'] = max(price_data['high'], new_price)
            price_data['low'] = min(price_data['low'], new_price)
            price_data['change_24h'] = new_price - price_data['open']
            price_data['change_percent_24h'] = ((new_price - price_data['open']) / price_data['open']) * 100

    def _push_updates(self):
        for symbol in self._default_symbols:
            price_data = self._prices[symbol]
            try:
                push_service.push_price_update(
                    symbol=symbol,
                    price=price_data['current'],
                    change_24h=price_data['change_percent_24h']
                )
            except Exception as e:
                print(f"[PriceUpdater] Failed to push {symbol}: {e}")

    def get_price(self, symbol: str) -> Optional[Dict[str, float]]:
        return self._prices.get(symbol)

    def get_all_prices(self) -> Dict[str, Dict[str, float]]:
        return self._prices.copy()

    def subscribe_symbol(self, symbol: str):
        self._subscribed_symbols.add(symbol)

    def unsubscribe_symbol(self, symbol: str):
        self._subscribed_symbols.discard(symbol)

    def calculate_pnl(self, entry_price: float, current_price: float, direction: str = 'long') -> Dict[str, float]:
        if direction == 'long':
            pnl = current_price - entry_price
            pnl_percent = ((current_price - entry_price) / entry_price) * 100
        else:  # short
            pnl = entry_price - current_price
            pnl_percent = ((entry_price - current_price) / entry_price) * 100
        
        return {
            'pnl': round(pnl, 2),
            'pnl_percent': round(pnl_percent, 2),
            'current_price': current_price
        }

    def update_signal_pnl(self, signal_id: int, entry_price: float, symbol: str, direction: str = 'long'):
        price_data = self.get_price(symbol)
        if not price_data:
            return None
        
        pnl_data = self.calculate_pnl(entry_price, price_data['current'], direction)
        
        try:
            push_service.push_pnl_update(
                signal_id=signal_id,
                pnl=pnl_data['pnl'],
                pnl_percent=pnl_data['pnl_percent']
            )
        except Exception as e:
            print(f"[PriceUpdater] Failed to push PnL for signal {signal_id}: {e}")
        
        return pnl_data


price_updater = PriceUpdater()
