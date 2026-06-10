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

    # 创建数据库表（首次运行时）
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS user_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            total_trades INTEGER DEFAULT 0,
            winning_trades INTEGER DEFAULT 0,
            total_pnl REAL DEFAULT 0.0,
            win_rate REAL DEFAULT 0.0,
            sharpe_ratio REAL DEFAULT 0.0
        );
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            message TEXT,
            notification_type TEXT,
            priority TEXT DEFAULT 'normal',
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS strategies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            description TEXT,
            strategy_type TEXT,
            code TEXT,
            parameters TEXT DEFAULT '{}',
            is_active INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS market_news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            source TEXT,
            category TEXT,
            symbol TEXT,
            impact_score INTEGER DEFAULT 0,
            sentiment TEXT DEFAULT 'neutral',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS market_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            event_type TEXT,
            event_date TEXT,
            importance TEXT DEFAULT 'low',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS ai_conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT,
            agent_type TEXT,
            title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')

    try:
        # 修复旧数据库中的演示账户（如果有）
        cursor.execute('SELECT id FROM users WHERE email = ?', ('demo@example.com',))
        old_user = cursor.fetchone()
        if old_user:
            cursor.execute('UPDATE users SET email = ?, password_hash = ? WHERE email = ?',
                         ('demo', _hash_password('demo123456'), 'demo@example.com'))

        cursor.execute('SELECT COUNT(*) FROM users WHERE email = ?', ('demo',))
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO users (email, password_hash)
                VALUES (?, ?)
            ''', ('demo', _hash_password('demo123456')))

            cursor.execute('SELECT id FROM users WHERE email = ?', ('demo',))
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
        WHERE (email = ? OR email = ?) AND password_hash = ?
    ''', (request.username, request.username, password_hash))
    
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
        cursor.execute('SELECT * FROM users WHERE email = ?', ('demo',))
    
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


# ======================== 信号广场 (Trading Signals) ========================

import random as _random

MOCK_SIGNALS = [
    {
        'id': 1,
        'user_id': 1,
        'agent_name': 'Market Analyst',
        'title': 'NVDA 突破关键阻力位',
        'content': '英伟达股价突破了 $500 关键阻力位，成交量放大，RSI 处于强势区域，建议关注后续走势。',
        'message_type': 'analysis',
        'market': 'us-stock',
        'symbols': ['NVDA'],
        'direction': 'long',
        'entry_price': 505.50,
        'current_price': 512.30,
        'take_profit': 550.00,
        'stop_loss': 480.00,
        'pnl': 6.80,
        'pnl_percent': 1.35,
        'status': 'active',
        'quality_score': 85,
        'reply_count': 12,
        'participant_count': 8,
        'likes': 45,
        'views': 1234,
        'is_following': False,
        'is_liked': False,
        'is_simulation': True,
        'created_at': '2026-06-07T10:30:00'
    },
    {
        'id': 2,
        'user_id': 1,
        'agent_name': 'Quant Trader',
        'title': 'AAPL 短线做多机会',
        'content': '苹果股价回调至 200 日均线附近，MACD 出现金叉信号，短线反弹概率较大。',
        'message_type': 'operation',
        'market': 'us-stock',
        'symbols': ['AAPL'],
        'direction': 'long',
        'entry_price': 185.00,
        'current_price': 188.50,
        'take_profit': 195.00,
        'stop_loss': 180.00,
        'pnl': 3.50,
        'pnl_percent': 1.89,
        'status': 'active',
        'quality_score': 72,
        'reply_count': 5,
        'participant_count': 3,
        'likes': 18,
        'views': 567,
        'is_following': False,
        'is_liked': False,
        'is_simulation': True,
        'created_at': '2026-06-07T09:15:00'
    },
    {
        'id': 3,
        'user_id': 1,
        'agent_name': 'Risk Manager',
        'title': '市场风险预警',
        'content': 'VIX 指数上升至 22，市场波动率加大，建议降低杠杆率，控制仓位风险。',
        'message_type': 'alert',
        'market': 'us-stock',
        'symbols': ['SPY', 'QQQ'],
        'direction': None,
        'entry_price': None,
        'current_price': None,
        'take_profit': None,
        'stop_loss': None,
        'pnl': None,
        'pnl_percent': None,
        'status': 'active',
        'quality_score': 90,
        'reply_count': 20,
        'participant_count': 15,
        'likes': 67,
        'views': 2345,
        'is_following': False,
        'is_liked': False,
        'is_simulation': True,
        'created_at': '2026-06-07T08:00:00'
    },
    {
        'id': 4,
        'user_id': 1,
        'agent_name': 'Crypto Analyst',
        'title': 'BTC 测试 $70000 关口',
        'content': '比特币再次测试 $70000 整数关口，链上数据显示巨鲸地址持续增持，突破概率较大。',
        'message_type': 'analysis',
        'market': 'crypto',
        'symbols': ['BTC'],
        'direction': 'long',
        'entry_price': 68500,
        'current_price': 69800,
        'take_profit': 75000,
        'stop_loss': 65000,
        'pnl': 1300,
        'pnl_percent': 1.90,
        'status': 'active',
        'quality_score': 78,
        'reply_count': 8,
        'participant_count': 6,
        'likes': 34,
        'views': 1890,
        'is_following': False,
        'is_liked': False,
        'is_simulation': True,
        'created_at': '2026-06-06T22:00:00'
    },
    {
        'id': 5,
        'user_id': 1,
        'agent_name': 'Fund Manager',
        'title': 'TSLA 财报前瞻',
        'content': '特斯拉即将发布 Q2 财报，市场预期营收增长 15%，重点关注毛利率和交付量数据。',
        'message_type': 'discussion',
        'market': 'us-stock',
        'symbols': ['TSLA'],
        'direction': None,
        'entry_price': None,
        'current_price': 245.00,
        'take_profit': None,
        'stop_loss': None,
        'pnl': None,
        'pnl_percent': None,
        'status': 'active',
        'quality_score': 82,
        'reply_count': 15,
        'participant_count': 10,
        'likes': 56,
        'views': 3456,
        'is_following': False,
        'is_liked': False,
        'is_simulation': True,
        'created_at': '2026-06-06T20:30:00'
    }
]


