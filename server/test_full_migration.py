"""
End-to-End Migration Test Script

This script simulates the complete migration process from SQLite to PostgreSQL
(using SQLite as the target for testing purposes).
"""

import os
import sys
import shutil
import sqlite3
import json
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, PROJECT_DIR)

ORIGINAL_DB = os.path.join(BASE_DIR, 'data', 'clawtrader.db')
BACKUP_DB = os.path.join(BASE_DIR, 'data', 'clawtrader.db.backup')
MIGRATION_TARGET_DB = os.path.join(BASE_DIR, 'data', 'migration_target.db')

print_step = 0


def print_header(title):
    global print_step
    print_step += 1
    print("\n" + "=" * 70)
    print(f"STEP {print_step}: {title}")
    print("=" * 70)


def step_backup_database():
    """Step 1: Backup original database"""
    print_header("Backup Original Database")
    
    if not os.path.exists(ORIGINAL_DB):
        print(f"❌ ERROR: Original database not found at {ORIGINAL_DB}")
        return False
    
    if os.path.exists(BACKUP_DB):
        os.remove(BACKUP_DB)
    
    shutil.copy2(ORIGINAL_DB, BACKUP_DB)
    print(f"✅ Database backed up to: {BACKUP_DB}")
    print(f"   Size: {os.path.getsize(BACKUP_DB) / 1024:.2f} KB")
    
    return True


def step_create_target_database():
    """Step 2: Create target database (simulating PostgreSQL)"""
    print_header("Create Target Database")
    
    if os.path.exists(MIGRATION_TARGET_DB):
        os.remove(MIGRATION_TARGET_DB)
        print("✅ Removed existing target database")
    
    conn = sqlite3.connect(MIGRATION_TARGET_DB)
    conn.close()
    
    print(f"✅ Target database created: {MIGRATION_TARGET_DB}")
    
    os.environ['POSTGRESQL_URL'] = f'sqlite:///{MIGRATION_TARGET_DB}'
    print(f"✅ POSTGRESQL_URL set to: {os.environ['POSTGRESQL_URL']}")
    
    return True


