"""
Notification System Routes

通知系统 API 路由
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

from database import _SQLITE_DB_PATH


class NotificationCreate(BaseModel):
    title: str
    message: str
    notification_type: str = 'general'
    priority: str = 'normal'
    data: Optional[Dict[str, Any]] = None


class WebhookCreate(BaseModel):
    name: str
    url: str
    events: List[str]
    is_active: bool = True


class EmailConfig(BaseModel):
    smtp_host: str
    smtp_port: int = 587
    smtp_user: str
    smtp_password: str
    sender_email: str
    recipient_email: str
    is_active: bool = True


def _init_notification_system_db():
    """初始化通知系统数据库表"""
    conn = sqlite3.connect(_SQLITE_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            notification_type TEXT DEFAULT 'general',
            priority TEXT DEFAULT 'normal',
            is_read INTEGER DEFAULT 0,
            data TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS webhooks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT NOT NULL,
            url TEXT NOT NULL,
            events TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS email_configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            smtp_host TEXT,
            smtp_port INTEGER,
            smtp_user TEXT,
            smtp_password TEXT,
            sender_email TEXT,
            recipient_email TEXT,
            is_active INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notification_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            price_alerts INTEGER DEFAULT 1,
            signal_updates INTEGER DEFAULT 1,
            risk_alerts INTEGER DEFAULT 1,
            system_notifications INTEGER DEFAULT 1,
            email_notifications INTEGER DEFAULT 0,
            webhook_notifications INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('SELECT COUNT(*) FROM notifications')
    if cursor.fetchone()[0] == 0:
        sample_notifications = [
            (1, 'NVDA 价格预警', 'NVDA 价格已突破 $500 阻力位', 'price_alert', 'high', json.dumps({'symbol': 'NVDA', 'price': 500.00})),
            (1, '新交易信号', '检测到 AAPL 买入信号，强度 85%', 'signal', 'normal', json.dumps({'symbol': 'AAPL', 'signal': 'buy', 'strength': 85})),
            (1, '风险预警', '您的投资组合集中度超过 30% 阈值', 'risk', 'high', json.dumps({'concentration': 0.35, 'threshold': 0.30})),
            (1, '系统更新', '系统已完成例行维护', 'system', 'low', json.dumps({})),
            (1, '策略回测完成', '移动平均线策略回测已完成，收益率 +28.5%', 'strategy', 'normal', json.dumps({'strategy': 'MA Crossover', 'return': 0.285})),
        ]
        cursor.executemany('''
            INSERT INTO notifications (user_id, title, message, notification_type, priority, data)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', sample_notifications)
    
    cursor.execute('SELECT COUNT(*) FROM notification_settings')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO notification_settings (user_id) VALUES (1)
        ''')
    
    conn.commit()
    conn.close()


def init_notification_system_routes(app: FastAPI):
    """注册通知系统路由"""
    _init_notification_system_db()
    
    @app.get('/api/notifications')
    async def get_notifications(limit: int = 20, offset: int = 0, unread_only: bool = False):
        """获取通知列表"""
        conn = sqlite3.connect(_SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = 'SELECT * FROM notifications WHERE user_id = 1'
        params = []
        
        if unread_only:
            query += ' AND is_read = 0'
        
        query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        notifications = []
        for row in rows:
            notifications.append({
                'id': row['id'],
                'title': row['title'],
                'message': row['message'],
                'notification_type': row['notification_type'],
                'priority': row['priority'],
                'is_read': bool(row['is_read']),
                'data': json.loads(row['data']) if row['data'] else {},
                'created_at': row['created_at']
            })
        
        cursor.execute('SELECT COUNT(*) as count FROM notifications WHERE user_id = 1 AND is_read = 0')
        unread_count = cursor.fetchone()['count']
        
        conn.close()
        
        return {
            'success': True,
            'notifications': notifications,
            'unread_count': unread_count
        }
    
    @app.post('/api/notifications')
    async def create_notification(notification: NotificationCreate):
        """创建新通知"""
        conn = sqlite3.connect(_SQLITE_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO notifications (user_id, title, message, notification_type, priority, data)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            1,
            notification.title,
            notification.message,
            notification.notification_type,
            notification.priority,
            json.dumps(notification.data or {})
        ))
        
        notification_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'notification_id': notification_id,
            'message': 'Notification created successfully'
        }
    
    @app.put('/api/notifications/{notification_id}/read')
    async def mark_notification_read(notification_id: int):
        """标记通知为已读"""
        conn = sqlite3.connect(_SQLITE_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE notifications SET is_read = 1 WHERE id = ? AND user_id = 1', (notification_id,))
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'message': 'Notification marked as read'
        }
    
    @app.put('/api/notifications/read-all')
    async def mark_all_notifications_read():
        """标记所有通知为已读"""
        conn = sqlite3.connect(_SQLITE_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE notifications SET is_read = 1 WHERE user_id = 1 AND is_read = 0')
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'message': 'All notifications marked as read'
        }
    
    @app.delete('/api/notifications/{notification_id}')
    async def delete_notification(notification_id: int):
        """删除通知"""
        conn = sqlite3.connect(_SQLITE_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM notifications WHERE id = ? AND user_id = 1', (notification_id,))
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'message': 'Notification deleted successfully'
        }
    
    @app.get('/api/notifications/settings')
    async def get_notification_settings():
        """获取通知设置"""
        conn = sqlite3.connect(_SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM notification_settings WHERE user_id = 1')
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail='Settings not found')
        
        return {
            'success': True,
            'settings': {
                'price_alerts': bool(row['price_alerts']),
                'signal_updates': bool(row['signal_updates']),
                'risk_alerts': bool(row['risk_alerts']),
                'system_notifications': bool(row['system_notifications']),
                'email_notifications': bool(row['email_notifications']),
                'webhook_notifications': bool(row['webhook_notifications'])
            }
        }
    
    @app.put('/api/notifications/settings')
    async def update_notification_settings(settings: dict):
        """更新通知设置"""
        conn = sqlite3.connect(_SQLITE_DB_PATH)
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if 'price_alerts' in settings:
            updates.append('price_alerts = ?')
            params.append(1 if settings['price_alerts'] else 0)
        if 'signal_updates' in settings:
            updates.append('signal_updates = ?')
            params.append(1 if settings['signal_updates'] else 0)
        if 'risk_alerts' in settings:
            updates.append('risk_alerts = ?')
            params.append(1 if settings['risk_alerts'] else 0)
        if 'system_notifications' in settings:
            updates.append('system_notifications = ?')
            params.append(1 if settings['system_notifications'] else 0)
        if 'email_notifications' in settings:
            updates.append('email_notifications = ?')
            params.append(1 if settings['email_notifications'] else 0)
        if 'webhook_notifications' in settings:
            updates.append('webhook_notifications = ?')
            params.append(1 if settings['webhook_notifications'] else 0)
        
        if updates:
            updates.append('updated_at = CURRENT_TIMESTAMP')
            params.append(1)
            cursor.execute(f'UPDATE notification_settings SET {", ".join(updates)} WHERE user_id = ?', params)
            conn.commit()
        
        conn.close()
        
        return {
            'success': True,
            'message': 'Settings updated successfully'
        }
    
    @app.get('/api/webhooks')
    async def get_webhooks():
        """获取 Webhook 列表"""
        conn = sqlite3.connect(_SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM webhooks WHERE user_id = 1 ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        
        webhooks = []
        for row in rows:
            webhooks.append({
                'id': row['id'],
                'name': row['name'],
                'url': row['url'],
                'events': json.loads(row['events']) if row['events'] else [],
                'is_active': bool(row['is_active']),
                'created_at': row['created_at']
            })
        
        return {
            'success': True,
            'webhooks': webhooks
        }
    
    @app.post('/api/webhooks')
    async def create_webhook(webhook: WebhookCreate):
        """创建 Webhook"""
        conn = sqlite3.connect(_SQLITE_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO webhooks (user_id, name, url, events, is_active)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            1,
            webhook.name,
            webhook.url,
            json.dumps(webhook.events),
            1 if webhook.is_active else 0
        ))
        
        webhook_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'webhook_id': webhook_id,
            'message': 'Webhook created successfully'
        }
    
    @app.delete('/api/webhooks/{webhook_id}')
    async def delete_webhook(webhook_id: int):
        """删除 Webhook"""
        conn = sqlite3.connect(_SQLITE_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM webhooks WHERE id = ? AND user_id = 1', (webhook_id,))
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'message': 'Webhook deleted successfully'
        }
    
    @app.get('/api/email/config')
    async def get_email_config():
        """获取邮件配置"""
        conn = sqlite3.connect(_SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM email_configs WHERE user_id = 1')
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return {
                'success': True,
                'config': None
            }
        
        return {
            'success': True,
            'config': {
                'smtp_host': row['smtp_host'],
                'smtp_port': row['smtp_port'],
                'smtp_user': row['smtp_user'],
                'sender_email': row['sender_email'],
                'recipient_email': row['recipient_email'],
                'is_active': bool(row['is_active'])
            }
        }
    
    @app.post('/api/email/config')
    async def save_email_config(config: EmailConfig):
        """保存邮件配置"""
        conn = sqlite3.connect(_SQLITE_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM email_configs WHERE user_id = 1')
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute('''
                UPDATE email_configs 
                SET smtp_host = ?, smtp_port = ?, smtp_user = ?, smtp_password = ?, 
                    sender_email = ?, recipient_email = ?, is_active = ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = 1
            ''', (
                config.smtp_host,
                config.smtp_port,
                config.smtp_user,
                config.smtp_password,
                config.sender_email,
                config.recipient_email,
                1 if config.is_active else 0
            ))
        else:
            cursor.execute('''
                INSERT INTO email_configs 
                (user_id, smtp_host, smtp_port, smtp_user, smtp_password, sender_email, recipient_email, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                1,
                config.smtp_host,
                config.smtp_port,
                config.smtp_user,
                config.smtp_password,
                config.sender_email,
                config.recipient_email,
                1 if config.is_active else 0
            ))
        
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'message': 'Email config saved successfully'
        }
    
    @app.post('/api/email/test')
    async def test_email():
        """测试邮件发送"""
        return {
            'success': True,
            'message': 'Test email would be sent (simulated)'
        }
