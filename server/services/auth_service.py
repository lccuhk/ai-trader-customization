"""
Authentication Service

Business logic for user authentication and authorization.
"""

from typing import Optional, Tuple, Dict, Any
from datetime import datetime

from database import get_db_session
from models import User, AuthToken
from utils.security import hash_password, verify_password, generate_token, get_token_expiry
from utils.helpers import model_to_dict


def login(username: str, password: str) -> Tuple[Dict[str, Any], int]:
    db = get_db_session()
    try:
        from sqlalchemy import or_
        user = db.query(User).filter(
            or_(User.email == username, User.username == username),
        ).first()

        if user and verify_password(password, user.password_hash):
            token = generate_token()
            expires_at = get_token_expiry()

            auth_token = AuthToken(
                user_id=user.id,
                token=token,
                expires_at=expires_at
            )
            db.add(auth_token)
            db.commit()

            user_username = user.username or user.email.split('@')[0]
            user_display_name = user.display_name or user_username

            return {
                'success': True,
                'token': token,
                'user': {
                    'id': user.id,
                    'username': user_username,
                    'email': user.email,
                    'display_name': user_display_name
                }
            }, 200
        else:
            return {
                'success': False,
                'message': '用户名或密码错误'
            }, 401
    finally:
        db.close()


def register(username: str, email: str, password: str) -> Tuple[Dict[str, Any], int]:
    if not username or not email or not password:
        return {
            'success': False,
            'message': '请填写所有必填字段'
        }, 400

    password_hash = hash_password(password)

    db = get_db_session()
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            return {
                'success': False,
                'message': '邮箱已被注册'
            }, 400

        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash
        )
        db.add(new_user)
        db.commit()

        return {
            'success': True,
            'message': '注册成功'
        }, 200
    except Exception as e:
        db.rollback()
        return {
            'success': False,
            'message': str(e)
        }, 500
    finally:
        db.close()


def get_current_user_info(user_id: int) -> Tuple[Dict[str, Any], int]:
    db = get_db_session()
    try:
        user = db.query(User).filter(User.id == user_id).first()

        if user:
            user_username = user.username or user.email.split('@')[0]
            user_display_name = user.display_name or user_username

            return {
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user_username,
                    'email': user.email,
                    'display_name': user_display_name,
                    'created_at': user.created_at.isoformat() if user.created_at else None
                }
            }, 200
        else:
            return {
                'success': False,
                'message': '用户不存在'
            }, 404
    finally:
        db.close()