def step_run_alembic_migration():
    """Step 3: Run Alembic migrations to create table structure"""
    print_header("Run Alembic Migrations")
    
    original_db_url = os.environ.get('DATABASE_URL', '')
    
    try:
        os.environ['DATABASE_URL'] = os.environ['POSTGRESQL_URL']
        print(f"   DATABASE_URL set to: {os.environ['DATABASE_URL']}")
        
        from alembic import command
        from alembic.config import Config
        
        alembic_cfg = Config(os.path.join(PROJECT_DIR, 'alembic.ini'))
        alembic_cfg.set_main_option('sqlalchemy.url', os.environ['DATABASE_URL'])
        
        print("   Running alembic upgrade head...")
        command.upgrade(alembic_cfg, 'head')
        print("✅ Alembic migrations completed successfully")
        
        conn = sqlite3.connect(MIGRATION_TARGET_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
        tables = cursor.fetchall()
        conn.close()
        
        print(f"   Created {len(tables)} tables:")
        for table in tables:
            print(f"   - {table[0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Alembic migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if original_db_url:
            os.environ['DATABASE_URL'] = original_db_url
        elif 'DATABASE_URL' in os.environ:
            del os.environ['DATABASE_URL']


def step_run_data_migration():
    """Step 4: Run data migration script"""
    print_header("Run Data Migration")
    
    original_db_url = os.environ.get('DATABASE_URL', '')
    
    try:
        from migrate_data import (
            TABLE_ORDER, TABLE_COLUMNS, JSON_COLUMNS, BOOLEAN_COLUMNS,
            parse_json_value, parse_boolean_value, parse_datetime_value,
            transform_row, get_sqlite_connection
        )
        
        source_conn = get_sqlite_connection()
        target_conn = sqlite3.connect(MIGRATION_TARGET_DB)
        target_conn.row_factory = sqlite3.Row
        
        total_migrated = 0
        
        for table_name in TABLE_ORDER:
            print(f"\n   Migrating {table_name}...")
            
            source_cursor = source_conn.cursor()
            source_cursor.execute(f"SELECT * FROM {table_name} ORDER BY id")
            source_rows = source_cursor.fetchall()
            
            if not source_rows:
                print(f"   No data to migrate")
                continue
            
            print(f"   Found {len(source_rows)} rows")
            
            columns = TABLE_COLUMNS[table_name]
            placeholders = ', '.join(['?' for _ in columns])
            insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
            
            migrated = 0
            for row in source_rows:
                transformed = transform_row(table_name, row)
                
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
            print(f"   ✅ Migrated {migrated} rows")
        
        source_conn.close()
        target_conn.close()
        
        print(f"\n✅ Data migration completed: {total_migrated} total rows")
        return True
        
    except Exception as e:
        print(f"❌ Data migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def step_verify_data_integrity():
    """Step 5: Verify data integrity"""
    print_header("Verify Data Integrity")
    
    try:
        source_conn = sqlite3.connect(ORIGINAL_DB)
        source_conn.row_factory = sqlite3.Row
        target_conn = sqlite3.connect(MIGRATION_TARGET_DB)
        target_conn.row_factory = sqlite3.Row
        
        all_ok = True
        
        print("\n   Record count verification:")
        from migrate_data import TABLE_ORDER
        
        for table_name in TABLE_ORDER:
            source_cursor = source_conn.cursor()
            source_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            source_count = source_cursor.fetchone()[0]
            
            target_cursor = target_conn.cursor()
            target_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            target_count = target_cursor.fetchone()[0]
            
            status = "✅" if source_count == target_count else "❌"
            if source_count != target_count:
                all_ok = False
            print(f"   {status} {table_name}: Source={source_count}, Target={target_count}")
        
        print("\n   Data content verification:")
        
        target_cursor = target_conn.cursor()
        target_cursor.execute("SELECT id, symbols FROM signals LIMIT 5")
        signal_rows = target_cursor.fetchall()
        
        for row in signal_rows:
            symbols = json.loads(row['symbols']) if row['symbols'] else []
            assert isinstance(symbols, list), f"symbols should be a list"
            print(f"   ✅ Signal {row['id']}: symbols = {symbols}")
        
        target_cursor.execute("SELECT id, is_read FROM notifications LIMIT 5")
        notif_rows = target_cursor.fetchall()
        
        for row in notif_rows:
            is_read = row['is_read']
            assert is_read in (0, 1), f"is_read should be 0 or 1"
            print(f"   ✅ Notification {row['id']}: is_read = {bool(is_read)}")
        
        target_cursor.execute("SELECT id, created_at FROM signals LIMIT 3")
        time_rows = target_cursor.fetchall()
        
        for row in time_rows:
            created_at = row['created_at']
            assert created_at is not None, f"created_at should not be None"
            print(f"   ✅ Signal {row['id']}: created_at = {created_at[:19]}")
        
        source_conn.close()
        target_conn.close()
        
        if all_ok:
            print("\n✅ Data integrity verification passed!")
        else:
            print("\n❌ Data integrity verification failed!")
        
        return all_ok
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def step_switch_database_config():
    """Step 6: Switch database configuration"""
    print_header("Switch Database Configuration")
    
    print(f"   Original DATABASE_URL: {os.environ.get('DATABASE_URL', 'not set')}")
    
    os.environ['DATABASE_URL'] = f'sqlite:///{MIGRATION_TARGET_DB}'
    print(f"   New DATABASE_URL: {os.environ['DATABASE_URL']}")
    
    print("✅ Database configuration switched")
    return True


def step_test_api_endpoints():
    """Step 7: Test API endpoints with new database"""
    print_header("Test API Endpoints")
    
    try:
        import importlib
        import flask_server
        importlib.reload(flask_server)
        
        client = flask_server.app.test_client()
        
        tests_passed = 0
        tests_failed = 0
        
        print("\n   Testing public endpoints:")
        
        response = client.get('/api/health')
        if response.status_code == 200:
            data = response.get_json()
            if data.get('status') == 'healthy':
                print("   ✅ /api/health")
                tests_passed += 1
            else:
                print("   ❌ /api/health - invalid response")
                tests_failed += 1
        else:
            print(f"   ❌ /api/health - status {response.status_code}")
            tests_failed += 1
        
        response = client.post('/api/auth/login', json={
            'username': 'demo@example.com',
            'password': 'demo123'
        })
        if response.status_code == 200:
            data = response.get_json()
            if data.get('success') and 'token' in data:
                token = data['token']
                print("   ✅ /api/auth/login")
                tests_passed += 1
            else:
                print("   ❌ /api/auth/login - invalid response")
                tests_failed += 1
        else:
            print(f"   ❌ /api/auth/login - status {response.status_code}")
            tests_failed += 1
            return False
        
        response = client.get('/api/signals/feed?limit=5')
        if response.status_code == 200:
            data = response.get_json()
            if data.get('success') and len(data.get('signals', [])) > 0:
                print(f"   ✅ /api/signals/feed (got {len(data['signals'])} signals)")
                tests_passed += 1
            else:
                print("   ❌ /api/signals/feed - no signals returned")
                tests_failed += 1
        else:
            print(f"   ❌ /api/signals/feed - status {response.status_code}")
            tests_failed += 1
        
        signal_id = response.get_json()['signals'][0]['id']
        
        response = client.get(f'/api/signals/{signal_id}')
        if response.status_code == 200:
            data = response.get_json()
            if data.get('success') and 'signal' in data:
                print(f"   ✅ /api/signals/{signal_id}")
                tests_passed += 1
            else:
                print(f"   ❌ /api/signals/{signal_id} - invalid response")
                tests_failed += 1
        else:
            print(f"   ❌ /api/signals/{signal_id} - status {response.status_code}")
            tests_failed += 1
        
        response = client.get(f'/api/signals/{signal_id}/replies')
        if response.status_code == 200:
            data = response.get_json()
            if data.get('success'):
                print(f"   ✅ /api/signals/{signal_id}/replies")
                tests_passed += 1
            else:
                print(f"   ❌ /api/signals/{signal_id}/replies - invalid response")
                tests_failed += 1
        else:
            print(f"   ❌ /api/signals/{signal_id}/replies - status {response.status_code}")
            tests_failed += 1
        
        response = client.get(f'/api/signals/{signal_id}/participants')
        if response.status_code == 200:
            data = response.get_json()
            if data.get('success'):
                print(f"   ✅ /api/signals/{signal_id}/participants")
                tests_passed += 1
            else:
                print(f"   ❌ /api/signals/{signal_id}/participants - invalid response")
                tests_failed += 1
        else:
            print(f"   ❌ /api/signals/{signal_id}/participants - status {response.status_code}")
            tests_failed += 1
        
        response = client.get(f'/api/signals/{signal_id}/quality-detail')
        if response.status_code == 200:
            data = response.get_json()
            if data.get('success') and 'quality' in data:
                print(f"   ✅ /api/signals/{signal_id}/quality-detail")
                tests_passed += 1
            else:
                print(f"   ❌ /api/signals/{signal_id}/quality-detail - invalid response")
                tests_failed += 1
        else:
            print(f"   ❌ /api/signals/{signal_id}/quality-detail - status {response.status_code}")
            tests_failed += 1
        
        response = client.get('/api/market/news?limit=3')
        if response.status_code == 200:
            data = response.get_json()
            if data.get('success'):
                print(f"   ✅ /api/market/news")
                tests_passed += 1
            else:
                print("   ❌ /api/market/news - invalid response")
                tests_failed += 1
        else:
            print(f"   ❌ /api/market/news - status {response.status_code}")
            tests_failed += 1
        
        response = client.get('/api/strategies')
        if response.status_code == 200:
            data = response.get_json()
            if data.get('success'):
                print(f"   ✅ /api/strategies")
                tests_passed += 1
            else:
                print("   ❌ /api/strategies - invalid response")
                tests_failed += 1
        else:
            print(f"   ❌ /api/strategies - status {response.status_code}")
            tests_failed += 1
        
        print("\n   Testing authenticated endpoints:")
        auth_headers = {'Authorization': f'Bearer {token}'}
        
        response = client.get('/api/users/me', headers=auth_headers)
        if response.status_code == 200:
            data = response.get_json()
            if data.get('success') and 'user' in data:
                print(f"   ✅ /api/users/me")
                tests_passed += 1
            else:
                print(f"   ❌ /api/users/me - invalid response")
                tests_failed += 1
        else:
            print(f"   ❌ /api/users/me - status {response.status_code}")
            tests_failed += 1
        
        response = client.get('/api/notifications', headers=auth_headers)
        if response.status_code == 200:
            data = response.get_json()
            if data.get('success'):
                print(f"   ✅ /api/notifications")
                tests_passed += 1
            else:
                print(f"   ❌ /api/notifications - invalid response")
                tests_failed += 1
        else:
            print(f"   ❌ /api/notifications - status {response.status_code}")
            tests_failed += 1
        
        response = client.post(f'/api/signals/{signal_id}/replies',
            json={'content': 'Test comment from migration test'},
            headers=auth_headers
        )
        if response.status_code == 200:
            data = response.get_json()
            if data.get('success'):
                print(f"   ✅ POST /api/signals/{signal_id}/replies")
                tests_passed += 1
            else:
                print(f"   ❌ POST /api/signals/{signal_id}/replies - {data.get('message')}")
                tests_failed += 1
        else:
            print(f"   ❌ POST /api/signals/{signal_id}/replies - status {response.status_code}")
            tests_failed += 1
        
        response = client.post(f'/api/signals/{signal_id}/follow',
            headers=auth_headers
        )
        if response.status_code == 200:
            data = response.get_json()
            if data.get('success'):
                print(f"   ✅ POST /api/signals/{signal_id}/follow")
                tests_passed += 1
            else:
                print(f"   ❌ POST /api/signals/{signal_id}/follow - {data.get('message')}")
                tests_failed += 1
        else:
            print(f"   ❌ POST /api/signals/{signal_id}/follow - status {response.status_code}")
            tests_failed += 1
        
        response = client.post('/api/signals',
            json={
                'title': 'Test Signal from Migration',
                'content': 'This is a test signal created during migration verification',
                'type': 'analysis',
                'market': 'us-stock'
            },
            headers=auth_headers
        )
        if response.status_code == 200:
            data = response.get_json()
            if data.get('success'):
                print(f"   ✅ POST /api/signals")
                tests_passed += 1
            else:
                print(f"   ❌ POST /api/signals - {data.get('message')}")
                tests_failed += 1
        else:
            print(f"   ❌ POST /api/signals - status {response.status_code}")
            tests_failed += 1
        
        print(f"\n   API Test Results: {tests_passed}/{tests_passed + tests_failed} passed")
        
        if tests_failed == 0:
            print("✅ All API endpoints working correctly!")
            return True
        else:
            print(f"❌ {tests_failed} API endpoints failed")
            return False
        
    except Exception as e:
        print(f"❌ API testing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def step_cleanup():
    """Step 8: Cleanup and restore original configuration"""
    print_header("Cleanup and Restore")
    
    if os.path.exists(BACKUP_DB):
        print(f"   Backup file kept at: {BACKUP_DB}")
    
    if os.path.exists(MIGRATION_TARGET_DB):
        print(f"   Migration test database at: {MIGRATION_TARGET_DB}")
        print("   (You can delete this file if not needed)")
    
    if 'DATABASE_URL' in os.environ:
        del os.environ['DATABASE_URL']
        print("   DATABASE_URL environment variable cleared")
    
    if 'POSTGRESQL_URL' in os.environ:
        del os.environ['POSTGRESQL_URL']
        print("   POSTGRESQL_URL environment variable cleared")
    
    print("\n✅ Cleanup completed")
    return True


def main():
    print("\n" + "=" * 70)
    print("END-TO-END MIGRATION TEST")
    print("=" * 70)
    print(f"\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Original database: {ORIGINAL_DB}")
    
    start_time = datetime.now()
    
    steps = [
        ("Backup Original Database", step_backup_database),
        ("Create Target Database", step_create_target_database),
        ("Run Alembic Migrations", step_run_alembic_migration),
        ("Run Data Migration", step_run_data_migration),
        ("Verify Data Integrity", step_verify_data_integrity),
        ("Switch Database Configuration", step_switch_database_config),
        ("Test API Endpoints", step_test_api_endpoints),
    ]
    
    results = []
    for step_name, step_func in steps:
        try:
            result = step_func()
            results.append((step_name, result))
            if not result:
                print(f"\n❌ Migration failed at step: {step_name}")
                break
        except Exception as e:
            print(f"\n❌ Exception at step '{step_name}': {e}")
            import traceback
            traceback.print_exc()
            results.append((step_name, False))
            break
    
    step_cleanup()
    
    elapsed = datetime.now() - start_time
    
    print("\n" + "=" * 70)
    print("MIGRATION TEST SUMMARY")
    print("=" * 70)
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total time: {elapsed}")
    print("\nStep Results:")
    
    all_passed = True
    for step_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        if not result:
            all_passed = False
        print(f"   {status} - {step_name}")
    
    if all_passed and len(results) == len(steps):
        print("\n🎉 MIGRATION TEST PASSED!")
        print("\nThe complete migration flow is working correctly:")
        print("   1. Database backup")
        print("   2. Target database creation")
        print("   3. Alembic schema migration")
        print("   4. Data migration with type conversion")
        print("   5. Data integrity verification")
        print("   6. Database configuration switch")
        print("   7. Full API endpoint testing")
        print("\nYou are ready to migrate to PostgreSQL!")
        return 0
    else:
        print("\n❌ MIGRATION TEST FAILED")
        print("Please review the errors above and fix them before proceeding.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
