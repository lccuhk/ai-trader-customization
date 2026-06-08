"""
Market Service

Business logic for market news, events, and economic indicators.
"""

from typing import Tuple, Dict, Any

from sqlalchemy import text

from database import get_db_session
from models import MarketNews, MarketEvent, EconomicIndicator, Strategy
from utils.helpers import model_to_dict, models_to_dict_list


def get_market_news(limit: int = 10, category: str = '') -> Tuple[Dict[str, Any], int]:
    db = get_db_session()
    try:
        query = db.query(MarketNews)
        if category:
            query = query.filter(MarketNews.category == category)
        news_list = query.order_by(text('created_at DESC')).limit(limit).all()
        
        return {
            'success': True,
            'news': models_to_dict_list(news_list)
        }, 200
    finally:
        db.close()


def get_news_detail(news_id: int) -> Tuple[Dict[str, Any], int]:
    db = get_db_session()
    try:
        news = db.query(MarketNews).filter(MarketNews.id == news_id).first()
        return {
            'success': True,
            'news': model_to_dict(news)
        }, 200
    finally:
        db.close()


def get_strategies() -> Tuple[Dict[str, Any], int]:
    db = get_db_session()
    try:
        strategies = db.query(Strategy).order_by(text('created_at DESC')).all()
        
        result = []
        for strategy in strategies:
            strategy_dict = model_to_dict(strategy)
            strategy_dict['parameters'] = strategy.parameters if strategy.parameters else {}
            result.append(strategy_dict)
        
        return {
            'success': True,
            'strategies': result
        }, 200
    finally:
        db.close()


def get_strategy_detail(strategy_id: int) -> Tuple[Dict[str, Any], int]:
    db = get_db_session()
    try:
        strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
        if strategy:
            strategy_dict = model_to_dict(strategy)
            strategy_dict['parameters'] = strategy.parameters if strategy.parameters else {}
            return {
                'success': True,
                'strategy': strategy_dict
            }, 200
        else:
            return {
                'success': False,
                'message': '策略不存在'
            }, 404
    finally:
        db.close()


def create_strategy(
    name: str,
    description: str = '',
    strategy_type: str = 'custom',
    code: str = '',
    parameters: dict = None
) -> Tuple[Dict[str, Any], int]:
    db = get_db_session()
    try:
        new_strategy = Strategy(
            name=name,
            description=description,
            strategy_type=strategy_type,
            code=code,
            parameters=parameters or {},
            is_active=True
        )
        db.add(new_strategy)
        db.commit()
        db.refresh(new_strategy)
        
        return {
            'success': True,
            'strategy_id': new_strategy.id,
            'message': '策略创建成功'
        }, 200
    except Exception as e:
        db.rollback()
        return {
            'success': False,
            'message': str(e)
        }, 500
    finally:
        db.close()
