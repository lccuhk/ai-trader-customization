"""
SQLite to PostgreSQL Data Migration Script

This script migrates all data from SQLite to PostgreSQL.
"""

import os
import sys
import sqlite3
import json
import traceback
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLITE_DB_PATH = os.path.join(BASE_DIR, 'data', 'clawtrader.db')

POSTGRESQL_URL = os.getenv('POSTGRESQL_URL')

try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import QueuePool
    import psycopg2
except ImportError:
    print("ERROR: Required packages not installed")
    print("Please run: pip install sqlalchemy psycopg2-binary")
    sys.exit(1)

TABLE_ORDER = [
    'users',
    'auth_tokens',
    'user_stats',
    'notification_settings',
    'notifications',
    'strategies',
    'strategy_templates',
    'market_news',
    'market_events',
    'economic_indicators',
    'signals',
    'signal_quality_scores',
    'signal_replies',
    'signal_participants',
    'email_configs',
    'webhooks',
]

TABLE_COLUMNS = {
    'users': ['id', 'username', 'email', 'password_hash', 'display_name', 'created_at'],
    'auth_tokens': ['id', 'user_id', 'token', 'created_at', 'expires_at'],
    'user_stats': ['id', 'user_id', 'total_trades', 'winning_trades', 'losing_trades', 'total_pnl', 'win_rate', 'sharpe_ratio', 'max_drawdown', 'avg_win', 'avg_loss', 'profit_factor', 'created_at'],
    'notification_settings': ['id', 'user_id', 'email_enabled', 'push_enabled', 'price_alerts', 'signal_alerts', 'risk_alerts', 'system_alerts', 'created_at'],
    'notifications': ['id', 'user_id', 'title', 'message', 'notification_type', 'priority', 'is_read', 'created_at'],
    'strategies': ['id', 'user_id', 'name', 'description', 'strategy_type', 'code', 'parameters', 'is_active', 'created_at'],
    'strategy_templates': ['id', 'name', 'description', 'category', 'created_at'],
    'market_news': ['id', 'title', 'content', 'source', 'category', 'symbol', 'impact_score', 'sentiment', 'created_at'],
    'market_events': ['id', 'title', 'date', 'importance', 'category', 'created_at'],
    'economic_indicators': ['id', 'name', 'value', 'period', 'category', 'created_at'],
    'signals': ['id', 'user_id', 'agent_name', 'title', 'content', 'message_type', 'market', 'symbols', 'quality_score', 'reply_count', 'participant_count', 'created_at'],
    'signal_quality_scores': ['id', 'signal_id', 'accuracy_score', 'analysis_depth', 'risk_management', 'timeliness', 'clarity', 'total_score'],
    'signal_replies': ['id', 'signal_id', 'user_id', 'user_name', 'content', 'parent_id', 'likes', 'created_at'],
    'signal_participants': ['id', 'signal_id', 'user_id', 'user_name', 'role', 'joined_at'],
    'email_configs': ['id', 'smtp_host', 'smtp_port', 'smtp_user', 'smtp_password', 'from_email', 'enabled', 'created_at'],
    'webhooks': ['id', 'name', 'url', 'events', 'active', 'created_at'],
}

JSON_COLUMNS = {
    'signals': ['symbols'],
    'strategies': ['parameters'],
    'webhooks': ['events'],
}

BOOLEAN_COLUMNS = {
    'notification_settings': ['email_enabled', 'push_enabled', 'price_alerts', 'signal_alerts', 'risk_alerts', 'system_alerts'],
    'notifications': ['is_read'],
    'strategies': ['is_active'],
    'email_configs': ['enabled'],
    'webhooks': ['active'],
}


def get_sqlite_connection():
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_postgresql_engine():
    return create_engine(
        POSTGRESQL_URL,
        poolclass=QueuePool,
        pool_size=10,
        max_overflow=20,
        pool_recycle=3600,
        pool_pre_ping=True,
        pool_use_lifo=True,
        echo=False
    )


def get_postgresql_session():
    engine = get_postgresql_engine()
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return Session()


def parse_json_value(value):
    if value is None or value == '':
        return None
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return None


def parse_boolean_value(value):
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes', 'on')
    return None


