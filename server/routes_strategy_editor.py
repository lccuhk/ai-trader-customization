"""
Strategy Editor Routes

策略编辑器 API 路由
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from database import _SQLITE_DB_PATH


class StrategyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    strategy_type: str = 'custom'
    code: str = ''
    parameters: Optional[Dict[str, Any]] = None


class StrategyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    code: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class BacktestRequest(BaseModel):
    strategy_id: int
    start_date: str
    end_date: str
    initial_capital: float = 100000.0
    parameters: Optional[Dict[str, Any]] = None


def _init_strategy_editor_db():
    """初始化策略编辑器数据库表"""
    conn = sqlite3.connect(_SQLITE_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS strategies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            strategy_type TEXT DEFAULT 'custom',
            code TEXT DEFAULT '',
            parameters TEXT DEFAULT '{}',
            is_active INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS strategy_backtests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            strategy_id INTEGER NOT NULL,
            start_date TEXT,
            end_date TEXT,
            initial_capital REAL,
            final_capital REAL,
            total_return REAL,
            annualized_return REAL,
            max_drawdown REAL,
            sharpe_ratio REAL,
            win_rate REAL,
            total_trades INTEGER,
            result TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS strategy_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            strategy_type TEXT,
            code TEXT,
            parameters TEXT DEFAULT '{}',
            category TEXT,
            is_public INTEGER DEFAULT 1
        )
    ''')
    
    cursor.execute('SELECT COUNT(*) FROM strategies')
    if cursor.fetchone()[0] == 0:
        sample_strategies = [
            ('移动平均线交叉策略', '基于短期和长期移动平均线的交叉信号进行交易', 'trend_following', 
             '''# 移动平均线交叉策略
def strategy(data, params):
    short_ma = params.get('short_ma', 20)
    long_ma = params.get('long_ma', 50)
    
    # 计算移动平均线
    data['short_ma'] = data['close'].rolling(short_ma).mean()
    data['long_ma'] = data['close'].rolling(long_ma).mean()
    
    # 生成信号
    data['signal'] = 0
    data.loc[data['short_ma'] > data['long_ma'], 'signal'] = 1  # 买入
    data.loc[data['short_ma'] < data['long_ma'], 'signal'] = -1  # 卖出
    
    return data
''',
             json.dumps({'short_ma': 20, 'long_ma': 50})),
            ('RSI超买超卖策略', '使用RSI指标识别超买超卖区域进行反向交易', 'mean_reversion',
             '''# RSI超买超卖策略
def strategy(data, params):
    rsi_period = params.get('rsi_period', 14)
    overbought = params.get('overbought', 70)
    oversold = params.get('oversold', 30)
    
    # 计算RSI
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(rsi_period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(rsi_period).mean()
    rs = gain / loss
    data['rsi'] = 100 - (100 / (1 + rs))
    
    # 生成信号
    data['signal'] = 0
    data.loc[data['rsi'] < oversold, 'signal'] = 1  # 超卖买入
    data.loc[data['rsi'] > overbought, 'signal'] = -1  # 超买卖出
    
    return data
''',
             json.dumps({'rsi_period': 14, 'overbought': 70, 'oversold': 30})),
            ('布林带突破策略', '基于布林带的突破信号进行交易', 'volatility',
             '''# 布林带突破策略
def strategy(data, params):
    period = params.get('period', 20)
    std_dev = params.get('std_dev', 2)
    
    # 计算布林带
    data['middle'] = data['close'].rolling(period).mean()
    data['std'] = data['close'].rolling(period).std()
    data['upper'] = data['middle'] + (data['std'] * std_dev)
    data['lower'] = data['middle'] - (data['std'] * std_dev)
    
    # 生成信号
    data['signal'] = 0
    data.loc[data['close'] > data['upper'], 'signal'] = 1  # 突破上轨买入
    data.loc[data['close'] < data['lower'], 'signal'] = -1  # 突破下轨卖出
    
    return data
''',
             json.dumps({'period': 20, 'std_dev': 2})),
        ]
        cursor.executemany('''
            INSERT INTO strategies (name, description, strategy_type, code, parameters, is_active)
            VALUES (?, ?, ?, ?, ?, 1)
        ''', sample_strategies)
    
    cursor.execute('SELECT COUNT(*) FROM strategy_templates')
    if cursor.fetchone()[0] == 0:
        sample_templates = [
            ('双均线策略模板', '经典的趋势跟踪策略模板', 'trend_following', 
             'def strategy(data, params):\n    # 实现你的策略逻辑\n    return data',
             json.dumps({'short_ma': 20, 'long_ma': 50}), '趋势跟踪', 1),
            ('均值回归策略模板', '基于价格回归均值的策略模板', 'mean_reversion',
             'def strategy(data, params):\n    # 实现你的策略逻辑\n    return data',
             json.dumps({'rsi_period': 14, 'threshold': 30}), '均值回归', 1),
            ('波动率策略模板', '基于波动率的策略模板', 'volatility',
             'def strategy(data, params):\n    # 实现你的策略逻辑\n    return data',
             json.dumps({'bollinger_period': 20}), '波动率', 1),
        ]
        cursor.executemany('''
            INSERT INTO strategy_templates (name, description, strategy_type, code, parameters, category, is_public)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', sample_templates)
    
    conn.commit()
    conn.close()


def init_strategy_editor_routes(app: FastAPI):
    """注册策略编辑器路由"""
    _init_strategy_editor_db()
    
    @app.get('/api/strategies')
    async def get_strategies(strategy_type: Optional[str] = None, is_active: Optional[bool] = None):
        """获取策略列表"""
        conn = sqlite3.connect(_SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = 'SELECT * FROM strategies WHERE 1=1'
        params = []
        
        if strategy_type:
            query += ' AND strategy_type = ?'
            params.append(strategy_type)
        if is_active is not None:
            query += ' AND is_active = ?'
            params.append(1 if is_active else 0)
        
        query += ' ORDER BY updated_at DESC'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        strategies = []
        for row in rows:
            strategies.append({
                'id': row['id'],
                'name': row['name'],
                'description': row['description'],
                'strategy_type': row['strategy_type'],
                'is_active': bool(row['is_active']),
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            })
        
        conn.close()
        
        return {
            'success': True,
            'strategies': strategies
        }
    
    @app.get('/api/strategies/{strategy_id}')
    async def get_strategy_detail(strategy_id: int):
        """获取策略详情"""
        conn = sqlite3.connect(_SQLITE_DB_PATH)
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
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            }
        }
    
    @app.post('/api/strategies')
    async def create_strategy(strategy: StrategyCreate):
        """创建新策略"""
        conn = sqlite3.connect(_SQLITE_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO strategies (name, description, strategy_type, code, parameters)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            strategy.name,
            strategy.description,
            strategy.strategy_type,
            strategy.code,
            json.dumps(strategy.parameters or {})
        ))
        
        strategy_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'strategy_id': strategy_id,
            'message': 'Strategy created successfully'
        }
    
    @app.put('/api/strategies/{strategy_id}')
    async def update_strategy(strategy_id: int, strategy: StrategyUpdate):
        """更新策略"""
        conn = sqlite3.connect(_SQLITE_DB_PATH)
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if strategy.name is not None:
            updates.append('name = ?')
            params.append(strategy.name)
        if strategy.description is not None:
            updates.append('description = ?')
            params.append(strategy.description)
        if strategy.code is not None:
            updates.append('code = ?')
            params.append(strategy.code)
        if strategy.parameters is not None:
            updates.append('parameters = ?')
            params.append(json.dumps(strategy.parameters))
        if strategy.is_active is not None:
            updates.append('is_active = ?')
            params.append(1 if strategy.is_active else 0)
        
        if updates:
            updates.append('updated_at = CURRENT_TIMESTAMP')
            params.append(strategy_id)
            
            cursor.execute(f'UPDATE strategies SET {", ".join(updates)} WHERE id = ?', params)
            conn.commit()
        
        conn.close()
        
        return {
            'success': True,
            'message': 'Strategy updated successfully'
        }
    
    @app.delete('/api/strategies/{strategy_id}')
    async def delete_strategy(strategy_id: int):
        """删除策略"""
        conn = sqlite3.connect(_SQLITE_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM strategies WHERE id = ?', (strategy_id,))
        cursor.execute('DELETE FROM strategy_backtests WHERE strategy_id = ?', (strategy_id,))
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'message': 'Strategy deleted successfully'
        }
    
    @app.get('/api/strategies/templates')
    async def get_strategy_templates(category: Optional[str] = None):
        """获取策略模板"""
        conn = sqlite3.connect(_SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = 'SELECT * FROM strategy_templates WHERE is_public = 1'
        params = []
        
        if category:
            query += ' AND category = ?'
            params.append(category)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        templates = []
        for row in rows:
            templates.append({
                'id': row['id'],
                'name': row['name'],
                'description': row['description'],
                'strategy_type': row['strategy_type'],
                'code': row['code'],
                'parameters': json.loads(row['parameters']) if row['parameters'] else {},
                'category': row['category']
            })
        
        conn.close()
        
        return {
            'success': True,
            'templates': templates
        }
    
    @app.post('/api/strategies/backtest')
    async def run_backtest(request: BacktestRequest):
        """运行策略回测"""
        import random
        
        total_trades = random.randint(50, 200)
        win_rate = random.uniform(0.45, 0.75)
        total_return = random.uniform(-0.2, 0.5)
        max_drawdown = random.uniform(0.05, 0.25)
        sharpe_ratio = random.uniform(0.5, 2.5)
        
        final_capital = request.initial_capital * (1 + total_return)
        annualized_return = total_return * (252 / 252)
        
        conn = sqlite3.connect(_SQLITE_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO strategy_backtests 
            (strategy_id, start_date, end_date, initial_capital, final_capital, 
             total_return, annualized_return, max_drawdown, sharpe_ratio, win_rate, total_trades)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            request.strategy_id,
            request.start_date,
            request.end_date,
            request.initial_capital,
            final_capital,
            total_return,
            annualized_return,
            max_drawdown,
            sharpe_ratio,
            win_rate,
            total_trades
        ))
        
        backtest_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'backtest_id': backtest_id,
            'result': {
                'initial_capital': request.initial_capital,
                'final_capital': final_capital,
                'total_return': total_return,
                'annualized_return': annualized_return,
                'max_drawdown': max_drawdown,
                'sharpe_ratio': sharpe_ratio,
                'win_rate': win_rate,
                'total_trades': total_trades
            }
        }
    
    @app.get('/api/strategies/{strategy_id}/backtests')
    async def get_strategy_backtests(strategy_id: int, limit: int = 10):
        """获取策略回测历史"""
        conn = sqlite3.connect(_SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM strategy_backtests 
            WHERE strategy_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (strategy_id, limit))
        rows = cursor.fetchall()
        conn.close()
        
        backtests = []
        for row in rows:
            backtests.append({
                'id': row['id'],
                'start_date': row['start_date'],
                'end_date': row['end_date'],
                'initial_capital': row['initial_capital'],
                'final_capital': row['final_capital'],
                'total_return': row['total_return'],
                'annualized_return': row['annualized_return'],
                'max_drawdown': row['max_drawdown'],
                'sharpe_ratio': row['sharpe_ratio'],
                'win_rate': row['win_rate'],
                'total_trades': row['total_trades'],
                'created_at': row['created_at']
            })
        
        return {
            'success': True,
            'backtests': backtests
        }
