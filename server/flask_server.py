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
import threading
import time
import random
import traceback
import sys
import ipaddress
from datetime import datetime, timedelta

try:
    import fcntl
    HAS_FCNTL = True
except ImportError:
    HAS_FCNTL = False
    print("[WARN] fcntl module not available, using thread lock instead", file=sys.stderr)
from functools import wraps

from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

CORS(app, supports_credentials=True)

@app.after_request
def ensure_cors(response):
    origin = request.headers.get('Origin', '')
    if origin:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
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
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signal_replies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_id INTEGER NOT NULL,
                user_id INTEGER,
                user_name TEXT NOT NULL,
                content TEXT NOT NULL,
                parent_id INTEGER,
                likes INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (signal_id) REFERENCES signals (id),
                FOREIGN KEY (parent_id) REFERENCES signal_replies (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signal_participants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_id INTEGER NOT NULL,
                user_id INTEGER,
                user_name TEXT NOT NULL,
                role TEXT DEFAULT 'follower',
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (signal_id) REFERENCES signals (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signal_quality_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_id INTEGER NOT NULL,
                accuracy_score REAL DEFAULT 0,
                analysis_depth REAL DEFAULT 0,
                risk_management REAL DEFAULT 0,
                timeliness REAL DEFAULT 0,
                clarity REAL DEFAULT 0,
                total_score REAL DEFAULT 0,
                FOREIGN KEY (signal_id) REFERENCES signals (id)
            )
        ''')
        
        conn.commit()
        
        # Always update demo account password to ensure it's correct
        cursor.execute('SELECT id, password_hash FROM users WHERE email = ? OR username = ?',
                      ('demo@example.com', 'demo'))
        existing = cursor.fetchone()
        new_hash = _hash_password('demo123456')
        if existing:
            if existing[1] != new_hash:
                cursor.execute('UPDATE users SET password_hash = ?, username = ? WHERE id = ?',
                             (new_hash, 'demo', existing[0]))
        else:
            cursor.execute('''
                INSERT INTO users (email, username, password_hash)
                VALUES (?, ?, ?)
            ''', ('demo@example.com', 'demo', new_hash))
            
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
                (1, '预测分析师', '2026 年美国总统大选预测', '根据最新民调数据，民主党候选人目前领先 3 个百分点，但摇摆州的竞争仍然激烈。建议关注关键摇摆州的选情变化。', 'analysis', 'polymarket', '["PRESIDENT2026"]', 76.8, 32, 56),
                (1, '体育预测员', 'NBA 总决赛预测', '凯尔特人队在东部决赛中 3-1 领先，晋级总决赛概率高达 85%。西部决赛掘金队与太阳队战成 2-2 平。', 'analysis', 'polymarket', '["NBA-FINALS-2026","CELTICS","NUGGETS","SUNS"]', 82.3, 18, 34),
                (1, '科技观察员', 'OpenAI 新产品发布预测', '市场普遍预期 OpenAI 将在 Q3 发布 GPT-5，预测概率 68%。建议关注相关 AI 概念股的波动。', 'analysis', 'polymarket', '["OPENAI-GPT5","AI-STOCKS"]', 71.5, 24, 42),
                (1, '政策研究员', '美联储 6 月降息预测', '联邦基金利率期货显示 6 月降息概率为 42%，7 月降息概率为 78%。建议关注 CPI 数据和鲍威尔讲话。', 'analysis', 'polymarket', '["FED-RATE-JUNE2026","FED-RATE-JULY2026"]', 88.7, 45, 78),
                (1, '加密分析师', 'ETH ETF 批准预测', 'SEC 批准以太坊现货 ETF 的预测概率已升至 92%，预计批准时间在 2026 年 Q3-Q4。', 'analysis', 'polymarket', '["ETH-ETF","ETH"]', 93.2, 56, 92),
                (1, '市场观察员', '特斯拉 Robotaxi 发布预测', '特斯拉预计在 8 月发布 Robotaxi 服务，预测成功概率 55%。建议关注 TSLA 股价波动。', 'discussion', 'polymarket', '["TSLA-ROBOTAXI","TSLA"]', 68.4, 28, 51),
            ]
            cursor.executemany('''
                INSERT INTO signals (user_id, agent_name, title, content, message_type, market, symbols, quality_score, reply_count, participant_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', sample_signals)
            
            cursor.execute('SELECT COUNT(*) FROM signal_replies')
            if cursor.fetchone()[0] == 0:
                sample_replies = [
                    (1, None, '量化先锋', '这个分析很到位，我已经建仓了！', 15),
                    (1, None, '趋势追踪者', '同意，NVDA 短期确实强势，但要注意大盘风险。', 8),
                    (1, 1, '价值投资者', '请问目标价 550 是怎么算出来的？', 3),
                    (1, None, '短线交易员', '已买入，止损设在 475，稍微保守一点。', 5),
                    (2, None, 'AI 研究员', 'AAPL 服务业务增长确实是亮点，长期看好。', 12),
                    (2, None, '宏观分析师', '回调到 175 我会加仓，现在先观望。', 6),
                    (3, None, '加密猎人', '减半行情值得期待，已经定投 BTC 半年了。', 20),
                    (3, None, '期权大师', 'BTC 期权市场显示看涨情绪浓厚。', 15),
                    (9, None, '政策研究员', '民调波动很大，现在下结论还太早。', 18),
                    (9, None, '市场观察员', '摇摆州的选情才是关键，建议关注俄亥俄和宾夕法尼亚。', 12),
                    (10, None, '体育预测员', '凯尔特人今年确实强，塔图姆状态太好了。', 8),
                    (10, None, '量化先锋', '掘金约基奇太稳了，我觉得掘金能夺冠。', 5),
                ]
                for reply in sample_replies:
                    cursor.execute('''
                        INSERT INTO signal_replies (signal_id, parent_id, user_name, content, likes)
                        VALUES (?, ?, ?, ?, ?)
                    ''', reply)
            
            cursor.execute('SELECT COUNT(*) FROM signal_participants')
            if cursor.fetchone()[0] == 0:
                sample_participants = [
                    (1, '量化先锋', 'author'),
                    (1, '趋势追踪者', 'follower'),
                    (1, '价值投资者', 'commenter'),
                    (1, '短线交易员', 'follower'),
                    (1, 'AI 研究员', 'follower'),
                    (2, '趋势追踪者', 'author'),
                    (2, '价值投资者', 'follower'),
                    (2, 'AI 研究员', 'commenter'),
                    (3, '加密猎人', 'author'),
                    (3, '期权大师', 'follower'),
                    (3, '宏观分析师', 'follower'),
                    (9, '预测分析师', 'author'),
                    (9, '政策研究员', 'commenter'),
                    (9, '市场观察员', 'follower'),
                    (10, '体育预测员', 'author'),
                    (10, '量化先锋', 'follower'),
                ]
                cursor.executemany('''
                    INSERT INTO signal_participants (signal_id, user_name, role)
                    VALUES (?, ?, ?)
                ''', sample_participants)
            
            cursor.execute('SELECT COUNT(*) FROM signal_quality_scores')
            if cursor.fetchone()[0] == 0:
                sample_quality_scores = [
                    (1, 88.0, 85.0, 82.0, 90.0, 82.5, 85.5),
                    (2, 75.0, 80.0, 78.0, 82.0, 76.0, 78.2),
                    (3, 95.0, 92.0, 88.0, 90.0, 95.0, 92.0),
                    (4, 68.0, 72.0, 75.0, 70.0, 74.0, 71.8),
                    (5, 90.0, 88.0, 85.0, 92.0, 86.5, 88.3),
                    (6, 62.0, 65.0, 68.0, 63.0, 67.0, 65.0),
                    (7, 80.0, 85.0, 82.0, 78.0, 87.0, 82.4),
                    (8, 92.0, 90.0, 88.0, 91.0, 89.5, 90.1),
                    (9, 72.0, 78.0, 75.0, 80.0, 79.0, 76.8),
                    (10, 78.0, 85.0, 80.0, 82.0, 86.5, 82.3),
                    (11, 65.0, 72.0, 70.0, 75.0, 75.5, 71.5),
                    (12, 85.0, 90.0, 88.0, 92.0, 88.5, 88.7),
                    (13, 90.0, 95.0, 92.0, 94.0, 95.0, 93.2),
                    (14, 60.0, 70.0, 68.0, 72.0, 72.0, 68.4),
                ]
                cursor.executemany('''
                    INSERT INTO signal_quality_scores (signal_id, accuracy_score, analysis_depth, risk_management, timeliness, clarity, total_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', sample_quality_scores)
        
        conn.commit()
    except Exception as e:
        conn.rollback()
    finally:
        conn.close()


_db_write_lock = threading.Lock()
_db_lock_file = os.path.join(os.path.dirname(DB_PATH), 'db_write.lock')


class FileLock:
    def __init__(self, lock_file):
        self.lock_file = lock_file
        self.lock_fd = None
        self._fallback_lock = threading.Lock()
    
    def __enter__(self):
        if HAS_FCNTL:
            try:
                self.lock_fd = open(self.lock_file, 'w')
                fcntl.flock(self.lock_fd, fcntl.LOCK_EX)
                return self
            except (OSError, IOError) as e:
                print(f"[WARN] 文件锁获取失败，使用线程锁: {e}", file=sys.stderr)
                if self.lock_fd:
                    self.lock_fd.close()
                    self.lock_fd = None
        self._fallback_lock.acquire()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.lock_fd:
            try:
                fcntl.flock(self.lock_fd, fcntl.LOCK_UN)
            except:
                pass
            self.lock_fd.close()
            self.lock_fd = None
        else:
            try:
                self._fallback_lock.release()
            except:
                pass
        return False


_db_file_lock = FileLock(_db_lock_file)


def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=60)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute('PRAGMA journal_mode=WAL')
    except:
        pass
    try:
        conn.execute('PRAGMA synchronous=NORMAL')
    except:
        pass
    try:
        conn.execute('PRAGMA busy_timeout=60000')
    except:
        pass
    try:
        conn.execute('PRAGMA cache_size=-20000')
    except:
        pass
    try:
        conn.execute('PRAGMA temp_store=MEMORY')
    except:
        pass
    return conn


def execute_db_with_retry(operation, max_retries=20, base_delay=0.2, use_lock=True):
    last_error = None
    
    for attempt in range(max_retries):
        try:
            if use_lock:
                try:
                    with _db_file_lock:
                        return operation()
                except (OSError, IOError) as e:
                    print(f"[WARN] 文件锁获取失败，尝试无锁执行: {e}", file=sys.stderr)
                    return operation()
            else:
                return operation()
        except sqlite3.OperationalError as e:
            error_msg = str(e).lower()
            if 'locked' in error_msg or 'busy' in error_msg:
                last_error = e
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt) + random.uniform(0, base_delay)
                    delay = min(delay, 8.0)
                    print(f"[WARN] 数据库锁定，第 {attempt + 1}/{max_retries} 次重试，等待 {delay:.2f}s: {e}", file=sys.stderr)
                    time.sleep(delay)
                    continue
            print(f"[ERROR] 数据库操作失败: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            raise
        except Exception as e:
            print(f"[ERROR] 操作失败: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            raise
    print(f"[ERROR] 重试 {max_retries} 次后仍然失败: {last_error}", file=sys.stderr)
    raise last_error


@app.errorhandler(Exception)
def handle_exception(e):
    print(f"[ERROR] 未捕获的异常: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    return jsonify({
        'success': False,
        'message': f'服务器内部错误: {str(e)}'
    }), 500


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


ip_request_history = {}
ip_failed_attempts = {}
ip_banned = {}
ip_lock = threading.Lock()

LOGIN_RATE_LIMIT = 5
LOGIN_RATE_WINDOW = 60
ME_RATE_LIMIT = 30
ME_RATE_WINDOW = 60
MAX_FAILED_ATTEMPTS = 5
BAN_DURATION = 300

ALLOWED_IP_NETWORKS = [
    '127.0.0.1/32',
    '10.0.0.0/8',
    '172.16.0.0/12',
    '192.168.0.0/16',
]

_parsed_networks = []
for network in ALLOWED_IP_NETWORKS:
    try:
        _parsed_networks.append(ipaddress.ip_network(network, strict=False))
    except ValueError as e:
        print(f"[WARN] Invalid IP network: {network} - {e}", file=sys.stderr)


def get_client_ip():
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr


def is_ip_banned(ip):
    with ip_lock:
        if ip in ip_banned:
            ban_time = ip_banned[ip]
            if time.time() - ban_time < BAN_DURATION:
                return True
            else:
                del ip_banned[ip]
                if ip in ip_failed_attempts:
                    del ip_failed_attempts[ip]
    return False


def record_failed_attempt(ip):
    with ip_lock:
        if ip not in ip_failed_attempts:
            ip_failed_attempts[ip] = 0
        ip_failed_attempts[ip] += 1
        
        if ip_failed_attempts[ip] >= MAX_FAILED_ATTEMPTS:
            ip_banned[ip] = time.time()
            return True
    return False


def reset_failed_attempts(ip):
    with ip_lock:
        if ip in ip_failed_attempts:
            del ip_failed_attempts[ip]
        if ip in ip_banned:
            del ip_banned[ip]


def check_rate_limit(ip, limit, window, endpoint):
    with ip_lock:
        key = f"{endpoint}:{ip}"
        now = time.time()
        
        if key not in ip_request_history:
            ip_request_history[key] = []
        
        ip_request_history[key] = [
            t for t in ip_request_history[key] 
            if now - t < window
        ]
        
        if len(ip_request_history[key]) >= limit:
            return False
        
        ip_request_history[key].append(now)
        return True


def rate_limit(limit, window, endpoint):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            ip = get_client_ip()
            
            if is_ip_banned(ip):
                return jsonify({
                    'success': False,
                    'message': f'IP 已被暂时封禁，请 {BAN_DURATION} 秒后再试'
                }), 429
            
            if not check_rate_limit(ip, limit, window, endpoint):
                return jsonify({
                    'success': False,
                    'message': f'请求过于频繁，请 {window} 秒后再试'
                }), 429
            
            return f(*args, **kwargs)
        return decorated
    return decorator


def is_ip_allowed(ip):
    try:
        ip_addr = ipaddress.ip_address(ip)
        for network in _parsed_networks:
            if ip_addr in network:
                return True
        return False
    except ValueError:
        return False


def ip_restriction(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        ip = get_client_ip()
        
        if not is_ip_allowed(ip):
            return jsonify({
                'success': False,
                'message': f'IP {ip} 不在允许的网段内，访问被拒绝'
            }), 403
        
        return f(*args, **kwargs)
    return decorated


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


@app.route('/api/signals/<int:signal_id>/replies')
def signal_replies(signal_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM signal_replies WHERE signal_id = ? ORDER BY created_at DESC', (signal_id,))
    rows = cursor.fetchall()
    conn.close()
    
    replies = []
    for row in rows:
        reply = dict(row)
        replies.append(reply)
    
    return jsonify({
        'success': True,
        'replies': replies
    })


@app.route('/api/signals/<int:signal_id>/participants')
def signal_participants(signal_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM signal_participants WHERE signal_id = ? ORDER BY joined_at', (signal_id,))
    rows = cursor.fetchall()
    conn.close()
    
    participants = []
    for row in rows:
        participant = dict(row)
        participants.append(participant)
    
    return jsonify({
        'success': True,
        'participants': participants
    })


@app.route('/api/signals/<int:signal_id>/quality-detail')
def signal_quality_detail(signal_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM signal_quality_scores WHERE signal_id = ?', (signal_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        quality = dict(row)
        return jsonify({
            'success': True,
            'quality': {
                'accuracy_score': quality.get('accuracy_score', 0),
                'analysis_depth': quality.get('analysis_depth', 0),
                'risk_management': quality.get('risk_management', 0),
                'timeliness': quality.get('timeliness', 0),
                'clarity': quality.get('clarity', 0),
                'total_score': quality.get('total_score', 0)
            }
        })
    else:
        return jsonify({
            'success': False,
            'message': '评分详情不存在'
        }), 404


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
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
        user_row = cursor.fetchone()
        user_name = user_row['username'] if user_row else '匿名用户'
        
        cursor.execute('''
            INSERT INTO signal_replies (signal_id, user_id, user_name, content, parent_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (signal_id, user_id, user_name, content, parent_id))
        
        reply_id = cursor.lastrowid
        
        cursor.execute('UPDATE signals SET reply_count = reply_count + 1 WHERE id = ?', (signal_id,))
        
        cursor.execute('SELECT * FROM signal_replies WHERE id = ?', (reply_id,))
        new_reply = cursor.fetchone()
        
        conn.commit()
        conn.close()
        
        return new_reply
    
    try:
        new_reply = execute_db_with_retry(_operation)
        return jsonify({
            'success': True,
            'message': '评论发布成功',
            'reply': dict(new_reply)
        })
    except sqlite3.OperationalError as e:
        return jsonify({
            'success': False,
            'message': '数据库繁忙，请稍后重试'
        }), 503


@app.route('/api/signals/<int:signal_id>/follow', methods=['GET'])
@require_auth
def get_follow_status(signal_id):
    user_id = request.current_user_id
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM signal_participants WHERE signal_id = ? AND user_id = ?', (signal_id, user_id))
    existing = cursor.fetchone()
    
    conn.close()
    
    return jsonify({
        'success': True,
        'is_following': existing is not None
    })


@app.route('/api/signals/<int:signal_id>/follow', methods=['POST'])
@require_auth
def follow_signal(signal_id):
    user_id = request.current_user_id
    
    def _operation():
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM signal_participants WHERE signal_id = ? AND user_id = ?', (signal_id, user_id))
        existing = cursor.fetchone()
        
        cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
        user_row = cursor.fetchone()
        user_name = user_row['username'] if user_row else '匿名用户'
        
        if existing:
            cursor.execute('DELETE FROM signal_participants WHERE id = ?', (existing['id'],))
            cursor.execute('UPDATE signals SET participant_count = participant_count - 1 WHERE id = ?', (signal_id,))
            is_following = False
            message = '已取消关注'
        else:
            cursor.execute('''
                INSERT INTO signal_participants (signal_id, user_id, user_name, role)
                VALUES (?, ?, ?, 'follower')
            ''', (signal_id, user_id, user_name))
            cursor.execute('UPDATE signals SET participant_count = participant_count + 1 WHERE id = ?', (signal_id,))
            is_following = True
            message = '关注成功'
        
        conn.commit()
        conn.close()
        
        return (is_following, message)
    
    try:
        is_following, message = execute_db_with_retry(_operation)
        return jsonify({
            'success': True,
            'message': message,
            'is_following': is_following
        })
    except sqlite3.OperationalError as e:
        return jsonify({
            'success': False,
            'message': '数据库繁忙，请稍后重试'
        }), 503


@app.route('/api/signals/replies/<int:reply_id>/like', methods=['POST'])
@require_auth
def like_reply(reply_id):
    def _operation():
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM signal_replies WHERE id = ?', (reply_id,))
        reply = cursor.fetchone()
        
        if not reply:
            conn.close()
            return (None, '评论不存在', 404)
        
        cursor.execute('UPDATE signal_replies SET likes = likes + 1 WHERE id = ?', (reply_id,))
        
        cursor.execute('SELECT * FROM signal_replies WHERE id = ?', (reply_id,))
        updated_reply = cursor.fetchone()
        
        conn.commit()
        conn.close()
        
        return (updated_reply['likes'], '点赞成功', 200)
    
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
    except sqlite3.OperationalError as e:
        return jsonify({
            'success': False,
            'message': '数据库繁忙，请稍后重试'
        }), 503


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
    
    import json
    import random
    
    def _operation():
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
        user_row = cursor.fetchone()
        agent_name = user_row['username'] if user_row else '匿名交易者'
        
        symbols = [symbol] if symbol else []
        symbols_json = json.dumps(symbols)
        
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
        
        cursor.execute('''
            INSERT INTO signals (user_id, agent_name, title, content, message_type, market, symbols, quality_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, agent_name, title, full_content, message_type, market, symbols_json, quality_score))
        
        signal_id = cursor.lastrowid
        
        cursor.execute('''
            INSERT INTO signal_participants (signal_id, user_id, user_name, role)
            VALUES (?, ?, ?, 'author')
        ''', (signal_id, user_id, agent_name))
        
        accuracy = round(random.uniform(60, 95), 1)
        analysis_depth = round(random.uniform(60, 95), 1)
        risk_management = round(random.uniform(60, 95), 1)
        timeliness = round(random.uniform(60, 95), 1)
        clarity = round(random.uniform(60, 95), 1)
        total_score = round((accuracy + analysis_depth + risk_management + timeliness + clarity) / 5, 1)
        
        cursor.execute('''
            INSERT INTO signal_quality_scores (signal_id, accuracy_score, analysis_depth, risk_management, timeliness, clarity, total_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (signal_id, accuracy, analysis_depth, risk_management, timeliness, clarity, total_score))
        
        cursor.execute('SELECT * FROM signals WHERE id = ?', (signal_id,))
        new_signal = cursor.fetchone()
        
        conn.commit()
        conn.close()
        
        return new_signal
    
    try:
        new_signal = execute_db_with_retry(_operation)
        signal_dict = dict(new_signal)
        try:
            signal_dict['symbols'] = json.loads(signal_dict['symbols']) if signal_dict['symbols'] else []
        except:
            signal_dict['symbols'] = []
        
        return jsonify({
            'success': True,
            'message': '信号发布成功',
            'signal': signal_dict
        })
    except sqlite3.OperationalError as e:
        return jsonify({
            'success': False,
            'message': '数据库繁忙，请稍后重试'
        }), 503


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
@ip_restriction
@rate_limit(LOGIN_RATE_LIMIT, LOGIN_RATE_WINDOW, 'login')
def login():
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')
    ip = get_client_ip()
    
    password_hash = _hash_password(password)
    
    def _operation():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, email, username, display_name FROM users 
            WHERE (email = ? OR username = ?) AND password_hash = ?
        ''', (username, username, password_hash))
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
            
            conn.close()
            return ({
                'success': True,
                'token': token,
                'user': {
                    'id': row['id'],
                    'username': user_username,
                    'email': row['email'],
                    'display_name': user_display_name
                }
            }, 200)
        else:
            conn.close()
            return ({
                'success': False,
                'message': '用户名或密码错误'
            }, 401)
    
    try:
        result, status = execute_db_with_retry(_operation)
        
        if status == 200:
            reset_failed_attempts(ip)
        else:
            banned = record_failed_attempt(ip)
            if banned:
                result['message'] = f'登录失败次数过多，IP 已被暂时封禁 {BAN_DURATION} 秒'
                status = 429
        
        return jsonify(result), status
    except sqlite3.OperationalError as e:
        return jsonify({
            'success': False,
            'message': '数据库繁忙，请稍后重试'
        }), 503
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
        conn = get_db()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
            if cursor.fetchone():
                conn.close()
                return ('邮箱已被注册', 400)
            
            cursor.execute('''
                INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
            ''', (username, email, password_hash))
            conn.commit()
            conn.close()
            return ('注册成功', 200)
        except Exception as e:
            conn.rollback()
            conn.close()
            raise
    
    try:
        message, status = execute_db_with_retry(_operation)
        return jsonify({
            'success': status == 200,
            'message': message
        }), status
    except sqlite3.OperationalError as e:
        return jsonify({
            'success': False,
            'message': '数据库繁忙，请稍后重试'
        }), 503
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/auth/me')
@ip_restriction
@rate_limit(ME_RATE_LIMIT, ME_RATE_WINDOW, 'auth_me')
@require_auth
def auth_me():
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


init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8001)), debug=False)
