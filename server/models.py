from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Boolean, JSON, Index, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()


def utc_now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(100))
    created_at = Column(DateTime(timezone=True), default=utc_now)

    signals = relationship('Signal', back_populates='author', cascade='all, delete-orphan')
    replies = relationship('SignalReply', back_populates='author')
    participants = relationship('SignalParticipant', back_populates='user', cascade='all, delete-orphan')
    notifications = relationship('Notification', back_populates='user', cascade='all, delete-orphan')
    notification_settings = relationship('NotificationSetting', back_populates='user', uselist=False, cascade='all, delete-orphan')
    strategies = relationship('Strategy', back_populates='author', cascade='all, delete-orphan')
    user_stats = relationship('UserStats', back_populates='user', uselist=False, cascade='all, delete-orphan')
    auth_tokens = relationship('AuthToken', back_populates='user', cascade='all, delete-orphan')

    __table_args__ = (
        Index('idx_users_email', 'email', unique=True),
        Index('idx_users_username', 'username', unique=True),
    )


class AuthToken(Base):
    __tablename__ = 'auth_tokens'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    token = Column(String(255), nullable=False, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    user = relationship('User', back_populates='auth_tokens')

    __table_args__ = (
        Index('idx_auth_tokens_token', 'token', unique=True),
        Index('idx_auth_tokens_user_id', 'user_id'),
        Index('idx_auth_tokens_expires_at', 'expires_at'),
    )


class Signal(Base):
    __tablename__ = 'signals'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), index=True)
    agent_name = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    message_type = Column(String(50), default='operation', index=True)
    market = Column(String(50), default='us-stock', index=True)
    symbols = Column(JSON, default=list)
    quality_score = Column(Float)
    reply_count = Column(Integer, default=0)
    participant_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=utc_now, index=True)

    author = relationship('User', back_populates='signals')
    replies = relationship('SignalReply', back_populates='signal', cascade='all, delete-orphan')
    participants = relationship('SignalParticipant', back_populates='signal', cascade='all, delete-orphan')
    quality_scores = relationship('SignalQualityScore', back_populates='signal', uselist=False, cascade='all, delete-orphan')

    __table_args__ = (
        Index('idx_signals_market', 'market'),
        Index('idx_signals_message_type', 'message_type'),
        Index('idx_signals_created_at', text('created_at DESC')),
        Index('idx_signals_quality_score', text('quality_score DESC')),
    )