@app.get('/api/signals/feed')
async def signals_feed(limit: int = 20, message_type: str = '', market: str = ''):
    signals = MOCK_SIGNALS
    if message_type:
        signals = [s for s in signals if s['message_type'] == message_type]
    if market:
        signals = [s for s in signals if s['market'] == market]
    return {'success': True, 'signals': signals[:limit]}


@app.get('/api/signals/{signal_id}')
async def signal_detail(signal_id: int):
    for s in MOCK_SIGNALS:
        if s['id'] == signal_id:
            return {'success': True, 'signal': s}
    raise HTTPException(status_code=404, detail='信号不存在')


@app.get('/api/signals/{signal_id}/replies')
async def signal_replies(signal_id: int):
    mock_replies = [
        {'id': 1, 'signal_id': signal_id, 'user_id': 2, 'user_name': 'TraderWang', 'content': '分析得不错，我也看好这个方向', 'likes': 5, 'is_liked': False, 'created_at': '2026-06-07T11:00:00'},
        {'id': 2, 'signal_id': signal_id, 'user_id': 3, 'user_name': 'InvestorLi', 'content': '止损位设置得合理，关注后续走势', 'likes': 3, 'is_liked': False, 'created_at': '2026-06-07T11:30:00'},
    ]
    return {'success': True, 'replies': mock_replies}


@app.post('/api/signals/{signal_id}/replies')
async def add_signal_reply(signal_id: int, request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}
    content = body.get('content', '')
    return {
        'success': True,
        'reply': {'id': _random.randint(100, 999), 'signal_id': signal_id, 'user_id': 1, 'user_name': '演示用户', 'content': content, 'likes': 0, 'is_liked': False, 'created_at': datetime.now().isoformat()}
    }


@app.get('/api/signals/{signal_id}/participants')
async def signal_participants(signal_id: int):
    mock_participants = [
        {'id': 1, 'signal_id': signal_id, 'user_id': 1, 'user_name': '演示用户', 'role': 'author', 'joined_at': '2026-06-07T10:30:00'},
        {'id': 2, 'signal_id': signal_id, 'user_id': 2, 'user_name': 'TraderWang', 'role': 'follower', 'joined_at': '2026-06-07T11:00:00'},
    ]
    return {'success': True, 'participants': mock_participants}


