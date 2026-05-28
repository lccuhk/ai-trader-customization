"""
Flask Backend Server

Flask 版本的后端服务，兼容性更好，支持所有 Python 版本
"""

import sqlite3
import json
import hashlib
import secrets
import os
import re
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, request, jsonify

app = Flask(__name__)

ALLOWED_ORIGINS = [
    'http://localhost:8080',
    'http://localhost:3000',
    'https://trading-agent-for-dscourse.surge.sh',
    'https://trading-agent-backend.deta.app',
    'https://trading-agent-for-dscourse-backend.onrender.com',
]

def cors_allowed(origin):
    if origin in ALLOWED_ORIGINS:
        return True
    if re.match(r'^https://.*\.deta\.app$', origin):
        return True
    if re.match(r'^https://.*\.deta\.dev$', origin):
        return True
    if re.match(r'^https://.*\.onrender\.com$', origin):
        return True
    return False

@app.after_request
def after_request(response):
    if request.method == 'OPTIONS':
        response.status_code = 200
    origin = request.headers.get('Origin', '')
    if cors_allowed(origin):
        response.headers.add('Access-Control-Allow-Origin', origin)
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'clawtrader.db')


def _hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def _generate_token():
    return secrets.token_hex(32)


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                display_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                total_trades INTEGER DEFAULT 0,
                winning_trades INTEGER DEFAULT 0,
                losing_trades INTEGER DEFAULT 0,
                total_pnl REAL DEFAULT 0,
                win_rate REAL DEFAULT 0,
                sharpe_ratio REAL DEFAULT 0,
                max_drawdown REAL DEFAULT 0,
                avg_win REAL DEFAULT 0,
                avg_loss REAL DEFAULT 0,
                profit_factor REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                message TEXT,
                notification_type TEXT,
                priority TEXT DEFAULT 'normal',
                is_read INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS strategies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                strategy_type TEXT,
                code TEXT,
                parameters TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                source TEXT,
                category TEXT,
                symbol TEXT,
                impact_score INTEGER,
                sentiment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                date TEXT,
                importance TEXT,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS economic_indicators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                value REAL,
                period TEXT,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS strategy_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS webhooks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT NOT NULL,
                events TEXT,
                active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                smtp_host TEXT,
                smtp_port INTEGER,
                smtp_user TEXT,
                smtp_password TEXT,
                from_email TEXT,
                enabled INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notification_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                email_enabled INTEGER DEFAULT 1,
                push_enabled INTEGER DEFAULT 1,
                price_alerts INTEGER DEFAULT 1,
                signal_alerts INTEGER DEFAULT 1,
                risk_alerts INTEGER DEFAULT 1,
                system_alerts INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS auth_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                agent_name TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT,
                message_type TEXT DEFAULT 'operation',
                market TEXT DEFAULT 'us-stock',
                symbols TEXT,
                quality_score REAL DEFAULT 0,
                reply_count INTEGER DEFAULT 0,
                participant_count INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        
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
        
        cursor.execute('SELECT COUNT(*) FROM signals')
        if cursor.fetchone()[0] == 0:
            sample_signals = [
                (1, '量化先锋', 'NVDA 突破买入信号', 'NVDA 已突破 500 美元关键阻力位，成交量放大，MACD 金叉，建议买入，目标价 550 美元，止损 480 美元。', 'operation', 'us-stock', '["NVDA"]', 85.5, 12, 24),
                (1, '趋势追踪者', 'AAPL 短期回调机会', 'AAPL 近期回调至 180 美元支撑位，RSI 处于超卖区域，可考虑逢低布局，长期看好 AI 服务增长。', 'analysis', 'us-stock', '["AAPL"]', 78.2, 8, 15),
                (1, '加密猎人', 'BTC 减半行情分析', '比特币第四次减半即将到来，历史数据显示减半后 12-18 个月通常有大幅上涨，建议分批建仓，控制仓位。', 'analysis', 'crypto', '["BTC","ETH"]', 92.0, 25, 45),
                (1, '期权大师', 'SPY 跨式期权策略', '当前市场波动率处于低位，建议构建 SPY 跨式期权组合，赌未来 1 个月内有大波动。', 'operation', 'us-stock', '["SPY"]', 71.8, 5, 10),
                (1, '宏观分析师', '美联储利率决议前瞻', '预计美联储将维持利率不变，但可能释放降息信号，建议关注鲍威尔讲话措辞，市场可能出现波动。', 'analysis', 'us-stock', '["SPY","QQQ"]', 88.3, 18, 32),
                (1, '短线交易员', 'TSLA 日内交易机会', 'TSLA 盘前波动较大，建议关注 240-250 美元区间突破，设置严格止损。', 'operation', 'us-stock', '["TSLA"]', 65.0, 3, 8),
                (1, '价值投资者', '巴菲特最新持仓分析', '巴菲特近期增持了日本商社和能源股，减持了苹果，值得关注其投资逻辑变化。', 'discussion', 'us-stock', '["AAPL","XOM"]', 82.4, 15, 28),
                (1, 'AI 研究员', 'AI 芯片赛道分析', 'AI 芯片需求爆发，NVDA、AMD、AVGO 都值得关注，但需注意估值和竞争风险。', 'analysis', 'us-stock', '["NVDA","AMD","AVGO"]', 90.1, 22, 41),
            ]
            cursor.executemany('''
                INSERT INTO signals (user_id, agent_name, title, content, message_type, market, symbols, quality_score, reply_count, participant_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', sample_signals)
        
        conn.commit()
    except Exception as e:
        conn.rollback()
    finally:
        conn.close()


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def row_to_dict(row):
    if row is None:
        return None
    return dict(row)


def rows_to_dict_list(rows):
    return [dict(row) for row in rows]


def get_current_user_id():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.replace('Bearer ', '').strip()
    if not token:
        return None
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM auth_tokens WHERE token = ?', (token,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return row['user_id']
    return None


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({'success': False, 'message': '未授权，请先登录'}), 401
        request.current_user_id = user_id
        return f(*args, **kwargs)
    return decorated


@app.route('/')
def root():
    return jsonify({
        'message': 'AI-Trader API',
        'version': '1.0.0',
        'docs': '/api/docs'
    })


@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})


@app.route('/api/docs')
def docs():
    return '''
    <h1>AI-Trader API Documentation</h1>
    <h2>Available Endpoints:</h2>
    <ul>
        <li>GET /api/health - Health check</li>
        <li>POST /api/auth/login - Login</li>
        <li>POST /api/auth/register - Register</li>
        <li>GET /api/ai/agents - List AI agents</li>
        <li>POST /api/ai/chat - Chat with AI</li>
        <li>GET /api/risk/dashboard - Risk dashboard</li>
        <li>GET /api/market/dashboard - Market dashboard</li>
        <li>GET /api/strategies - List strategies</li>
        <li>GET /api/notifications - List notifications</li>
        <li>GET /api/users/me - Get current user</li>
    </ul>
    '''


@app.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    data = request.get_json()
    message = data.get('message', '')
    agent_id = data.get('agent_id', 'market-analyst')
    
    agent_responses = {
        'market-analyst': f'作为市场分析师，我分析了你的问题："{message}"。\n\n当前市场趋势显示主要指数处于震荡整理阶段。建议关注关键支撑位和阻力位的突破情况。',
        'trading-coach': f'作为交易教练，我理解你的困惑："{message}"。\n\n记住，成功的交易需要纪律和耐心。建议你先回顾交易计划，确保风险控制在可接受范围内。',
        'portfolio-manager': f'作为投资组合经理，我分析了你的问题："{message}"。\n\n当前投资组合配置建议：60% 股票、30% 债券、10% 现金。建议定期再平衡以控制风险。',
        'quant-researcher': f'作为量化研究员，我分析了你的问题："{message}"。\n\n从量化角度看，当前市场波动率处于历史低位，建议使用多因子模型进行选股，关注动量和质量因子。'
    }
    
    response = agent_responses.get(agent_id, agent_responses['market-analyst'])
    
    return jsonify({
        'success': True,
        'response': response,
        'agent_id': agent_id,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/ai/conversations')
def ai_conversations():
    return jsonify({
        'success': True,
        'conversations': [
            {'id': 1, 'title': '市场趋势分析', 'agent_id': 'market-analyst', 'last_message': '当前市场趋势如何？', 'created_at': '2024-01-15T10:30:00'},
            {'id': 2, 'title': '交易心理辅导', 'agent_id': 'trading-coach', 'last_message': '如何控制贪婪情绪？', 'created_at': '2024-01-14T15:20:00'},
        ]
    })


@app.route('/api/ai/conversations/<int:conv_id>')
def ai_conversation(conv_id):
    return jsonify({
        'success': True,
        'conversation': {
            'id': conv_id,
            'title': '市场趋势分析',
            'agent_id': 'market-analyst',
            'messages': [
                {'role': 'user', 'content': '当前市场趋势如何？', 'timestamp': '2024-01-15T10:30:00'},
                {'role': 'assistant', 'content': '当前市场处于上升趋势中，建议关注科技板块。', 'timestamp': '2024-01-15T10:30:05'},
            ]
        }
    })


@app.route('/api/ai/agents')
def ai_agents():
    return jsonify({
        'success': True,
        'agents': [
            {'id': 'market-analyst', 'name': '市场分析师', 'icon': '📊', 'description': '分析市场趋势、技术指标和宏观经济'},
            {'id': 'trading-coach', 'name': '交易教练', 'icon': '🎯', 'description': '提供交易心理指导和纪律训练'},
            {'id': 'portfolio-manager', 'name': '投资组合经理', 'icon': '💼', 'description': '优化资产配置和风险管理'},
            {'id': 'quant-researcher', 'name': '量化研究员', 'icon': '🔬', 'description': '量化策略分析和回测建议'},
        ]
    })


@app.route('/api/risk/dashboard')
def risk_dashboard():
    return jsonify({
        'success': True,
        'metrics': {
            'concentration_risk': 25.5,
            'net_exposure': 65.2,
            'max_drawdown': -12.3,
            'win_rate': 65.4,
            'sharpe_ratio': 1.85,
            'var_95': -5.2,
            'total_positions': 12,
            'total_value': 125000.00
        }
    })


@app.route('/api/risk/settings')
def risk_settings():
    return jsonify({
        'success': True,
        'settings': {
            'max_position_size': 10.0,
            'max_daily_loss': 5.0,
            'max_portfolio_risk': 15.0,
            'default_stop_loss': 2.0,
            'default_take_profit': 4.0,
            'risk_per_trade': 1.0
        }
    })


@app.route('/api/risk/alerts')
def risk_alerts():
    return jsonify({
        'success': True,
        'alerts': [
            {'id': 1, 'type': 'concentration', 'message': 'NVDA 仓位超过 15% 阈值', 'severity': 'high', 'created_at': '2024-01-15T09:00:00'},
            {'id': 2, 'type': 'drawdown', 'message': '账户回撤达到 8%', 'severity': 'medium', 'created_at': '2024-01-14T14:30:00'},
        ]
    })


@app.route('/api/risk/calculate-position-size', methods=['POST'])
def calculate_position_size():
    data = request.get_json()
    account_size = float(data.get('account_size', 0))
    risk_percent = float(data.get('risk_percent', 1))
    entry_price = float(data.get('entry_price', 0))
    stop_loss = float(data.get('stop_loss', 0))
    
    if entry_price > 0 and stop_loss > 0 and entry_price != stop_loss:
        risk_amount = account_size * (risk_percent / 100)
        price_risk = abs(entry_price - stop_loss)
        shares = int(risk_amount / price_risk)
        position_value = shares * entry_price
        position_percent = (position_value / account_size) * 100
    else:
        shares = 0
        position_value = 0
        position_percent = 0
    
    return jsonify({
        'success': True,
        'result': {
            'shares': shares,
            'position_value': round(position_value, 2),
            'position_percent': round(position_percent, 2),
            'risk_amount': round(account_size * (risk_percent / 100), 2)
        }
    })


@app.route('/api/market/dashboard')
def market_dashboard():
    return jsonify({
        'success': True,
        'dashboard': {
            'market_sentiment': 65.5,
            'fear_greed_index': 58,
            'vix': 15.2,
            'sp500_change': 0.85,
            'nasdaq_change': 1.23,
            'dow_change': 0.45,
            'top_gainers': [
                {'symbol': 'NVDA', 'change': 5.2, 'price': 485.50},
                {'symbol': 'TSLA', 'change': 3.8, 'price': 245.30},
            ],
            'top_losers': [
                {'symbol': 'AAPL', 'change': -1.5, 'price': 185.20},
                {'symbol': 'MSFT', 'change': -0.8, 'price': 378.90},
            ]
        }
    })


@app.route('/api/market/news')
def market_news():
    limit = int(request.args.get('limit', 10))
    category = request.args.get('category', '')
    
    conn = get_db()
    cursor = conn.cursor()
    
    query = 'SELECT * FROM market_news'
    params = []
    if category:
        query += ' WHERE category = ?'
        params.append(category)
    query += ' ORDER BY created_at DESC LIMIT ?'
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return jsonify({
        'success': True,
        'news': rows_to_dict_list(rows)
    })


@app.route('/api/market/news/<int:news_id>')
def market_news_detail(news_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM market_news WHERE id = ?', (news_id,))
    row = cursor.fetchone()
    conn.close()
    
    return jsonify({
        'success': True,
        'news': row_to_dict(row)
    })


@app.route('/api/market/events')
def market_events():
    limit = int(request.args.get('limit', 10))
    return jsonify({
        'success': True,
        'events': [
            {'id': 1, 'title': '美联储利率决议', 'date': '2024-01-31', 'importance': 'high', 'category': 'economic'},
            {'id': 2, 'title': '苹果财报', 'date': '2024-02-01', 'importance': 'medium', 'category': 'earnings'},
        ]
    })


@app.route('/api/market/indicators')
def market_indicators():
    limit = int(request.args.get('limit', 10))
    return jsonify({
        'success': True,
        'indicators': [
            {'id': 1, 'name': 'GDP增长率', 'value': 2.5, 'period': 'Q4 2023', 'category': 'macro'},
            {'id': 2, 'name': '失业率', 'value': 3.7, 'period': 'Dec 2023', 'category': 'macro'},
            {'id': 3, 'name': 'CPI通胀率', 'value': 3.4, 'period': 'Dec 2023', 'category': 'macro'},
        ]
    })


@app.route('/api/signals/feed')
def signals_feed():
    limit = int(request.args.get('limit', 20))
    message_type = request.args.get('message_type', '')
    market = request.args.get('market', '')
    
    conn = get_db()
    cursor = conn.cursor()
    
    query = 'SELECT * FROM signals'
    params = []
    conditions = []
    
    if message_type:
        conditions.append('message_type = ?')
        params.append(message_type)
    
    if market:
        conditions.append('market = ?')
        params.append(market)
    
    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)
    
    query += ' ORDER BY created_at DESC LIMIT ?'
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    signals = []
    for row in rows:
        signal = dict(row)
        try:
            signal['symbols'] = json.loads(signal['symbols']) if signal['symbols'] else []
        except:
            signal['symbols'] = []
        signals.append(signal)
    
    return jsonify({
        'success': True,
        'signals': signals
    })


@app.route('/api/signals/<int:signal_id>')
def signal_detail(signal_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM signals WHERE id = ?', (signal_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        signal = dict(row)
        try:
            signal['symbols'] = json.loads(signal['symbols']) if signal['symbols'] else []
        except:
            signal['symbols'] = []
        return jsonify({
            'success': True,
            'signal': signal
        })
    else:
        return jsonify({
            'success': False,
            'message': '信号不存在'
        }), 404


@app.route('/api/leaderboard/position-pnl')
def leaderboard_position_pnl():
    limit = int(request.args.get('limit', 20))
    
    top_agents = [
        {'id': 1, 'name': '量化先锋', 'position_pnl': 12580.50, 'trade_count': 156, 'position_count': 23},
        {'id': 2, 'name': '趋势追踪者', 'position_pnl': 8920.30, 'trade_count': 89, 'position_count': 15},
        {'id': 3, 'name': '价值投资者', 'position_pnl': 6750.80, 'trade_count': 45, 'position_count': 8},
        {'id': 4, 'name': 'AI 研究员', 'position_pnl': 5420.00, 'trade_count': 78, 'position_count': 12},
        {'id': 5, 'name': '短线交易员', 'position_pnl': 3210.50, 'trade_count': 234, 'position_count': 45},
        {'id': 6, 'name': '宏观分析师', 'position_pnl': 2180.20, 'trade_count': 34, 'position_count': 6},
        {'id': 7, 'name': '加密猎人', 'position_pnl': -1250.80, 'trade_count': 67, 'position_count': 18},
        {'id': 8, 'name': '期权大师', 'position_pnl': -2890.40, 'trade_count': 112, 'position_count': 28},
    ]
    
    if limit < len(top_agents):
        top_agents = top_agents[:limit]
    
    return jsonify({
        'success': True,
        'top_agents': top_agents
    })


@app.route('/api/strategies')
def strategies():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM strategies ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    
    return jsonify({
        'success': True,
        'strategies': rows_to_dict_list(rows)
    })


@app.route('/api/strategies/<int:strategy_id>')
def strategy_detail(strategy_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM strategies WHERE id = ?', (strategy_id,))
    row = cursor.fetchone()
    conn.close()
    
    return jsonify({
        'success': True,
        'strategy': row_to_dict(row)
    })


@app.route('/api/strategies', methods=['POST'])
def create_strategy():
    data = request.get_json()
    name = data.get('name', '')
    description = data.get('description', '')
    strategy_type = data.get('strategy_type', 'custom')
    code = data.get('code', '')
    parameters = json.dumps(data.get('parameters', {}))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO strategies (name, description, strategy_type, code, parameters, is_active)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, description, strategy_type, code, parameters, 1))
    conn.commit()
    strategy_id = cursor.lastrowid
    conn.close()
    
    return jsonify({
        'success': True,
        'strategy_id': strategy_id,
        'message': '策略创建成功'
    })


@app.route('/api/strategies/backtest', methods=['POST'])
def backtest_strategy():
    data = request.get_json()
    strategy_id = data.get('strategy_id', 0)
    
    return jsonify({
        'success': True,
        'backtest': {
            'total_return': 25.5,
            'annualized_return': 15.2,
            'max_drawdown': -8.3,
            'sharpe_ratio': 1.65,
            'win_rate': 62.3,
            'total_trades': 156,
            'equity_curve': [100, 105, 103, 110, 115, 112, 120, 125, 122, 125]
        }
    })


@app.route('/api/strategies/templates')
def strategy_templates():
    return jsonify({
        'success': True,
        'templates': [
            {'id': 1, 'name': '移动平均线交叉', 'description': '基于 MA 交叉的趋势跟踪策略', 'category': 'trend_following'},
            {'id': 2, 'name': 'RSI 超买超卖', 'description': '基于 RSI 指标的均值回归策略', 'category': 'mean_reversion'},
            {'id': 3, 'name': '布林带突破', 'description': '基于布林带的波动率突破策略', 'category': 'volatility'},
        ]
    })


@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')
    
    password_hash = _hash_password(password)
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, email, username, display_name FROM users 
        WHERE email = ? AND password_hash = ?
    ''', (username, password_hash))
    row = cursor.fetchone()
    
    if row:
        token = _generate_token()
        expires_at = (datetime.now() + timedelta(days=30)).isoformat()
        
        cursor.execute('''
            INSERT INTO auth_tokens (user_id, token, expires_at)
            VALUES (?, ?, ?)
        ''', (row['id'], token, expires_at))
        conn.commit()
        
        user_username = row['username'] or row['email'].split('@')[0]
        user_display_name = row['display_name'] or user_username
        
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'id': row['id'],
                'username': user_username,
                'email': row['email'],
                'display_name': user_display_name
            }
        })
    else:
        return jsonify({
            'success': False,
            'message': '用户名或密码错误'
        }), 401