def parse_datetime_value(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        except ValueError:
            try:
                return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return None
    return None


def transform_row(table_name, row):
    result = {}
    columns = TABLE_COLUMNS[table_name]
    
    for col in columns:
        value = row[col] if col in row.keys() else None
        
        if table_name in JSON_COLUMNS and col in JSON_COLUMNS[table_name]:
            result[col] = parse_json_value(value)
        elif table_name in BOOLEAN_COLUMNS and col in BOOLEAN_COLUMNS[table_name]:
            result[col] = parse_boolean_value(value)
        elif col.endswith('_at') or col == 'date':
            result[col] = parse_datetime_value(value)
        else:
            result[col] = value
    
    return result


def migrate_table(table_name, sqlite_conn, pg_session):
    print(f"\nMigrating table: {table_name}")
    
    cursor = sqlite_conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name} ORDER BY id")
    rows = cursor.fetchall()
    
    if not rows:
        print(f"  No data to migrate")
        return 0
    
    print(f"  Found {len(rows)} rows")
    
    columns = TABLE_COLUMNS[table_name]
    placeholders = ', '.join([f':{col}' for col in columns])
    insert_sql = f"""
        INSERT INTO {table_name} ({', '.join(columns)})
        VALUES ({placeholders})
        ON CONFLICT (id) DO NOTHING
    """
    
    migrated = 0
    skipped = 0
    errors = []
    
    for i, row in enumerate(rows, 1):
        try:
            transformed = transform_row(table_name, row)
            result = pg_session.execute(text(insert_sql), transformed)
            if result.rowcount > 0:
                migrated += 1
            else:
                skipped += 1
            
            if i % 100 == 0:
                pg_session.commit()
                print(f"  Processed {i}/{len(rows)} rows...")
                
        except Exception as e:
            errors.append(f"Row {row['id']}: {str(e)}")
            print(f"  ERROR row {row['id']}: {e}")
    
    pg_session.commit()
    
    if errors:
        print(f"  Errors ({len(errors)}):")
        for err in errors[:10]:
            print(f"    - {err}")
        if len(errors) > 10:
            print(f"    ... and {len(errors) - 10} more")
    
    print(f"  Migrated: {migrated}, Skipped: {skipped}, Errors: {len(errors)}")
    return migrated


def reset_postgresql_sequences(pg_session):
    print("\nResetting PostgreSQL sequences...")
    
    for table_name in TABLE_ORDER:
        try:
            result = pg_session.execute(text(f"SELECT MAX(id) FROM {table_name}"))
            max_id = result.scalar() or 0
            
            pg_session.execute(text(
                f"SELECT setval(pg_get_serial_sequence('{table_name}', 'id'), {max_id})"
            ))
            pg_session.commit()
            print(f"  {table_name}: set to {max_id}")
        except Exception as e:
            print(f"  WARNING {table_name}: {e}")
            pg_session.rollback()


def verify_migration(sqlite_conn, pg_session):
    print("\n=== Verifying Migration ===")
    
    all_ok = True
    
    for table_name in TABLE_ORDER:
        try:
            sqlite_cursor = sqlite_conn.cursor()
            sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            sqlite_count = sqlite_cursor.fetchone()[0]
            
            result = pg_session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            pg_count = result.scalar()
            
            status = "✓" if sqlite_count == pg_count else "✗"
            if sqlite_count != pg_count:
                all_ok = False
            print(f"  {status} {table_name}: SQLite={sqlite_count}, PostgreSQL={pg_count}")
            
        except Exception as e:
            print(f"  ✗ {table_name}: ERROR - {e}")
            all_ok = False
    
    return all_ok


def main():
    global POSTGRESQL_URL
    POSTGRESQL_URL = os.getenv('POSTGRESQL_URL')
    
    print("=" * 60)
    print("SQLite to PostgreSQL Data Migration")
    print("=" * 60)
    
    if not POSTGRESQL_URL:
        print("\nERROR: POSTGRESQL_URL environment variable is not set")
        print("Example: postgresql://user:password@localhost:5432/trading")
        sys.exit(1)
    
    print(f"\nSQLite Database: {SQLITE_DB_PATH}")
    print(f"PostgreSQL Database: {POSTGRESQL_URL}")
    
    if not os.path.exists(SQLITE_DB_PATH):
        print(f"\nERROR: SQLite database not found at {SQLITE_DB_PATH}")
        sys.exit(1)
    
    print("\nChecking connections...")
    
    try:
        sqlite_conn = get_sqlite_connection()
        print("✓ SQLite connection successful")
    except Exception as e:
        print(f"✗ SQLite connection failed: {e}")
        sys.exit(1)
    
    try:
        pg_session = get_postgresql_session()
        pg_session.execute(text("SELECT 1"))
        print("✓ PostgreSQL connection successful")
    except Exception as e:
        print(f"✗ PostgreSQL connection failed: {e}")
        traceback.print_exc()
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Starting migration...")
    print("=" * 60)
    
    total_migrated = 0
    start_time = datetime.now()
    
    try:
        for table_name in TABLE_ORDER:
            migrated = migrate_table(table_name, sqlite_conn, pg_session)
            total_migrated += migrated
        
        reset_postgresql_sequences(pg_session)
        
        success = verify_migration(sqlite_conn, pg_session)
        
        elapsed = datetime.now() - start_time
        
        print("\n" + "=" * 60)
        print("Migration Summary")
        print("=" * 60)
        print(f"Total rows migrated: {total_migrated}")
        print(f"Time elapsed: {elapsed}")
        print(f"Status: {'SUCCESS' if success else 'FAILED'}")
        
        if success:
            print("\n🎉 Migration completed successfully!")
            print("\nNext steps:")
            print("1. Update DATABASE_URL environment variable to PostgreSQL URL")
            print("2. Restart the backend server")
            print("3. Test the application")
        else:
            print("\n⚠️  Migration completed with discrepancies")
            print("Please check the logs above and resolve any issues")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        traceback.print_exc()
        pg_session.rollback()
        sys.exit(1)
    finally:
        sqlite_conn.close()
        pg_session.close()


if __name__ == '__main__':
    main()