class SignalReply(Base):
    __tablename__ = 'signal_replies'

    id = Column(Integer, primary_key=True)
    signal_id = Column(Integer, ForeignKey('signals.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), index=True)
    user_name = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    parent_id = Column(Integer, ForeignKey('signal_replies.id', ondelete='SET NULL'), index=True)
    likes = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=utc_now, index=True)

    signal = relationship('Signal', back_populates='replies')
    author = relationship('User', back_populates='replies')
    parent = relationship('SignalReply', remote_side=[id], backref='children')

    __table_args__ = (
        Index('idx_signal_replies_signal_id', 'signal_id'),
        Index('idx_signal_replies_user_id', 'user_id'),
        Index('idx_signal_replies_parent_id', 'parent_id'),
        Index('idx_signal_replies_created_at', text('created_at DESC')),
    )


class SignalParticipant(Base):
    __tablename__ = 'signal_participants'

    id = Column(Integer, primary_key=True)
    signal_id = Column(Integer, ForeignKey('signals.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), index=True)
    user_name = Column(String(100), nullable=False)
    role = Column(String(50), default='follower', index=True)
    joined_at = Column(DateTime(timezone=True), default=utc_now)

    signal = relationship('Signal', back_populates='participants')
    user = relationship('User', back_populates='participants')

    __table_args__ = (
        Index('idx_signal_participants_signal_id', 'signal_id'),
        Index('idx_signal_participants_user_id', 'user_id'),
        Index('idx_signal_participants_signal_user', 'signal_id', 'user_id', unique=True),
        Index('idx_signal_participants_role', 'role'),
    )


class SignalQualityScore(Base):
    __tablename__ = 'signal_quality_scores'

    id = Column(Integer, primary_key=True)
    signal_id = Column(Integer, ForeignKey('signals.id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    accuracy_score = Column(Float)
    analysis_depth = Column(Float)
    risk_management = Column(Float)
    timeliness = Column(Float)
    clarity = Column(Float)
    total_score = Column(Float, index=True)

    signal = relationship('Signal', back_populates='quality_scores')

    __table_args__ = (
        Index('idx_signal_quality_scores_signal_id', 'signal_id', unique=True),
        Index('idx_signal_quality_scores_total_score', text('total_score DESC')),
    )


class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), index=True)
    priority = Column(String(20), default='normal', index=True)
    is_read = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, index=True)

    user = relationship('User', back_populates='notifications')

    __table_args__ = (
        Index('idx_notifications_user_id', 'user_id'),
        Index('idx_notifications_is_read', 'is_read'),
        Index('idx_notifications_created_at', text('created_at DESC')),
        Index('idx_notifications_type', 'notification_type'),
    )


class NotificationSetting(Base):
    __tablename__ = 'notification_settings'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    email_enabled = Column(Boolean, default=False)
    push_enabled = Column(Boolean, default=False)
    price_alerts = Column(Boolean, default=True)
    signal_alerts = Column(Boolean, default=True)
    risk_alerts = Column(Boolean, default=True)
    system_alerts = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    user = relationship('User', back_populates='notification_settings')

    __table_args__ = (
        Index('idx_notification_settings_user_id', 'user_id', unique=True),
    )


class Strategy(Base):
    __tablename__ = 'strategies'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    strategy_type = Column(String(50), index=True)
    code = Column(Text, nullable=False)
    parameters = Column(JSON, default=dict)
    is_active = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, index=True)

    author = relationship('User', back_populates='strategies')

    __table_args__ = (
        Index('idx_strategies_user_id', 'user_id'),
        Index('idx_strategies_type', 'strategy_type'),
        Index('idx_strategies_is_active', 'is_active'),
        Index('idx_strategies_created_at', text('created_at DESC')),
    )


class StrategyTemplate(Base):
    __tablename__ = 'strategy_templates'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    category = Column(String(50), index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    __table_args__ = (
        Index('idx_strategy_templates_category', 'category'),
        Index('idx_strategy_templates_name', 'name'),
    )


class UserStats(Base):
    __tablename__ = 'user_stats'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    total_pnl = Column(Float, default=0.0)
    win_rate = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    avg_win = Column(Float, default=0.0)
    avg_loss = Column(Float, default=0.0)
    profit_factor = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    user = relationship('User', back_populates='user_stats')

    __table_args__ = (
        Index('idx_user_stats_user_id', 'user_id', unique=True),
        Index('idx_user_stats_win_rate', text('win_rate DESC')),
        Index('idx_user_stats_total_pnl', text('total_pnl DESC')),
    )


class MarketNews(Base):
    __tablename__ = 'market_news'

    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False, index=True)
    content = Column(Text)
    source = Column(String(100), index=True)
    category = Column(String(50), index=True)
    symbol = Column(String(50), index=True)
    impact_score = Column(Integer, default=0, index=True)
    sentiment = Column(String(20), index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, index=True)

    __table_args__ = (
        Index('idx_market_news_category', 'category'),
        Index('idx_market_news_symbol', 'symbol'),
        Index('idx_market_news_created_at', text('created_at DESC')),
        Index('idx_market_news_impact_score', text('impact_score DESC')),
        Index('idx_market_news_sentiment', 'sentiment'),
    )


class MarketEvent(Base):
    __tablename__ = 'market_events'

    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False, index=True)
    date = Column(String(50))
    importance = Column(String(20), index=True)
    category = Column(String(50), index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    __table_args__ = (
        Index('idx_market_events_importance', 'importance'),
        Index('idx_market_events_category', 'category'),
        Index('idx_market_events_date', 'date'),
    )


class EconomicIndicator(Base):
    __tablename__ = 'economic_indicators'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    value = Column(Float)
    period = Column(String(50))
    category = Column(String(50), index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    __table_args__ = (
        Index('idx_economic_indicators_name', 'name'),
        Index('idx_economic_indicators_category', 'category'),
        Index('idx_economic_indicators_period', 'period'),
    )


class EmailConfig(Base):
    __tablename__ = 'email_configs'

    id = Column(Integer, primary_key=True)
    smtp_host = Column(String(255))
    smtp_port = Column(Integer)
    smtp_user = Column(String(255))
    smtp_password = Column(String(255))
    from_email = Column(String(255))
    enabled = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)


class Webhook(Base):
    __tablename__ = 'webhooks'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    url = Column(String(500), nullable=False)
    events = Column(JSON, default=list)
    active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    __table_args__ = (
        Index('idx_webhooks_active', 'active'),
        Index('idx_webhooks_name', 'name'),
    )


class ExchangeAccount(Base):
    __tablename__ = 'exchange_accounts'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    exchange = Column(String(50), nullable=False, index=True)
    account_name = Column(String(100))
    api_key = Column(String(255), nullable=False)
    api_secret = Column(String(255), nullable=False)
    passphrase = Column(String(255))
    is_sandbox = Column(Boolean, default=False, index=True)
    is_active = Column(Boolean, default=True, index=True)
    balance = Column(JSON, default=dict)
    last_sync_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=utc_now)

    __table_args__ = (
        Index('idx_exchange_accounts_user_id', 'user_id'),
        Index('idx_exchange_accounts_exchange', 'exchange'),
        Index('idx_exchange_accounts_is_active', 'is_active'),
    )


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    exchange_account_id = Column(Integer, ForeignKey('exchange_accounts.id', ondelete='SET NULL'), index=True)
    signal_id = Column(Integer, ForeignKey('signals.id', ondelete='SET NULL'), index=True)
    order_type = Column(String(20), nullable=False, index=True)
    side = Column(String(10), nullable=False, index=True)
    symbol = Column(String(50), nullable=False, index=True)
    quantity = Column(Float, nullable=False)
    price = Column(Float)
    stop_loss = Column(Float)
    take_profit = Column(Float)
    leverage = Column(Integer, default=1)
    status = Column(String(20), default='pending', index=True)
    exchange_order_id = Column(String(100), index=True)
    filled_quantity = Column(Float, default=0)
    avg_fill_price = Column(Float)
    is_simulation = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, index=True)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    __table_args__ = (
        Index('idx_orders_user_id', 'user_id'),
        Index('idx_orders_symbol', 'symbol'),
        Index('idx_orders_status', 'status'),
        Index('idx_orders_is_simulation', 'is_simulation'),
        Index('idx_orders_created_at', text('created_at DESC')),
    )


