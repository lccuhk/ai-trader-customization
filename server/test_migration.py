"""
Test Migration Script

This script tests the migration logic using SQLite as the target database.
It validates that all data is correctly transformed and migrated.
"""

import os
import sys
import sqlite3
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from migrate_data import (
    TABLE_ORDER, TABLE_COLUMNS, JSON_COLUMNS, BOOLEAN_COLUMNS,
    parse_json_value, parse_boolean_value, parse_datetime_value,
    transform_row, get_sqlite_connection
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_DB = os.path.join(BASE_DIR, 'data', 'clawtrader.db')
TEST_TARGET_DB = os.path.join(BASE_DIR, 'data', 'test_migration_target.db')


def create_target_schema(conn):
    """Create the target database schema matching PostgreSQL structure"""
    
    schemas = {
        'users': '''
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE,
                email VARCHAR(255) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                display_name VARCHAR(100),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        ''',
        'auth_tokens': '''
            CREATE TABLE auth_tokens (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                token VARCHAR(255) NOT NULL UNIQUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP WITH TIME ZONE NOT NULL
            )
        ''',
        'user_stats': '''
            CREATE TABLE user_stats (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
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
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        ''',
        'notification_settings': '''
            CREATE TABLE notification_settings (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
                email_enabled BOOLEAN DEFAULT TRUE,
                push_enabled BOOLEAN DEFAULT TRUE,
                price_alerts BOOLEAN DEFAULT TRUE,
                signal_alerts BOOLEAN DEFAULT TRUE,
                risk_alerts BOOLEAN DEFAULT TRUE,
                system_alerts BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        ''',
        'notifications': '''
            CREATE TABLE notifications (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                title VARCHAR(255) NOT NULL,
                message TEXT,
                notification_type VARCHAR(50),
                priority VARCHAR(20) DEFAULT 'normal',
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        ''',
        'strategies': '''
            CREATE TABLE strategies (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                strategy_type VARCHAR(50),
                code TEXT NOT NULL,
                parameters JSONB DEFAULT '{}',
                is_active BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        ''',
        'strategy_templates': '''
            CREATE TABLE strategy_templates (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                category VARCHAR(50),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        ''',
        'market_news': '''
            CREATE TABLE market_news (
                id SERIAL PRIMARY KEY,
                title VARCHAR(500) NOT NULL,
                content TEXT,
                source VARCHAR(100),
                category VARCHAR(50),
                symbol VARCHAR(50),
                impact_score INTEGER,
                sentiment VARCHAR(20),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        ''',
        'market_events': '''
            CREATE TABLE market_events (
                id SERIAL PRIMARY KEY,
                title VARCHAR(500) NOT NULL,
                date VARCHAR(50),
                importance VARCHAR(20),
                category VARCHAR(50),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        ''',
        'economic_indicators': '''
            CREATE TABLE economic_indicators (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                value REAL,
                period VARCHAR(50),
                category VARCHAR(50),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        ''',
        'signals': '''
            CREATE TABLE signals (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                agent_name VARCHAR(100) NOT NULL,
                title VARCHAR(255) NOT NULL,
                content TEXT NOT NULL,
                message_type VARCHAR(50) DEFAULT 'operation',
                market VARCHAR(50) DEFAULT 'us-stock',
                symbols JSONB DEFAULT '[]',
                quality_score REAL DEFAULT 0,
                reply_count INTEGER DEFAULT 0,
                participant_count INTEGER DEFAULT 1,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        ''',
        'signal_quality_scores': '''
            CREATE TABLE signal_quality_scores (
                id SERIAL PRIMARY KEY,
                signal_id INTEGER NOT NULL UNIQUE REFERENCES signals(id) ON DELETE CASCADE,
                accuracy_score REAL DEFAULT 0,
                analysis_depth REAL DEFAULT 0,
                risk_management REAL DEFAULT 0,
                timeliness REAL DEFAULT 0,
                clarity REAL DEFAULT 0,
                total_score REAL DEFAULT 0
            )
        ''',
        'signal_replies': '''
            CREATE TABLE signal_replies (
                id SERIAL PRIMARY KEY,
                signal_id INTEGER NOT NULL REFERENCES signals(id) ON DELETE CASCADE,
                user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                user_name VARCHAR(100) NOT NULL,
                content TEXT NOT NULL,
                parent_id INTEGER REFERENCES signal_replies(id) ON DELETE SET NULL,
                likes INTEGER DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        ''',
        'signal_participants': '''
            CREATE TABLE signal_participants (
                id SERIAL PRIMARY KEY,
                signal_id INTEGER NOT NULL REFERENCES signals(id) ON DELETE CASCADE,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                user_name VARCHAR(100) NOT NULL,
                role VARCHAR(50) DEFAULT 'follower',
                joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(signal_id, user_id)
            )
        ''',
        'email_configs': '''
            CREATE TABLE email_configs (
                id SERIAL PRIMARY KEY,
                smtp_host VARCHAR(255),
                smtp_port INTEGER,
                smtp_user VARCHAR(255),
                smtp_password VARCHAR(255),
                from_email VARCHAR(255),
                enabled BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        ''',
        'webhooks': '''
            CREATE TABLE webhooks (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                url VARCHAR(500) NOT NULL,
                events JSONB DEFAULT '[]',
                active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        ''',
    }
    
    for table_name in TABLE_ORDER:
        if table_name in schemas:
            conn.execute(schemas[table_name])
    
    conn.commit()


def test_data_transformation():
    """Test data transformation functions"""
    print("=== Testing Data Transformation Functions ===")
    
    # Test JSON parsing
    assert parse_json_value('["AAPL", "GOOGL"]') == ['AAPL', 'GOOGL']
    assert parse_json_value('{"key": "value"}') == {'key': 'value'}
    assert parse_json_value(None) is None
    assert parse_json_value('') is None
    assert parse_json_value(['AAPL']) == ['AAPL']
    print("✓ JSON parsing tests passed")
    
    # Test boolean parsing
    assert parse_boolean_value(1) == True
    assert parse_boolean_value(0) == False
    assert parse_boolean_value('true') == True
    assert parse_boolean_value('false') == False
    assert parse_boolean_value('1') == True
    assert parse_boolean_value('0') == False
    assert parse_boolean_value(None) is None
    print("✓ Boolean parsing tests passed")
    
    # Test datetime parsing
    dt = parse_datetime_value('2024-01-15 10:30:00')
    assert dt is not None
    assert dt.year == 2024
    assert dt.month == 1
    assert dt.day == 15
    
    dt2 = parse_datetime_value('2024-01-15T10:30:00+00:00')
    assert dt2 is not None
    assert parse_datetime_value(None) is None
    print("✓ Datetime parsing tests passed")
    
    print("\n✅ All transformation tests passed!\n")


def test_migration():
    """Test the full migration process"""
    print("=== Testing Full Migration Process ===")
    
    # Remove existing test database
    if os.path.exists(TEST_TARGET_DB):
        os.remove(TEST_TARGET_DB)
    
    # Connect to source and target
    source_conn = get_sqlite_connection()
    target_conn = sqlite3.connect(TEST_TARGET_DB)
    target_conn.row_factory = sqlite3.Row
    
    try:
        # Create target schema
        print("Creating target schema...")
        create_target_schema(target_conn)
        print("✓ Target schema created")
        
        # Migrate each table
        total_migrated = 0
        for table_name in TABLE_ORDER:
            print(f"\nMigrating {table_name}...")
            
            # Read from source
            source_cursor = source_conn.cursor()
            source_cursor.execute(f"SELECT * FROM {table_name} ORDER BY id")
            source_rows = source_cursor.fetchall()
            
            if not source_rows:
                print(f"  No data to migrate")
                continue
            
            print(f"  Found {len(source_rows)} rows")
            
            # Transform and insert
            columns = TABLE_COLUMNS[table_name]
            placeholders = ', '.join(['?' for _ in columns])
            insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
            
            migrated = 0
            for row in source_rows:
                transformed = transform_row(table_name, row)
                
                # Convert values to SQLite-compatible formats
                values = []
                for col in columns:
                    val = transformed[col]
                    if isinstance(val, (dict, list)):
                        values.append(json.dumps(val))
                    elif isinstance(val, datetime):
                        values.append(val.isoformat())
                    elif isinstance(val, bool):
                        values.append(1 if val else 0)
                    else:
                        values.append(val)
                
                target_conn.execute(insert_sql, values)
                migrated += 1
            
            target_conn.commit()
            total_migrated += migrated
            print(f"  Migrated {migrated} rows")
        
        # Verify migration
        print("\n=== Verifying Migration ===")
        all_ok = True
        
        for table_name in TABLE_ORDER:
            source_cursor = source_conn.cursor()
            source_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            source_count = source_cursor.fetchone()[0]
            
            target_cursor = target_conn.cursor()
            target_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            target_count = target_cursor.fetchone()[0]
            
            status = "✓" if source_count == target_count else "✗"
            if source_count != target_count:
                all_ok = False
            print(f"  {status} {table_name}: Source={source_count}, Target={target_count}")
        
        # Verify data integrity for a sample table
        print("\n=== Verifying Data Integrity ===")
        
        # Check signals table JSON data
        target_cursor = target_conn.cursor()
        target_cursor.execute("SELECT id, symbols FROM signals WHERE symbols IS NOT NULL LIMIT 5")
        signal_rows = target_cursor.fetchall()
        
        for row in signal_rows:
            symbols = json.loads(row['symbols'])
            assert isinstance(symbols, list), f"symbols should be a list, got {type(symbols)}"
            print(f"  ✓ Signal {row['id']}: symbols = {symbols}")
        
        # Check boolean values
        target_cursor.execute("SELECT id, is_read FROM notifications LIMIT 5")
        notif_rows = target_cursor.fetchall()
        
        for row in notif_rows:
            is_read = row['is_read']
            assert is_read in (0, 1), f"is_read should be 0 or 1, got {is_read}"
            print(f"  ✓ Notification {row['id']}: is_read = {bool(is_read)}")
        
        print("\n✅ Data integrity verification passed!")
        
        print(f"\n=== Migration Summary ===")
        print(f"Total rows migrated: {total_migrated}")
        print(f"Status: {'SUCCESS' if all_ok else 'FAILED'}")
        
        if all_ok:
            print("\n🎉 Migration test completed successfully!")
        else:
            print("\n⚠️  Migration test completed with discrepancies")
            sys.exit(1)
            
    finally:
        source_conn.close()
        target_conn.close()
        
        # Clean up test database
        if os.path.exists(TEST_TARGET_DB):
            os.remove(TEST_TARGET_DB)


def main():
    print("=" * 60)
    print("Migration Script Test Suite")
    print("=" * 60)
    
    if not os.path.exists(SOURCE_DB):
        print(f"\nERROR: Source database not found at {SOURCE_DB}")
        sys.exit(1)
    
    try:
        test_data_transformation()
        test_migration()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
