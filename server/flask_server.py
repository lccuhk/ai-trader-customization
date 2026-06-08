"""
Flask Backend Server

Flask 版本的后端服务，兼容性更好，支持所有 Python 版本
"""

import json
import hashlib
import secrets
import os
import re
import time
import random
import traceback
import sys
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, request, jsonify
from sqlalchemy import text, func, and_
from sqlalchemy.orm import joinedload

from database import SessionLocal, get_db_session, init_db as orm_init_db
from models import (
    User, AuthToken, Signal, SignalReply, SignalParticipant,
    SignalQualityScore, Notification, NotificationSetting, Strategy,
    StrategyTemplate, UserStats, MarketNews, MarketEvent,
    EconomicIndicator, EmailConfig, Webhook
)

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

def _hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def _generate_token():
    return secrets.token_hex(32)


def model_to_dict(model):
    if model is None:
        return None
    result = {}
    for column in model.__table__.columns:
        value = getattr(model, column.name)
        if isinstance(value, datetime):
            result[column.name] = value.isoformat()
        else:
            result[column.name] = value
    return result


def models_to_dict_list(models):
    return [model_to_dict(m) for m in models]


def execute_db_with_retry(operation, max_retries=20, base_delay=0.2):
    last_error = None
    
    for attempt in range(max_retries):
        try:
            return operation()
        except Exception as e:
            error_msg = str(e).lower()
            if 'locked' in error_msg or 'busy' in error_msg or 'deadlock' in error_msg:
                last_error = e
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt) + random.uniform(0, base_delay)
                    delay = min(delay, 8.0)
                    print(f"[WARN] 数据库繁忙，第 {attempt + 1}/{max_retries} 次重试，等待 {delay:.2f}s: {e}", file=sys.stderr)
                    time.sleep(delay)
                    continue
            print(f"[ERROR] 数据库操作失败: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            raise
    print(f"[ERROR] 重试 {max_retries} 次后仍然失败: {last_error}", file=sys.stderr)
    raise last_error


def init_db():
    orm_init_db()
    
    db = get_db_session()
    try:
        if db.query(User).filter(User.email == 'demo@example.com').count() == 0:
            demo_user = User(
                email='demo@example.com',
                password_hash=_hash_password('demo123')
            )
            db.add(demo_user)
            db.flush()
            
            if db.query(UserStats).filter(UserStats.user_id == demo_user.id).count() == 0:
                demo_stats = UserStats(
                    user_id=demo_user.id,
                    total_trades=156,
                    winning_trades=102,
                    total_pnl=25430.50,
                    win_rate=0.654,
                    sharpe_ratio=1.85
                )
                db.add(demo_stats)
        
        if db.query(Notification).count() == 0:
            sample_notifications = [
                Notification(user_id=1, title='NVDA 价格预警', message='NVDA 价格已突破 $500 阻力位', notification_type='price_alert', priority='high'),
                Notification(user_id=1, title='新交易信号', message='检测到 AAPL 买入信号，强度 85%', notification_type='signal', priority='normal'),
                Notification(user_id=1, title='风险预警', message='您的投资组合集中度超过 30% 阈值', notification_type='risk', priority='high'),
                Notification(user_id=1, title='系统更新', message='系统已完成例行维护', notification_type='system', priority='low'),
            ]
            db.add_all(sample_notifications)
        
        if db.query(Strategy).count() == 0:
            sample_strategies = [
                Strategy(name='移动平均线交叉策略', description='基于短期和长期移动平均线的交叉信号', strategy_type='trend_following', code='# 策略代码', parameters={}, is_active=True),
                Strategy(name='RSI超买超卖策略', description='使用RSI指标识别超买超卖区域', strategy_type='mean_reversion', code='# 策略代码', parameters={}, is_active=True),
                Strategy(name='布林带突破策略', description='基于布林带的突破信号', strategy_type='volatility', code='# 策略代码', parameters={}, is_active=False),
            ]
            db.add_all(sample_strategies)
        
        if db.query(MarketNews).count() == 0:
            sample_news = [
                MarketNews(title='美联储暗示可能在年内降息', content='美联储主席鲍威尔暗示可能降息', source='Reuters', category='macro', symbol='SPY', impact_score=85, sentiment='bullish'),
                MarketNews(title='英伟达发布新一代AI芯片', content='性能提升3倍', source='TechCrunch', category='earnings', symbol='NVDA', impact_score=90, sentiment='bullish'),
                MarketNews(title='苹果Vision Pro销量不及预期', content='影响供应链企业', source='Bloomberg', category='earnings', symbol='AAPL', impact_score=60, sentiment='bearish'),
            ]
            db.add_all(sample_news)
        
        if db.query(Signal).count() == 0:
            sample_signals = [
                Signal(user_id=1, agent_name='量化先锋', title='NVDA 突破买入信号', content='NVDA 已突破 500 美元关键阻力位，成交量放大，MACD 金叉，建议买入，目标价 550 美元，止损 480 美元。', message_type='operation', market='us-stock', symbols=['NVDA'], quality_score=85.5, reply_count=12, participant_count=24),
                Signal(user_id=1, agent_name='趋势追踪者', title='AAPL 短期回调机会', content='AAPL 近期回调至 180 美元支撑位，RSI 处于超卖区域，可考虑逢低布局，长期看好 AI 服务增长。', message_type='analysis', market='us-stock', symbols=['AAPL'], quality_score=78.2, reply_count=8, participant_count=15),
                Signal(user_id=1, agent_name='加密猎人', title='BTC 减半行情分析', content='比特币第四次减半即将到来，历史数据显示减半后 12-18 个月通常有大幅上涨，建议分批建仓，控制仓位。', message_type='analysis', market='crypto', symbols=['BTC','ETH'], quality_score=92.0, reply_count=25, participant_count=45),
                Signal(user_id=1, agent_name='期权大师', title='SPY 跨式期权策略', content='当前市场波动率处于低位，建议构建 SPY 跨式期权组合，赌未来 1 个月内有大波动。', message_type='operation', market='us-stock', symbols=['SPY'], quality_score=71.8, reply_count=5, participant_count=10),
                Signal(user_id=1, agent_name='宏观分析师', title='美联储利率决议前瞻', content='预计美联储将维持利率不变，但可能释放降息信号，建议关注鲍威尔讲话措辞，市场可能出现波动。', message_type='analysis', market='us-stock', symbols=['SPY','QQQ'], quality_score=88.3, reply_count=18, participant_count=32),
                Signal(user_id=1, agent_name='短线交易员', title='TSLA 日内交易机会', content='TSLA 盘前波动较大，建议关注 240-250 美元区间突破，设置严格止损。', message_type='operation', market='us-stock', symbols=['TSLA'], quality_score=65.0, reply_count=3, participant_count=8),
                Signal(user_id=1, agent_name='价值投资者', title='巴菲特最新持仓分析', content='巴菲特近期增持了日本商社和能源股，减持了苹果，值得关注其投资逻辑变化。', message_type='discussion', market='us-stock', symbols=['AAPL','XOM'], quality_score=82.4, reply_count=15, participant_count=28),
                Signal(user_id=1, agent_name='AI 研究员', title='AI 芯片赛道分析', content='AI 芯片需求爆发，NVDA、AMD、AVGO 都值得关注，但需注意估值和竞争风险。', message_type='analysis', market='us-stock', symbols=['NVDA','AMD','AVGO'], quality_score=90.1, reply_count=22, participant_count=41),
                Signal(user_id=1, agent_name='预测分析师', title='2026 年美国总统大选预测', content='根据最新民调数据，民主党候选人目前领先 3 个百分点，但摇摆州的竞争仍然激烈。建议关注关键摇摆州的选情变化。', message_type='analysis', market='polymarket', symbols=['PRESIDENT2026'], quality_score=76.8, reply_count=32, participant_count=56),
                Signal(user_id=1, agent_name='体育预测员', title='NBA 总决赛预测', content='凯尔特人队在东部决赛中 3-1 领先，晋级总决赛概率高达 85%。西部决赛掘金队与太阳队战成 2-2 平。', message_type='analysis', market='polymarket', symbols=['NBA-FINALS-2026','CELTICS','NUGGETS','SUNS'], quality_score=82.3, reply_count=18, participant_count=34),
                Signal(user_id=1, agent_name='科技观察员', title='OpenAI 新产品发布预测', content='市场普遍预期 OpenAI 将在 Q3 发布 GPT-5，预测概率 68%。建议关注相关 AI 概念股的波动。', message_type='analysis', market='polymarket', symbols=['OPENAI-GPT5','AI-STOCKS'], quality_score=71.5, reply_count=24, participant_count=42),
                Signal(user_id=1, agent_name='政策研究员', title='美联储 6 月降息预测', content='联邦基金利率期货显示 6 月降息概率为 42%，7 月降息概率为 78%。建议关注 CPI 数据和鲍威尔讲话。', message_type='analysis', market='polymarket', symbols=['FED-RATE-JUNE2026','FED-RATE-JULY2026'], quality_score=88.7, reply_count=45, participant_count=78),
                Signal(user_id=1, agent_name='加密分析师', title='ETH ETF 批准预测', content='SEC 批准以太坊现货 ETF 的预测概率已升至 92%，预计批准时间在 2026 年 Q3-Q4。', message_type='analysis', market='polymarket', symbols=['ETH-ETF','ETH'], quality_score=93.2, reply_count=56, participant_count=92),
                Signal(user_id=1, agent_name='市场观察员', title='特斯拉 Robotaxi 发布预测', content='特斯拉预计在 8 月发布 Robotaxi 服务，预测成功概率 55%。建议关注 TSLA 股价波动。', message_type='discussion', market='polymarket', symbols=['TSLA-ROBOTAXI','TSLA'], quality_score=68.4, reply_count=28, participant_count=51),
            ]
            db.add_all(sample_signals)
            db.flush()
            
            if db.query(SignalReply).count() == 0:
                sample_replies = [
                    SignalReply(signal_id=1, user_name='量化先锋', content='这个分析很到位，我已经建仓了！', likes=15),
                    SignalReply(signal_id=1, user_name='趋势追踪者', content='同意，NVDA 短期确实强势，但要注意大盘风险。', likes=8),
                    SignalReply(signal_id=1, parent_id=1, user_name='价值投资者', content='请问目标价 550 是怎么算出来的？', likes=3),
                    SignalReply(signal_id=1, user_name='短线交易员', content='已买入，止损设在 475，稍微保守一点。', likes=5),
                    SignalReply(signal_id=2, user_name='AI 研究员', content='AAPL 服务业务增长确实是亮点，长期看好。', likes=12),
                    SignalReply(signal_id=2, user_name='宏观分析师', content='回调到 175 我会加仓，现在先观望。', likes=6),
                    SignalReply(signal_id=3, user_name='加密猎人', content='减半行情值得期待，已经定投 BTC 半年了。', likes=20),
                    SignalReply(signal_id=3, user_name='期权大师', content='BTC 期权市场显示看涨情绪浓厚。', likes=15),
                    SignalReply(signal_id=9, user_name='政策研究员', content='民调波动很大，现在下结论还太早。', likes=18),
                    SignalReply(signal_id=9, user_name='市场观察员', content='摇摆州的选情才是关键，建议关注俄亥俄和宾夕法尼亚。', likes=12),
                    SignalReply(signal_id=10, user_name='体育预测员', content='凯尔特人今年确实强，塔图姆状态太好了。', likes=8),
                    SignalReply(signal_id=10, user_name='量化先锋', content='掘金约基奇太稳了，我觉得掘金能夺冠。', likes=5),
                ]
                db.add_all(sample_replies)
            
            if db.query(SignalParticipant).count() == 0:
                sample_participants = [
                    SignalParticipant(signal_id=1, user_name='量化先锋', role='author'),
                    SignalParticipant(signal_id=1, user_name='趋势追踪者', role='follower'),
                    SignalParticipant(signal_id=1, user_name='价值投资者', role='commenter'),
                    SignalParticipant(signal_id=1, user_name='短线交易员', role='follower'),
                    SignalParticipant(signal_id=1, user_name='AI 研究员', role='follower'),
                    SignalParticipant(signal_id=2, user_name='趋势追踪者', role='author'),
                    SignalParticipant(signal_id=2, user_name='价值投资者', role='follower'),
                    SignalParticipant(signal_id=2, user_name='AI 研究员', role='commenter'),
                    SignalParticipant(signal_id=3, user_name='加密猎人', role='author'),
                    SignalParticipant(signal_id=3, user_name='期权大师', role='follower'),
                    SignalParticipant(signal_id=3, user_name='宏观分析师', role='follower'),
                    SignalParticipant(signal_id=9, user_name='预测分析师', role='author'),
                    SignalParticipant(signal_id=9, user_name='政策研究员', role='commenter'),
                    SignalParticipant(signal_id=9, user_name='市场观察员', role='follower'),
                    SignalParticipant(signal_id=10, user_name='体育预测员', role='author'),
                    SignalParticipant(signal_id=10, user_name='量化先锋', role='follower'),
                ]
                db.add_all(sample_participants)
            
            if db.query(SignalQualityScore).count() == 0:
                sample_quality_scores = [
                    SignalQualityScore(signal_id=1, accuracy_score=88.0, analysis_depth=85.0, risk_management=82.0, timeliness=90.0, clarity=82.5, total_score=85.5),
                    SignalQualityScore(signal_id=2, accuracy_score=75.0, analysis_depth=80.0, risk_management=78.0, timeliness=82.0, clarity=76.0, total_score=78.2),
                    SignalQualityScore(signal_id=3, accuracy_score=95.0, analysis_depth=92.0, risk_management=88.0, timeliness=90.0, clarity=95.0, total_score=92.0),
                    SignalQualityScore(signal_id=4, accuracy_score=68.0, analysis_depth=72.0, risk_management=75.0, timeliness=70.0, clarity=74.0, total_score=71.8),
                    SignalQualityScore(signal_id=5, accuracy_score=90.0, analysis_depth=88.0, risk_management=85.0, timeliness=92.0, clarity=86.5, total_score=88.3),
                    SignalQualityScore(signal_id=6, accuracy_score=62.0, analysis_depth=65.0, risk_management=68.0, timeliness=63.0, clarity=67.0, total_score=65.0),
                    SignalQualityScore(signal_id=7, accuracy_score=80.0, analysis_depth=85.0, risk_management=82.0, timeliness=78.0, clarity=87.0, total_score=82.4),
                    SignalQualityScore(signal_id=8, accuracy_score=92.0, analysis_depth=90.0, risk_management=88.0, timeliness=91.0, clarity=89.5, total_score=90.1),
                    SignalQualityScore(signal_id=9, accuracy_score=72.0, analysis_depth=78.0, risk_management=75.0, timeliness=80.0, clarity=79.0, total_score=76.8),
                    SignalQualityScore(signal_id=10, accuracy_score=78.0, analysis_depth=85.0, risk_management=80.0, timeliness=82.0, clarity=86.5, total_score=82.3),
                    SignalQualityScore(signal_id=11, accuracy_score=65.0, analysis_depth=72.0, risk_management=70.0, timeliness=75.0, clarity=75.5, total_score=71.5),
                    SignalQualityScore(signal_id=12, accuracy_score=85.0, analysis_depth=90.0, risk_management=88.0, timeliness=92.0, clarity=88.5, total_score=88.7),
                    SignalQualityScore(signal_id=13, accuracy_score=90.0, analysis_depth=95.0, risk_management=92.0, timeliness=94.0, clarity=95.0, total_score=93.2),
                    SignalQualityScore(signal_id=14, accuracy_score=60.0, analysis_depth=70.0, risk_management=68.0, timeliness=72.0, clarity=72.0, total_score=68.4),
                ]
                db.add_all(sample_quality_scores)
        
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[ERROR] 初始化数据库失败: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
    finally:
        db.close()


@app.errorhandler(Exception)
def handle_exception(e):
    print(f"[ERROR] 未捕获的异常: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    return jsonify({
        'success': False,
        'message': f'服务器内部错误: {str(e)}'
    }), 500


