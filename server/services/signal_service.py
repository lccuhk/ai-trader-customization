"""
Signal Service

Business logic for trading signals, comments, and participants.
"""

import random
import json
from typing import Optional, Tuple, Dict, Any, List
from datetime import datetime

from sqlalchemy import text, and_

from database import get_db_session
from models import (
    Signal, SignalReply, SignalParticipant, SignalQualityScore,
    User
)
from utils.helpers import model_to_dict, models_to_dict_list
import websocket


def get_signals(limit: int = 20, message_type: str = '', market: str = '') -> Tuple[Dict[str, Any], int]:
    db = get_db_session()
    try:
        query = db.query(Signal)
        if message_type:
            query = query.filter(Signal.message_type == message_type)
        if market:
            query = query.filter(Signal.market == market)
        
        signals = query.order_by(text('created_at DESC')).limit(limit).all()
        
        result = []
        for signal in signals:
            signal_dict = model_to_dict(signal)
            signal_dict['symbols'] = signal.symbols if signal.symbols else []
            result.append(signal_dict)
        
        return {
            'success': True,
            'signals': result
        }, 200
    finally:
        db.close()


def get_signal_detail(signal_id: int) -> Tuple[Dict[str, Any], int]:
    db = get_db_session()
    try:
        signal = db.query(Signal).filter(Signal.id == signal_id).first()
        if signal:
            signal_dict = model_to_dict(signal)
            signal_dict['symbols'] = signal.symbols if signal.symbols else []
            return {
                'success': True,
                'signal': signal_dict
            }, 200
        else:
            return {
                'success': False,
                'message': '信号不存在'
            }, 404
    finally:
        db.close()


def get_signal_replies(signal_id: int) -> Tuple[Dict[str, Any], int]:
    db = get_db_session()
    try:
        replies = db.query(SignalReply).filter(
            SignalReply.signal_id == signal_id
        ).order_by(text('created_at DESC')).all()
        
        return {
            'success': True,
            'replies': models_to_dict_list(replies)
        }, 200
    finally:
        db.close()


def get_signal_participants(signal_id: int) -> Tuple[Dict[str, Any], int]:
    db = get_db_session()
    try:
        participants = db.query(SignalParticipant).filter(
            SignalParticipant.signal_id == signal_id
        ).order_by(SignalParticipant.joined_at).all()
        
        return {
            'success': True,
            'participants': models_to_dict_list(participants)
        }, 200
    finally:
        db.close()


def get_signal_quality(signal_id: int) -> Tuple[Dict[str, Any], int]:
    db = get_db_session()
    try:
        quality = db.query(SignalQualityScore).filter(
            SignalQualityScore.signal_id == signal_id
        ).first()
        
        if quality:
            return {
                'success': True,
                'quality': {
                    'accuracy_score': quality.accuracy_score or 0,
                    'analysis_depth': quality.analysis_depth or 0,
                    'risk_management': quality.risk_management or 0,
                    'timeliness': quality.timeliness or 0,
                    'clarity': quality.clarity or 0,
                    'total_score': quality.total_score or 0
                }
            }, 200
        else:
            return {
                'success': False,
                'message': '评分详情不存在'
            }, 404
    finally:
        db.close()


def add_reply(signal_id: int, user_id: int, content: str, parent_id: Optional[int] = None) -> Tuple[Dict[str, Any], int]:
    if not content:
        return {
            'success': False,
            'message': '评论内容不能为空'
        }, 400
    
    db = get_db_session()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        user_name = user.username if user else '匿名用户'
        
        new_reply = SignalReply(
            signal_id=signal_id,
            user_id=user_id,
            user_name=user_name,
            content=content,
            parent_id=parent_id
        )
        db.add(new_reply)
        
        signal = db.query(Signal).filter(Signal.id == signal_id).first()
        if signal:
            signal.reply_count = (signal.reply_count or 0) + 1
        
        db.commit()
        db.refresh(new_reply)
        
        reply_dict = model_to_dict(new_reply)
        
        try:
            websocket.push_service.push_new_comment(signal_id, reply_dict)
        except Exception as e:
            print(f"[WS] Failed to push comment: {e}")
        
        return {
            'success': True,
            'message': '评论发布成功',
            'reply': reply_dict
        }, 200
    except Exception as e:
        db.rollback()
        return {
            'success': False,
            'message': str(e)
        }, 500
    finally:
        db.close()


def toggle_follow(signal_id: int, user_id: int) -> Tuple[Dict[str, Any], int]:
    db = get_db_session()
    try:
        existing = db.query(SignalParticipant).filter(
            and_(
                SignalParticipant.signal_id == signal_id,
                SignalParticipant.user_id == user_id
            )
        ).first()
        
        user = db.query(User).filter(User.id == user_id).first()
        user_name = user.username if user else '匿名用户'
        
        signal = db.query(Signal).filter(Signal.id == signal_id).first()
        
        if existing:
            db.delete(existing)
            if signal:
                signal.participant_count = (signal.participant_count or 0) - 1
            is_following = False
            message = '已取消关注'
        else:
            new_participant = SignalParticipant(
                signal_id=signal_id,
                user_id=user_id,
                user_name=user_name,
                role='follower'
            )
            db.add(new_participant)
            if signal:
                signal.participant_count = (signal.participant_count or 0) + 1
            is_following = True
            message = '关注成功'
        
        db.commit()
        
        participant_count = signal.participant_count if signal else 0
        
        try:
            websocket.push_service.push_follow_update(signal_id, is_following, participant_count)
        except Exception as e:
            print(f"[WS] Failed to push follow update: {e}")
        
        return {
            'success': True,
            'message': message,
            'is_following': is_following,
            'participant_count': participant_count
        }, 200
    except Exception as e:
        db.rollback()
        return {
            'success': False,
            'message': str(e)
        }, 500
    finally:
        db.close()