class Trade(Base):
    __tablename__ = 'trades'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey('orders.id', ondelete='SET NULL'), index=True)
    signal_id = Column(Integer, ForeignKey('signals.id', ondelete='SET NULL'), index=True)
    symbol = Column(String(50), nullable=False, index=True)
    side = Column(String(10), nullable=False)
    quantity = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float)
    pnl = Column(Float, default=0)
    pnl_percent = Column(Float, default=0)
    entry_time = Column(DateTime(timezone=True), nullable=False)
    exit_time = Column(DateTime(timezone=True))
    is_simulation = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, index=True)

    __table_args__ = (
        Index('idx_trades_user_id', 'user_id'),
        Index('idx_trades_symbol', 'symbol'),
        Index('idx_trades_is_simulation', 'is_simulation'),
        Index('idx_trades_created_at', text('created_at DESC')),
        Index('idx_trades_pnl', text('pnl DESC')),
    )


class Position(Base):
    __tablename__ = 'positions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    exchange_account_id = Column(Integer, ForeignKey('exchange_accounts.id', ondelete='SET NULL'), index=True)
    symbol = Column(String(50), nullable=False, index=True)
    side = Column(String(10), nullable=False)
    quantity = Column(Float, nullable=False)
    avg_entry_price = Column(Float, nullable=False)
    current_price = Column(Float)
    unrealized_pnl = Column(Float, default=0)
    unrealized_pnl_percent = Column(Float, default=0)
    leverage = Column(Integer, default=1)
    liquidation_price = Column(Float)
    is_simulation = Column(Boolean, default=False, index=True)
    opened_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    __table_args__ = (
        Index('idx_positions_user_id', 'user_id'),
        Index('idx_positions_symbol', 'symbol'),
        Index('idx_positions_is_simulation', 'is_simulation'),
        Index('idx_positions_user_symbol', 'user_id', 'symbol', unique=True),
    )


