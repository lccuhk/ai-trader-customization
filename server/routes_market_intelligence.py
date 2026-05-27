"""
Market Intelligence Routes

市场情报中心 API 路由
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from database import _SQLITE_DB_PATH


class NewsFilter(BaseModel):
    category: Optional[str] = None
    symbol: Optional[str] = None
    limit: int = 20
    offset: int = 0


class MarketEventFilter(BaseModel):
    event_type: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    limit: int = 20


def _init_market_intelligence_db():
    """初始化市场情报数据库表"""
    conn = sqlite3.connect(_SQLITE_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS market_news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
            source TEXT,
            category TEXT,
            symbol TEXT,
            impact_score INTEGER DEFAULT 50,
            sentiment TEXT DEFAULT 'neutral',
            url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS market_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            event_type TEXT,
            event_date TIMESTAMP,
            symbol TEXT,
            importance TEXT DEFAULT 'medium',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS market_sentiment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            sentiment_score REAL,
            bullish_percent REAL,
            bearish_percent REAL,
            neutral_percent REAL,
            volume_24h REAL,
            price_change_24h REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS economic_indicators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            value REAL,
            previous_value REAL,
            forecast_value REAL,
            unit TEXT,
            release_date TIMESTAMP,
            impact TEXT DEFAULT 'medium',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('SELECT COUNT(*) FROM market_news')
    if cursor.fetchone()[0] == 0:
        sample_news = [
            ('美联储暗示可能在年内降息', '美联储主席鲍威尔在最新讲话中暗示，如果通胀继续下降，美联储可能在年内开始降息。这一消息推动股市上涨。', 'Reuters', 'macro', 'SPY', 85, 'bullish', 'https://example.com/news/1'),
            ('英伟达发布新一代AI芯片，性能提升3倍', '英伟达在GTC大会上发布了新一代Blackwell架构AI芯片，性能较前代提升3倍。', 'TechCrunch', 'earnings', 'NVDA', 90, 'bullish', 'https://example.com/news/2'),
            ('苹果Vision Pro销量不及预期', '据供应链消息，苹果Vision Pro的销量低于公司预期，可能影响相关供应链企业。', 'Bloomberg', 'earnings', 'AAPL', 60, 'bearish', 'https://example.com/news/3'),
            ('特斯拉扩大超级充电网络', '特斯拉宣布将在全球范围内扩大超级充电网络，计划今年新增1万个充电桩。', 'WSJ', 'business', 'TSLA', 70, 'bullish', 'https://example.com/news/4'),
            ('微软Azure云服务增长超预期', '微软最新财报显示，Azure云服务营收增长28%，超出市场预期。', 'CNBC', 'earnings', 'MSFT', 80, 'bullish', 'https://example.com/news/5'),
            ('黄金价格创历史新高', '受地缘政治紧张和降息预期影响，黄金价格突破历史新高。', 'Financial Times', 'macro', 'GLD', 75, 'bullish', 'https://example.com/news/6'),
            ('比特币突破7万美元', '比特币价格突破7万美元大关，市场情绪极度乐观。', 'CoinDesk', 'crypto', 'BTC', 85, 'bullish', 'https://example.com/news/7'),
            ('亚马逊AWS推出新AI服务', '亚马逊AWS宣布推出一系列新的AI服务，包括Bedrock升级和新的训练芯片。', 'AWS Blog', 'business', 'AMZN', 75, 'bullish', 'https://example.com/news/8'),
        ]
        cursor.executemany('''
            INSERT INTO market_news (title, content, source, category, symbol, impact_score, sentiment, url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_news)
    
    cursor.execute('SELECT COUNT(*) FROM market_events')
    if cursor.fetchone()[0] == 0:
        now = datetime.now()
        sample_events = [
            ('美联储利率决议', '美联储FOMC会议，市场预期维持利率不变', 'fed', (now + timedelta(days=5)).isoformat(), None, 'high'),
            ('英伟达财报', '英伟达Q1财报发布，市场关注AI业务增长', 'earnings', (now + timedelta(days=10)).isoformat(), 'NVDA', 'high'),
            ('苹果发布会', '苹果春季发布会，可能发布新产品', 'event', (now + timedelta(days=15)).isoformat(), 'AAPL', 'medium'),
            ('非农就业数据', '美国非农就业数据发布', 'economic', (now + timedelta(days=3)).isoformat(), None, 'high'),
            ('CPI数据发布', '美国消费者价格指数', 'economic', (now + timedelta(days=7)).isoformat(), None, 'high'),
            ('特斯拉股东大会', '特斯拉年度股东大会', 'event', (now + timedelta(days=20)).isoformat(), 'TSLA', 'medium'),
        ]
        cursor.executemany('''
            INSERT INTO market_events (title, description, event_type, event_date, symbol, importance)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', sample_events)
    
    cursor.execute('SELECT COUNT(*) FROM market_sentiment')
    if cursor.fetchone()[0] == 0:
        sample_sentiment = [
            ('AAPL', 0.65, 55, 25, 20, 50000000, 2.5),
            ('NVDA', 0.85, 75, 15, 10, 80000000, 5.2),
            ('TSLA', 0.45, 40, 45, 15, 60000000, -1.8),
            ('MSFT', 0.70, 60, 20, 20, 45000000, 1.2),
            ('GOOGL', 0.55, 45, 30, 25, 35000000, 0.8),
            ('AMZN', 0.60, 50, 30, 20, 40000000, 1.5),
            ('META', 0.65, 55, 25, 20, 30000000, 2.0),
            ('BTC', 0.80, 70, 20, 10, 500000000, 8.5),
        ]
        cursor.executemany('''
            INSERT INTO market_sentiment (symbol, sentiment_score, bullish_percent, bearish_percent, neutral_percent, volume_24h, price_change_24h)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', sample_sentiment)
    
    cursor.execute('SELECT COUNT(*) FROM economic_indicators')
    if cursor.fetchone()[0] == 0:
        sample_indicators = [
            ('联邦基金利率', 5.25, 5.25, 5.25, '%', (now - timedelta(days=30)).isoformat(), 'high'),
            ('CPI同比', 3.2, 3.1, 3.3, '%', (now - timedelta(days=15)).isoformat(), 'high'),
            ('失业率', 3.8, 3.9, 3.8, '%', (now - timedelta(days=10)).isoformat(), 'high'),
            ('GDP环比', 3.2, 4.9, 3.0, '%', (now - timedelta(days=20)).isoformat(), 'high'),
            ('非农就业', 275000, 229000, 200000, '人', (now - timedelta(days=5)).isoformat(), 'high'),
            ('零售销售', 0.6, 0.8, 0.4, '%', (now - timedelta(days=12)).isoformat(), 'medium'),
        ]
        cursor.executemany('''
            INSERT INTO economic_indicators (name, value, previous_value, forecast_value, unit, release_date, impact)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', sample_indicators)
    
    conn.commit()
    conn.close()


def init_market_intelligence_routes(app: FastAPI):
    """注册市场情报路由"""
    _init_market_intelligence_db()
    
    @app.get('/api/market/news')
    async def get_market_news(category: Optional[str] = None, symbol: Optional[str] = None, limit: int = 20, offset: int = 0):
        """获取市场新闻"""
        conn = sqlite3.connect(_SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = 'SELECT * FROM market_news WHERE 1=1'
        params = []
        
        if category:
            query += ' AND category = ?'
            params.append(category)
        if symbol:
            query += ' AND symbol = ?'
            params.append(symbol)
        
        query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
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
                'url': row['url'],
                'created_at': row['created_at']
            })
        
        conn.close()
        
        return {
            'success': True,
            'news': news,
            'total': len(news)
        }
    
    @app.get('/api/market/news/{news_id}')
    async def get_news_detail(news_id: int):
        """获取新闻详情"""
        conn = sqlite3.connect(_SQLITE_DB_PATH)
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
                'url': row['url'],
                'created_at': row['created_at']
            }
        }
    
    @app.get('/api/market/events')
    async def get_market_events(event_type: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None, limit: int = 20):
        """获取市场事件日历"""
        conn = sqlite3.connect(_SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = 'SELECT * FROM market_events WHERE 1=1'
        params = []
        
        if event_type:
            query += ' AND event_type = ?'
            params.append(event_type)
        if start_date:
            query += ' AND event_date >= ?'
            params.append(start_date)
        if end_date:
            query += ' AND event_date <= ?'
            params.append(end_date)
        
        query += ' ORDER BY event_date ASC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        events = []
        for row in rows:
            events.append({
                'id': row['id'],
                'title': row['title'],
                'description': row['description'],
                'event_type': row['event_type'],
                'event_date': row['event_date'],
                'symbol': row['symbol'],
                'importance': row['importance']
            })
        
        conn.close()
        
        return {
            'success': True,
            'events': events
        }
    
    @app.get('/api/market/sentiment')
    async def get_market_sentiment(symbol: Optional[str] = None):
        """获取市场情绪数据"""
        conn = sqlite3.connect(_SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if symbol:
            cursor.execute('SELECT * FROM market_sentiment WHERE symbol = ? ORDER BY created_at DESC LIMIT 1', (symbol,))
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                raise HTTPException(status_code=404, detail='Sentiment data not found')
            
            return {
                'success': True,
                'sentiment': {
                    'symbol': row['symbol'],
                    'sentiment_score': row['sentiment_score'],
                    'bullish_percent': row['bullish_percent'],
                    'bearish_percent': row['bearish_percent'],
                    'neutral_percent': row['neutral_percent'],
                    'volume_24h': row['volume_24h'],
                    'price_change_24h': row['price_change_24h']
                }
            }
        
        cursor.execute('SELECT * FROM market_sentiment ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        
        sentiments = []
        for row in rows:
            sentiments.append({
                'symbol': row['symbol'],
                'sentiment_score': row['sentiment_score'],
                'bullish_percent': row['bullish_percent'],
                'bearish_percent': row['bearish_percent'],
                'neutral_percent': row['neutral_percent'],
                'volume_24h': row['volume_24h'],
                'price_change_24h': row['price_change_24h']
            })
        
        return {
            'success': True,
            'sentiments': sentiments
        }
    
    @app.get('/api/market/indicators')
    async def get_economic_indicators(limit: int = 10):
        """获取经济指标"""
        conn = sqlite3.connect(_SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM economic_indicators ORDER BY release_date DESC LIMIT ?', (limit,))
        rows = cursor.fetchall()
        conn.close()
        
        indicators = []
        for row in rows:
            value_change = None
            if row['value'] is not None and row['previous_value'] is not None:
                value_change = row['value'] - row['previous_value']
            
            indicators.append({
                'id': row['id'],
                'name': row['name'],
                'value': row['value'],
                'previous_value': row['previous_value'],
                'forecast_value': row['forecast_value'],
                'value_change': value_change,
                'unit': row['unit'],
                'release_date': row['release_date'],
                'impact': row['impact']
            })
        
        return {
            'success': True,
            'indicators': indicators
        }
    
    @app.get('/api/market/dashboard')
    async def get_market_dashboard():
        """获取市场情报仪表盘汇总数据"""
        conn = sqlite3.connect(_SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as count FROM market_news WHERE created_at >= datetime("now", "-24 hours")')
        news_24h = cursor.fetchone()['count']
        
        cursor.execute('SELECT sentiment, COUNT(*) as count FROM market_news GROUP BY sentiment')
        sentiment_counts = {row['sentiment']: row['count'] for row in cursor.fetchall()}
        
        cursor.execute('SELECT event_type, COUNT(*) as count FROM market_events WHERE event_date >= datetime("now") GROUP BY event_type')
        upcoming_events = {row['event_type']: row['count'] for row in cursor.fetchall()}
        
        cursor.execute('SELECT AVG(sentiment_score) as avg_score FROM market_sentiment')
        avg_sentiment = cursor.fetchone()['avg_score']
        
        conn.close()
        
        return {
            'success': True,
            'dashboard': {
                'news_24h': news_24h,
                'sentiment_breakdown': {
                    'bullish': sentiment_counts.get('bullish', 0),
                    'bearish': sentiment_counts.get('bearish', 0),
                    'neutral': sentiment_counts.get('neutral', 0)
                },
                'upcoming_events': upcoming_events,
                'average_market_sentiment': avg_sentiment or 0.5
            }
        }
