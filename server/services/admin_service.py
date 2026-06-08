from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from sqlalchemy import func, desc, and_

from database import get_db
from models import User, Signal, Trade, Order, AdminAction, Notification
from middleware.error_handler import success_response, error_response


def _is_admin(user_id: int, db) -> bool:
    user = db.query(User).filter(User.id == user_id).first()
    return user and user.role == 'admin'


def get_users(admin_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
    db = next(get_db())
    try:
        if not _is_admin(admin_id, db):
            return error_response('权限不足', 403)

        search = params.get('search')
        role = params.get('role')
        is_verified = params.get('is_verified')
        is_active = params.get('is_active')
        page = int(params.get('page', 1))
        per_page = int(params.get('per_page', 20))

        query = db.query(User)

        if search:
            query = query.filter(
                (User.username.ilike(f'%{search}%')) |
                (User.email.ilike(f'%{search}%')) |
                (User.display_name.ilike(f'%{search}%'))
            )
        if role:
            query = query.filter(User.role == role)
        if is_verified is not None:
            query = query.filter(User.is_verified == is_verified)
        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        total = query.count()
        users = query.order_by(desc(User.created_at)).offset((page - 1) * per_page).limit(per_page).all()

        return success_response({
            'items': [{
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'display_name': u.display_name,
                'avatar_url': u.avatar_url,
                'role': u.role,
                'is_verified': u.is_verified,
                'is_active': u.is_active,
                'follower_count': u.follower_count or 0,
                'following_count': u.following_count or 0,
                'created_at': u.created_at.isoformat() if u.created_at else None,
                'last_login_at': u.last_login_at.isoformat() if u.last_login_at else None
            } for u in users],
            'total': total,
            'page': page,
            'per_page': per_page
        })

    except Exception as e:
        return error_response(f'获取用户列表失败: {str(e)}', 500)
    finally:
        db.close()


def update_user_status(admin_id: int, user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    db = next(get_db())
    try:
        if not _is_admin(admin_id, db):
            return error_response('权限不足', 403)

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return error_response('用户不存在', 404)

        old_values = {
            'is_active': user.is_active,
            'role': user.role,
            'is_verified': user.is_verified
        }

        if 'is_active' in data:
            user.is_active = data['is_active']
        if 'role' in data:
            user.role = data['role']
        if 'is_verified' in data:
            user.is_verified = data['is_verified']

        new_values = {
            'is_active': user.is_active,
            'role': user.role,
            'is_verified': user.is_verified
        }

        admin_action = AdminAction(
            admin_id=admin_id,
            action='update_user_status',
            target_user_id=user_id,
            reason=data.get('reason', ''),
            details={'old_values': old_values, 'new_values': new_values}
        )
        db.add(admin_action)

        db.commit()

        return success_response({'message': '用户状态已更新'})

    except Exception as e:
        db.rollback()
        return error_response(f'更新用户状态失败: {str(e)}', 500)
    finally:
        db.close()


def get_signals(admin_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
    db = next(get_db())
    try:
        if not _is_admin(admin_id, db):
            return error_response('权限不足', 403)

        status = params.get('status')
        user_id = params.get('user_id')
        is_public = params.get('is_public')
        page = int(params.get('page', 1))
        per_page = int(params.get('per_page', 20))

        query = db.query(Signal)

        if status:
            query = query.filter(Signal.status == status)
        if user_id:
            query = query.filter(Signal.user_id == user_id)
        if is_public is not None:
            query = query.filter(Signal.is_public == is_public)

        total = query.count()
        signals = query.order_by(desc(Signal.created_at)).offset((page - 1) * per_page).limit(per_page).all()

        return success_response({
            'items': [{
                'id': s.id,
                'title': s.title,
                'content': s.content,
                'symbols': s.symbols,
                'direction': s.direction,
                'status': s.status,
                'is_public': s.is_public,
                'user_id': s.user_id,
                'pnl': s.pnl,
                'pnl_percent': s.pnl_percent,
                'like_count': s.like_count or 0,
                'reply_count': s.reply_count or 0,
                'created_at': s.created_at.isoformat() if s.created_at else None
            } for s in signals],
            'total': total,
            'page': page,
            'per_page': per_page
        })

    except Exception as e:
        return error_response(f'获取信号列表失败: {str(e)}', 500)
    finally:
        db.close()


def moderate_signal(admin_id: int, signal_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    db = next(get_db())
    try:
        if not _is_admin(admin_id, db):
            return error_response('权限不足', 403)

        signal = db.query(Signal).filter(Signal.id == signal_id).first()
        if not signal:
            return error_response('信号不存在', 404)

        action = data.get('action')
        reason = data.get('reason', '')

        if action == 'approve':
            signal.is_public = True
            signal.moderation_status = 'approved'
        elif action == 'reject':
            signal.is_public = False
            signal.moderation_status = 'rejected'
        elif action == 'remove':
            signal.is_public = False
            signal.status = 'removed'
            signal.moderation_status = 'removed'
        else:
            return error_response('无效的操作', 400)

        admin_action = AdminAction(
            admin_id=admin_id,
            action=f'moderate_signal_{action}',
            target_user_id=signal.user_id,
            reason=reason,
            details={'signal_id': signal_id, 'action': action}
        )
        db.add(admin_action)

        notification = Notification(
            user_id=signal.user_id,
            type='signal_moderation',
            content=f'你的信号已被{action}',
            data={'signal_id': signal_id, 'action': action, 'reason': reason}
        )
        db.add(notification)

        db.commit()

        return success_response({'message': f'信号已{action}'})

    except Exception as e:
        db.rollback()
        return error_response(f'审核信号失败: {str(e)}', 500)
    finally:
        db.close()


def get_admin_stats(admin_id: int) -> Dict[str, Any]:
    db = next(get_db())
    try:
        if not _is_admin(admin_id, db):
            return error_response('权限不足', 403)

        total_users = db.query(User).count()
        total_signals = db.query(Signal).count()
        total_trades = db.query(Trade).count()
        total_orders = db.query(Order).count()

        today = datetime.now(timezone.utc).date()
        today_start = datetime.combine(today, datetime.min.time(), tzinfo=timezone.utc)

        new_users_today = db.query(User).filter(User.created_at >= today_start).count()
        new_signals_today = db.query(Signal).filter(Signal.created_at >= today_start).count()
        new_trades_today = db.query(Trade).filter(Trade.created_at >= today_start).count()

        pending_moderation = db.query(Signal).filter(Signal.moderation_status == 'pending').count()

        recent_actions = db.query(AdminAction).order_by(desc(AdminAction.created_at)).limit(20).all()

        return success_response({
            'overview': {
                'total_users': total_users,
                'total_signals': total_signals,
                'total_trades': total_trades,
                'total_orders': total_orders
            },
            'today': {
                'new_users': new_users_today,
                'new_signals': new_signals_today,
                'new_trades': new_trades_today
            },
            'moderation': {
                'pending_count': pending_moderation
            },
            'recent_actions': [{
                'id': a.id,
                'action': a.action,
                'target_user_id': a.target_user_id,
                'reason': a.reason,
                'created_at': a.created_at.isoformat() if a.created_at else None
            } for a in recent_actions]
        })

    except Exception as e:
        return error_response(f'获取管理统计失败: {str(e)}', 500)
    finally:
        db.close()


def send_system_notification(admin_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    db = next(get_db())
    try:
        if not _is_admin(admin_id, db):
            return error_response('权限不足', 403)

        title = data.get('title')
        content = data.get('content')
        target_user_ids = data.get('user_ids')
        broadcast = data.get('broadcast', False)

        if not title or not content:
            return error_response('缺少标题或内容', 400)

        if broadcast:
            users = db.query(User).filter(User.is_active == True).all()
            target_user_ids = [u.id for u in users]
        elif not target_user_ids:
            return error_response('请指定目标用户或设置为广播', 400)

        notifications = []
        for user_id in target_user_ids:
            notification = Notification(
                user_id=user_id,
                type='system',
                title=title,
                content=content,
                data=data.get('data', {})
            )
            notifications.append(notification)

        db.bulk_save_objects(notifications)

        admin_action = AdminAction(
            admin_id=admin_id,
            action='send_system_notification',
            reason=title,
            details={'user_count': len(target_user_ids), 'broadcast': broadcast}
        )
        db.add(admin_action)

        db.commit()

        return success_response({'message': f'已发送{len(target_user_ids)}条通知'})

    except Exception as e:
        db.rollback()
        return error_response(f'发送系统通知失败: {str(e)}', 500)
    finally:
        db.close()


def get_admin_actions(admin_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
    db = next(get_db())
    try:
        if not _is_admin(admin_id, db):
            return error_response('权限不足', 403)

        action_type = params.get('action')
        target_user_id = params.get('target_user_id')
        page = int(params.get('page', 1))
        per_page = int(params.get('per_page', 20))

        query = db.query(AdminAction)

        if action_type:
            query = query.filter(AdminAction.action == action_type)
        if target_user_id:
            query = query.filter(AdminAction.target_user_id == target_user_id)

        total = query.count()
        actions = query.order_by(desc(AdminAction.created_at)).offset((page - 1) * per_page).limit(per_page).all()

        admin_ids = [a.admin_id for a in actions]
        admins = db.query(User).filter(User.id.in_(admin_ids)).all()
        admin_map = {u.id: u for u in admins}

        return success_response({
            'items': [{
                'id': a.id,
                'action': a.action,
                'admin': {
                    'id': admin_map.get(a.admin_id).id if admin_map.get(a.admin_id) else None,
                    'username': admin_map.get(a.admin_id).username if admin_map.get(a.admin_id) else None,
                    'display_name': admin_map.get(a.admin_id).display_name if admin_map.get(a.admin_id) else None
                },
                'target_user_id': a.target_user_id,
                'reason': a.reason,
                'details': a.details,
                'created_at': a.created_at.isoformat() if a.created_at else None
            } for a in actions],
            'total': total,
            'page': page,
            'per_page': per_page
        })

    except Exception as e:
        return error_response(f'获取管理操作日志失败: {str(e)}', 500)
    finally:
        db.close()