class Portfolio(Base):
    __tablename__ = 'portfolios'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    total_balance = Column(Float, default=0)
    available_balance = Column(Float, default=0)
    used_balance = Column(Float, default=0)
    unrealized_pnl = Column(Float, default=0)
    realized_pnl = Column(Float, default=0)
    total_pnl = Column(Float, default=0)
    daily_pnl = Column(Float, default=0)
    weekly_pnl = Column(Float, default=0)
    monthly_pnl = Column(Float, default=0)
    win_rate = Column(Float, default=0)
    profit_factor = Column(Float, default=0)
    sharpe_ratio = Column(Float, default=0)
    max_drawdown = Column(Float, default=0)
    is_simulation = Column(Boolean, default=False, index=True)
    last_updated = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    __table_args__ = (
        Index('idx_portfolios_user_id', 'user_id', unique=True),
        Index('idx_portfolios_is_simulation', 'is_simulation'),
    )


class UserFollow(Base):
    __tablename__ = 'user_follows'

    id = Column(Integer, primary_key=True)
    follower_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    following_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    __table_args__ = (
        Index('idx_user_follows_follower_id', 'follower_id'),
        Index('idx_user_follows_following_id', 'following_id'),
        Index('idx_user_follows_pair', 'follower_id', 'following_id', unique=True),
    )


class DirectMessage(Base):
    __tablename__ = 'direct_messages'

    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    receiver_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, index=True)

    __table_args__ = (
        Index('idx_direct_messages_sender_id', 'sender_id'),
        Index('idx_direct_messages_receiver_id', 'receiver_id'),
        Index('idx_direct_messages_conversation', 'sender_id', 'receiver_id'),
        Index('idx_direct_messages_created_at', text('created_at DESC')),
    )


class SignalShare(Base):
    __tablename__ = 'signal_shares'

    id = Column(Integer, primary_key=True)
    signal_id = Column(Integer, ForeignKey('signals.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    platform = Column(String(50), index=True)
    message = Column(Text)
    share_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), default=utc_now)

    __table_args__ = (
        Index('idx_signal_shares_signal_id', 'signal_id'),
        Index('idx_signal_shares_user_id', 'user_id'),
        Index('idx_signal_shares_platform', 'platform'),
    )


class Mention(Base):
    __tablename__ = 'mentions'

    id = Column(Integer, primary_key=True)
    mentioned_user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    mentioning_user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    signal_id = Column(Integer, ForeignKey('signals.id', ondelete='CASCADE'), index=True)
    reply_id = Column(Integer, ForeignKey('signal_replies.id', ondelete='CASCADE'), index=True)
    is_read = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, index=True)

    __table_args__ = (
        Index('idx_mentions_mentioned_user_id', 'mentioned_user_id'),
        Index('idx_mentions_mentioning_user_id', 'mentioning_user_id'),
        Index('idx_mentions_is_read', 'is_read'),
        Index('idx_mentions_created_at', text('created_at DESC')),
    )


