"""
Online Users Management

Tracks connected users and their WebSocket sessions.
"""

from typing import Dict, Set, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class UserSession:
    user_id: int
    username: str
    display_name: str
    socket_ids: Set[str] = field(default_factory=set)
    connected_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)


class OnlineUsersManager:
    def __init__(self):
        self._sessions: Dict[int, UserSession] = {}
        self._socket_to_user: Dict[str, int] = {}

    def add_user(self, user_id: int, username: str, display_name: str, socket_id: str) -> None:
        if user_id not in self._sessions:
            self._sessions[user_id] = UserSession(
                user_id=user_id,
                username=username,
                display_name=display_name
            )
        self._sessions[user_id].socket_ids.add(socket_id)
        self._sessions[user_id].last_active = datetime.now()
        self._socket_to_user[socket_id] = user_id

    def remove_user(self, socket_id: str) -> Optional[int]:
        user_id = self._socket_to_user.pop(socket_id, None)
        if user_id and user_id in self._sessions:
            self._sessions[user_id].socket_ids.discard(socket_id)
            if not self._sessions[user_id].socket_ids:
                del self._sessions[user_id]
        return user_id

    def get_user(self, user_id: int) -> Optional[UserSession]:
        return self._sessions.get(user_id)

    def is_online(self, user_id: int) -> bool:
        return user_id in self._sessions and len(self._sessions[user_id].socket_ids) > 0

    def get_online_users(self) -> Dict[int, UserSession]:
        return self._sessions.copy()

    def get_online_count(self) -> int:
        return len(self._sessions)

    def get_user_sockets(self, user_id: int) -> Set[str]:
        if user_id in self._sessions:
            return self._sessions[user_id].socket_ids.copy()
        return set()

    def update_activity(self, socket_id: str) -> None:
        user_id = self._socket_to_user.get(socket_id)
        if user_id and user_id in self._sessions:
            self._sessions[user_id].last_active = datetime.now()

    def get_user_id_by_socket(self, socket_id: str) -> Optional[int]:
        return self._socket_to_user.get(socket_id)

    def get_online_user_list(self) -> list:
        return [
            {
                'user_id': session.user_id,
                'username': session.username,
                'display_name': session.display_name,
                'connected_at': session.connected_at.isoformat(),
                'last_active': session.last_active.isoformat()
            }
            for session in self._sessions.values()
        ]


online_users = OnlineUsersManager()