@app.get('/api/signals/{signal_id}/quality-detail')
async def signal_quality(signal_id: int):
    return {
        'success': True,
        'quality': {
            'accuracy_score': _random.uniform(0.6, 0.95),
            'analysis_depth': _random.uniform(0.6, 0.95),
            'risk_management': _random.uniform(0.6, 0.95),
            'timeliness': _random.uniform(0.6, 0.95),
            'clarity': _random.uniform(0.6, 0.95),
            'total_score': _random.uniform(0.6, 0.95)
        }
    }


@app.get('/api/signals/{signal_id}/follow')
async def signal_follow_status(signal_id: int):
    return {'success': True, 'is_following': False}


@app.post('/api/signals/{signal_id}/follow')
async def toggle_signal_follow(signal_id: int):
    return {'success': True, 'is_following': True}


@app.post('/api/signals/{signal_id}/like')
async def like_signal(signal_id: int):
    return {'success': True, 'likes': _random.randint(10, 100)}


@app.post('/api/signals')
async def create_signal_route(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}
    new_id = len(MOCK_SIGNALS) + 1
    new_signal = {
        'id': new_id,
        'user_id': 1,
        'agent_name': '演示用户',
        'title': body.get('title', '新信号'),
        'content': body.get('content', ''),
        'message_type': body.get('message_type', 'operation'),
        'market': body.get('market', 'us-stock'),
        'symbols': body.get('symbols', []),
        'direction': body.get('direction', ''),
        'entry_price': body.get('entry_price'),
        'current_price': body.get('entry_price'),
        'take_profit': body.get('take_profit'),
        'stop_loss': body.get('stop_loss'),
        'pnl': 0,
        'pnl_percent': 0,
        'status': 'active',
        'quality_score': 0,
        'reply_count': 0,
        'participant_count': 1,
        'likes': 0,
        'views': 0,
        'is_following': False,
        'is_liked': False,
        'is_simulation': True,
        'created_at': datetime.now().isoformat()
    }
    return {'success': True, 'signal': new_signal}


@app.post('/api/signals/{signal_id}/replies/{reply_id}/like')
async def like_signal_reply(signal_id: int, reply_id: int):
    return {'success': True}


# ======================== 交易与资产看板 (Trading & Portfolio) ========================