class AISignal(Base):
    __tablename__ = 'ai_signals'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), index=True)
    symbol = Column(String(50), nullable=False, index=True)
    signal_type = Column(String(20), nullable=False, index=True)
    direction = Column(String(10), nullable=False)
    entry_price = Column(Float, nullable=False)
    stop_loss = Column(Float)
    take_profit = Column(Float)
    confidence = Column(Float, nullable=False, index=True)
    reasoning = Column(Text)
    indicators = Column(JSON, default=dict)
    market_conditions = Column(JSON, default=dict)
    status = Column(String(20), default='active', index=True)
    pnl = Column(Float, default=0)
    created_at = Column(DateTime(timezone=True), default=utc_now, index=True)

    __table_args__ = (
        Index('idx_ai_signals_user_id', 'user_id'),
        Index('idx_ai_signals_symbol', 'symbol'),
        Index('idx_ai_signals_status', 'status'),
        Index('idx_ai_signals_confidence', text('confidence DESC')),
        Index('idx_ai_signals_created_at', text('created_at DESC')),
    )


class AIAnalysis(Base):
    __tablename__ = 'ai_analyses'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    analysis_type = Column(String(50), nullable=False, index=True)
    symbol = Column(String(50), index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text)
    recommendations = Column(JSON, default=list)
    risk_score = Column(Float, index=True)
    metrics = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=utc_now, index=True)

    __table_args__ = (
        Index('idx_ai_analyses_user_id', 'user_id'),
        Index('idx_ai_analyses_type', 'analysis_type'),
        Index('idx_ai_analyses_symbol', 'symbol'),
        Index('idx_ai_analyses_created_at', text('created_at DESC')),
    )


class AIRiskAlert(Base):
    __tablename__ = 'ai_risk_alerts'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    alert_type = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), nullable=False, index=True)
    symbol = Column(String(50), index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    suggested_action = Column(Text)
    is_acknowledged = Column(Boolean, default=False, index=True)
    acknowledged_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=utc_now, index=True)

    __table_args__ = (
        Index('idx_ai_risk_alerts_user_id', 'user_id'),
        Index('idx_ai_risk_alerts_severity', 'severity'),
        Index('idx_ai_risk_alerts_is_acknowledged', 'is_acknowledged'),
        Index('idx_ai_risk_alerts_created_at', text('created_at DESC')),
    )


class AIStrategy(Base):
    __tablename__ = 'ai_strategies'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    strategy_code = Column(Text)
    parameters = Column(JSON, default=dict)
    backtest_results = Column(JSON, default=dict)
    performance_metrics = Column(JSON, default=dict)
    is_active = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, index=True)

    __table_args__ = (
        Index('idx_ai_strategies_user_id', 'user_id'),
        Index('idx_ai_strategies_is_active', 'is_active'),
        Index('idx_ai_strategies_created_at', text('created_at DESC')),
    )


class ApiRequestLog(Base):
    __tablename__ = 'api_request_logs'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), index=True)
    endpoint = Column(String(255), nullable=False, index=True)
    method = Column(String(10), nullable=False)
    status_code = Column(Integer, index=True)
    ip_address = Column(String(50), index=True)
    user_agent = Column(String(500))
    response_time = Column(Float)
    request_body = Column(JSON)
    response_body = Column(JSON)
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), default=utc_now, index=True)

    __table_args__ = (
        Index('idx_api_request_logs_user_id', 'user_id'),
        Index('idx_api_request_logs_endpoint', 'endpoint'),
        Index('idx_api_request_logs_ip_address', 'ip_address'),
        Index('idx_api_request_logs_created_at', text('created_at DESC')),
    )


