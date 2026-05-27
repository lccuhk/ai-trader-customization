"""
Simple Backend Server

简化版后端服务，只包含新添加的功能
"""

import sqlite3
import json
import hashlib
import secrets
import os
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title='AI-Trader Simple API')

allowed_origins = [
    'http://localhost:8080',
    'http://localhost:3000',
    'https://trading-agent-for-dscourse.surge.sh',
    'https://trading-agent-backend.deta.app',
    'https://trading-agent-for-dscourse-backend.onrender.com',
]

class RegexCORSMiddleware(CORSMiddleware):
    def is_allowed_origin(self, origin: str) -> bool:
        if super().is_allowed_origin(origin):
            return True
        if re.match(r'^https://.*\.deta\.app$', origin):
            return True
        if re.match(r'^https://.*\.deta\.dev$', origin):
            return True
        if re.match(r'^https://.*\.onrender\.com$', origin):
            return True
        return False

app.add_middleware(
    RegexCORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'clawtrader.db')


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _generate_token() -> str:
    return secrets.token_hex(32)


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT COUNT(*) FROM users WHERE email = ?', ('demo@example.com',))
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO users (email, password_hash)
                VALUES (?, ?)
            ''', ('demo@example.com', _hash_password('demo123')))
            
            cursor.execute('SELECT id FROM users WHERE email = ?', ('demo@example.com',))
            user_id = cursor.fetchone()[0]
            
            try:
                cursor.execute('SELECT COUNT(*) FROM user_stats WHERE user_id = ?', (user_id,))
                if cursor.fetchone()[0] == 0:
                    cursor.execute('''
                        INSERT INTO user_stats (user_id, total_trades, winning_trades, total_pnl, win_rate, sharpe_ratio)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (user_id, 156, 102, 25430.50, 0.654, 1.85))
            except:
                pass
        
        cursor.execute('SELECT COUNT(*) FROM notifications')
        if cursor.fetchone()[0] == 0:
            sample_notifications = [
                (1, 'NVDA 价格预警', 'NVDA 价格已突破 $500 阻力位', 'price_alert', 'high'),
                (1, '新交易信号', '检测到 AAPL 买入信号，强度 85%', 'signal', 'normal'),
                (1, '风险预警', '您的投资组合集中度超过 30% 阈值', 'risk', 'high'),
                (1, '系统更新', '系统已完成例行维护', 'system', 'low'),
            ]
            cursor.executemany('''
                INSERT INTO notifications (user_id, title, message, notification_type, priority)
                VALUES (?, ?, ?, ?, ?)
            ''', sample_notifications)
        
        cursor.execute('SELECT COUNT(*) FROM strategies')
        if cursor.fetchone()[0] == 0:
            sample_strategies = [
                ('移动平均线交叉策略', '基于短期和长期移动平均线的交叉信号', 'trend_following', '# 策略代码', '{}', 1),
                ('RSI超买超卖策略', '使用RSI指标识别超买超卖区域', 'mean_reversion', '# 策略代码', '{}', 1),
                ('布林带突破策略', '基于布林带的突破信号', 'volatility', '# 策略代码', '{}', 0),
            ]
            cursor.executemany('''
                INSERT INTO strategies (name, description, strategy_type, code, parameters, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', sample_strategies)
        
        cursor.execute('SELECT COUNT(*) FROM market_news')
        if cursor.fetchone()[0] == 0:
            sample_news = [
                ('美联储暗示可能在年内降息', '美联储主席鲍威尔暗示可能降息', 'Reuters', 'macro', 'SPY', 85, 'bullish'),
                ('英伟达发布新一代AI芯片', '性能提升3倍', 'TechCrunch', 'earnings', 'NVDA', 90, 'bullish'),
                ('苹果Vision Pro销量不及预期', '影响供应链企业', 'Bloomberg', 'earnings', 'AAPL', 60, 'bearish'),
            ]
            cursor.executemany('''
                INSERT INTO market_news (title, content, source, category, symbol, impact_score, sentiment)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', sample_news)
        
        cursor.execute('SELECT COUNT(*) FROM market_events')
        if cursor.fetchone()[0] == 0:
            now = datetime.now()
            sample_events = [
                ('美联储利率决议', 'FOMC会议', 'fed', (now + timedelta(days=5)).isoformat(), 'high'),
                ('英伟达财报', 'Q1财报发布', 'earnings', (now + timedelta(days=10)).isoformat(), 'high'),
                ('非农就业数据', '美国非农数据', 'economic', (now + timedelta(days=3)).isoformat(), 'high'),
            ]
            cursor.executemany('''
                INSERT INTO market_events (title, description, event_type, event_date, importance)
                VALUES (?, ?, ?, ?, ?)
            ''', sample_events)
    except Exception as e:
        print(f'Warning during init_db: {e}')
    
    conn.commit()
    conn.close()


init_db()


MOCK_RESPONSES = {
    'default': [
        '基于当前市场环境，我建议保持谨慎乐观的态度。',
        '从技术面来看，RSI指标显示当前处于中性区域。',
        '建议关注成交量变化和资金流向。',
        '风险管理永远是第一位的，请确保设置合理的止损。',
    ],
    'market': [
        '当前市场处于震荡整理阶段，建议等待明确方向。',
        '从宏观角度看，美联储政策是关键变量。',
        '科技板块近期表现强势，但需警惕估值压力。',
    ],
    'stock': [
        '从技术面分析，该股处于上升趋势中。',
        '基本面稳健，营收和利润增长符合预期。',
        '建议关注支撑位和阻力位的突破情况。',
    ],
    'risk': [
        '单笔交易风险建议控制在总资金的 1-2%。',
        '最大回撤超过 20% 时应考虑降低仓位。',
        '止损不是认输，而是保护资金的必要手段。',
    ]
}


def _generate_mock_response(user_message: str, agent_type: str) -> str:
    import random
    message_lower = user_message.lower()
    
    if any(keyword in message_lower for keyword in ['股票', 'stock', 'aapl', 'tsla', 'nvda']):
        responses = MOCK_RESPONSES['stock']
    elif any(keyword in message_lower for keyword in ['风险', '止损', 'risk']):
        responses = MOCK_RESPONSES['risk']
    elif any(keyword in message_lower for keyword in ['市场', '大盘', 'market']):
        responses = MOCK_RESPONSES['market']
    else:
        responses = MOCK_RESPONSES['default']
    
    return random.choice(responses)


@app.get('/')
async def root():
    return {'message': 'AI-Trader API is running', 'status': 'ok'}


@app.get('/api/health')
async def health():
    return {'status': 'healthy'}


class ChatRequest(BaseModel):
    message: str
    agent_id: str = 'market-analyst'
    conversation_id: Optional[int] = None


@app.post('/api/ai/chat')
async def chat_with_ai(request: ChatRequest):
    import time
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    conversation_id = request.conversation_id
    if not conversation_id:
        conv_id = f'conv_{int(time.time() * 1000)}'
        cursor.execute('''
            INSERT INTO ai_conversations (conversation_id, agent_type, title, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (conv_id, request.agent_id, request.message[:30], datetime.now().isoformat(), datetime.now().isoformat()))
        conversation_id = cursor.lastrowid
    
    ai_response = _generate_mock_response(request.message, request.agent_id)
    
    conn.commit()
    conn.close()
    
    return {
        'success': True,
        'response': ai_response,
        'conversation_id': conversation_id
    }


@app.get('/api/ai/conversations')
async def get_conversations():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM ai_conversations ORDER BY updated_at DESC LIMIT 20')
    rows = cursor.fetchall()
    conn.close()
    
    conversations = []
    for row in rows:
        conversations.append({
            'id': row['id'],
            'title': row['title'],
            'agent_type': row['agent_type'],
            'updated_at': row['updated_at']
        })
    
    return {'success': True, 'conversations': conversations}


@app.get('/api/ai/conversations/{conv_id}')
async def get_conversation(conv_id: int):
    return {
        'success': True,
        'conversation': {
            'id': conv_id,
            'messages': []
        }
    }


@app.get('/api/ai/agents')
async def get_agents():
    return {
        'success': True,
        'agents': [
            {'id': 'market-analyst', 'name': '市场分析师', 'icon': '📊', 'description': '分析市场趋势、技术指标和宏观经济'},
            {'id': 'trading-coach', 'name': '交易教练', 'icon': '🎯', 'description': '提供交易心理指导和纪律训练'},
            {'id': 'portfolio-manager', 'name': '投资组合经理', 'icon': '💼', 'description': '优化资产配置和风险管理'},
            {'id': 'quant-researcher', 'name': '量化研究员', 'icon': '🔬', 'description': '量化策略分析和回测建议'}
        ]
    }


@app.get('/api/risk/dashboard')
async def get_risk_dashboard():
    import random
    return {
        'success': True,
        'metrics': {
            'risk_score': random.randint(40, 80),
            'concentration_risk': random.uniform(0.2, 0.5),
            'net_exposure': random.uniform(-0.3, 0.3),
            'max_drawdown': random.uniform(0.05, 0.15),
            'win_rate': random.uniform(0.5, 0.75)
        }
    }


@app.get('/api/risk/settings')
async def get_risk_settings():
    return {
        'success': True,
        'settings': {
            'max_single_risk_percent': 2,
            'max_daily_risk_percent': 5,
            'max_position_concentration': 30,
            'max_acceptable_drawdown': 15,
            'risk_alert_threshold': 30
        }
    }


@app.get('/api/risk/alerts')
async def get_risk_alerts():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM notifications WHERE notification_type = "risk" ORDER BY created_at DESC LIMIT 10')
    rows = cursor.fetchall()
    conn.close()
    
    alerts = []
    for row in rows:
        alerts.append({
            'id': row['id'],
            'title': row['title'],
            'message': row['message'],
            'severity': row['priority'],
            'created_at': row['created_at']
        })
    
    return {'success': True, 'alerts': alerts}


class PositionCalcRequest(BaseModel):
    account_size: float
    risk_percent: float
    entry_price: float
    stop_price: float


@app.post('/api/risk/calculate-position-size')
async def calculate_position_size(request: PositionCalcRequest):
    risk_amount = request.account_size * (request.risk_percent / 100)
    stop_distance = abs(request.entry_price - request.stop_price)
    stop_distance_percent = stop_distance / request.entry_price
    position_size = risk_amount / stop_distance if stop_distance > 0 else 0
    position_value = position_size * request.entry_price
    
    return {
        'success': True,
        'result': {
            'risk_amount': risk_amount,
            'stop_distance': stop_distance,
            'stop_distance_percent': stop_distance_percent,
            'position_size': position_size,
            'position_value': position_value
        }
    }


@app.get('/api/market/dashboard')
async def get_market_dashboard():
    return {
        'success': True,
        'dashboard': {
            'news_24h': 8,
            'sentiment_breakdown': {'bullish': 5, 'bearish': 2, 'neutral': 1},
            'upcoming_events': {'fed': 1, 'earnings': 2, 'economic': 1},
            'average_market_sentiment': 0.65
        }
    }


@app.get('/api/market/news')
async def get_market_news(category: Optional[str] = None, limit: int = 10):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = 'SELECT * FROM market_news WHERE 1=1'
    params = []
    
    if category:
        query += ' AND category = ?'
        params.append(category)
    
    query += ' ORDER BY created_at DESC LIMIT ?'
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    news = []
    for row in rows:
        news.append({
            'id': row['id'],
            'title': row['title'],
            'content': row['content'],
            'source': row['source'],
            'category': row['category'],
            'symbol': row['symbol'],
            'impact_score': row['impact_score'],
            'sentiment': row['sentiment'],
            'created_at': row['created_at']
        })
    
    return {'success': True, 'news': news, 'total': len(news)}


@app.get('/api/market/news/{news_id}')
async def get_news_detail(news_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM market_news WHERE id = ?', (news_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail='News not found')
    
    return {
        'success': True,
        'news': {
            'id': row['id'],
            'title': row['title'],
            'content': row['content'],
            'source': row['source'],
            'category': row['category'],
            'symbol': row['symbol'],
            'impact_score': row['impact_score'],
            'sentiment': row['sentiment'],
            'created_at': row['created_at']
        }
    }


@app.get('/api/market/events')
async def get_market_events(limit: int = 10):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM market_events ORDER BY event_date ASC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    events = []
    for row in rows:
        events.append({
            'id': row['id'],
            'title': row['title'],
            'description': row['description'],
            'event_type': row['event_type'],
            'event_date': row['event_date'],
            'importance': row['importance']
        })
    
    return {'success': True, 'events': events}


@app.get('/api/market/indicators')
async def get_economic_indicators(limit: int = 10):
    return {
        'success': True,
        'indicators': [
            {'name': '联邦基金利率', 'value': 5.25, 'previous_value': 5.25, 'forecast_value': 5.25, 'unit': '%', 'impact': 'high'},
            {'name': 'CPI同比', 'value': 3.2, 'previous_value': 3.1, 'forecast_value': 3.3, 'unit': '%', 'impact': 'high'},
            {'name': '失业率', 'value': 3.8, 'previous_value': 3.9, 'forecast_value': 3.8, 'unit': '%', 'impact': 'high'},
            {'name': 'GDP环比', 'value': 3.2, 'previous_value': 4.9, 'forecast_value': 3.0, 'unit': '%', 'impact': 'high'},
        ]
    }


@app.get('/api/strategies')
async def get_strategies():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM strategies ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    
    strategies = []
    for row in rows:
        strategies.append({
            'id': row['id'],
            'name': row['name'],
            'description': row['description'],
            'strategy_type': row['strategy_type'],
            'is_active': bool(row['is_active']),
            'created_at': row['created_at']
        })
    
    return {'success': True, 'strategies': strategies}


@app.get('/api/strategies/{strategy_id}')
async def get_strategy_detail(strategy_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM strategies WHERE id = ?', (strategy_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail='Strategy not found')
    
    return {
        'success': True,
        'strategy': {
            'id': row['id'],
            'name': row['name'],
            'description': row['description'],
            'strategy_type': row['strategy_type'],
            'code': row['code'],
            'parameters': json.loads(row['parameters']) if row['parameters'] else {},
            'is_active': bool(row['is_active']),
            'created_at': row['created_at']
        }
    }


class StrategyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    strategy_type: str = 'custom'
    code: str = ''
    parameters: Optional[Dict[str, Any]] = None


@app.post('/api/strategies')
async def create_strategy(strategy: StrategyCreate):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO strategies (name, description, strategy_type, code, parameters)
        VALUES (?, ?, ?, ?, ?)
    ''', (strategy.name, strategy.description, strategy.strategy_type, strategy.code, json.dumps(strategy.parameters or {})))
    
    strategy_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {'success': True, 'strategy_id': strategy_id}


class BacktestRequest(BaseModel):
    strategy_id: int
    start_date: str
    end_date: str
    initial_capital: float = 100000.0


@app.post('/api/strategies/backtest')
async def run_backtest(request: BacktestRequest):
    import random
    total_trades = random.randint(50, 200)
    win_rate = random.uniform(0.45, 0.75)
    total_return = random.uniform(-0.2, 0.5)
    max_drawdown = random.uniform(0.05, 0.25)
    sharpe_ratio = random.uniform(0.5, 2.5)
    
    return {
        'success': True,
        'result': {
            'initial_capital': request.initial_capital,
            'final_capital': request.initial_capital * (1 + total_return),
            'total_return': total_return,
            'annualized_return': total_return,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'win_rate': win_rate,
            'total_trades': total_trades
        }
    }


class LoginRequest(BaseModel):
    username: str
    password: str


@app.post('/api/auth/login')
async def login(request: LoginRequest):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    password_hash = _hash_password(request.password)
    
    cursor.execute('''
        SELECT id, email FROM users 
        WHERE email = ? AND password_hash = ?
    ''', (request.username, password_hash))
    
    row = cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=401, detail='Invalid credentials')
    
    token = _generate_token()
    expires_at = (datetime.now() + timedelta(days=7)).isoformat()
    
    try:
        cursor.execute('''
            INSERT INTO user_sessions (user_id, token, expires_at)
            VALUES (?, ?, ?)
        ''', (row['id'], token, expires_at))
    except:
        pass
    
    conn.commit()
    conn.close()
    
    return {
        'success': True,
        'token': token,
        'user': {
            'id': row['id'],
            'username': row['email'].split('@')[0],
            'email': row['email'],
            'display_name': '演示用户'
        }
    }


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    display_name: Optional[str] = None


