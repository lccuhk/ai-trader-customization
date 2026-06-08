from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from sqlalchemy import and_, or_, desc, func

from database import get_db
from models import User, UserFollow, DirectMessage, Mention, Signal, Notification
from websocket import push_service
from middleware.error_handler import success_response, error_response


def follow_user(follower_id: int, following_id: int) -> Dict[str, Any]:
    if follower_id == following_id:
        return error_response('不能关注自己', 400)

    db = next(get_db())
    try:
        user = db.query(User).filter(User.id == following_id).first()
        if not user:
            return error_response('用户不存在', 404)

        existing = db.query(UserFollow).filter(
            UserFollow.follower_id == follower_id,
            UserFollow.following_id == following_id
        ).first()

        if existing:
            return error_response('已经关注该用户', 400)

        follow = UserFollow(
            follower_id=follower_id,
            following_id=following_id
        )

        db.add(follow)

        follower = db.query(User).filter(User.id == follower_id).first()
        if follower:
            follower.following_count = (follower.following_count or 0) + 1
        if user:
            user.follower_count = (user.follower_count or 0) + 1

        db.commit()

        notification = Notification(
            user_id=following_id,
            type='new_follower',
            content=f'{follower.username if follower else "有人"} 关注了你',
            data={'follower_id': follower_id, 'follower_username': follower.username if follower else None}
        )
        db.add(notification)
        db.commit()

        try:
            push_service.push_new_notification(following_id, {
                'id': notification.id,
                'type': notification.type,
                'content': notification.content,
                'read': notification.is_read,
                'created_at': notification.created_at.isoformat() if notification.created_at else None
            })
        except Exception as e:
            print(f"[Social] Failed to push notification: {e}")

        return success_response({'message': '关注成功'})

    except Exception as e:
        db.rollback()
        return error_response(f'关注失败: {str(e)}', 500)
    finally:
        db.close()


def unfollow_user(follower_id: int, following_id: int) -> Dict[str, Any]:
    db = next(get_db())
    try:
        follow = db.query(UserFollow).filter(
            UserFollow.follower_id == follower_id,
            UserFollow.following_id == following_id
        ).first()

        if not follow:
            return error_response('未关注该用户', 400)

        db.delete(follow)

        follower = db.query(User).filter(User.id == follower_id).first()
        if follower and follower.following_count:
            follower.following_count -= 1

        following = db.query(User).filter(User.id == following_id).first()
        if following and following.follower_count:
            following.follower_count -= 1

        db.commit()

        return success_response({'message': '取消关注成功'})

    except Exception as e:
        db.rollback()
        return error_response(f'取消关注失败: {str(e)}', 500)
    finally:
        db.close()


