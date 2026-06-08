"""
Notification Service

Business logic for notifications and notification settings.
"""

from typing import Tuple, Dict, Any, Optional
from datetime import datetime
from sqlalchemy import and_, text

from database import get_db_session
from models import Notification
from utils.helpers import models_to_dict_list, model_to_dict
import websocket


def get_notifications(user_id: int, limit: int = 20) -> Tuple[Dict[str, Any], int]:
    db = get_db_session()
    try:
        notifications = db.query(Notification).filter(
            Notification.user_id == user_id
        ).order_by(text('created_at DESC')).limit(limit).all()
        
        return {
            'success': True,
            'notifications': models_to_dict_list(notifications)
        }, 200
    finally:
        db.close()


def mark_notification_read(notification_id: int, user_id: int) -> Tuple[Dict[str, Any], int]:
    db = get_db_session()
    try:
        notification = db.query(Notification).filter(
            and_(
                Notification.id == notification_id,
                Notification.user_id == user_id
            )
        ).first()
        
        if notification:
            notification.is_read = True
            db.commit()
            return {
                'success': True,
                'message': '通知已标记为已读'
            }, 200
        else:
            return {
                'success': False,
                'message': '通知不存在'
            }, 404
    except Exception as e:
        db.rollback()
        return {
            'success': False,
            'message': str(e)
        }, 500
    finally:
        db.close()


def mark_all_read(user_id: int) -> Tuple[Dict[str, Any], int]:
    db = get_db_session()
    try:
        db.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        ).update({Notification.is_read: True})
        db.commit()
        
        return {
            'success': True,
            'message': '所有通知已标记为已读'
        }, 200
    except Exception as e:
        db.rollback()
        return {
            'success': False,
            'message': str(e)
        }, 500
    finally:
        db.close()


def create_notification(
    user_id: int,
    title: str,
    message: str,
    notification_type: str = 'system',
    priority: str = 'normal',
    related_url: Optional[str] = None
) -> Tuple[Dict[str, Any], int]:
    db = get_db_session()
    try:
        new_notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            is_read=False,
            related_url=related_url
        )
        db.add(new_notification)
        db.commit()
        db.refresh(new_notification)
        
        notification_dict = model_to_dict(new_notification)
        
        try:
            websocket.push_service.push_new_notification(user_id, notification_dict)
        except Exception as e:
            print(f"[WS] Failed to push notification: {e}")
        
        return {
            'success': True,
            'message': '通知创建成功',
            'notification': notification_dict
        }, 201
    except Exception as e:
        db.rollback()
        return {
            'success': False,
            'message': str(e)
        }, 500
    finally:
        db.close()


def notify_new_comment(signal_author_id: int, comment_author_name: str, signal_title: str) -> None:
    create_notification(
        user_id=signal_author_id,
        title='新评论',
        message=f'{comment_author_name} 评论了你的信号: {signal_title}',
        notification_type='comment',
        priority='normal'
    )


def notify_new_like(signal_author_id: int, liker_name: str, signal_title: str) -> None:
    create_notification(
        user_id=signal_author_id,
        title='新点赞',
        message=f'{liker_name} 点赞了你的信号: {signal_title}',
        notification_type='like',
        priority='low'
    )


def notify_new_follow(followed_user_id: int, follower_name: str) -> None:
    create_notification(
        user_id=followed_user_id,
        title='新关注',
        message=f'{follower_name} 关注了你的信号',
        notification_type='follow',
        priority='low'
    )


def notify_price_alert(user_id: int, symbol: str, condition: str, current_price: float) -> None:
    create_notification(
        user_id=user_id,
        title='价格提醒',
        message=f'{symbol} {condition}，当前价格: {current_price}',
        notification_type='price_alert',
        priority='high'
    )


def notify_signal_update(user_id: int, signal_title: str, update_type: str) -> None:
    create_notification(
        user_id=user_id,
        title='信号更新',
        message=f'你关注的信号 "{signal_title}" 有新的{update_type}',
        notification_type='signal',
        priority='normal'
    )