@app.post('/api/auth/register')
async def register(request: RegisterRequest):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT id FROM users WHERE email = ?', (request.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail='Email already exists')
        
        password_hash = _hash_password(request.password)
        
        cursor.execute('''
            INSERT INTO users (email, password_hash)
            VALUES (?, ?)
        ''', (request.email, password_hash))
        
        user_id = cursor.lastrowid
        
        try:
            cursor.execute('INSERT INTO user_stats (user_id) VALUES (?)', (user_id,))
        except:
            pass
        
        conn.commit()
        return {'success': True, 'user_id': user_id}
    finally:
        conn.close()


@app.get('/api/users/me')
async def get_current_user(request: Request):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        raise HTTPException(status_code=401, detail='Not authenticated')
    
    token = auth_header.replace('Bearer ', '')
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT u.* FROM users u
            JOIN user_sessions s ON u.id = s.user_id
            WHERE s.token = ?
        ''', (token,))
    except:
        cursor.execute('SELECT * FROM users WHERE email = ?', ('demo@example.com',))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=401, detail='Invalid token')
    
    created_at = None
    try:
        created_at = row['created_at']
    except:
        created_at = datetime.now().isoformat()
    
    return {
        'success': True,
        'user': {
            'id': row['id'],
            'username': row['email'].split('@')[0],
            'email': row['email'],
            'display_name': '演示用户',
            'bio': '这是一个演示账户',
            'created_at': created_at
        }
    }


@app.get('/api/users/me/stats')
async def get_user_stats(request: Request):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        raise HTTPException(status_code=401, detail='Not authenticated')
    
    token = auth_header.replace('Bearer ', '')
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT st.* FROM user_stats st
            JOIN user_sessions s ON st.user_id = s.user_id
            WHERE s.token = ?
        ''', (token,))
        row = cursor.fetchone()
    except:
        row = None
    
    if not row:
        return {
            'success': True,
            'stats': {
                'total_trades': 156,
                'winning_trades': 102,
                'losing_trades': 54,
                'total_pnl': 25430.50,
                'win_rate': 0.654,
                'sharpe_ratio': 1.85,
                'max_drawdown': 0.082
            }
        }
    
    conn.close()
    
    return {
        'success': True,
        'stats': {
            'total_trades': row['total_trades'],
            'winning_trades': row['winning_trades'],
            'losing_trades': row['total_trades'] - row['winning_trades'],
            'total_pnl': row['total_pnl'],
            'win_rate': row['win_rate'],
            'sharpe_ratio': row['sharpe_ratio'],
            'max_drawdown': 0.082
        }
    }


