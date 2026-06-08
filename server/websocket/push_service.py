"""
Push Service

Real-time push notifications for signals, comments, notifications, and price updates.
"""

from typing import Any, Dict, Optional, List
from datetime import datetime
from flask import json


class PushService:
    def __init__(self):
        self._socketio = None

    def init_app(self, socketio):
        self._socketio = socketio

    def _emit(self, event: str, data: Dict[str, Any], room: Optional[str] = None, namespace: str = '/') -> None:
        if self._socketio is None:
            raise RuntimeError("PushService not initialized with socketio")
        
        if room:
            self._socketio.emit(event, data, room=room, namespace=namespace)
        else:
            self._socketio.emit(event, data, namespace=namespace)

    def push_new_signal(self, signal: Dict[str, Any]) -> None:
        data = {
            'type': 'new_signal',
            'data': signal,
            'timestamp': datetime.now().isoformat()
        }
        self._emit('signal:new', data, room='signals')

    def push_new_comment(self, signal_id: int, comment: Dict[str, Any]) -> None:
        data = {
            'type': 'new_comment',
            'signal_id': signal_id,
            'data': comment,
            'timestamp': datetime.now().isoformat()
        }
        self._emit('comment:new', data, room=f'signal:{signal_id}')
        self._emit('comment:new', data, room='signals')

    def push_new_notification(self, user_id: int, notification: Dict[str, Any]) -> None:
        data = {
            'type': 'new_notification',
            'data': notification,
            'timestamp': datetime.now().isoformat()
        }
        self._emit('notification:new', data, room=f'user:{user_id}')

    def push_signal_update(self, signal_id: int, updates: Dict[str, Any]) -> None:
        data = {
            'type': 'signal_update',
            'signal_id': signal_id,
            'data': updates,
            'timestamp': datetime.now().isoformat()
        }
        self._emit('signal:update', data, room=f'signal:{signal_id}')
        self._emit('signal:update', data, room='signals')

    def push_price_update(self, symbol: str, price: float, change_24h: float) -> None:
        data = {
            'type': 'price_update',
            'symbol': symbol,
            'price': price,
            'change_24h': change_24h,
            'timestamp': datetime.now().isoformat()
        }
        self._emit('price:update', data, room='market')

    def push_pnl_update(self, signal_id: int, pnl: float, pnl_percent: float) -> None:
        data = {
            'type': 'pnl_update',
            'signal_id': signal_id,
            'pnl': pnl,
            'pnl_percent': pnl_percent,
            'timestamp': datetime.now().isoformat()
        }
        self._emit('pnl:update', data, room=f'signal:{signal_id}')

    def push_online_users_update(self, online_users: List[Dict[str, Any]]) -> None:
        data = {
            'type': 'online_users_update',
            'data': online_users,
            'count': len(online_users),
            'timestamp': datetime.now().isoformat()
        }
        self._emit('users:online', data, room='online')

    def push_user_status_change(self, user_id: int, status: str, user_info: Dict[str, Any]) -> None:
        data = {
            'type': 'user_status_change',
            'user_id': user_id,
            'status': status,
            'user': user_info,
            'timestamp': datetime.now().isoformat()
        }
        self._emit('user:status', data, room='online')

    def push_like_update(self, signal_id: int, likes: int, is_liked: bool) -> None:
        data = {
            'type': 'like_update',
            'signal_id': signal_id,
            'likes': likes,
            'is_liked': is_liked,
            'timestamp': datetime.now().isoformat()
        }
        self._emit('like:update', data, room=f'signal:{signal_id}')
        self._emit('like:update', data, room='signals')

    def push_follow_update(self, signal_id: int, is_following: bool, participant_count: int) -> None:
        data = {
            'type': 'follow_update',
            'signal_id': signal_id,
            'is_following': is_following,
            'participant_count': participant_count,
            'timestamp': datetime.now().isoformat()
        }
        self._emit('follow:update', data, room=f'signal:{signal_id}')
        self._emit('follow:update', data, room='signals')

    def broadcast_system_message(self, message: str, level: str = 'info') -> None:
        data = {
            'type': 'system_message',
            'message': message,
            'level': level,
            'timestamp': datetime.now().isoformat()
        }
        self._emit('system:message', data)

    def push_order_update(self, user_id: int, order: Dict[str, Any]) -> None:
        data = {
            'type': 'order_update',
            'data': order,
            'timestamp': datetime.now().isoformat()
        }
        self._emit('order:update', data, room=f'user:{user_id}')

    def push_trade_update(self, user_id: int, trade: Dict[str, Any]) -> None:
        data = {
            'type': 'trade_update',
            'data': trade,
            'timestamp': datetime.now().isoformat()
        }
        self._emit('trade:update', data, room=f'user:{user_id}')

    def push_position_update(self, user_id: int, position: Dict[str, Any]) -> None:
        data = {
            'type': 'position_update',
            'data': position,
            'timestamp': datetime.now().isoformat()
        }
        self._emit('position:update', data, room=f'user:{user_id}')

    def push_portfolio_update(self, user_id: int, portfolio: Dict[str, Any]) -> None:
        data = {
            'type': 'portfolio_update',
            'data': portfolio,
            'timestamp': datetime.now().isoformat()
        }
        self._emit('portfolio:update', data, room=f'user:{user_id}')

    def push_direct_message(self, receiver_id: int, message: Dict[str, Any]) -> None:
        data = {
            'type': 'direct_message',
            'data': message,
            'timestamp': datetime.now().isoformat()
        }
        self._emit('message:new', data, room=f'user:{receiver_id}')

    def push_mention(self, user_id: int, mention: Dict[str, Any]) -> None:
        data = {
            'type': 'mention',
            'data': mention,
            'timestamp': datetime.now().isoformat()
        }
        self._emit('mention:new', data, room=f'user:{user_id}')

    def push_ai_alert(self, user_id: int, alert: Dict[str, Any]) -> None:
        data = {
            'type': 'ai_alert',
            'data': alert,
            'timestamp': datetime.now().isoformat()
        }
        self._emit('ai:alert', data, room=f'user:{user_id}')

    def push_ai_signal(self, user_id: int, signal: Dict[str, Any]) -> None:
        data = {
            'type': 'ai_signal',
            'data': signal,
            'timestamp': datetime.now().isoformat()
        }
        self._emit('ai:signal', data, room=f'user:{user_id}')


push_service = PushService()
