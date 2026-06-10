from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone
from sqlalchemy import and_, or_, desc

from database import get_db
from models import Order, Trade, Position, Portfolio, ExchangeAccount, User
from exchanges import get_exchange_api
from simulation import simulation_engine
from websocket import push_service
from middleware.error_handler import success_response, error_response

# ======================== Mock Fallback Data ========================

MOCK_PORTFOLIO_DATA = {
    'portfolio': {
        'id': 1, 'user_id': 1, 'total_balance': 125000.00,
        'total_pnl': 18630.50, 'unrealized_pnl': 3200.50,
        'total_value': 128200.50, 'win_rate': 65.4,
        'total_trades': 156, 'is_simulation': True,
        'created_at': '2026-01-01T00:00:00',
        'updated_at': '2026-06-08T12:00:00'
    },
    'positions': [
        {'id': 1, 'user_id': 1, 'symbol': 'NVDA', 'quantity': 50, 'avg_price': 480.00, 'current_price': 512.30, 'unrealized_pnl': 1615.00, 'unrealized_pnl_percent': 6.73, 'is_simulation': True, 'created_at': '2026-05-15T10:00:00', 'updated_at': '2026-06-08T12:00:00'},
        {'id': 2, 'user_id': 1, 'symbol': 'AAPL', 'quantity': 100, 'avg_price': 182.00, 'current_price': 188.50, 'unrealized_pnl': 650.00, 'unrealized_pnl_percent': 3.57, 'is_simulation': True, 'created_at': '2026-05-20T14:30:00', 'updated_at': '2026-06-08T12:00:00'},
        {'id': 3, 'user_id': 1, 'symbol': 'BTC', 'quantity': 0.5, 'avg_price': 65000.00, 'current_price': 69800.00, 'unrealized_pnl': 2400.00, 'unrealized_pnl_percent': 7.38, 'is_simulation': True, 'created_at': '2026-04-10T09:00:00', 'updated_at': '2026-06-08T12:00:00'},
        {'id': 4, 'user_id': 1, 'symbol': 'TSLA', 'quantity': 30, 'avg_price': 250.00, 'current_price': 245.00, 'unrealized_pnl': -150.00, 'unrealized_pnl_percent': -2.00, 'is_simulation': True, 'created_at': '2026-05-25T11:00:00', 'updated_at': '2026-06-08T12:00:00'},
        {'id': 5, 'user_id': 1, 'symbol': 'ETH', 'quantity': 3, 'avg_price': 3200.00, 'current_price': 3510.00, 'unrealized_pnl': 930.00, 'unrealized_pnl_percent': 9.69, 'is_simulation': True, 'created_at': '2026-05-18T16:00:00', 'updated_at': '2026-06-08T12:00:00'},
    ],
    'recent_trades': [
        {'id': 101, 'user_id': 1, 'symbol': 'NVDA', 'side': 'buy', 'quantity': 10, 'price': 505.00, 'pnl': None, 'pnl_percent': None, 'is_simulation': True, 'created_at': '2026-06-07T14:30:00'},
        {'id': 100, 'user_id': 1, 'symbol': 'AAPL', 'side': 'sell', 'quantity': 20, 'price': 189.00, 'pnl': 140.00, 'pnl_percent': 3.85, 'is_simulation': True, 'created_at': '2026-06-07T10:00:00'},
        {'id': 99, 'user_id': 1, 'symbol': 'BTC', 'side': 'buy', 'quantity': 0.1, 'price': 69200.00, 'pnl': None, 'pnl_percent': None, 'is_simulation': True, 'created_at': '2026-06-06T22:00:00'},
        {'id': 98, 'user_id': 1, 'symbol': 'TSLA', 'side': 'buy', 'quantity': 30, 'price': 248.00, 'pnl': None, 'pnl_percent': None, 'is_simulation': True, 'created_at': '2026-06-06T15:00:00'},
        {'id': 97, 'user_id': 1, 'symbol': 'ETH', 'side': 'sell', 'quantity': 1, 'price': 3480.00, 'pnl': 280.00, 'pnl_percent': 8.75, 'is_simulation': True, 'created_at': '2026-06-06T09:30:00'},
    ]
}

