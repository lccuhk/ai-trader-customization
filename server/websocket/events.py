"""
WebSocket Events

Handles all WebSocket events including connection, authentication, and real-time features.
"""

from typing import Optional
from datetime import datetime
from flask import request
from flask_socketio import SocketIO, join_room, leave_room, emit

from config import settings
from database import get_db_session
from models import AuthToken, User
from .online_users import online_users
from .push_service import push_service

socketio: Optional[SocketIO] = None


def init_socketio(app):
    global socketio
    socketio = SocketIO(
        app,
        cors_allowed_origins=settings.ALLOWED_ORIGINS,
        cors_credentials=True,
        async_mode='eventlet',
        ping_timeout=60,
        ping_interval=25,
        max_http_buffer_size=1e8,
        transports=['websocket', 'polling']
    )
    
    push_service.init_app(socketio)
    _register_events()
    
    return socketio


def _get_user_from_token(token: str) -> Optional[User]:
    if not token:
        return None
    
    db = get_db_session()
    try:
        auth_token = db.query(AuthToken).filter(
            AuthToken.token == token,
            AuthToken.expires_at > datetime.now()
        ).first()
        
        if auth_token:
            user = db.query(User).filter(User.id == auth_token.user_id).first()
            return user
        return None
    finally:
        db.close()


def _authenticate():
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header[7:]
    else:
        token = request.args.get('token', '')
    
    return _get_user_from_token(token)


def _register_events():
    @socketio.on('connect')
    def handle_connect():
        user = _authenticate()
        
        if not user:
            emit('auth:error', {
                'success': False,
                'message': '未授权，请先登录'
            })
            return False
        
        online_users.add_user(
            user_id=user.id,
            username=user.username,
            display_name=user.display_name or user.username,
            socket_id=request.sid
        )
        
        join_room(f'user:{user.id}')
        join_room('signals')
        join_room('market')
        join_room('online')
        
        emit('auth:success', {
            'success': True,
            'message': '连接成功',
            'user': {
                'id': user.id,
                'username': user.username,
                'display_name': user.display_name or user.username,
                'email': user.email
            },
            'online_count': online_users.get_online_count()
        })
        
        push_service.push_user_status_change(
            user_id=user.id,
            status='online',
            user_info={
                'user_id': user.id,
                'username': user.username,
                'display_name': user.display_name or user.username
            }
        )
        
        push_service.push_online_users_update(online_users.get_online_user_list())
        
        print(f"[WS] User {user.username} connected (sid: {request.sid})")

    @socketio.on('disconnect')
    def handle_disconnect():
        user_id = online_users.get_user_id_by_socket(request.sid)
        user = online_users.get_user(user_id) if user_id else None
        
        user_id = online_users.remove_user(request.sid)
        
        leave_room(f'user:{user_id}')
        leave_room('signals')
        leave_room('market')
        leave_room('online')
        
        if user and not online_users.is_online(user_id):
            push_service.push_user_status_change(
                user_id=user_id,
                status='offline',
                user_info={
                    'user_id': user_id,
                    'username': user.username,
                    'display_name': user.display_name or user.username
                }
            )
        
        push_service.push_online_users_update(online_users.get_online_user_list())
        
        if user:
            print(f"[WS] User {user.username} disconnected (sid: {request.sid})")

    @socketio.on('ping')
    def handle_ping(data=None):
        online_users.update_activity(request.sid)
        emit('pong', {
            'timestamp': datetime.now().isoformat(),
            'online_count': online_users.get_online_count()
        })

    @socketio.on('signal:join')
    def handle_join_signal(data):
        signal_id = data.get('signal_id')
        if signal_id:
            join_room(f'signal:{signal_id}')
            emit('signal:joined', {
                'success': True,
                'signal_id': signal_id,
                'message': f'Joined signal room: {signal_id}'
            })

    @socketio.on('signal:leave')
    def handle_leave_signal(data):
        signal_id = data.get('signal_id')
        if signal_id:
            leave_room(f'signal:{signal_id}')
            emit('signal:left', {
                'success': True,
                'signal_id': signal_id,
                'message': f'Left signal room: {signal_id}'
            })

    @socketio.on('users:get_online')
    def handle_get_online_users():
        emit('users:online', {
            'success': True,
            'data': online_users.get_online_user_list(),
            'count': online_users.get_online_count()
        })

    @socketio.on('market:subscribe')
    def handle_market_subscribe(data):
        symbols = data.get('symbols', [])
        for symbol in symbols:
            join_room(f'market:{symbol}')
        emit('market:subscribed', {
            'success': True,
            'symbols': symbols
        })

    @socketio.on('market:unsubscribe')
    def handle_market_unsubscribe(data):
        symbols = data.get('symbols', [])
        for symbol in symbols:
            leave_room(f'market:{symbol}')
        emit('market:unsubscribed', {
            'success': True,
            'symbols': symbols
        })

    @socketio.on('typing:start')
    def handle_typing_start(data):
        signal_id = data.get('signal_id')
        user_id = online_users.get_user_id_by_socket(request.sid)
        if signal_id and user_id:
            user = online_users.get_user(user_id)
            if user:
                emit('typing:user', {
                    'signal_id': signal_id,
                    'user': {
                        'user_id': user_id,
                        'username': user.username,
                        'display_name': user.display_name
                    }
                }, room=f'signal:{signal_id}', include_self=False)

    @socketio.on('typing:stop')
    def handle_typing_stop(data):
        signal_id = data.get('signal_id')
        user_id = online_users.get_user_id_by_socket(request.sid)
        if signal_id and user_id:
            user = online_users.get_user(user_id)
            if user:
                emit('typing:user_stop', {
                    'signal_id': signal_id,
                    'user_id': user_id
                }, room=f'signal:{signal_id}', include_self=False)

    @socketio.on_error_default
    def default_error_handler(e):
        print(f"[WS Error] {str(e)}")
        emit('error', {
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        })
