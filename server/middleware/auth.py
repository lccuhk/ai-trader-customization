"""
Authentication Middleware

User authentication and authorization middleware.
"""

from functools import wraps
from typing import Callable, Optional

from flask import request, jsonify, g

from database import get_db_session
from models import AuthToken


def get_current_user_id() -> Optional[int]:
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.replace('Bearer ', '').strip()
    if not token:
        return None
    
    db = get_db_session()
    try:
        auth_token = db.query(AuthToken).filter(AuthToken.token == token).first()
        if auth_token:
            return auth_token.user_id
        return None
    finally:
        db.close()


def require_auth(f: Callable) -> Callable:
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({
                'success': False,
                'message': '未授权，请先登录'
            }), 401
        
        request.current_user_id = user_id
        g.current_user_id = user_id
        return f(*args, **kwargs)
    
    return decorated
