"""
WebSocket Module

Real-time communication module using Flask-SocketIO.
"""

from . import events
from .online_users import online_users
from .push_service import push_service
from .price_updater import price_updater

init_socketio = events.init_socketio

def __getattr__(name):
    if name == 'socketio':
        return events.socketio
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ['socketio', 'init_socketio', 'online_users', 'push_service', 'price_updater']