def get_followers(user_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
    page = int(params.get('page', 1))
    per_page = int(params.get('per_page', 20))

    db = next(get_db())
    try:
        query = db.query(UserFollow).filter(UserFollow.following_id == user_id)
        total = query.count()

        follows = query.order_by(desc(UserFollow.created_at)).offset((page - 1) * per_page).limit(per_page).all()

        follower_ids = [f.follower_id for f in follows]
        users = db.query(User).filter(User.id.in_(follower_ids)).all()
        user_map = {u.id: u for u in users}

        result = []
        for f in follows:
            user = user_map.get(f.follower_id)
            if user:
                result.append({
                    'id': user.id,
                    'username': user.username,
                    'display_name': user.display_name,
                    'avatar_url': user.avatar_url,
                    'bio': user.bio,
                    'follower_count': user.follower_count or 0,
                    'following_count': user.following_count or 0,
                    'followed_at': f.created_at.isoformat() if f.created_at else None
                })

        return success_response({
            'items': result,
            'total': total,
            'page': page,
            'per_page': per_page
        })

    except Exception as e:
        return error_response(f'获取粉丝列表失败: {str(e)}', 500)
    finally:
        db.close()


def get_following(user_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
    page = int(params.get('page', 1))
    per_page = int(params.get('per_page', 20))

    db = next(get_db())
    try:
        query = db.query(UserFollow).filter(UserFollow.follower_id == user_id)
        total = query.count()

        follows = query.order_by(desc(UserFollow.created_at)).offset((page - 1) * per_page).limit(per_page).all()

        following_ids = [f.following_id for f in follows]
        users = db.query(User).filter(User.id.in_(following_ids)).all()
        user_map = {u.id: u for u in users}

        result = []
        for f in follows:
            user = user_map.get(f.following_id)
            if user:
                result.append({
                    'id': user.id,
                    'username': user.username,
                    'display_name': user.display_name,
                    'avatar_url': user.avatar_url,
                    'bio': user.bio,
                    'follower_count': user.follower_count or 0,
                    'following_count': user.following_count or 0,
                    'followed_at': f.created_at.isoformat() if f.created_at else None
                })

        return success_response({
            'items': result,
            'total': total,
            'page': page,
            'per_page': per_page
        })

    except Exception as e:
        return error_response(f'获取关注列表失败: {str(e)}', 500)
    finally:
        db.close()


def get_user_profile(user_id: int, current_user_id: Optional[int] = None) -> Dict[str, Any]:
    db = next(get_db())
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return error_response('用户不存在', 404)

        signals = db.query(Signal).filter(
            Signal.user_id == user_id,
            Signal.is_public == True
        ).order_by(desc(Signal.created_at)).limit(20).all()

        is_following = False
        if current_user_id and current_user_id != user_id:
            is_following = db.query(UserFollow).filter(
                UserFollow.follower_id == current_user_id,
                UserFollow.following_id == user_id
            ).first() is not None

        from models import Trade
        total_trades = db.query(func.count(Trade.id)).filter(
            Trade.user_id == user_id,
            Trade.is_simulation == True
        ).scalar() or 0

        winning_trades = db.query(func.count(Trade.id)).filter(
            Trade.user_id == user_id,
            Trade.is_simulation == True,
            Trade.pnl > 0
        ).scalar() or 0

        total_pnl = db.query(func.sum(Trade.pnl)).filter(
            Trade.user_id == user_id,
            Trade.is_simulation == True
        ).scalar() or 0

        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

        return success_response({
            'user': {
                'id': user.id,
                'username': user.username,
                'display_name': user.display_name,
                'avatar_url': user.avatar_url,
                'bio': user.bio,
                'location': user.location,
                'website': user.website,
                'follower_count': user.follower_count or 0,
                'following_count': user.following_count or 0,
                'signal_count': len(signals),
                'total_trades': total_trades,
                'win_rate': round(win_rate, 2),
                'total_pnl': total_pnl,
                'created_at': user.created_at.isoformat() if user.created_at else None
            },
            'signals': [{
                'id': s.id,
                'title': s.title,
                'symbols': s.symbols,
                'direction': s.direction,
                'status': s.status,
                'pnl': s.pnl,
                'pnl_percent': s.pnl_percent,
                'created_at': s.created_at.isoformat() if s.created_at else None
            } for s in signals],
            'is_following': is_following
        })

    except Exception as e:
        return error_response(f'获取用户资料失败: {str(e)}', 500)
    finally:
        db.close()


def send_direct_message(sender_id: int, receiver_id: int, content: str) -> Dict[str, Any]:
    if not content or not content.strip():
        return error_response('消息内容不能为空', 400)

    if sender_id == receiver_id:
        return error_response('不能给自己发消息', 400)

    db = next(get_db())
    try:
        receiver = db.query(User).filter(User.id == receiver_id).first()
        if not receiver:
            return error_response('接收用户不存在', 404)

        message = DirectMessage(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content.strip()
        )

        db.add(message)
        db.commit()
        db.refresh(message)

        sender = db.query(User).filter(User.id == sender_id).first()

        message_dict = {
            'id': message.id,
            'sender_id': sender_id,
            'receiver_id': receiver_id,
            'content': message.content,
            'is_read': message.is_read,
            'sender': {
                'id': sender.id,
                'username': sender.username,
                'display_name': sender.display_name,
                'avatar_url': sender.avatar_url
            } if sender else None,
            'created_at': message.created_at.isoformat() if message.created_at else None
        }

        try:
            push_service.push_direct_message(receiver_id, message_dict)
        except Exception as e:
            print(f"[Social] Failed to push direct message: {e}")

        notification = Notification(
            user_id=receiver_id,
            type='new_message',
            content=f'{sender.username if sender else "有人"} 给你发了一条消息',
            data={'sender_id': sender_id, 'message_id': message.id}
        )
        db.add(notification)
        db.commit()

        try:
            push_service.push_new_notification(receiver_id, {
                'id': notification.id,
                'type': notification.type,
                'content': notification.content,
                'read': notification.is_read,
                'created_at': notification.created_at.isoformat() if notification.created_at else None
            })
        except Exception as e:
            print(f"[Social] Failed to push notification: {e}")

        return success_response(message_dict)

    except Exception as e:
        db.rollback()
        return error_response(f'发送消息失败: {str(e)}', 500)
    finally:
        db.close()


def get_direct_messages(user_id: int, other_user_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
    page = int(params.get('page', 1))
    per_page = int(params.get('per_page', 50))

    db = next(get_db())
    try:
        query = db.query(DirectMessage).filter(
            or_(
                and_(DirectMessage.sender_id == user_id, DirectMessage.receiver_id == other_user_id),
                and_(DirectMessage.sender_id == other_user_id, DirectMessage.receiver_id == user_id)
            )
        )

        total = query.count()
        messages = query.order_by(desc(DirectMessage.created_at)).offset((page - 1) * per_page).limit(per_page).all()

        sender_ids = list(set([m.sender_id for m in messages] + [m.receiver_id for m in messages]))
        users = db.query(User).filter(User.id.in_(sender_ids)).all()
        user_map = {u.id: u for u in users}

        result = []
        for m in reversed(messages):
            sender = user_map.get(m.sender_id)
            result.append({
                'id': m.id,
                'sender_id': m.sender_id,
                'receiver_id': m.receiver_id,
                'content': m.content,
                'is_read': m.is_read,
                'sender': {
                    'id': sender.id,
                    'username': sender.username,
                    'display_name': sender.display_name,
                    'avatar_url': sender.avatar_url
                } if sender else None,
                'created_at': m.created_at.isoformat() if m.created_at else None
            })

        db.query(DirectMessage).filter(
            DirectMessage.sender_id == other_user_id,
            DirectMessage.receiver_id == user_id,
            DirectMessage.is_read == False
        ).update({'is_read': True})
        db.commit()

        return success_response({
            'items': result,
            'total': total,
            'page': page,
            'per_page': per_page
        })

    except Exception as e:
        db.rollback()
        return error_response(f'获取消息列表失败: {str(e)}', 500)
    finally:
        db.close()


def get_conversations(user_id: int) -> Dict[str, Any]:
    db = next(get_db())
    try:
        subquery = db.query(
            func.max(DirectMessage.created_at).label('last_message_time'),
            func.least(DirectMessage.sender_id, DirectMessage.receiver_id).label('user1'),
            func.greatest(DirectMessage.sender_id, DirectMessage.receiver_id).label('user2')
        ).filter(
            or_(DirectMessage.sender_id == user_id, DirectMessage.receiver_id == user_id)
        ).group_by('user1', 'user2').subquery()

        query = db.query(DirectMessage).join(
            subquery,
            and_(
                DirectMessage.created_at == subquery.c.last_message_time,
                func.least(DirectMessage.sender_id, DirectMessage.receiver_id) == subquery.c.user1,
                func.greatest(DirectMessage.sender_id, DirectMessage.receiver_id) == subquery.c.user2
            )
        ).filter(
            or_(DirectMessage.sender_id == user_id, DirectMessage.receiver_id == user_id)
        ).order_by(desc(DirectMessage.created_at))

        messages = query.all()

        other_user_ids = []
        for m in messages:
            other_id = m.receiver_id if m.sender_id == user_id else m.sender_id
            other_user_ids.append(other_id)

        users = db.query(User).filter(User.id.in_(other_user_ids)).all()
        user_map = {u.id: u for u in users}

        unread_counts = db.query(
            DirectMessage.sender_id,
            func.count(DirectMessage.id).label('count')
        ).filter(
            DirectMessage.receiver_id == user_id,
            DirectMessage.is_read == False
        ).group_by(DirectMessage.sender_id).all()

        unread_map = {sender_id: count for sender_id, count in unread_counts}

        result = []
        for m in messages:
            other_id = m.receiver_id if m.sender_id == user_id else m.sender_id
            other_user = user_map.get(other_id)
            if other_user:
                result.append({
                    'user': {
                        'id': other_user.id,
                        'username': other_user.username,
                        'display_name': other_user.display_name,
                        'avatar_url': other_user.avatar_url
                    },
                    'last_message': {
                        'id': m.id,
                        'content': m.content,
                        'is_read': m.is_read,
                        'is_sent': m.sender_id == user_id,
                        'created_at': m.created_at.isoformat() if m.created_at else None
                    },
                    'unread_count': unread_map.get(other_id, 0)
                })

        return success_response(result)

    except Exception as e:
        return error_response(f'获取会话列表失败: {str(e)}', 500)
    finally:
        db.close()


def create_mention(mentioning_user_id: int, mentioned_user_id: int, signal_id: Optional[int] = None, reply_id: Optional[int] = None) -> Dict[str, Any]:
    db = next(get_db())
    try:
        mentioned_user = db.query(User).filter(User.id == mentioned_user_id).first()
        if not mentioned_user:
            return error_response('被提及用户不存在', 404)

        mention = Mention(
            mentioned_user_id=mentioned_user_id,
            mentioning_user_id=mentioning_user_id,
            signal_id=signal_id,
            reply_id=reply_id
        )

        db.add(mention)
        db.commit()
        db.refresh(mention)

        mentioning_user = db.query(User).filter(User.id == mentioning_user_id).first()

        notification = Notification(
            user_id=mentioned_user_id,
            type='mention',
            content=f'{mentioning_user.username if mentioning_user else "有人"} 在帖子中@了你',
            data={'signal_id': signal_id, 'reply_id': reply_id}
        )
        db.add(notification)
        db.commit()

        try:
            push_service.push_mention(mentioned_user_id, {
                'id': mention.id,
                'mentioned_by': mentioning_user_id,
                'signal_id': signal_id,
                'reply_id': reply_id,
                'created_at': mention.created_at.isoformat() if mention.created_at else None
            })

            push_service.push_new_notification(mentioned_user_id, {
                'id': notification.id,
                'type': notification.type,
                'content': notification.content,
                'read': notification.is_read,
                'created_at': notification.created_at.isoformat() if notification.created_at else None
            })
        except Exception as e:
            print(f"[Social] Failed to push mention: {e}")

        return success_response({'message': '提及成功'})

    except Exception as e:
        db.rollback()
        return error_response(f'创建提及失败: {str(e)}', 500)
    finally:
        db.close()


def get_mentions(user_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
    page = int(params.get('page', 1))
    per_page = int(params.get('per_page', 20))

    db = next(get_db())
    try:
        query = db.query(Mention).filter(Mention.mentioned_user_id == user_id)
        total = query.count()

        mentions = query.order_by(desc(Mention.created_at)).offset((page - 1) * per_page).limit(per_page).all()

        mentioning_user_ids = [m.mentioning_user_id for m in mentions]
        users = db.query(User).filter(User.id.in_(mentioning_user_ids)).all()
        user_map = {u.id: u for u in users}

        result = []
        for m in mentions:
            user = user_map.get(m.mentioning_user_id)
            result.append({
                'id': m.id,
                'mentioning_user': {
                    'id': user.id,
                    'username': user.username,
                    'display_name': user.display_name,
                    'avatar_url': user.avatar_url
                } if user else None,
                'signal_id': m.signal_id,
                'reply_id': m.reply_id,
                'is_read': m.is_read,
                'created_at': m.created_at.isoformat() if m.created_at else None
            })

        return success_response({
            'items': result,
            'total': total,
            'page': page,
            'per_page': per_page
        })

    except Exception as e:
        return error_response(f'获取提及列表失败: {str(e)}', 500)
    finally:
        db.close()


def share_signal(user_id: int, signal_id: int, platform: str) -> Dict[str, Any]:
    db = next(get_db())
    try:
        signal = db.query(Signal).filter(
            Signal.id == signal_id,
            Signal.is_public == True
        ).first()

        if not signal:
            return error_response('信号不存在或未公开', 404)

        author = db.query(User).filter(User.id == signal.user_id).first()

        share_url = f'/signals/{signal_id}'
        share_title = signal.title
        share_content = f'{author.display_name if author else "匿名用户"} 发布了交易信号: {signal.title}'

        return success_response({
            'url': share_url,
            'title': share_title,
            'content': share_content,
            'platform': platform
        })

    except Exception as e:
        return error_response(f'分享失败: {str(e)}', 500)
    finally:
        db.close()


def search_users(query: str, params: Dict[str, Any]) -> Dict[str, Any]:
    page = int(params.get('page', 1))
    per_page = int(params.get('per_page', 20))

    db = next(get_db())
    try:
        search_query = db.query(User).filter(
            or_(
                User.username.ilike(f'%{query}%'),
                User.display_name.ilike(f'%{query}%')
            )
        )

        total = search_query.count()
        users = search_query.order_by(desc(User.follower_count)).offset((page - 1) * per_page).limit(per_page).all()

        return success_response({
            'items': [{
                'id': u.id,
                'username': u.username,
                'display_name': u.display_name,
                'avatar_url': u.avatar_url,
                'bio': u.bio,
                'follower_count': u.follower_count or 0,
                'following_count': u.following_count or 0
            } for u in users],
            'total': total,
            'page': page,
            'per_page': per_page
        })

    except Exception as e:
        return error_response(f'搜索用户失败: {str(e)}', 500)
    finally:
        db.close()