@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '')
    email = data.get('email', '')
    password = data.get('password', '')
    
    if not username or not email or not password:
        return jsonify({
            'success': False,
            'message': '请填写所有必填字段'
        }), 400
    
    password_hash = _hash_password(password)
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            return jsonify({
                'success': False,
                'message': '邮箱已被注册'
            }), 400
        
        cursor.execute('''
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
        ''', (username, email, password_hash))
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': '注册成功'
        })
    except Exception as e:
        conn.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
    finally:
        conn.close()


@app.route('/api/users/me')
@require_auth
def get_current_user():
    user_id = request.current_user_id
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, username, email, display_name, created_at 
        FROM users WHERE id = ?
    ''', (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        user_username = row['username'] or row['email'].split('@')[0]
        user_display_name = row['display_name'] or user_username
        
        return jsonify({
            'success': True,
            'user': {
                'id': row['id'],
                'username': user_username,
                'email': row['email'],
                'display_name': user_display_name,
                'created_at': row['created_at']
            }
        })
    else:
        return jsonify({
            'success': False,
            'message': '用户不存在'
        }), 404


@app.route('/api/users/me/stats')
def get_user_stats():
    return jsonify({
        'success': True,
        'stats': {
            'total_trades': 156,
            'winning_trades': 102,
            'losing_trades': 54,
            'total_pnl': 25430.50,
            'win_rate': 65.4,
            'sharpe_ratio': 1.85,
            'max_drawdown': -12.3,
            'avg_win': 450.25,
            'avg_loss': -380.50,
            'profit_factor': 1.85
        }
    })


@app.route('/api/users/me/preferences')
def get_user_preferences():
    return jsonify({
        'success': True,
        'preferences': {
            'theme': 'dark',
            'language': 'zh-CN',
            'notifications_enabled': True,
            'email_notifications': True,
            'risk_warnings': True
        }
    })


@app.route('/api/notifications')
def get_notifications():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM notifications ORDER BY created_at DESC LIMIT 20')
    rows = cursor.fetchall()
    conn.close()
    
    return jsonify({
        'success': True,
        'notifications': rows_to_dict_list(rows)
    })


@app.route('/api/notifications/<int:notification_id>/read', methods=['PUT'])
def mark_notification_read(notification_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE notifications SET is_read = 1 WHERE id = ?', (notification_id,))
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'message': '通知已标记为已读'
    })


@app.route('/api/notifications/read-all', methods=['PUT'])
def mark_all_notifications_read():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE notifications SET is_read = 1 WHERE user_id = 1')
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'message': '所有通知已标记为已读'
    })


@app.route('/api/notifications/settings')
def get_notification_settings():
    return jsonify({
        'success': True,
        'settings': {
            'email_enabled': True,
            'push_enabled': True,
            'price_alerts': True,
            'signal_alerts': True,
            'risk_alerts': True,
            'system_alerts': True
        }
    })


@app.route('/api/webhooks')
def get_webhooks():
    return jsonify({
        'success': True,
        'webhooks': [
            {'id': 1, 'name': '交易信号 Webhook', 'url': 'https://example.com/webhook/signals', 'events': ['new_signal'], 'active': True},
            {'id': 2, 'name': '风险预警 Webhook', 'url': 'https://example.com/webhook/risk', 'events': ['risk_alert'], 'active': True},
        ]
    })


@app.route('/api/email/config')
def get_email_config():
    return jsonify({
        'success': True,
        'config': {
            'smtp_host': 'smtp.example.com',
            'smtp_port': 587,
            'smtp_user': 'user@example.com',
            'from_email': 'noreply@trading-agent.com',
            'enabled': True
        }
    })


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8001)), debug=False)