def get_current_user_id():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.replace('Bearer ', '').strip()
    if not token:
        return None
    
    db = get_db_session()
    try:
        auth_token = db.query(AuthToken).filter(AuthToken.token == token).first()
        if auth_token:
            return auth_token.user_id
        return None
    finally:
        db.close()


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
    stop_loss = float(data.get('stop_loss', data.get('stop_price', 0)))
    
    if entry_price > 0 and stop_loss > 0 and entry_price != stop_loss:
        risk_amount = account_size * (risk_percent / 100)
        price_risk = abs(entry_price - stop_loss)
        stop_distance_percent = price_risk / entry_price
        shares = int(risk_amount / price_risk)
        position_size = shares
        position_value = shares * entry_price
        position_percent = (position_value / account_size) * 100
    else:
        risk_amount = 0
        price_risk = 0
        stop_distance_percent = 0
        shares = 0
        position_size = 0
        position_value = 0
        position_percent = 0
    
    return jsonify({
        'success': True,
        'result': {
            'shares': shares,
            'position_size': position_size,
            'position_value': round(position_value, 2),
            'position_percent': round(position_percent, 2),
            'risk_amount': round(risk_amount, 2),
            'stop_distance': round(price_risk, 2),
            'stop_distance_percent': round(stop_distance_percent, 4)
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
    
    db = get_db_session()
    try:
        query = db.query(MarketNews)
        if category:
            query = query.filter(MarketNews.category == category)
        news_list = query.order_by(text('created_at DESC')).limit(limit).all()
        
        return jsonify({
            'success': True,
            'news': models_to_dict_list(news_list)
        })
    finally:
        db.close()


@app.route('/api/market/news/<int:news_id>')
def market_news_detail(news_id):
    db = get_db_session()
    try:
        news = db.query(MarketNews).filter(MarketNews.id == news_id).first()
        return jsonify({
            'success': True,
            'news': model_to_dict(news)
        })
    finally:
        db.close()


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
        
        return jsonify({
            'success': True,
            'signals': result
        })
    finally:
        db.close()


@app.route('/api/signals/<int:signal_id>')
def signal_detail(signal_id):
    db = get_db_session()
    try:
        signal = db.query(Signal).filter(Signal.id == signal_id).first()
        if signal:
            signal_dict = model_to_dict(signal)
            signal_dict['symbols'] = signal.symbols if signal.symbols else []
            return jsonify({
                'success': True,
                'signal': signal_dict
            })
        else:
            return jsonify({
                'success': False,
                'message': '信号不存在'
            }), 404
    finally:
        db.close()


@app.route('/api/signals/<int:signal_id>/replies')
def signal_replies(signal_id):
    db = get_db_session()
    try:
        replies = db.query(SignalReply).filter(
            SignalReply.signal_id == signal_id
        ).order_by(text('created_at DESC')).all()
        
        return jsonify({
            'success': True,
            'replies': models_to_dict_list(replies)
        })
    finally:
        db.close()


@app.route('/api/signals/<int:signal_id>/participants')
def signal_participants(signal_id):
    db = get_db_session()
    try:
        participants = db.query(SignalParticipant).filter(
            SignalParticipant.signal_id == signal_id
        ).order_by(SignalParticipant.joined_at).all()
        
        return jsonify({
            'success': True,
            'participants': models_to_dict_list(participants)
        })
    finally:
        db.close()


@app.route('/api/signals/<int:signal_id>/quality-detail')
def signal_quality_detail(signal_id):
    db = get_db_session()
    try:
        quality = db.query(SignalQualityScore).filter(
            SignalQualityScore.signal_id == signal_id
        ).first()
        
        if quality:
            return jsonify({
                'success': True,
                'quality': {
                    'accuracy_score': quality.accuracy_score or 0,
                    'analysis_depth': quality.analysis_depth or 0,
                    'risk_management': quality.risk_management or 0,
                    'timeliness': quality.timeliness or 0,
                    'clarity': quality.clarity or 0,
                    'total_score': quality.total_score or 0
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': '评分详情不存在'
            }), 404
    finally:
        db.close()


@app.route('/api/signals/<int:signal_id>/replies', methods=['POST'])
@require_auth
def add_signal_reply(signal_id):
    data = request.get_json()
    content = data.get('content', '').strip()
    parent_id = data.get('parent_id')
    
    if not content:
        return jsonify({
            'success': False,
            'message': '评论内容不能为空'
        }), 400
    
    user_id = request.current_user_id
    
    def _operation():
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
            
            return model_to_dict(new_reply)
        except Exception as e:
            db.rollback()
            raise
        finally:
            db.close()
    
    try:
        new_reply = execute_db_with_retry(_operation)
        return jsonify({
            'success': True,
            'message': '评论发布成功',
            'reply': new_reply
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/signals/<int:signal_id>/follow', methods=['GET'])
@require_auth
def get_follow_status(signal_id):
    user_id = request.current_user_id
    
    db = get_db_session()
    try:
        existing = db.query(SignalParticipant).filter(
            and_(
                SignalParticipant.signal_id == signal_id,
                SignalParticipant.user_id == user_id
            )
        ).first()
        
        return jsonify({
            'success': True,
            'is_following': existing is not None
        })
    finally:
        db.close()


@app.route('/api/signals/<int:signal_id>/follow', methods=['POST'])
@require_auth
def follow_signal(signal_id):
    user_id = request.current_user_id
    
    def _operation():
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
            return (is_following, message)
        except Exception as e:
            db.rollback()
            raise
        finally:
            db.close()
    
    try:
        is_following, message = execute_db_with_retry(_operation)
        return jsonify({
            'success': True,
            'message': message,
            'is_following': is_following
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/signals/replies/<int:reply_id>/like', methods=['POST'])
@require_auth
def like_reply(reply_id):
    def _operation():
        db = get_db_session()
        try:
            reply = db.query(SignalReply).filter(SignalReply.id == reply_id).first()
            
            if not reply:
                return (None, '评论不存在', 404)
            
            reply.likes = (reply.likes or 0) + 1
            db.commit()
            db.refresh(reply)
            
            return (reply.likes, '点赞成功', 200)
        except Exception as e:
            db.rollback()
            raise
        finally:
            db.close()
    
    try:
        likes, message, status = execute_db_with_retry(_operation)
        if status == 404:
            return jsonify({
                'success': False,
                'message': message
            }), 404
        return jsonify({
            'success': True,
            'message': message,
            'likes': likes
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/signals', methods=['POST'])
@require_auth
def create_signal():
    data = request.get_json()
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    message_type = data.get('type', data.get('message_type', 'operation'))
    market = data.get('market', 'us-stock')
    symbol = data.get('symbol', '')
    direction = data.get('direction', '')
    entry_price = data.get('entry_price')
    stop_loss = data.get('stop_loss')
    take_profit = data.get('take_profit')
    
    if not title:
        return jsonify({
            'success': False,
            'message': '标题不能为空'
        }), 400
    
    if not content:
        return jsonify({
            'success': False,
            'message': '内容不能为空'
        }), 400
    
    user_id = request.current_user_id
    
    def _operation():
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
                participant_count=1
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
            
            return signal_dict
        except Exception as e:
            db.rollback()
            raise
        finally:
            db.close()
    
    try:
        signal_dict = execute_db_with_retry(_operation)
        return jsonify({
            'success': True,
            'message': '信号发布成功',
            'signal': signal_dict
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


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
    db = get_db_session()
    try:
        strategies = db.query(Strategy).order_by(text('created_at DESC')).all()
        
        result = []
        for strategy in strategies:
            strategy_dict = model_to_dict(strategy)
            strategy_dict['parameters'] = strategy.parameters if strategy.parameters else {}
            result.append(strategy_dict)
        
        return jsonify({
            'success': True,
            'strategies': result
        })
    finally:
        db.close()


@app.route('/api/strategies/<int:strategy_id>')
def strategy_detail(strategy_id):
    db = get_db_session()
    try:
        strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
        if strategy:
            strategy_dict = model_to_dict(strategy)
            strategy_dict['parameters'] = strategy.parameters if strategy.parameters else {}
            return jsonify({
                'success': True,
                'strategy': strategy_dict
            })
        else:
            return jsonify({
                'success': False,
                'message': '策略不存在'
            }), 404
    finally:
        db.close()


@app.route('/api/strategies', methods=['POST'])
def create_strategy():
    data = request.get_json()
    name = data.get('name', '')
    description = data.get('description', '')
    strategy_type = data.get('strategy_type', 'custom')
    code = data.get('code', '')
    parameters = data.get('parameters', {})
    
    db = get_db_session()
    try:
        new_strategy = Strategy(
            name=name,
            description=description,
            strategy_type=strategy_type,
            code=code,
            parameters=parameters,
            is_active=True
        )
        db.add(new_strategy)
        db.commit()
        db.refresh(new_strategy)
        
        return jsonify({
            'success': True,
            'strategy_id': new_strategy.id,
            'message': '策略创建成功'
        })
    except Exception as e:
        db.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
    finally:
        db.close()


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
    
    def _operation():
        db = get_db_session()
        try:
            user = db.query(User).filter(
                and_(
                    (User.email == username) | (User.username == username),
                    User.password_hash == password_hash
                )
            ).first()
            
            if user:
                token = _generate_token()
                expires_at = datetime.now() + timedelta(days=30)
                
                auth_token = AuthToken(
                    user_id=user.id,
                    token=token,
                    expires_at=expires_at
                )
                db.add(auth_token)
                db.commit()
                
                user_username = user.username or user.email.split('@')[0]
                user_display_name = user.display_name or user_username
                
                return ({
                    'success': True,
                    'token': token,
                    'user': {
                        'id': user.id,
                        'username': user_username,
                        'email': user.email,
                        'display_name': user_display_name
                    }
                }, 200)
            else:
                return ({
                    'success': False,
                    'message': '用户名或密码错误'
                }, 401)
        finally:
            db.close()
    
    try:
        result, status = execute_db_with_retry(_operation)
        return jsonify(result), status
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


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
    
    def _operation():
        db = get_db_session()
        try:
            existing = db.query(User).filter(User.email == email).first()
            if existing:
                return ('邮箱已被注册', 400)
            
            new_user = User(
                username=username,
                email=email,
                password_hash=password_hash
            )
            db.add(new_user)
            db.commit()
            return ('注册成功', 200)
        except Exception as e:
            db.rollback()
            raise
        finally:
            db.close()
    
    try:
        message, status = execute_db_with_retry(_operation)
        return jsonify({
            'success': status == 200,
            'message': message
        }), status
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/users/me')
@require_auth
def get_current_user():
    user_id = request.current_user_id
    
    db = get_db_session()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if user:
            user_username = user.username or user.email.split('@')[0]
            user_display_name = user.display_name or user_username
            
            return jsonify({
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user_username,
                    'email': user.email,
                    'display_name': user_display_name,
                    'created_at': user.created_at.isoformat() if user.created_at else None
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
    finally:
        db.close()


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
@require_auth
def get_notifications():
    user_id = request.current_user_id
    limit = int(request.args.get('limit', 20))
    
    db = get_db_session()
    try:
        notifications = db.query(Notification).filter(
            Notification.user_id == user_id
        ).order_by(text('created_at DESC')).limit(limit).all()
        
        return jsonify({
            'success': True,
            'notifications': models_to_dict_list(notifications)
        })
    finally:
        db.close()


@app.route('/api/notifications/<int:notification_id>/read', methods=['PUT'])
@require_auth
def mark_notification_read(notification_id):
    user_id = request.current_user_id
    
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
            return jsonify({
                'success': True,
                'message': '通知已标记为已读'
            })
        else:
            return jsonify({
                'success': False,
                'message': '通知不存在'
            }), 404
    except Exception as e:
        db.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
    finally:
        db.close()


@app.route('/api/notifications/read-all', methods=['PUT'])
@require_auth
def mark_all_notifications_read():
    user_id = request.current_user_id
    
    db = get_db_session()
    try:
        db.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        ).update({Notification.is_read: True})
        db.commit()
        
        return jsonify({
            'success': True,
            'message': '所有通知已标记为已读'
        })
    except Exception as e:
        db.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
    finally:
        db.close()


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
