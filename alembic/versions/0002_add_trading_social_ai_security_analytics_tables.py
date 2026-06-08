"""add trading social ai security analytics tables

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-31 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


revision: str = '0002'
down_revision: Union[str, None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('exchange_accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('exchange', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=True),
        sa.Column('api_key', sa.String(length=255), nullable=False),
        sa.Column('api_secret', sa.String(length=255), nullable=False),
        sa.Column('passphrase', sa.String(length=255), nullable=True),
        sa.Column('is_sandbox', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_exchange_accounts_user_id', 'exchange_accounts', ['user_id'], unique=False)
    op.create_index('idx_exchange_accounts_exchange', 'exchange_accounts', ['exchange'], unique=False)
    op.create_index('idx_exchange_accounts_is_active', 'exchange_accounts', ['is_active'], unique=False)

    op.create_table('portfolios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('total_balance', sa.Float(), nullable=True),
        sa.Column('total_pnl', sa.Float(), nullable=True),
        sa.Column('unrealized_pnl', sa.Float(), nullable=True),
        sa.Column('total_value', sa.Float(), nullable=True),
        sa.Column('win_rate', sa.Float(), nullable=True),
        sa.Column('total_trades', sa.Integer(), nullable=True),
        sa.Column('is_simulation', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'is_simulation', name='uq_user_simulation_portfolio')
    )
    op.create_index('idx_portfolios_user_id', 'portfolios', ['user_id'], unique=False)
    op.create_index('idx_portfolios_is_simulation', 'portfolios', ['is_simulation'], unique=False)

    op.create_table('orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('exchange_account_id', sa.Integer(), nullable=True),
        sa.Column('signal_id', sa.Integer(), nullable=True),
        sa.Column('symbol', sa.String(length=50), nullable=False),
        sa.Column('side', sa.String(length=10), nullable=False),
        sa.Column('order_type', sa.String(length=20), nullable=False),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.Column('price', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('filled_price', sa.Float(), nullable=True),
        sa.Column('filled_quantity', sa.Float(), nullable=True),
        sa.Column('exchange_order_id', sa.String(length=100), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('is_simulation', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('filled_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['exchange_account_id'], ['exchange_accounts.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['signal_id'], ['signals.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_orders_user_id', 'orders', ['user_id'], unique=False)
    op.create_index('idx_orders_symbol', 'orders', ['symbol'], unique=False)
    op.create_index('idx_orders_status', 'orders', ['status'], unique=False)
    op.create_index('idx_orders_side', 'orders', ['side'], unique=False)
    op.create_index('idx_orders_is_simulation', 'orders', ['is_simulation'], unique=False)
    op.create_index('idx_orders_created_at', 'orders', [text('created_at DESC')], unique=False)

    op.create_table('positions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(length=50), nullable=False),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.Column('avg_price', sa.Float(), nullable=False),
        sa.Column('current_price', sa.Float(), nullable=True),
        sa.Column('unrealized_pnl', sa.Float(), nullable=True),
        sa.Column('is_simulation', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_positions_user_id', 'positions', ['user_id'], unique=False)
    op.create_index('idx_positions_symbol', 'positions', ['symbol'], unique=False)
    op.create_index('idx_positions_is_simulation', 'positions', ['is_simulation'], unique=False)

    op.create_table('trades',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=True),
        sa.Column('signal_id', sa.Integer(), nullable=True),
        sa.Column('symbol', sa.String(length=50), nullable=False),
        sa.Column('side', sa.String(length=10), nullable=False),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('pnl', sa.Float(), nullable=True),
        sa.Column('pnl_percent', sa.Float(), nullable=True),
        sa.Column('is_simulation', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['signal_id'], ['signals.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_trades_user_id', 'trades', ['user_id'], unique=False)
    op.create_index('idx_trades_symbol', 'trades', ['symbol'], unique=False)
    op.create_index('idx_trades_is_simulation', 'trades', ['is_simulation'], unique=False)
    op.create_index('idx_trades_created_at', 'trades', [text('created_at DESC')], unique=False)

    op.create_table('user_follows',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('follower_id', sa.Integer(), nullable=False),
        sa.Column('following_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['follower_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['following_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('follower_id', 'following_id', name='idx_user_follows_pair')
    )
    op.create_index('idx_user_follows_follower_id', 'user_follows', ['follower_id'], unique=False)
    op.create_index('idx_user_follows_following_id', 'user_follows', ['following_id'], unique=False)

    op.create_table('direct_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sender_id', sa.Integer(), nullable=False),
        sa.Column('receiver_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['receiver_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_direct_messages_sender_id', 'direct_messages', ['sender_id'], unique=False)
    op.create_index('idx_direct_messages_receiver_id', 'direct_messages', ['receiver_id'], unique=False)
    op.create_index('idx_direct_messages_is_read', 'direct_messages', ['is_read'], unique=False)
    op.create_index('idx_direct_messages_created_at', 'direct_messages', [text('created_at DESC')], unique=False)

    op.create_table('mentions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('mentioned_user_id', sa.Integer(), nullable=False),
        sa.Column('mentioning_user_id', sa.Integer(), nullable=False),
        sa.Column('signal_id', sa.Integer(), nullable=True),
        sa.Column('reply_id', sa.Integer(), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['mentioned_user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['mentioning_user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reply_id'], ['signal_replies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['signal_id'], ['signals.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_mentions_mentioned_user_id', 'mentions', ['mentioned_user_id'], unique=False)
    op.create_index('idx_mentions_mentioning_user_id', 'mentions', ['mentioning_user_id'], unique=False)
    op.create_index('idx_mentions_signal_id', 'mentions', ['signal_id'], unique=False)
    op.create_index('idx_mentions_is_read', 'mentions', ['is_read'], unique=False)

    op.create_table('ai_signals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('symbol', sa.String(length=50), nullable=False),
        sa.Column('direction', sa.String(length=10), nullable=False),
        sa.Column('entry_price', sa.Float(), nullable=True),
        sa.Column('take_profit', sa.Float(), nullable=True),
        sa.Column('stop_loss', sa.Float(), nullable=True),
        sa.Column('current_price', sa.Float(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('reasoning', sa.Text(), nullable=True),
        sa.Column('strategy', sa.String(length=50), nullable=True),
        sa.Column('risk_level', sa.String(length=20), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('pnl', sa.Float(), nullable=True),
        sa.Column('pnl_percent', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_ai_signals_user_id', 'ai_signals', ['user_id'], unique=False)
    op.create_index('idx_ai_signals_symbol', 'ai_signals', ['symbol'], unique=False)
    op.create_index('idx_ai_signals_status', 'ai_signals', ['status'], unique=False)
    op.create_index('idx_ai_signals_confidence', 'ai_signals', ['confidence'], unique=False)

    op.create_table('ai_analyses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('analysis_type', sa.String(length=50), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('strengths', sa.JSON(), nullable=True),
        sa.Column('weaknesses', sa.JSON(), nullable=True),
        sa.Column('recommendations', sa.JSON(), nullable=True),
        sa.Column('risk_score', sa.Float(), nullable=True),
        sa.Column('performance_metrics', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_ai_analyses_user_id', 'ai_analyses', ['user_id'], unique=False)
    op.create_index('idx_ai_analyses_analysis_type', 'ai_analyses', ['analysis_type'], unique=False)
    op.create_index('idx_ai_analyses_risk_score', 'ai_analyses', ['risk_score'], unique=False)

    op.create_table('ai_risk_alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('suggested_action', sa.Text(), nullable=True),
        sa.Column('is_acknowledged', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_ai_risk_alerts_user_id', 'ai_risk_alerts', ['user_id'], unique=False)
    op.create_index('idx_ai_risk_alerts_severity', 'ai_risk_alerts', ['severity'], unique=False)
    op.create_index('idx_ai_risk_alerts_is_acknowledged', 'ai_risk_alerts', ['is_acknowledged'], unique=False)

    op.create_table('ai_strategies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('strategy_type', sa.String(length=50), nullable=True),
        sa.Column('strategy_code', sa.Text(), nullable=True),
        sa.Column('parameters', sa.JSON(), nullable=True),
        sa.Column('risk_level', sa.String(length=20), nullable=True),
        sa.Column('target_symbols', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('backtest_results', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_backtest_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_ai_strategies_user_id', 'ai_strategies', ['user_id'], unique=False)
    op.create_index('idx_ai_strategies_is_active', 'ai_strategies', ['is_active'], unique=False)

    op.create_table('two_factor_auths',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('secret', sa.String(length=255), nullable=False),
        sa.Column('method', sa.String(length=20), nullable=True),
        sa.Column('backup_codes', sa.JSON(), nullable=True),
        sa.Column('is_enabled', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index('idx_two_factor_auths_user_id', 'two_factor_auths', ['user_id'], unique=True)
    op.create_index('idx_two_factor_auths_method', 'two_factor_auths', ['method'], unique=False)
    op.create_index('idx_two_factor_auths_is_enabled', 'two_factor_auths', ['is_enabled'], unique=False)

    op.create_table('oauth_accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('provider_user_id', sa.String(length=255), nullable=False),
        sa.Column('access_token', sa.String(length=500), nullable=True),
        sa.Column('refresh_token', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_oauth_accounts_user_id', 'oauth_accounts', ['user_id'], unique=False)
    op.create_index('idx_oauth_accounts_provider', 'oauth_accounts', ['provider'], unique=False)
    op.create_index('idx_oauth_accounts_provider_user_id', 'oauth_accounts', ['provider_user_id'], unique=False)

    op.create_table('password_histories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_password_histories_user_id', 'password_histories', ['user_id'], unique=False)

    op.create_table('audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=True),
        sa.Column('resource_id', sa.Integer(), nullable=True),
        sa.Column('old_values', sa.JSON(), nullable=True),
        sa.Column('new_values', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_audit_logs_user_id', 'audit_logs', ['user_id'], unique=False)
    op.create_index('idx_audit_logs_action', 'audit_logs', ['action'], unique=False)
    op.create_index('idx_audit_logs_resource_type', 'audit_logs', ['resource_type'], unique=False)
    op.create_index('idx_audit_logs_created_at', 'audit_logs', [text('created_at DESC')], unique=False)

    op.create_table('analytics_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('event_name', sa.String(length=255), nullable=False),
        sa.Column('properties', sa.JSON(), nullable=True),
        sa.Column('session_id', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_analytics_events_user_id', 'analytics_events', ['user_id'], unique=False)
    op.create_index('idx_analytics_events_event_type', 'analytics_events', ['event_type'], unique=False)
    op.create_index('idx_analytics_events_event_name', 'analytics_events', ['event_name'], unique=False)
    op.create_index('idx_analytics_events_session_id', 'analytics_events', ['session_id'], unique=False)

    op.create_table('ab_tests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('feature_name', sa.String(length=100), nullable=False),
        sa.Column('variants', sa.JSON(), nullable=True),
        sa.Column('traffic_split', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('results', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_ab_tests_name', 'ab_tests', ['name'], unique=True)
    op.create_index('idx_ab_tests_feature_name', 'ab_tests', ['feature_name'], unique=False)
    op.create_index('idx_ab_tests_is_active', 'ab_tests', ['is_active'], unique=False)

    op.create_table('admin_actions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admin_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('target_user_id', sa.Integer(), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['admin_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_admin_actions_admin_id', 'admin_actions', ['admin_id'], unique=False)
    op.create_index('idx_admin_actions_action', 'admin_actions', ['action'], unique=False)
    op.create_index('idx_admin_actions_target_user_id', 'admin_actions', ['target_user_id'], unique=False)

    op.create_table('api_request_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('endpoint', sa.String(length=255), nullable=False),
        sa.Column('method', sa.String(length=10), nullable=False),
        sa.Column('status_code', sa.Integer(), nullable=True),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.Column('response_time', sa.Float(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_api_request_logs_user_id', 'api_request_logs', ['user_id'], unique=False)
    op.create_index('idx_api_request_logs_endpoint', 'api_request_logs', ['endpoint'], unique=False)
    op.create_index('idx_api_request_logs_status_code', 'api_request_logs', ['status_code'], unique=False)
    op.create_index('idx_api_request_logs_ip_address', 'api_request_logs', ['ip_address'], unique=False)

    op.add_column('users', sa.Column('avatar_url', sa.String(length=500), nullable=True))
    op.add_column('users', sa.Column('bio', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('location', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('website', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('role', sa.String(length=20), nullable=True, server_default='user'))
    op.add_column('users', sa.Column('is_verified', sa.Boolean(), nullable=True, server_default=sa.text('false')))
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=True, server_default=sa.text('true')))
    op.add_column('users', sa.Column('follower_count', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('users', sa.Column('following_count', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('users', sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))

    op.add_column('signals', sa.Column('is_simulation', sa.Boolean(), nullable=True, server_default=sa.text('true')))
    op.add_column('signals', sa.Column('moderation_status', sa.String(length=20), nullable=True, server_default='pending'))


def downgrade() -> None:
    op.drop_index('idx_api_request_logs_ip_address', table_name='api_request_logs')
    op.drop_index('idx_api_request_logs_status_code', table_name='api_request_logs')
    op.drop_index('idx_api_request_logs_endpoint', table_name='api_request_logs')
    op.drop_index('idx_api_request_logs_user_id', table_name='api_request_logs')
    op.drop_table('api_request_logs')

    op.drop_index('idx_admin_actions_target_user_id', table_name='admin_actions')
    op.drop_index('idx_admin_actions_action', table_name='admin_actions')
    op.drop_index('idx_admin_actions_admin_id', table_name='admin_actions')
    op.drop_table('admin_actions')

    op.drop_index('idx_ab_tests_is_active', table_name='ab_tests')
    op.drop_index('idx_ab_tests_feature_name', table_name='ab_tests')
    op.drop_index('idx_ab_tests_name', table_name='ab_tests')
    op.drop_table('ab_tests')

    op.drop_index('idx_analytics_events_session_id', table_name='analytics_events')
    op.drop_index('idx_analytics_events_event_name', table_name='analytics_events')
    op.drop_index('idx_analytics_events_event_type', table_name='analytics_events')
    op.drop_index('idx_analytics_events_user_id', table_name='analytics_events')
    op.drop_table('analytics_events')

    op.drop_index('idx_audit_logs_created_at', table_name='audit_logs')
    op.drop_index('idx_audit_logs_resource_type', table_name='audit_logs')
    op.drop_index('idx_audit_logs_action', table_name='audit_logs')
    op.drop_index('idx_audit_logs_user_id', table_name='audit_logs')
    op.drop_table('audit_logs')

    op.drop_index('idx_password_histories_user_id', table_name='password_histories')
    op.drop_table('password_histories')

    op.drop_index('idx_oauth_accounts_provider_user_id', table_name='oauth_accounts')
    op.drop_index('idx_oauth_accounts_provider', table_name='oauth_accounts')
    op.drop_index('idx_oauth_accounts_user_id', table_name='oauth_accounts')
    op.drop_table('oauth_accounts')

    op.drop_index('idx_two_factor_auths_is_enabled', table_name='two_factor_auths')
    op.drop_index('idx_two_factor_auths_method', table_name='two_factor_auths')
    op.drop_index('idx_two_factor_auths_user_id', table_name='two_factor_auths')
    op.drop_table('two_factor_auths')

    op.drop_index('idx_ai_strategies_is_active', table_name='ai_strategies')
    op.drop_index('idx_ai_strategies_user_id', table_name='ai_strategies')
    op.drop_table('ai_strategies')

    op.drop_index('idx_ai_risk_alerts_is_acknowledged', table_name='ai_risk_alerts')
    op.drop_index('idx_ai_risk_alerts_severity', table_name='ai_risk_alerts')
    op.drop_index('idx_ai_risk_alerts_user_id', table_name='ai_risk_alerts')
    op.drop_table('ai_risk_alerts')

    op.drop_index('idx_ai_analyses_risk_score', table_name='ai_analyses')
    op.drop_index('idx_ai_analyses_analysis_type', table_name='ai_analyses')
    op.drop_index('idx_ai_analyses_user_id', table_name='ai_analyses')
    op.drop_table('ai_analyses')

    op.drop_index('idx_ai_signals_confidence', table_name='ai_signals')
    op.drop_index('idx_ai_signals_status', table_name='ai_signals')
    op.drop_index('idx_ai_signals_symbol', table_name='ai_signals')
    op.drop_index('idx_ai_signals_user_id', table_name='ai_signals')
    op.drop_table('ai_signals')

    op.drop_index('idx_mentions_is_read', table_name='mentions')
    op.drop_index('idx_mentions_signal_id', table_name='mentions')
    op.drop_index('idx_mentions_mentioning_user_id', table_name='mentions')
    op.drop_index('idx_mentions_mentioned_user_id', table_name='mentions')
    op.drop_table('mentions')

    op.drop_index('idx_direct_messages_created_at', table_name='direct_messages')
    op.drop_index('idx_direct_messages_is_read', table_name='direct_messages')
    op.drop_index('idx_direct_messages_receiver_id', table_name='direct_messages')
    op.drop_index('idx_direct_messages_sender_id', table_name='direct_messages')
    op.drop_table('direct_messages')

    op.drop_index('idx_user_follows_following_id', table_name='user_follows')
    op.drop_index('idx_user_follows_follower_id', table_name='user_follows')
    op.drop_table('user_follows')

    op.drop_index('idx_trades_created_at', table_name='trades')
    op.drop_index('idx_trades_is_simulation', table_name='trades')
    op.drop_index('idx_trades_symbol', table_name='trades')
    op.drop_index('idx_trades_user_id', table_name='trades')
    op.drop_table('trades')

    op.drop_index('idx_positions_is_simulation', table_name='positions')
    op.drop_index('idx_positions_symbol', table_name='positions')
    op.drop_index('idx_positions_user_id', table_name='positions')
    op.drop_table('positions')

    op.drop_index('idx_orders_created_at', table_name='orders')
    op.drop_index('idx_orders_is_simulation', table_name='orders')
    op.drop_index('idx_orders_side', table_name='orders')
    op.drop_index('idx_orders_status', table_name='orders')
    op.drop_index('idx_orders_symbol', table_name='orders')
    op.drop_index('idx_orders_user_id', table_name='orders')
    op.drop_table('orders')

    op.drop_index('idx_portfolios_is_simulation', table_name='portfolios')
    op.drop_index('idx_portfolios_user_id', table_name='portfolios')
    op.drop_table('portfolios')

    op.drop_index('idx_exchange_accounts_is_active', table_name='exchange_accounts')
    op.drop_index('idx_exchange_accounts_exchange', table_name='exchange_accounts')
    op.drop_index('idx_exchange_accounts_user_id', table_name='exchange_accounts')
    op.drop_table('exchange_accounts')

    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'last_login_at')
    op.drop_column('users', 'following_count')
    op.drop_column('users', 'follower_count')
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'is_verified')
    op.drop_column('users', 'role')
    op.drop_column('users', 'website')
    op.drop_column('users', 'location')
    op.drop_column('users', 'bio')
    op.drop_column('users', 'avatar_url')

    op.drop_column('signals', 'moderation_status')
    op.drop_column('signals', 'is_simulation')