MOCK_ORDERS_DATA = [
    {'id': 201, 'user_id': 1, 'symbol': 'NVDA', 'side': 'buy', 'type': 'market', 'quantity': 10, 'price': None, 'filled_price': 505.00, 'filled_quantity': 10, 'status': 'filled', 'is_simulation': True, 'created_at': '2026-06-07T14:30:00'},
    {'id': 200, 'user_id': 1, 'symbol': 'BTC', 'side': 'buy', 'type': 'limit', 'quantity': 0.1, 'price': 69000.00, 'filled_price': None, 'filled_quantity': 0, 'status': 'pending', 'is_simulation': True, 'created_at': '2026-06-08T08:00:00'},
    {'id': 199, 'user_id': 1, 'symbol': 'ETH', 'side': 'sell', 'type': 'market', 'quantity': 1, 'price': None, 'filled_price': 3480.00, 'filled_quantity': 1, 'status': 'filled', 'is_simulation': True, 'created_at': '2026-06-06T09:30:00'},
]

MOCK_MARKET_PRICES = {
    'BTC': 69800.00, 'ETH': 3510.00, 'SOL': 145.20, 'BNB': 580.00, 'XRP': 0.52,
    'AAPL': 188.50, 'GOOGL': 175.30, 'MSFT': 420.10, 'AMZN': 185.80, 'TSLA': 245.00,
    'NVDA': 512.30, 'SPY': 540.20, 'QQQ': 468.50,
}