@app.get('/api/users/me/preferences')
async def get_user_preferences():
    return {
        'success': True,
        'preferences': {
            'theme': 'dark',
            'language': 'zh-CN',
            'notifications_enabled': True,
            'risk_alerts_enabled': True,
            'email_notifications': True
        }
    }


@app.get('/api/notifications')
async def get_notifications(limit: int = 20, unread_only: bool = False):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = 'SELECT * FROM notifications WHERE user_id = 1'
    params = []
    
    if unread_only:
        query += ' AND is_read = 0'
    
    query += ' ORDER BY created_at DESC LIMIT ?'
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    cursor.execute('SELECT COUNT(*) as count FROM notifications WHERE user_id = 1 AND is_read = 0')
    unread_count = cursor.fetchone()['count']
    
    conn.close()
    
    notifications = []
    for row in rows:
        notifications.append({
            'id': row['id'],
            'title': row['title'],
            'message': row['message'],
            'notification_type': row['notification_type'],
            'priority': row['priority'],
            'is_read': bool(row['is_read']),
            'created_at': row['created_at']
        })
    
    return {'success': True, 'notifications': notifications, 'unread_count': unread_count}


@app.put('/api/notifications/{notification_id}/read')
async def mark_notification_read(notification_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('UPDATE notifications SET is_read = 1 WHERE id = ?', (notification_id,))
    conn.commit()
    conn.close()
    
    return {'success': True}


@app.put('/api/notifications/read-all')
async def mark_all_read():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('UPDATE notifications SET is_read = 1 WHERE user_id = 1 AND is_read = 0')
    conn.commit()
    conn.close()
    
    return {'success': True}


@app.get('/api/notifications/settings')
async def get_notification_settings():
    return {
        'success': True,
        'settings': {
            'price_alerts': True,
            'signal_updates': True,
            'risk_alerts': True,
            'system_notifications': True,
            'email_notifications': False,
            'webhook_notifications': False
        }
    }


@app.get('/api/webhooks')
async def get_webhooks():
    return {'success': True, 'webhooks': []}


@app.get('/api/email/config')
async def get_email_config():
    return {'success': True, 'config': None}


@app.get('/api/strategies/templates')
async def get_strategy_templates():
    return {
        'success': True,
        'templates': [
            {'id': 1, 'name': '双均线策略模板', 'category': '趋势跟踪', 'description': '经典的趋势跟踪策略'},
            {'id': 2, 'name': '均值回归策略模板', 'category': '均值回归', 'description': '基于价格回归均值的策略'},
            {'id': 3, 'name': '波动率策略模板', 'category': '波动率', 'description': '基于波动率的策略'},
        ]
    }


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8001)
