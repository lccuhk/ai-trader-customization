import threading
import time
import random
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

from database import get_db
from models import Order, Trade, Position, Portfolio, Signal
from websocket import push_service


class SimulationEngine:
    def __init__(self):
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._prices: Dict[str, float] = {}
        self._lock = threading.Lock()
        self._default_symbols = [
            'BTC', 'ETH', 'BNB', 'SOL', 'XRP',
            'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA',
            'EUR/USD', 'GBP/USD', 'USD/JPY', 'XAU/USD'
        ]
        self._base_prices = {
            'BTC': 65000.0, 'ETH': 3500.0, 'BNB': 580.0, 'SOL': 145.0, 'XRP': 0.52,
            'AAPL': 190.0, 'GOOGL': 140.0, 'MSFT': 420.0, 'AMZN': 180.0, 'TSLA': 250.0,
            'EUR/USD': 1.08, 'GBP/USD': 1.27, 'USD/JPY': 155.0, 'XAU/USD': 2350.0
        }

    def start(self):
        if self._running:
            return
        self._running = True
        self._init_prices()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        print(f"[Simulation] Engine started, monitoring {len(self._default_symbols)} symbols")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)

    def _init_prices(self):
        with self._lock:
            self._prices = dict(self._base_prices)

    def _run(self):
        while self._running:
            try:
                self._update_prices()
                self._process_pending_orders()
                self._update_positions()
                self._update_portfolios()
                self._update_signal_pnl()
            except Exception as e:
                print(f"[Simulation] Error in main loop: {e}")
            time.sleep(5)

    def _update_prices(self):
        with self._lock:
            for symbol in self._default_symbols:
                volatility = 0.002 if '/' in symbol else 0.005
                change = random.uniform(-volatility, volatility)
                self._prices[symbol] = float(
                    Decimal(str(self._prices[symbol] * (1 + change)))
                    .quantize(Decimal('0.01' if '/' in symbol else '0.0001'), rounding=ROUND_HALF_UP)
                )

    def get_price(self, symbol: str) -> Optional[float]:
        with self._lock:
            return self._prices.get(symbol)

    def get_all_prices(self) -> Dict[str, float]:
        with self._lock:
            return dict(self._prices)

    def _process_pending_orders(self):
        db = next(get_db())
        try:
            pending_orders = db.query(Order).filter(
                Order.status == 'pending',
                Order.is_simulation == True
            ).all()

            for order in pending_orders:
                self._process_order(order, db)
        except Exception as e:
            print(f"[Simulation] Error processing orders: {e}")
            db.rollback()
        finally:
            db.close()

    def _process_order(self, order: Order, db):
        current_price = self.get_price(order.symbol)
        if not current_price:
            return

        should_execute = False
        execution_price = current_price

        if order.order_type == 'market':
            should_execute = True
            execution_price = current_price
        elif order.order_type == 'limit':
            if order.side == 'buy' and current_price <= order.price:
                should_execute = True
                execution_price = order.price
            elif order.side == 'sell' and current_price >= order.price:
                should_execute = True
                execution_price = order.price
        elif order.order_type == 'stop':
            if order.side == 'sell' and current_price <= order.price:
                should_execute = True
                execution_price = current_price
            elif order.side == 'buy' and current_price >= order.price:
                should_execute = True
                execution_price = current_price

        if should_execute:
            self._execute_order(order, execution_price, db)

    def _execute_order(self, order: Order, execution_price: float, db):
        try:
            order.status = 'filled'
            order.filled_price = execution_price
            order.filled_quantity = order.quantity
            order.filled_at = datetime.now(timezone.utc)

            trade = Trade(
                user_id=order.user_id,
                order_id=order.id,
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                price=execution_price,
                pnl=0,
                pnl_percent=0,
                is_simulation=True,
                signal_id=order.signal_id
            )

            self._update_position(order, execution_price, trade, db)

            db.add(trade)
            db.commit()

            try:
                push_service.push_order_update(order.user_id, self._order_to_dict(order))
                push_service.push_trade_update(order.user_id, self._trade_to_dict(trade))
            except Exception as e:
                print(f"[Simulation] Failed to push updates: {e}")

        except Exception as e:
            print(f"[Simulation] Error executing order {order.id}: {e}")
            db.rollback()

    def _update_position(self, order: Order, execution_price: float, trade: Trade, db):
        position = db.query(Position).filter(
            Position.user_id == order.user_id,
            Position.symbol == order.symbol,
            Position.is_simulation == True
        ).first()

        if order.side == 'buy':
            if not position:
                position = Position(
                    user_id=order.user_id,
                    symbol=order.symbol,
                    quantity=order.quantity,
                    avg_price=execution_price,
                    current_price=execution_price,
                    unrealized_pnl=0,
                    is_simulation=True
                )
                db.add(position)
            else:
                total_quantity = position.quantity + order.quantity
                total_cost = position.quantity * position.avg_price + order.quantity * execution_price
                position.avg_price = total_cost / total_quantity
                position.quantity = total_quantity
                position.current_price = execution_price
                position.unrealized_pnl = (execution_price - position.avg_price) * position.quantity
        else:
            if position and position.quantity >= order.quantity:
                pnl = (execution_price - position.avg_price) * order.quantity
                pnl_percent = (execution_price - position.avg_price) / position.avg_price * 100
                trade.pnl = pnl
                trade.pnl_percent = pnl_percent

                position.quantity -= order.quantity
                position.current_price = execution_price
                if position.quantity > 0:
                    position.unrealized_pnl = (execution_price - position.avg_price) * position.quantity
                else:
                    db.delete(position)

    def _update_positions(self):
        db = next(get_db())
        try:
            positions = db.query(Position).filter(Position.is_simulation == True).all()
            for position in positions:
                current_price = self.get_price(position.symbol)
                if current_price:
                    position.current_price = current_price
                    position.unrealized_pnl = (current_price - position.avg_price) * position.quantity
                    position.updated_at = datetime.now(timezone.utc)
            db.commit()
        except Exception as e:
            print(f"[Simulation] Error updating positions: {e}")
            db.rollback()
        finally:
            db.close()

    def _update_portfolios(self):
        db = next(get_db())
        try:
            portfolios = db.query(Portfolio).filter(Portfolio.is_simulation == True).all()
            for portfolio in portfolios:
                self._update_portfolio(portfolio, db)
            db.commit()
        except Exception as e:
            print(f"[Simulation] Error updating portfolios: {e}")
            db.rollback()
        finally:
            db.close()

    def _update_portfolio(self, portfolio: Portfolio, db):
        positions = db.query(Position).filter(
            Position.user_id == portfolio.user_id,
            Position.is_simulation == True
        ).all()

        trades = db.query(Trade).filter(
            Trade.user_id == portfolio.user_id,
            Trade.is_simulation == True
        ).all()

        total_position_value = sum(
            (pos.current_price or self.get_price(pos.symbol) or 0) * pos.quantity
            for pos in positions
        )

        total_pnl = sum(trade.pnl for trade in trades)
        unrealized_pnl = sum(pos.unrealized_pnl for pos in positions)

        winning_trades = [t for t in trades if t.pnl > 0]
        win_rate = len(winning_trades) / len(trades) * 100 if trades else 0

        portfolio.total_pnl = total_pnl
        portfolio.unrealized_pnl = unrealized_pnl
        portfolio.total_value = portfolio.total_balance + total_position_value
        portfolio.win_rate = win_rate
        portfolio.total_trades = len(trades)
        portfolio.updated_at = datetime.now(timezone.utc)

    def _update_signal_pnl(self):
        db = next(get_db())
        try:
            signals = db.query(Signal).filter(
                Signal.status.in_(['active', 'partial']),
                Signal.is_simulation == True
            ).all()

            for signal in signals:
                if not signal.symbols:
                    continue
                symbol = signal.symbols[0]
                current_price = self.get_price(symbol)
                if not current_price or not signal.entry_price:
                    continue

                if signal.direction == 'long':
                    pnl_percent = (current_price - signal.entry_price) / signal.entry_price * 100
                else:
                    pnl_percent = (signal.entry_price - current_price) / signal.entry_price * 100

                pnl = pnl_percent / 100 * (signal.position_size or 1000)

                signal.current_price = current_price
                signal.pnl = pnl
                signal.pnl_percent = pnl_percent

                if signal.take_profit and signal.direction == 'long' and current_price >= signal.take_profit:
                    signal.status = 'closed'
                    signal.close_reason = 'take_profit'
                elif signal.take_profit and signal.direction == 'short' and current_price <= signal.take_profit:
                    signal.status = 'closed'
                    signal.close_reason = 'take_profit'
                elif signal.stop_loss and signal.direction == 'long' and current_price <= signal.stop_loss:
                    signal.status = 'closed'
                    signal.close_reason = 'stop_loss'
                elif signal.stop_loss and signal.direction == 'short' and current_price >= signal.stop_loss:
                    signal.status = 'closed'
                    signal.close_reason = 'stop_loss'

                try:
                    push_service.push_pnl_update(signal.id, pnl, pnl_percent)
                except Exception as e:
                    print(f"[Simulation] Failed to push PnL update: {e}")

            db.commit()
        except Exception as e:
            print(f"[Simulation] Error updating signal PnL: {e}")
            db.rollback()
        finally:
            db.close()

    def _order_to_dict(self, order: Order) -> Dict[str, Any]:
        return {
            'id': order.id,
            'symbol': order.symbol,
            'side': order.side,
            'type': order.order_type,
            'quantity': order.quantity,
            'price': order.price,
            'status': order.status,
            'filled_price': order.filled_price,
            'filled_quantity': order.filled_quantity,
            'is_simulation': order.is_simulation
        }

    def _trade_to_dict(self, trade: Trade) -> Dict[str, Any]:
        return {
            'id': trade.id,
            'symbol': trade.symbol,
            'side': trade.side,
            'quantity': trade.quantity,
            'price': trade.price,
            'pnl': trade.pnl,
            'pnl_percent': trade.pnl_percent,
            'is_simulation': trade.is_simulation,
            'created_at': trade.created_at.isoformat() if trade.created_at else None
        }


simulation_engine = SimulationEngine()
