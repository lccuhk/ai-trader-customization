"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-05-31 20:43:45.184482

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('display_name', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    op.create_index('idx_users_email', 'users', ['email'], unique=True)
    op.create_index('idx_users_username', 'users', ['username'], unique=True)

    op.create_table('auth_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token')
    )
    op.create_index('idx_auth_tokens_token', 'auth_tokens', ['token'], unique=True)
    op.create_index('idx_auth_tokens_user_id', 'auth_tokens', ['user_id'], unique=False)
    op.create_index('idx_auth_tokens_expires_at', 'auth_tokens', ['expires_at'], unique=False)

    op.create_table('economic_indicators',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('value', sa.Float(), nullable=True),
        sa.Column('period', sa.String(length=50), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_economic_indicators_name', 'economic_indicators', ['name'], unique=False)
    op.create_index('idx_economic_indicators_category', 'economic_indicators', ['category'], unique=False)
    op.create_index('idx_economic_indicators_period', 'economic_indicators', ['period'], unique=False)

    op.create_table('email_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('smtp_host', sa.String(length=255), nullable=True),
        sa.Column('smtp_port', sa.Integer(), nullable=True),
        sa.Column('smtp_user', sa.String(length=255), nullable=True),
        sa.Column('smtp_password', sa.String(length=255), nullable=True),
        sa.Column('from_email', sa.String(length=255), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('market_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('date', sa.String(length=50), nullable=True),
        sa.Column('importance', sa.String(length=20), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_market_events_importance', 'market_events', ['importance'], unique=False)
    op.create_index('idx_market_events_category', 'market_events', ['category'], unique=False)
    op.create_index('idx_market_events_date', 'market_events', ['date'], unique=False)

    op.create_table('market_news',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('source', sa.String(length=100), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('symbol', sa.String(length=50), nullable=True),
        sa.Column('impact_score', sa.Integer(), nullable=True),
        sa.Column('sentiment', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_market_news_category', 'market_news', ['category'], unique=False)
    op.create_index('idx_market_news_symbol', 'market_news', ['symbol'], unique=False)
    op.create_index('idx_market_news_created_at', 'market_news', [text('created_at DESC')], unique=False)
    op.create_index('idx_market_news_impact_score', 'market_news', [text('impact_score DESC')], unique=False)
    op.create_index('idx_market_news_sentiment', 'market_news', ['sentiment'], unique=False)

    op.create_table('notification_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('email_enabled', sa.Boolean(), nullable=True),
        sa.Column('push_enabled', sa.Boolean(), nullable=True),
        sa.Column('price_alerts', sa.Boolean(), nullable=True),
        sa.Column('signal_alerts', sa.Boolean(), nullable=True),
        sa.Column('risk_alerts', sa.Boolean(), nullable=True),
        sa.Column('system_alerts', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index('idx_notification_settings_user_id', 'notification_settings', ['user_id'], unique=True)

    op.create_table('notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('notification_type', sa.String(length=50), nullable=True),
        sa.Column('priority', sa.String(length=20), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_notifications_user_id', 'notifications', ['user_id'], unique=False)
    op.create_index('idx_notifications_is_read', 'notifications', ['is_read'], unique=False)
    op.create_index('idx_notifications_created_at', 'notifications', [text('created_at DESC')], unique=False)
    op.create_index('idx_notifications_type', 'notifications', ['notification_type'], unique=False)

    op.create_table('signals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('agent_name', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('message_type', sa.String(length=50), nullable=True),
        sa.Column('market', sa.String(length=50), nullable=True),
        sa.Column('symbols', sa.JSON(), nullable=True),
        sa.Column('quality_score', sa.Float(), nullable=True),
        sa.Column('reply_count', sa.Integer(), nullable=True),
        sa.Column('participant_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_signals_market', 'signals', ['market'], unique=False)
    op.create_index('idx_signals_message_type', 'signals', ['message_type'], unique=False)
    op.create_index('idx_signals_created_at', 'signals', [text('created_at DESC')], unique=False)
    op.create_index('idx_signals_quality_score', 'signals', [text('quality_score DESC')], unique=False)

    op.create_table('signal_participants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('signal_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('user_name', sa.String(length=100), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=True),
        sa.Column('joined_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['signal_id'], ['signals.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('signal_id', 'user_id', name='idx_signal_participants_signal_user')
    )
    op.create_index('idx_signal_participants_signal_id', 'signal_participants', ['signal_id'], unique=False)
    op.create_index('idx_signal_participants_user_id', 'signal_participants', ['user_id'], unique=False)
    op.create_index('idx_signal_participants_role', 'signal_participants', ['role'], unique=False)

    op.create_table('signal_quality_scores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('signal_id', sa.Integer(), nullable=False),
        sa.Column('accuracy_score', sa.Float(), nullable=True),
        sa.Column('analysis_depth', sa.Float(), nullable=True),
        sa.Column('risk_management', sa.Float(), nullable=True),
        sa.Column('timeliness', sa.Float(), nullable=True),
        sa.Column('clarity', sa.Float(), nullable=True),
        sa.Column('total_score', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['signal_id'], ['signals.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('signal_id')
    )
    op.create_index('idx_signal_quality_scores_signal_id', 'signal_quality_scores', ['signal_id'], unique=True)
    op.create_index('idx_signal_quality_scores_total_score', 'signal_quality_scores', [text('total_score DESC')], unique=False)

    op.create_table('signal_replies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('signal_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('user_name', sa.String(length=100), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('likes', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['signal_replies.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['signal_id'], ['signals.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_signal_replies_signal_id', 'signal_replies', ['signal_id'], unique=False)
    op.create_index('idx_signal_replies_user_id', 'signal_replies', ['user_id'], unique=False)
    op.create_index('idx_signal_replies_parent_id', 'signal_replies', ['parent_id'], unique=False)
    op.create_index('idx_signal_replies_created_at', 'signal_replies', [text('created_at DESC')], unique=False)

    op.create_table('strategies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('strategy_type', sa.String(length=50), nullable=True),
        sa.Column('code', sa.Text(), nullable=False),
        sa.Column('parameters', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_strategies_user_id', 'strategies', ['user_id'], unique=False)
    op.create_index('idx_strategies_type', 'strategies', ['strategy_type'], unique=False)
    op.create_index('idx_strategies_is_active', 'strategies', ['is_active'], unique=False)
    op.create_index('idx_strategies_created_at', 'strategies', [text('created_at DESC')], unique=False)

    op.create_table('strategy_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_strategy_templates_category', 'strategy_templates', ['category'], unique=False)
    op.create_index('idx_strategy_templates_name', 'strategy_templates', ['name'], unique=False)

    op.create_table('user_stats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('total_trades', sa.Integer(), nullable=True),
        sa.Column('winning_trades', sa.Integer(), nullable=True),
        sa.Column('losing_trades', sa.Integer(), nullable=True),
        sa.Column('total_pnl', sa.Float(), nullable=True),
        sa.Column('win_rate', sa.Float(), nullable=True),
        sa.Column('sharpe_ratio', sa.Float(), nullable=True),
        sa.Column('max_drawdown', sa.Float(), nullable=True),
        sa.Column('avg_win', sa.Float(), nullable=True),
        sa.Column('avg_loss', sa.Float(), nullable=True),
        sa.Column('profit_factor', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index('idx_user_stats_user_id', 'user_stats', ['user_id'], unique=True)
    op.create_index('idx_user_stats_win_rate', 'user_stats', [text('win_rate DESC')], unique=False)
    op.create_index('idx_user_stats_total_pnl', 'user_stats', [text('total_pnl DESC')], unique=False)

    op.create_table('webhooks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=False),
        sa.Column('events', sa.JSON(), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_webhooks_active', 'webhooks', ['active'], unique=False)
    op.create_index('idx_webhooks_name', 'webhooks', ['name'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_webhooks_name', table_name='webhooks')
    op.drop_index('idx_webhooks_active', table_name='webhooks')
    op.drop_table('webhooks')

    op.drop_index('idx_user_stats_total_pnl', table_name='user_stats')
    op.drop_index('idx_user_stats_win_rate', table_name='user_stats')
    op.drop_index('idx_user_stats_user_id', table_name='user_stats')
    op.drop_table('user_stats')

    op.drop_index('idx_strategy_templates_name', table_name='strategy_templates')
    op.drop_index('idx_strategy_templates_category', table_name='strategy_templates')
    op.drop_table('strategy_templates')

    op.drop_index('idx_strategies_created_at', table_name='strategies')
    op.drop_index('idx_strategies_is_active', table_name='strategies')
    op.drop_index('idx_strategies_type', table_name='strategies')
    op.drop_index('idx_strategies_user_id', table_name='strategies')
    op.drop_table('strategies')

    op.drop_index('idx_signal_replies_created_at', table_name='signal_replies')
    op.drop_index('idx_signal_replies_parent_id', table_name='signal_replies')
    op.drop_index('idx_signal_replies_user_id', table_name='signal_replies')
    op.drop_index('idx_signal_replies_signal_id', table_name='signal_replies')
    op.drop_table('signal_replies')

    op.drop_index('idx_signal_quality_scores_total_score', table_name='signal_quality_scores')
    op.drop_index('idx_signal_quality_scores_signal_id', table_name='signal_quality_scores')
    op.drop_table('signal_quality_scores')

    op.drop_index('idx_signal_participants_role', table_name='signal_participants')
    op.drop_index('idx_signal_participants_user_id', table_name='signal_participants')
    op.drop_index('idx_signal_participants_signal_id', table_name='signal_participants')
    op.drop_table('signal_participants')

    op.drop_index('idx_signals_quality_score', table_name='signals')
    op.drop_index('idx_signals_created_at', table_name='signals')
    op.drop_index('idx_signals_message_type', table_name='signals')
    op.drop_index('idx_signals_market', table_name='signals')
    op.drop_table('signals')

    op.drop_index('idx_notifications_type', table_name='notifications')
    op.drop_index('idx_notifications_created_at', table_name='notifications')
    op.drop_index('idx_notifications_is_read', table_name='notifications')
    op.drop_index('idx_notifications_user_id', table_name='notifications')
    op.drop_table('notifications')

    op.drop_index('idx_notification_settings_user_id', table_name='notification_settings')
    op.drop_table('notification_settings')

    op.drop_index('idx_market_news_sentiment', table_name='market_news')
    op.drop_index('idx_market_news_impact_score', table_name='market_news')
    op.drop_index('idx_market_news_created_at', table_name='market_news')
    op.drop_index('idx_market_news_symbol', table_name='market_news')
    op.drop_index('idx_market_news_category', table_name='market_news')
    op.drop_table('market_news')

    op.drop_index('idx_market_events_date', table_name='market_events')
    op.drop_index('idx_market_events_category', table_name='market_events')
    op.drop_index('idx_market_events_importance', table_name='market_events')
    op.drop_table('market_events')

    op.drop_table('email_configs')

    op.drop_index('idx_economic_indicators_period', table_name='economic_indicators')
    op.drop_index('idx_economic_indicators_category', table_name='economic_indicators')
    op.drop_index('idx_economic_indicators_name', table_name='economic_indicators')
    op.drop_table('economic_indicators')

    op.drop_index('idx_auth_tokens_expires_at', table_name='auth_tokens')
    op.drop_index('idx_auth_tokens_user_id', table_name='auth_tokens')
    op.drop_index('idx_auth_tokens_token', table_name='auth_tokens')
    op.drop_table('auth_tokens')

    op.drop_index('idx_users_username', table_name='users')
    op.drop_index('idx_users_email', table_name='users')
    op.drop_table('users')