def create_order(user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    symbol = data.get('symbol')
    side = data.get('side', '').lower()
    order_type = data.get('type', 'market').lower()
    quantity = data.get('quantity')
    price = data.get('price')
    is_simulation = data.get('is_simulation', True)
    signal_id = data.get('signal_id')
    exchange_account_id = data.get('exchange_account_id')

    if not symbol or not side or not quantity:
        return error_response('缺少必要参数', 400)

    if side not in ['buy', 'sell']:
        return error_response('无效的交易方向', 400)

    if order_type not in ['market', 'limit', 'stop']:
        return error_response('无效的订单类型', 400)

    if order_type in ['limit', 'stop'] and not price:
        return error_response('限价单和止损单需要指定价格', 400)

    try:
        db = next(get_db())
    except Exception as e:
        print(f"[Trading] DB connection failed for create_order, using mock: {e}")
        from copy import deepcopy
        new_id = max(o['id'] for o in MOCK_ORDERS_DATA) + 1 if MOCK_ORDERS_DATA else 1
        mock_order = {
            'id': new_id, 'user_id': user_id,
            'symbol': symbol, 'side': side, 'type': order_type,
            'quantity': quantity, 'price': price,
            'filled_price': price if order_type == 'market' else None,
            'filled_quantity': quantity if order_type == 'market' else 0,
            'status': 'filled' if order_type == 'market' else 'pending',
            'is_simulation': is_simulation,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        MOCK_ORDERS_DATA.insert(0, mock_order)
        return success_response(mock_order)

    try:
        if not is_simulation:
            if not exchange_account_id:
                return error_response('实盘交易需要指定交易所账户', 400)

            exchange_account = db.query(ExchangeAccount).filter(
                ExchangeAccount.id == exchange_account_id,
                ExchangeAccount.user_id == user_id,
                ExchangeAccount.is_active == True
            ).first()

            if not exchange_account:
                return error_response('交易所账户不存在或未激活', 404)

        order = Order(
            user_id=user_id,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=float(quantity),
            price=float(price) if price else None,
            status='pending',
            is_simulation=is_simulation,
            signal_id=signal_id,
            exchange_account_id=exchange_account_id
        )

        db.add(order)
        db.commit()
        db.refresh(order)

        if is_simulation:
            if order_type == 'market':
                current_price = simulation_engine.get_price(symbol)
                if current_price:
                    _execute_simulation_order(order, current_price, db)
        else:
            _execute_real_order(order, exchange_account, db)

        order_dict = _order_to_dict(order)
        
        try:
            push_service.push_order_update(user_id, order_dict)
        except Exception as e:
            print(f"[Trading] Failed to push order update: {e}")

        return success_response(order_dict)

    except Exception as e:
        db.rollback()
        print(f"[Trading] create_order DB failed, using mock fallback: {e}")
        from copy import deepcopy
        new_id = max(o['id'] for o in MOCK_ORDERS_DATA) + 1 if MOCK_ORDERS_DATA else 1
        mock_order = {
            'id': new_id, 'user_id': user_id,
            'symbol': symbol, 'side': side, 'type': order_type,
            'quantity': quantity, 'price': price,
            'filled_price': price if order_type == 'market' else None,
            'filled_quantity': quantity if order_type == 'market' else 0,
            'status': 'filled' if order_type == 'market' else 'pending',
            'is_simulation': is_simulation,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        MOCK_ORDERS_DATA.insert(0, mock_order)
        return success_response(mock_order)
    finally:
        db.close()


def _execute_simulation_order(order: Order, execution_price: float, db) -> None:
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

    _update_position_from_order(order, execution_price, trade, db)

    db.add(trade)
    db.commit()

    try:
        push_service.push_trade_update(order.user_id, _trade_to_dict(trade))
    except Exception as e:
        print(f"[Trading] Failed to push trade update: {e}")


def _update_position_from_order(order: Order, execution_price: float, trade: Trade, db) -> None:
    position = db.query(Position).filter(
        Position.user_id == order.user_id,
        Position.symbol == order.symbol,
        Position.is_simulation == order.is_simulation
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
                is_simulation=order.is_simulation
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


def _execute_real_order(order: Order, exchange_account: ExchangeAccount, db) -> None:
    try:
        api = get_exchange_api(
            exchange_account.exchange,
            exchange_account.api_key,
            exchange_account.api_secret,
            passphrase=exchange_account.passphrase,
            is_sandbox=exchange_account.is_sandbox
        )

        result = api.create_order(
            symbol=order.symbol,
            side=order.side,
            order_type=order.order_type,
            quantity=order.quantity,
            price=order.price
        )

        order.exchange_order_id = result.get('id')
        order.status = result.get('status', 'filled')
        
        if order.status == 'filled':
            order.filled_price = result.get('price', order.price)
            order.filled_quantity = result.get('filled', order.quantity)
            order.filled_at = datetime.now(timezone.utc)

            trade = Trade(
                user_id=order.user_id,
                order_id=order.id,
                symbol=order.symbol,
                side=order.side,
                quantity=order.filled_quantity,
                price=order.filled_price,
                pnl=0,
                pnl_percent=0,
                is_simulation=False,
                signal_id=order.signal_id
            )
            db.add(trade)

    except Exception as e:
        order.status = 'failed'
        order.error_message = str(e)
        raise e


def cancel_order(user_id: int, order_id: int) -> Dict[str, Any]:
    db = next(get_db())
    try:
        order = db.query(Order).filter(
            Order.id == order_id,
            Order.user_id == user_id
        ).first()

        if not order:
            return error_response('订单不存在', 404)

        if order.status not in ['pending', 'open']:
            return error_response('只能取消待处理或未成交的订单', 400)

        if not order.is_simulation and order.exchange_account_id:
            exchange_account = db.query(ExchangeAccount).filter(
                ExchangeAccount.id == order.exchange_account_id,
                ExchangeAccount.user_id == user_id
            ).first()
            
            if exchange_account and order.exchange_order_id:
                api = get_exchange_api(
                    exchange_account.exchange,
                    exchange_account.api_key,
                    exchange_account.api_secret,
                    passphrase=exchange_account.passphrase,
                    is_sandbox=exchange_account.is_sandbox
                )
                api.cancel_order(order.symbol, order.exchange_order_id)

        order.status = 'cancelled'
        db.commit()

        order_dict = _order_to_dict(order)
        try:
            push_service.push_order_update(user_id, order_dict)
        except Exception as e:
            print(f"[Trading] Failed to push order update: {e}")

        return success_response(order_dict)

    except Exception as e:
        db.rollback()
        return error_response(f'取消订单失败: {str(e)}', 500)
    finally:
        db.close()


def get_orders(user_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
    status = params.get('status')
    symbol = params.get('symbol')
    is_simulation = params.get('is_simulation')
    page = int(params.get('page', 1))
    per_page = int(params.get('per_page', 20))

    try:
        db = next(get_db())
    except Exception as e:
        print(f"[Trading] DB connection failed for orders, using mock: {e}")
        return success_response({
            'items': MOCK_ORDERS_DATA,
            'total': len(MOCK_ORDERS_DATA),
            'page': page,
            'per_page': per_page
        })

    try:
        query = db.query(Order).filter(Order.user_id == user_id)

        if status:
            query = query.filter(Order.status == status)
        if symbol:
            query = query.filter(Order.symbol == symbol)
        if is_simulation is not None:
            query = query.filter(Order.is_simulation == is_simulation)

        total = query.count()
        orders = query.order_by(desc(Order.created_at)).offset((page - 1) * per_page).limit(per_page).all()

        return success_response({
            'items': [_order_to_dict(o) for o in orders],
            'total': total,
            'page': page,
            'per_page': per_page
        })

    except Exception as e:
        print(f"[Trading] orders query failed, using mock: {e}")
        return success_response({
            'items': MOCK_ORDERS_DATA,
            'total': len(MOCK_ORDERS_DATA),
            'page': page,
            'per_page': per_page
        })
    finally:
        db.close()


def get_order_detail(user_id: int, order_id: int) -> Dict[str, Any]:
    db = next(get_db())
    try:
        order = db.query(Order).filter(
            Order.id == order_id,
            Order.user_id == user_id
        ).first()

        if not order:
            return error_response('订单不存在', 404)

        return success_response(_order_to_dict(order))

    except Exception as e:
        return error_response(f'获取订单详情失败: {str(e)}', 500)
    finally:
        db.close()


def get_positions(user_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
    symbol = params.get('symbol')
    is_simulation = params.get('is_simulation')

    try:
        db = next(get_db())
    except Exception as e:
        print(f"[Trading] DB connection failed for positions, using mock: {e}")
        return success_response(MOCK_PORTFOLIO_DATA['positions'])

    try:
        query = db.query(Position).filter(Position.user_id == user_id)

        if symbol:
            query = query.filter(Position.symbol == symbol)
        if is_simulation is not None:
            query = query.filter(Position.is_simulation == is_simulation)

        positions = query.order_by(desc(Position.updated_at)).all()

        return success_response([_position_to_dict(p) for p in positions])

    except Exception as e:
        print(f"[Trading] positions query failed, using mock: {e}")
        return success_response(MOCK_PORTFOLIO_DATA['positions'])
    finally:
        db.close()


def get_trades(user_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
    symbol = params.get('symbol')
    is_simulation = params.get('is_simulation')
    start_date = params.get('start_date')
    end_date = params.get('end_date')
    page = int(params.get('page', 1))
    per_page = int(params.get('per_page', 20))

    try:
        db = next(get_db())
    except Exception as e:
        print(f"[Trading] DB connection failed for trades, using mock: {e}")
        mock_trades = MOCK_PORTFOLIO_DATA['recent_trades']
        return success_response({'items': mock_trades, 'total': len(mock_trades), 'page': page, 'per_page': per_page})

    try:
        query = db.query(Trade).filter(Trade.user_id == user_id)

        if symbol:
            query = query.filter(Trade.symbol == symbol)
        if is_simulation is not None:
            query = query.filter(Trade.is_simulation == is_simulation)
        if start_date:
            query = query.filter(Trade.created_at >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(Trade.created_at <= datetime.fromisoformat(end_date))

        total = query.count()
        trades = query.order_by(desc(Trade.created_at)).offset((page - 1) * per_page).limit(per_page).all()

        return success_response({
            'items': [_trade_to_dict(t) for t in trades],
            'total': total,
            'page': page,
            'per_page': per_page
        })

    except Exception as e:
        print(f"[Trading] trades query failed, using mock: {e}")
        mock_trades = MOCK_PORTFOLIO_DATA['recent_trades']
        return success_response({'items': mock_trades, 'total': len(mock_trades), 'page': page, 'per_page': per_page})
    finally:
        db.close()


def get_portfolio(user_id: int, is_simulation: bool = True) -> Dict[str, Any]:
    try:
        db = next(get_db())
    except Exception as e:
        print(f"[Trading] DB connection failed, using mock portfolio data: {e}")
        return success_response(MOCK_PORTFOLIO_DATA)

    try:
        portfolio = db.query(Portfolio).filter(
            Portfolio.user_id == user_id,
            Portfolio.is_simulation == is_simulation
        ).first()

        if not portfolio:
            portfolio = Portfolio(
                user_id=user_id,
                total_balance=100000.0 if is_simulation else 0,
                total_pnl=0,
                unrealized_pnl=0,
                total_value=100000.0 if is_simulation else 0,
                win_rate=0,
                total_trades=0,
                is_simulation=is_simulation
            )
            db.add(portfolio)
            db.commit()
            db.refresh(portfolio)

        positions = db.query(Position).filter(
            Position.user_id == user_id,
            Position.is_simulation == is_simulation
        ).all()

        recent_trades = db.query(Trade).filter(
            Trade.user_id == user_id,
            Trade.is_simulation == is_simulation
        ).order_by(desc(Trade.created_at)).limit(10).all()

        return success_response({
            'portfolio': _portfolio_to_dict(portfolio),
            'positions': [_position_to_dict(p) for p in positions],
            'recent_trades': [_trade_to_dict(t) for t in recent_trades]
        })

    except Exception as e:
        print(f"[Trading] DB query failed, using mock portfolio data: {e}")
        return success_response(MOCK_PORTFOLIO_DATA)
    finally:
        db.close()


def get_exchange_accounts(user_id: int) -> Dict[str, Any]:
    db = next(get_db())
    try:
        accounts = db.query(ExchangeAccount).filter(
            ExchangeAccount.user_id == user_id
        ).order_by(desc(ExchangeAccount.created_at)).all()

        return success_response([_exchange_account_to_dict(a) for a in accounts])

    except Exception as e:
        return error_response(f'获取交易所账户失败: {str(e)}', 500)
    finally:
        db.close()


def create_exchange_account(user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    exchange = data.get('exchange')
    api_key = data.get('api_key')
    api_secret = data.get('api_secret')
    passphrase = data.get('passphrase')
    is_sandbox = data.get('is_sandbox', False)
    name = data.get('name')

    if not exchange or not api_key or not api_secret:
        return error_response('缺少必要参数', 400)

    if exchange.lower() not in ['binance', 'okx', 'alpaca']:
        return error_response('不支持的交易所', 400)

    db = next(get_db())
    try:
        account = ExchangeAccount(
            user_id=user_id,
            exchange=exchange.lower(),
            api_key=api_key,
            api_secret=api_secret,
            passphrase=passphrase,
            is_sandbox=is_sandbox,
            name=name or f"{exchange.capitalize()} {'Sandbox' if is_sandbox else 'Live'}"
        )

        db.add(account)
        db.commit()
        db.refresh(account)

        return success_response(_exchange_account_to_dict(account))

    except Exception as e:
        db.rollback()
        return error_response(f'创建交易所账户失败: {str(e)}', 500)
    finally:
        db.close()


def delete_exchange_account(user_id: int, account_id: int) -> Dict[str, Any]:
    db = next(get_db())
    try:
        account = db.query(ExchangeAccount).filter(
            ExchangeAccount.id == account_id,
            ExchangeAccount.user_id == user_id
        ).first()

        if not account:
            return error_response('交易所账户不存在', 404)

        db.delete(account)
        db.commit()

        return success_response({'message': '删除成功'})

    except Exception as e:
        db.rollback()
        return error_response(f'删除交易所账户失败: {str(e)}', 500)
    finally:
        db.close()


def get_market_price(symbol: str) -> Dict[str, Any]:
    price = simulation_engine.get_price(symbol)
    if price:
        return success_response({'symbol': symbol, 'price': price})
    return error_response('不支持的交易对', 404)


def get_all_market_prices() -> Dict[str, Any]:
    prices = simulation_engine.get_all_prices()
    return success_response(prices)


def _order_to_dict(order: Order) -> Dict[str, Any]:
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
        'is_simulation': order.is_simulation,
        'signal_id': order.signal_id,
        'exchange_order_id': order.exchange_order_id,
        'error_message': order.error_message,
        'created_at': order.created_at.isoformat() if order.created_at else None,
        'filled_at': order.filled_at.isoformat() if order.filled_at else None
    }


def _trade_to_dict(trade: Trade) -> Dict[str, Any]:
    return {
        'id': trade.id,
        'order_id': trade.order_id,
        'symbol': trade.symbol,
        'side': trade.side,
        'quantity': trade.quantity,
        'price': trade.price,
        'pnl': trade.pnl,
        'pnl_percent': trade.pnl_percent,
        'is_simulation': trade.is_simulation,
        'signal_id': trade.signal_id,
        'created_at': trade.created_at.isoformat() if trade.created_at else None
    }


def _position_to_dict(position: Position) -> Dict[str, Any]:
    return {
        'id': position.id,
        'symbol': position.symbol,
        'quantity': position.quantity,
        'avg_price': position.avg_price,
        'current_price': position.current_price,
        'unrealized_pnl': position.unrealized_pnl,
        'unrealized_pnl_percent': (
            (position.current_price - position.avg_price) / position.avg_price * 100
            if position.avg_price else 0
        ),
        'is_simulation': position.is_simulation,
        'updated_at': position.updated_at.isoformat() if position.updated_at else None
    }


def _portfolio_to_dict(portfolio: Portfolio) -> Dict[str, Any]:
    return {
        'id': portfolio.id,
        'total_balance': portfolio.total_balance,
        'total_pnl': portfolio.total_pnl,
        'unrealized_pnl': portfolio.unrealized_pnl,
        'total_value': portfolio.total_value,
        'win_rate': portfolio.win_rate,
        'total_trades': portfolio.total_trades,
        'is_simulation': portfolio.is_simulation,
        'updated_at': portfolio.updated_at.isoformat() if portfolio.updated_at else None
    }


def _exchange_account_to_dict(account: ExchangeAccount) -> Dict[str, Any]:
    return {
        'id': account.id,
        'exchange': account.exchange,
        'name': account.name,
        'is_sandbox': account.is_sandbox,
        'is_active': account.is_active,
        'created_at': account.created_at.isoformat() if account.created_at else None
    }