def get_follow_status(signal_id: int, user_id: int) -> Tuple[Dict[str, Any], int]:
    db = get_db_session()
    try:
        existing = db.query(SignalParticipant).filter(
            and_(
                SignalParticipant.signal_id == signal_id,
                SignalParticipant.user_id == user_id
            )
        ).first()
        
        return {
            'success': True,
            'is_following': existing is not None
        }, 200
    finally:
        db.close()


def like_signal(signal_id: int, user_id: int) -> Tuple[Dict[str, Any], int]:
    db = get_db_session()
    try:
        signal = db.query(Signal).filter(Signal.id == signal_id).first()
        
        if not signal:
            return {
                'success': False,
                'message': '信号不存在'
            }, 404
        
        signal.likes = (signal.likes or 0) + 1
        db.commit()
        db.refresh(signal)
        
        try:
            websocket.push_service.push_like_update(signal_id, signal.likes, True)
        except Exception as e:
            print(f"[WS] Failed to push like update: {e}")
        
        return {
            'success': True,
            'message': '点赞成功',
            'likes': signal.likes
        }, 200
    except Exception as e:
        db.rollback()
        return {
            'success': False,
            'message': str(e)
        }, 500
    finally:
        db.close()


def like_reply(signal_id: int, reply_id: int) -> Tuple[Dict[str, Any], int]:
    db = get_db_session()
    try:
        reply = db.query(SignalReply).filter(SignalReply.id == reply_id).first()
        
        if not reply:
            return {
                'success': False,
                'message': '评论不存在'
            }, 404
        
        reply.likes = (reply.likes or 0) + 1
        db.commit()
        db.refresh(reply)
        
        return {
            'success': True,
            'message': '点赞成功',
            'likes': reply.likes
        }, 200
    except Exception as e:
        db.rollback()
        return {
            'success': False,
            'message': str(e)
        }, 500
    finally:
        db.close()


def create_signal(
    user_id: int,
    title: str,
    content: str,
    message_type: str = 'operation',
    market: str = 'us-stock',
    symbol: str = '',
    direction: str = '',
    entry_price: Optional[float] = None,
    stop_loss: Optional[float] = None,
    take_profit: Optional[float] = None
) -> Tuple[Dict[str, Any], int]:
    if not title:
        return {
            'success': False,
            'message': '标题不能为空'
        }, 400
    
    if not content:
        return {
            'success': False,
            'message': '内容不能为空'
        }, 400
    
    db = get_db_session()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        agent_name = user.username if user else '匿名交易者'
        
        symbols = [symbol] if symbol else []
        
        full_content = content
        if direction or entry_price or stop_loss or take_profit:
            full_content += '\n\n---\n'
            if direction:
                dir_text = {'long': '看涨', 'short': '看跌', 'neutral': '中性'}.get(direction, direction)
                full_content += f'\n**交易方向**: {dir_text}'
            if entry_price:
                full_content += f'\n**入场价格**: {entry_price}'
            if stop_loss:
                full_content += f'\n**止损价格**: {stop_loss}'
            if take_profit:
                full_content += f'\n**目标价格**: {take_profit}'
        
        quality_score = round(random.uniform(60, 95), 1)
        
        new_signal = Signal(
            user_id=user_id,
            agent_name=agent_name,
            title=title,
            content=full_content,
            message_type=message_type,
            market=market,
            symbols=symbols,
            quality_score=quality_score,
            reply_count=0,
            participant_count=1,
            likes=0,
            views=0
        )
        db.add(new_signal)
        db.flush()
        
        new_participant = SignalParticipant(
            signal_id=new_signal.id,
            user_id=user_id,
            user_name=agent_name,
            role='author'
        )
        db.add(new_participant)
        
        accuracy = round(random.uniform(60, 95), 1)
        analysis_depth = round(random.uniform(60, 95), 1)
        risk_management = round(random.uniform(60, 95), 1)
        timeliness = round(random.uniform(60, 95), 1)
        clarity = round(random.uniform(60, 95), 1)
        total_score = round((accuracy + analysis_depth + risk_management + timeliness + clarity) / 5, 1)
        
        new_quality = SignalQualityScore(
            signal_id=new_signal.id,
            accuracy_score=accuracy,
            analysis_depth=analysis_depth,
            risk_management=risk_management,
            timeliness=timeliness,
            clarity=clarity,
            total_score=total_score
        )
        db.add(new_quality)
        
        db.commit()
        db.refresh(new_signal)
        
        signal_dict = model_to_dict(new_signal)
        signal_dict['symbols'] = new_signal.symbols if new_signal.symbols else []
        signal_dict['is_following'] = True
        signal_dict['is_liked'] = False
        
        try:
            websocket.push_service.push_new_signal(signal_dict)
        except Exception as e:
            print(f"[WS] Failed to push new signal: {e}")
        
        return {
            'success': True,
            'message': '信号发布成功',
            'signal': signal_dict
        }, 201
    except Exception as e:
        db.rollback()
        return {
            'success': False,
            'message': str(e)
        }, 500
    finally:
        db.close()
