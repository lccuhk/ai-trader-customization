"""
User System Routes

用户系统 API 路由
"""

import sqlite3
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

from database import _SQLITE_DB_PATH


class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    display_name: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    email: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


class UserPreferences(BaseModel):
    theme: Optional[str] = None
    language: Optional[str] = None
    notifications_enabled: Optional[bool] = None
    risk_alerts_enabled: Optional[bool] = None


def _hash_password(password: str) -> str:
    """简单的密码哈希（生产环境应使用 bcrypt 或 argon2）"""
    return hashlib.sha256(password.encode()).hexdigest()


def _generate_token() -> str:
    """生成会话令牌"""
    return secrets.token_hex(32)


def _init_user_system_db():
    """初始化用户系统数据库表"""
    conn = sqlite3.connect(_SQLITE_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            display_name TEXT,
            bio TEXT,
            avatar_url TEXT,
            is_active INTEGER DEFAULT 1,
            is_admin INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            theme TEXT DEFAULT 'dark',
            language TEXT DEFAULT 'zh-CN',
            notifications_enabled INTEGER DEFAULT 1,
            risk_alerts_enabled INTEGER DEFAULT 1,
            email_notifications INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            total_trades INTEGER DEFAULT 0,
            winning_trades INTEGER DEFAULT 0,
            losing_trades INTEGER DEFAULT 0,
            total_pnl REAL DEFAULT 0,
            win_rate REAL DEFAULT 0,
            sharpe_ratio REAL DEFAULT 0,
            max_drawdown REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        sample_users = [
            ('demo_user', 'demo@example.com', _hash_password('demo123'), '演示用户', '这是一个演示账户', None),
            ('trader_pro', 'pro@example.com', _hash_password('pro123'), '专业交易者', '10年交易经验', None),
            ('quant_king', 'quant@example.com', _hash_password('quant123'), '量化之王', '专注量化策略', None),
        ]
        cursor.executemany('''
            INSERT INTO users (username, email, password_hash, display_name, bio, avatar_url)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', sample_users)
        
        for user_id in [1, 2, 3]:
            cursor.execute('''
                INSERT INTO user_preferences (user_id) VALUES (?)
            ''', (user_id,))
            
            if user_id == 1:
                cursor.execute('''
                    INSERT INTO user_stats (user_id, total_trades, winning_trades, losing_trades, total_pnl, win_rate, sharpe_ratio, max_drawdown)
                    VALUES (?, 156, 102, 54, 25430.50, 0.654, 1.85, 0.082)
                ''', (user_id,))
            elif user_id == 2:
                cursor.execute('''
                    INSERT INTO user_stats (user_id, total_trades, winning_trades, losing_trades, total_pnl, win_rate, sharpe_ratio, max_drawdown)
                    VALUES (?, 423, 298, 125, 89200.30, 0.704, 2.35, 0.065)
                ''', (user_id,))
            else:
                cursor.execute('''
                    INSERT INTO user_stats (user_id, total_trades, winning_trades, losing_trades, total_pnl, win_rate, sharpe_ratio, max_drawdown)
                    VALUES (?, 89, 62, 27, 15680.00, 0.697, 2.10, 0.058)
                ''', (user_id,))
    
    conn.commit()
    conn.close()


def init_user_system_routes(app: FastAPI):
    """注册用户系统路由"""
    _init_user_system_db()
    
    @app.post('/api/auth/register')
    async def register_user(user: UserRegister):
        """用户注册"""
        conn = sqlite3.connect(_SQLITE_DB_PATH)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT id FROM users WHERE username = ?', (user.username,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail='Username already exists')
            
            cursor.execute('SELECT id FROM users WHERE email = ?', (user.email,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail='Email already exists')
            
            password_hash = _hash_password(user.password)
            
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, display_name)
                VALUES (?, ?, ?, ?)
            ''', (user.username, user.email, password_hash, user.display_name or user.username))
            
            user_id = cursor.lastrowid
            
            cursor.execute('INSERT INTO user_preferences (user_id) VALUES (?)', (user_id,))
            cursor.execute('INSERT INTO user_stats (user_id) VALUES (?)', (user_id,))
            
            conn.commit()
            
            return {
                'success': True,
                'user_id': user_id,
                'message': 'Registration successful'
            }
        finally:
            conn.close()
    
    @app.post('/api/auth/login')
    async def login_user(user: UserLogin):
        """用户登录"""
        conn = sqlite3.connect(_SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, username, email, password_hash, display_name, is_active 
                FROM users WHERE username = ?
            ''', (user.username,))
            
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=401, detail='Invalid credentials')
            
            if not row['is_active']:
                raise HTTPException(status_code=403, detail='Account disabled')
            
            password_hash = _hash_password(user.password)
            if password_hash != row['password_hash']:
                raise HTTPException(status_code=401, detail='Invalid credentials')
            
            token = _generate_token()
            expires_at = (datetime.now() + timedelta(days=7)).isoformat()
            
            cursor.execute('''
                INSERT INTO user_sessions (user_id, token, expires_at)
                VALUES (?, ?, ?)
            ''', (row['id'], token, expires_at))
            
            cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (row['id'],))
            conn.commit()
            
            return {
                'success': True,
                'token': token,
                'user': {
                    'id': row['id'],
                    'username': row['username'],
                    'email': row['email'],
                    'display_name': row['display_name']
                }
            }
        finally:
            conn.close()
    
    @app.post('/api/auth/logout')
    async def logout_user(request: Request):
        """用户登出"""
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return {'success': True, 'message': 'No active session'}
        
        token = auth_header.split(' ')[1]
        
        conn = sqlite3.connect(_SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM user_sessions WHERE token = ?', (token,))
        conn.commit()
        conn.close()
        
        return {'success': True, 'message': 'Logged out successfully'}
    
    @app.get('/api/users/me')
    async def get_current_user(request: Request):
        """获取当前用户信息"""
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise HTTPException(status_code=401, detail='Not authenticated')
        
        token = auth_header.split(' ')[1]
        
        conn = sqlite3.connect(_SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT u.* FROM users u
                JOIN user_sessions s ON u.id = s.user_id
                WHERE s.token = ? AND s.expires_at > CURRENT_TIMESTAMP
            ''', (token,))
            
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=401, detail='Invalid or expired token')
            
            return {
                'success': True,
                'user': {
                    'id': row['id'],
                    'username': row['username'],
                    'email': row['email'],
                    'display_name': row['display_name'],
                    'bio': row['bio'],
                    'avatar_url': row['avatar_url'],
                    'is_admin': bool(row['is_admin']),
                    'created_at': row['created_at'],
                    'last_login': row['last_login']
                }
            }
        finally:
            conn.close()
    
    @app.put('/api/users/me')
    async def update_current_user(request: Request, user_update: UserUpdate):
        """更新当前用户信息"""
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise HTTPException(status_code=401, detail='Not authenticated')
        
        token = auth_header.split(' ')[1]
        
        conn = sqlite3.connect(_SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT user_id FROM user_sessions 
                WHERE token = ? AND expires_at > CURRENT_TIMESTAMP
            ''', (token,))
            
            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=401, detail='Invalid or expired token')
            
            user_id = row['user_id']
            
            updates = []
            params = []
            
            if user_update.display_name is not None:
                updates.append('display_name = ?')
                params.append(user_update.display_name)
            if user_update.email is not None:
                updates.append('email = ?')
                params.append(user_update.email)
            if user_update.bio is not None:
                updates.append('bio = ?')
                params.append(user_update.bio)
            if user_update.avatar_url is not None:
                updates.append('avatar_url = ?')
                params.append(user_update.avatar_url)
            
            if updates:
                params.append(user_id)
                cursor.execute(f'UPDATE users SET {", ".join(updates)} WHERE id = ?', params)
                conn.commit()
            
            return {'success': True, 'message': 'Profile updated successfully'}
        finally:
            conn.close()
    
    @app.get('/api/users/me/preferences')
    async def get_user_preferences(request: Request):
        """获取用户偏好设置"""
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise HTTPException(status_code=401, detail='Not authenticated')
        
        token = auth_header.split(' ')[1]
        
        conn = sqlite3.connect(_SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT p.* FROM user_preferences p
                JOIN user_sessions s ON p.user_id = s.user_id
                WHERE s.token = ? AND s.expires_at > CURRENT_TIMESTAMP
            ''', (token,))
            
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail='Preferences not found')
            
            return {
                'success': True,
                'preferences': {
                    'theme': row['theme'],
                    'language': row['language'],
                    'notifications_enabled': bool(row['notifications_enabled']),
                    'risk_alerts_enabled': bool(row['risk_alerts_enabled']),
                    'email_notifications': bool(row['email_notifications'])
                }
            }
        finally:
            conn.close()
    
    @app.put('/api/users/me/preferences')
    async def update_user_preferences(request: Request, prefs: UserPreferences):
        """更新用户偏好设置"""
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise HTTPException(status_code=401, detail='Not authenticated')
        
        token = auth_header.split(' ')[1]
        
        conn = sqlite3.connect(_SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT user_id FROM user_sessions 
                WHERE token = ? AND expires_at > CURRENT_TIMESTAMP
            ''', (token,))
            
            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=401, detail='Invalid or expired token')
            
            user_id = row['user_id']
            
            updates = []
            params = []
            
            if prefs.theme is not None:
                updates.append('theme = ?')
                params.append(prefs.theme)
            if prefs.language is not None:
                updates.append('language = ?')
                params.append(prefs.language)
            if prefs.notifications_enabled is not None:
                updates.append('notifications_enabled = ?')
                params.append(1 if prefs.notifications_enabled else 0)
            if prefs.risk_alerts_enabled is not None:
                updates.append('risk_alerts_enabled = ?')
                params.append(1 if prefs.risk_alerts_enabled else 0)
            
            if updates:
                updates.append('updated_at = CURRENT_TIMESTAMP')
                params.append(user_id)
                cursor.execute(f'UPDATE user_preferences SET {", ".join(updates)} WHERE user_id = ?', params)
                conn.commit()
            
            return {'success': True, 'message': 'Preferences updated successfully'}
        finally:
            conn.close()
    
    @app.get('/api/users/me/stats')
    async def get_user_stats(request: Request):
        """获取用户统计数据"""
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise HTTPException(status_code=401, detail='Not authenticated')
        
        token = auth_header.split(' ')[1]
        
        conn = sqlite3.connect(_SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT st.* FROM user_stats st
                JOIN user_sessions s ON st.user_id = s.user_id
                WHERE s.token = ? AND s.expires_at > CURRENT_TIMESTAMP
            ''', (token,))
            
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail='Stats not found')
            
            return {
                'success': True,
                'stats': {
                    'total_trades': row['total_trades'],
                    'winning_trades': row['winning_trades'],
                    'losing_trades': row['losing_trades'],
                    'total_pnl': row['total_pnl'],
                    'win_rate': row['win_rate'],
                    'sharpe_ratio': row['sharpe_ratio'],
                    'max_drawdown': row['max_drawdown']
                }
            }
        finally:
            conn.close()
    
    @app.get('/api/users/{user_id}/profile')
    async def get_user_profile(user_id: int):
        """获取用户公开资料"""
        conn = sqlite3.connect(_SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT u.id, u.username, u.display_name, u.bio, u.avatar_url, u.created_at,
                       st.total_trades, st.winning_trades, st.total_pnl, st.win_rate, st.sharpe_ratio
                FROM users u
                LEFT JOIN user_stats st ON u.id = st.user_id
                WHERE u.id = ? AND u.is_active = 1
            ''', (user_id,))
            
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail='User not found')
            
            return {
                'success': True,
                'profile': {
                    'id': row['id'],
                    'username': row['username'],
                    'display_name': row['display_name'],
                    'bio': row['bio'],
                    'avatar_url': row['avatar_url'],
                    'created_at': row['created_at'],
                    'stats': {
                        'total_trades': row['total_trades'] or 0,
                        'winning_trades': row['winning_trades'] or 0,
                        'total_pnl': row['total_pnl'] or 0,
                        'win_rate': row['win_rate'] or 0,
                        'sharpe_ratio': row['sharpe_ratio'] or 0
                    }
                }
            }
        finally:
            conn.close()