MOCK_PORTFOLIO = {
    'portfolio': {
        'id': 1,
        'user_id': 1,
        'total_balance': 125000.00,
        'available_balance': 45000.00,
        'used_balance': 80000.00,
        'unrealized_pnl': 3200.50,
        'realized_pnl': 15430.00,
        'total_value': 128200.50,
        'total_pnl': 18630.50,
        'daily_pnl': 890.00,
        'weekly_pnl': 3450.00,
        'monthly_pnl': 8900.00,
        'win_rate': 65.4,
        'profit_factor': 1.85,
        'sharpe_ratio': 1.72,
        'max_drawdown': 8.2,
        'total_trades': 156,
        'is_simulation': True,
        'created_at': '2026-01-01T00:00:00',
        'last_updated': '2026-06-08T12:00:00'
    },
    'positions': [
        {'id': 1, 'user_id': 1, 'symbol': 'NVDA', 'quantity': 50, 'avg_price': 480.00, 'current_price': 512.30, 'unrealized_pnl': 1615.00, 'unrealized_pnl_percent': 6.73, 'is_simulation': True, 'created_at': '2026-05-15T10:00:00', 'updated_at': '2026-06-08T12:00:00'},
        {'id': 2, 'user_id': 1, 'symbol': 'AAPL', 'quantity': 100, 'avg_price': 182.00, 'current_price': 188.50, 'unrealized_pnl': 650.00, 'unrealized_pnl_percent': 3.57, 'is_simulation': True, 'created_at': '2026-05-20T14:30:00', 'updated_at': '2026-06-08T12:00:00'},
        {'id': 3, 'user_id': 1, 'symbol': 'BTC', 'quantity': 0.5, 'avg_price': 65000.00, 'current_price': 69800.00, 'unrealized_pnl': 2400.00, 'unrealized_pnl_percent': 7.38, 'is_simulation': True, 'created_at': '2026-04-10T09:00:00', 'updated_at': '2026-06-08T12:00:00'},
        {'id': 4, 'user_id': 1, 'symbol': 'TSLA', 'quantity': 30, 'avg_price': 250.00, 'current_price': 245.00, 'unrealized_pnl': -150.00, 'unrealized_pnl_percent': -2.00, 'is_simulation': True, 'created_at': '2026-05-25T11:00:00', 'updated_at': '2026-06-08T12:00:00'},
        {'id': 5, 'user_id': 1, 'symbol': 'ETH', 'quantity': 3, 'avg_price': 3200.00, 'current_price': 3510.00, 'unrealized_pnl': 930.00, 'unrealized_pnl_percent': 9.69, 'is_simulation': True, 'created_at': '2026-05-18T16:00:00', 'updated_at': '2026-06-08T12:00:00'},
    ],
    'recent_trades': [
        {'id': 101, 'user_id': 1, 'symbol': 'NVDA', 'side': 'buy', 'quantity': 10, 'price': 505.00, 'pnl': None, 'pnl_percent': None, 'is_simulation': True, 'created_at': '2026-06-07T14:30:00'},
        {'id': 100, 'user_id': 1, 'symbol': 'AAPL', 'side': 'sell', 'quantity': 20, 'price': 189.00, 'pnl': 140.00, 'pnl_percent': 3.85, 'is_simulation': True, 'created_at': '2026-06-07T10:00:00'},
        {'id': 99, 'user_id': 1, 'symbol': 'BTC', 'side': 'buy', 'quantity': 0.1, 'price': 69200.00, 'pnl': None, 'pnl_percent': None, 'is_simulation': True, 'created_at': '2026-06-06T22:00:00'},
        {'id': 98, 'user_id': 1, 'symbol': 'TSLA', 'side': 'buy', 'quantity': 30, 'price': 248.00, 'pnl': None, 'pnl_percent': None, 'is_simulation': True, 'created_at': '2026-06-06T15:00:00'},
        {'id': 97, 'user_id': 1, 'symbol': 'ETH', 'side': 'sell', 'quantity': 1, 'price': 3480.00, 'pnl': 280.00, 'pnl_percent': 8.75, 'is_simulation': True, 'created_at': '2026-06-06T09:30:00'},
    ]
}

MOCK_ORDERS = [
    {'id': 201, 'user_id': 1, 'symbol': 'NVDA', 'side': 'buy', 'type': 'market', 'quantity': 10, 'price': None, 'filled_price': 505.00, 'filled_quantity': 10, 'status': 'filled', 'is_simulation': True, 'created_at': '2026-06-07T14:30:00', 'updated_at': '2026-06-07T14:30:05'},
    {'id': 200, 'user_id': 1, 'symbol': 'BTC', 'side': 'buy', 'type': 'limit', 'quantity': 0.1, 'price': 69000.00, 'filled_price': None, 'filled_quantity': 0, 'status': 'pending', 'is_simulation': True, 'created_at': '2026-06-08T08:00:00', 'updated_at': '2026-06-08T08:00:00'},
    {'id': 199, 'user_id': 1, 'symbol': 'ETH', 'side': 'sell', 'type': 'market', 'quantity': 1, 'price': None, 'filled_price': 3480.00, 'filled_quantity': 1, 'status': 'filled', 'is_simulation': True, 'created_at': '2026-06-06T09:30:00', 'updated_at': '2026-06-06T09:30:02'},
    {'id': 198, 'user_id': 1, 'symbol': 'AAPL', 'side': 'sell', 'type': 'limit', 'quantity': 20, 'price': 190.00, 'filled_price': 189.00, 'filled_quantity': 20, 'status': 'filled', 'is_simulation': True, 'created_at': '2026-06-05T10:00:00', 'updated_at': '2026-06-05T14:30:00'},
    {'id': 197, 'user_id': 1, 'symbol': 'TSLA', 'side': 'buy', 'type': 'stop', 'quantity': 30, 'price': 245.00, 'filled_price': None, 'filled_quantity': 0, 'status': 'pending', 'is_simulation': True, 'created_at': '2026-06-05T09:00:00', 'updated_at': '2026-06-05T09:00:00'},
]