class TwoFactorAuth(Base):
    __tablename__ = 'two_factor_auths'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    secret = Column(String(255), nullable=False)
    method = Column(String(20), default='totp', index=True)
    is_enabled = Column(Boolean, default=False, index=True)
    backup_codes = Column(JSON, default=list)
    last_used_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=utc_now)

    __table_args__ = (
        Index('idx_two_factor_auths_user_id', 'user_id', unique=True),
        Index('idx_two_factor_auths_is_enabled', 'is_enabled'),
    )


class OAuthAccount(Base):
    __tablename__ = 'oauth_accounts'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    provider = Column(String(50), nullable=False, index=True)
    provider_user_id = Column(String(255), nullable=False, index=True)
    email = Column(String(255))
    name = Column(String(255))
    avatar_url = Column(String(500))
    access_token = Column(String(500))
    refresh_token = Column(String(500))
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=utc_now)

    __table_args__ = (
        Index('idx_oauth_accounts_user_id', 'user_id'),
        Index('idx_oauth_accounts_provider', 'provider'),
        Index('idx_oauth_accounts_provider_user', 'provider', 'provider_user_id', unique=True),
    )


class AuditLog(Base):
    __tablename__ = 'audit_logs'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), index=True)
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), index=True)
    resource_id = Column(Integer, index=True)
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    old_values = Column(JSON)
    new_values = Column(JSON)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), default=utc_now, index=True)

    __table_args__ = (
        Index('idx_audit_logs_user_id', 'user_id'),
        Index('idx_audit_logs_action', 'action'),
        Index('idx_audit_logs_resource', 'resource_type', 'resource_id'),
        Index('idx_audit_logs_created_at', text('created_at DESC')),
    )


class PasswordHistory(Base):
    __tablename__ = 'password_histories'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    __table_args__ = (
        Index('idx_password_histories_user_id', 'user_id'),
        Index('idx_password_histories_created_at', text('created_at DESC')),
    )


class AnalyticsEvent(Base):
    __tablename__ = 'analytics_events'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), index=True)
    event_type = Column(String(100), nullable=False, index=True)
    event_name = Column(String(255), nullable=False, index=True)
    properties = Column(JSON, default=dict)
    url = Column(String(500))
    referrer = Column(String(500))
    user_agent = Column(String(500))
    ip_address = Column(String(50))
    session_id = Column(String(100), index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, index=True)

    __table_args__ = (
        Index('idx_analytics_events_user_id', 'user_id'),
        Index('idx_analytics_events_type', 'event_type'),
        Index('idx_analytics_events_name', 'event_name'),
        Index('idx_analytics_events_session_id', 'session_id'),
        Index('idx_analytics_events_created_at', text('created_at DESC')),
    )


class ABTest(Base):
    __tablename__ = 'ab_tests'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text)
    feature_name = Column(String(100), nullable=False, index=True)
    variants = Column(JSON, default=list)
    traffic_split = Column(JSON, default=dict)
    is_active = Column(Boolean, default=False, index=True)
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    metrics = Column(JSON, default=dict)
    results = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    __table_args__ = (
        Index('idx_ab_tests_name', 'name', unique=True),
        Index('idx_ab_tests_feature_name', 'feature_name'),
        Index('idx_ab_tests_is_active', 'is_active'),
    )


class AdminAction(Base):
    __tablename__ = 'admin_actions'

    id = Column(Integer, primary_key=True)
    admin_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    action = Column(String(100), nullable=False, index=True)
    target_user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), index=True)
    target_type = Column(String(50), index=True)
    target_id = Column(Integer, index=True)
    reason = Column(Text)
    details = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=utc_now, index=True)

    __table_args__ = (
        Index('idx_admin_actions_admin_id', 'admin_id'),
        Index('idx_admin_actions_action', 'action'),
        Index('idx_admin_actions_target_user_id', 'target_user_id'),
        Index('idx_admin_actions_created_at', text('created_at DESC')),
    )