MOCK_MARKET_PRICES = {
    'BTC': 69800.00,
    'ETH': 3510.00,
    'SOL': 145.20,
    'BNB': 580.00,
    'XRP': 0.52,
    'AAPL': 188.50,
    'GOOGL': 175.30,
    'MSFT': 420.10,
    'AMZN': 185.80,
    'TSLA': 245.00,
    'NVDA': 512.30,
    'SPY': 540.20,
    'QQQ': 468.50,
}


@app.get('/api/trading/portfolio')
async def get_portfolio(is_simulation: bool = True):
    return {'success': True, 'data': MOCK_PORTFOLIO}


@app.get('/api/trading/positions')
async def get_positions(is_simulation: bool = True):
    return {'success': True, 'data': MOCK_PORTFOLIO['positions']}


@app.get('/api/trading/trades')
async def get_trades(is_simulation: bool = True, page: int = 1, per_page: int = 20):
    trades = MOCK_PORTFOLIO['recent_trades']
    return {
        'success': True,
        'data': {
            'items': trades,
            'total': len(trades),
            'page': page,
            'per_page': per_page
        }
    }


@app.get('/api/trading/orders')
async def get_orders(status: str = '', symbol: str = '', is_simulation: bool = True):
    orders = MOCK_ORDERS
    if status:
        orders = [o for o in orders if o['status'] == status]
    if symbol:
        orders = [o for o in orders if o['symbol'] == symbol]
    return {
        'success': True,
        'data': {
            'items': orders,
            'total': len(orders),
            'page': 1,
            'per_page': 20
        }
    }


@app.get('/api/trading/orders/{order_id}')
async def get_order_detail(order_id: int):
    for o in MOCK_ORDERS:
        if o['id'] == order_id:
            return {'success': True, 'data': o}
    raise HTTPException(status_code=404, detail='订单不存在')


@app.post('/api/trading/orders')
async def create_order(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}
    order_id = max(o['id'] for o in MOCK_ORDERS) + 1
    new_order = {
        'id': order_id,
        'user_id': 1,
        'symbol': body.get('symbol', 'BTC'),
        'side': body.get('side', 'buy'),
        'type': body.get('type', 'market'),
        'quantity': body.get('quantity', 0),
        'price': body.get('price'),
        'filled_price': body.get('price') if body.get('type') == 'market' else None,
        'filled_quantity': body.get('quantity') if body.get('type') == 'market' else 0,
        'status': 'filled' if body.get('type') == 'market' else 'pending',
        'is_simulation': body.get('is_simulation', True),
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    MOCK_ORDERS.insert(0, new_order)
    return {'success': True, 'data': new_order}


@app.post('/api/trading/orders/{order_id}/cancel')
async def cancel_order(order_id: int):
    for o in MOCK_ORDERS:
        if o['id'] == order_id:
            o['status'] = 'cancelled'
            return {'success': True, 'data': o}
    return {'success': True}


@app.get('/api/trading/exchange-accounts')
async def get_exchange_accounts():
    return {
        'success': True,
        'data': [
            {'id': 1, 'user_id': 1, 'exchange': 'binance', 'name': '币安模拟账户', 'is_sandbox': True, 'is_active': True, 'created_at': '2026-01-01T00:00:00'},
            {'id': 2, 'user_id': 1, 'exchange': 'alpaca', 'name': 'Alpaca美股', 'is_sandbox': True, 'is_active': True, 'created_at': '2026-01-15T00:00:00'},
        ]
    }


@app.post('/api/trading/exchange-accounts')
async def add_exchange_account(request: Request):
    return {'success': True, 'data': {'id': 3, 'user_id': 1, 'exchange': 'binance', 'name': '新账户', 'is_sandbox': True, 'is_active': True, 'created_at': datetime.now().isoformat()}}


@app.delete('/api/trading/exchange-accounts/{account_id}')
async def delete_exchange_account(account_id: int):
    return {'success': True, 'message': '账户已删除'}


@app.get('/api/trading/market/price/{symbol}')
async def get_market_price(symbol: str):
    price = MOCK_MARKET_PRICES.get(symbol.upper())
    if price:
        return {'success': True, 'data': {'symbol': symbol.upper(), 'price': price}}
    return {'success': True, 'data': {'symbol': symbol.upper(), 'price': _random.uniform(10, 1000)}}


@app.get('/api/trading/market/prices')
async def get_all_market_prices():
    return {'success': True, 'data': MOCK_MARKET_PRICES}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8001)
