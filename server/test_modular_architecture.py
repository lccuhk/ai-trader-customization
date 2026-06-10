"""
Modular Architecture Test Script

Tests the complete modular architecture including all routes, services, and middleware.
"""

import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print_step = 0


def print_header(title):
    global print_step
    print_step += 1
    print("\n" + "=" * 70)
    print(f"STEP {print_step}: {title}")
    print("=" * 70)


def test_module_imports():
    """Test that all modules can be imported correctly"""
    print_header("Test Module Imports")
    
    modules = [
        ('config', 'settings'),
        ('database', 'get_db_session, init_db'),
        ('models', 'User, Signal, Notification'),
        ('utils.security', 'hash_password, verify_password, generate_token'),
        ('utils.helpers', 'model_to_dict, models_to_dict_list'),
        ('middleware.auth', 'require_auth, get_current_user_id'),
        ('middleware.error_handler', 'register_error_handlers'),
        ('services.auth_service', 'login, register, get_current_user_info'),
        ('services.signal_service', 'get_signals, get_signal_detail, add_reply'),
        ('services.notification_service', 'get_notifications, mark_notification_read'),
        ('services.market_service', 'get_market_news, get_strategies'),
        ('routes.auth', 'auth_bp'),
        ('routes.signals', 'signals_bp'),
        ('routes.notifications', 'notifications_bp'),
        ('routes.market', 'market_bp'),
        ('routes.users', 'users_bp'),
        ('app', 'create_app'),
    ]
    
    all_passed = True
    for module_name, exports in modules:
        try:
            module = __import__(module_name, fromlist=['*'])
            print(f"   ✅ {module_name}")
            for export in exports.split(', '):
                if not hasattr(module, export):
                    print(f"      ❌ Missing export: {export}")
                    all_passed = False
        except Exception as e:
            print(f"   ❌ {module_name}: {e}")
            import traceback
            traceback.print_exc()
            all_passed = False
    
    return all_passed


def test_config_module():
    """Test the configuration module"""
    print_header("Test Configuration Module")
    
    from config import settings
    
    tests = [
        ('DATABASE_URL is set', bool(settings.DATABASE_URL)),
        ('SECRET_KEY is set', bool(settings.secret_key)),
        ('ALLOWED_ORIGINS is a list', isinstance(settings.ALLOWED_ORIGINS, list)),
        ('PORT is integer', isinstance(settings.PORT, int)),
        ('is_development works', isinstance(settings.is_development, bool)),
        ('is_postgresql works', isinstance(settings.is_postgresql, bool)),
    ]
    
    all_passed = True
    for test_name, result in tests:
        status = "✅" if result else "❌"
        if not result:
            all_passed = False
        print(f"   {status} {test_name}")
    
    print(f"\n   DATABASE_URL: {settings.DATABASE_URL}")
    print(f"   ALLOWED_ORIGINS: {settings.ALLOWED_ORIGINS}")
    print(f"   PORT: {settings.PORT}")
    
    return all_passed


def test_database_connection():
    """Test database connection and ORM"""
    print_header("Test Database Connection")
    
    from database import get_db_session
    from models import User, Signal, Notification, Strategy
    
    try:
        db = get_db_session()
        print("   ✅ Database session created")
        
        user_count = db.query(User).count()
        print(f"   ✅ User table: {user_count} records")
        
        signal_count = db.query(Signal).count()
        print(f"   ✅ Signal table: {signal_count} records")
        
        notification_count = db.query(Notification).count()
        print(f"   ✅ Notification table: {notification_count} records")
        
        strategy_count = db.query(Strategy).count()
        print(f"   ✅ Strategy table: {strategy_count} records")
        
        db.close()
        print("   ✅ Database session closed")
        
        return True
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_utils_module():
    """Test utility functions"""
    print_header("Test Utility Functions")
    
    from utils.security import hash_password, verify_password, generate_token
    from utils.helpers import model_to_dict, parse_json_value, parse_bool_value, parse_datetime_value
    
    all_passed = True
    
    # Test password hashing
    password = "test123"
    hashed = hash_password(password)
    if verify_password(password, hashed):
        print("   ✅ Password hashing/verification")
    else:
        print("   ❌ Password hashing/verification failed")
        all_passed = False
    
    # Test token generation
    token = generate_token()
    if len(token) == 64:
        print("   ✅ Token generation")
    else:
        print(f"   ❌ Token generation failed (length: {len(token)})")
        all_passed = False
    
    # Test JSON parsing
    if parse_json_value('["AAPL", "GOOGL"]') == ['AAPL', 'GOOGL']:
        print("   ✅ JSON parsing (array)")
    else:
        print("   ❌ JSON parsing (array) failed")
        all_passed = False
    
    if parse_json_value('{"key": "value"}') == {'key': 'value'}:
        print("   ✅ JSON parsing (object)")
    else:
        print("   ❌ JSON parsing (object) failed")
        all_passed = False
    
    # Test boolean parsing
    if parse_bool_value(1) == True and parse_bool_value(0) == False:
        print("   ✅ Boolean parsing (integer)")
    else:
        print("   ❌ Boolean parsing (integer) failed")
        all_passed = False
    
    if parse_bool_value('true') == True and parse_bool_value('false') == False:
        print("   ✅ Boolean parsing (string)")
    else:
        print("   ❌ Boolean parsing (string) failed")
        all_passed = False
    
    # Test datetime parsing
    dt = parse_datetime_value('2024-01-15 10:30:00')
    if dt and dt.year == 2024:
        print("   ✅ Datetime parsing")
    else:
        print("   ❌ Datetime parsing failed")
        all_passed = False
    
    return all_passed


def test_services():
    """Test service layer functions"""
    print_header("Test Service Layer")
    
    from services.auth_service import login, get_current_user_info
    from services.signal_service import get_signals, get_signal_detail
    from services.market_service import get_market_news, get_strategies
    from services.notification_service import get_notifications
    
    all_passed = True
    
    # Test auth service
    result, status = login('demo@example.com', 'demo123')
    if status == 200 and result.get('success') and 'token' in result:
        print("   ✅ AuthService.login()")
        token = result['token']
        user_id = result['user']['id']
    else:
        print(f"   ❌ AuthService.login() failed: {result.get('message')}")
        all_passed = False
        return all_passed
    
    # Test get_current_user_info
    result, status = get_current_user_info(user_id)
    if status == 200 and result.get('success') and 'user' in result:
        print("   ✅ AuthService.get_current_user_info()")
    else:
        print(f"   ❌ AuthService.get_current_user_info() failed")
        all_passed = False
    
    # Test signal service
    result, status = get_signals(limit=5)
    if status == 200 and result.get('success') and len(result.get('signals', [])) > 0:
        print(f"   ✅ SignalService.get_signals() ({len(result['signals'])} signals)")
        signal_id = result['signals'][0]['id']
    else:
        print(f"   ❌ SignalService.get_signals() failed")
        all_passed = False
        return all_passed
    
    # Test get_signal_detail
    result, status = get_signal_detail(signal_id)
    if status == 200 and result.get('success') and 'signal' in result:
        print("   ✅ SignalService.get_signal_detail()")
    else:
        print(f"   ❌ SignalService.get_signal_detail() failed")
        all_passed = False
    
    # Test market service
    result, status = get_market_news(limit=3)
    if status == 200 and result.get('success'):
        print(f"   ✅ MarketService.get_market_news() ({len(result['news'])} news)")
    else:
        print(f"   ❌ MarketService.get_market_news() failed")
        all_passed = False
    
    # Test get_strategies
    result, status = get_strategies()
    if status == 200 and result.get('success'):
        print(f"   ✅ MarketService.get_strategies() ({len(result['strategies'])} strategies)")
    else:
        print(f"   ❌ MarketService.get_strategies() failed")
        all_passed = False
    
    # Test notification service
    result, status = get_notifications(user_id, limit=5)
    if status == 200 and result.get('success'):
        print(f"   ✅ NotificationService.get_notifications() ({len(result['notifications'])} notifications)")
    else:
        print(f"   ❌ NotificationService.get_notifications() failed")
        all_passed = False
    
    return all_passed


def test_api_endpoints():
    """Test all API endpoints through the Flask app"""
    print_header("Test API Endpoints")
    
    from app import create_app
    
    app = create_app()
    client = app.test_client()
    
    all_passed = True
    tests_passed = 0
    tests_failed = 0
    
    # Test public endpoints
    print("\n   Public endpoints:")
    
    response = client.get('/api/health')
    if response.status_code == 200 and response.get_json().get('status') == 'healthy':
        print("   ✅ GET /api/health")
        tests_passed += 1
    else:
        print(f"   ❌ GET /api/health ({response.status_code})")
        tests_failed += 1
        all_passed = False
    
    response = client.get('/api/')
    if response.status_code == 200 and 'endpoints' in response.get_json():
        print("   ✅ GET /api/")
        tests_passed += 1
    else:
        print(f"   ❌ GET /api/ ({response.status_code})")
        tests_failed += 1
        all_passed = False
    
    response = client.post('/api/auth/login', json={
        'username': 'demo@example.com',
        'password': 'demo123'
    })
    if response.status_code == 200 and response.get_json().get('success'):
        print("   ✅ POST /api/auth/login")
        token = response.get_json()['token']
        tests_passed += 1
    else:
        print(f"   ❌ POST /api/auth/login ({response.status_code})")
        tests_failed += 1
        all_passed = False
        return all_passed
    
    auth_headers = {'Authorization': f'Bearer {token}'}
    
    response = client.get('/api/signals/feed?limit=5')
    if response.status_code == 200 and response.get_json().get('success'):
        print(f"   ✅ GET /api/signals/feed")
        signal_id = response.get_json()['signals'][0]['id']
        tests_passed += 1
    else:
        print(f"   ❌ GET /api/signals/feed ({response.status_code})")
        tests_failed += 1
        all_passed = False
        return all_passed
    
    response = client.get(f'/api/signals/{signal_id}')
    if response.status_code == 200 and response.get_json().get('success'):
        print(f"   ✅ GET /api/signals/{signal_id}")
        tests_passed += 1
    else:
        print(f"   ❌ GET /api/signals/{signal_id} ({response.status_code})")
        tests_failed += 1
        all_passed = False
    
    response = client.get(f'/api/signals/{signal_id}/replies')
    if response.status_code == 200 and response.get_json().get('success'):
        print(f"   ✅ GET /api/signals/{signal_id}/replies")
        tests_passed += 1
    else:
        print(f"   ❌ GET /api/signals/{signal_id}/replies ({response.status_code})")
        tests_failed += 1
        all_passed = False
    
    response = client.get(f'/api/signals/{signal_id}/participants')
    if response.status_code == 200 and response.get_json().get('success'):
        print(f"   ✅ GET /api/signals/{signal_id}/participants")
        tests_passed += 1
    else:
        print(f"   ❌ GET /api/signals/{signal_id}/participants ({response.status_code})")
        tests_failed += 1
        all_passed = False
    
    response = client.get(f'/api/signals/{signal_id}/quality-detail')
    if response.status_code == 200 and response.get_json().get('success'):
        print(f"   ✅ GET /api/signals/{signal_id}/quality-detail")
        tests_passed += 1
    else:
        print(f"   ❌ GET /api/signals/{signal_id}/quality-detail ({response.status_code})")
        tests_failed += 1
        all_passed = False
    
    response = client.get('/api/market/news?limit=3')
    if response.status_code == 200 and response.get_json().get('success'):
        print(f"   ✅ GET /api/market/news")
        tests_passed += 1
    else:
        print(f"   ❌ GET /api/market/news ({response.status_code})")
        tests_failed += 1
        all_passed = False
    
    response = client.get('/api/strategies')
    if response.status_code == 200 and response.get_json().get('success'):
        print(f"   ✅ GET /api/strategies")
        tests_passed += 1
    else:
        print(f"   ❌ GET /api/strategies ({response.status_code})")
        tests_failed += 1
        all_passed = False
    
    # Test authenticated endpoints
    print("\n   Authenticated endpoints:")
    
    response = client.get('/api/users/me', headers=auth_headers)
    if response.status_code == 200 and response.get_json().get('success'):
        print(f"   ✅ GET /api/users/me")
        tests_passed += 1
    else:
        print(f"   ❌ GET /api/users/me ({response.status_code})")
        tests_failed += 1
        all_passed = False
    
    response = client.get('/api/notifications', headers=auth_headers)
    if response.status_code == 200 and response.get_json().get('success'):
        print(f"   ✅ GET /api/notifications")
        tests_passed += 1
    else:
        print(f"   ❌ GET /api/notifications ({response.status_code})")
        tests_failed += 1
        all_passed = False
    
    response = client.post(f'/api/signals/{signal_id}/replies',
        json={'content': 'Test comment from modular architecture test'},
        headers=auth_headers
    )
    if response.status_code == 200 and response.get_json().get('success'):
        print(f"   ✅ POST /api/signals/{signal_id}/replies")
        tests_passed += 1
    else:
        print(f"   ❌ POST /api/signals/{signal_id}/replies ({response.status_code}): {response.get_json().get('message')}")
        tests_failed += 1
        all_passed = False
    
    response = client.post(f'/api/signals/{signal_id}/follow', headers=auth_headers)
    if response.status_code == 200 and response.get_json().get('success'):
        print(f"   ✅ POST /api/signals/{signal_id}/follow")
        tests_passed += 1
    else:
        print(f"   ❌ POST /api/signals/{signal_id}/follow ({response.status_code})")
        tests_failed += 1
        all_passed = False
    
    response = client.post('/api/signals',
        json={
            'title': 'Test Signal from Modular Architecture',
            'content': 'This is a test signal created during modular architecture verification',
            'type': 'analysis',
            'market': 'us-stock'
        },
        headers=auth_headers
    )
    if response.status_code == 200 and response.get_json().get('success'):
        print(f"   ✅ POST /api/signals")
        tests_passed += 1
    else:
        print(f"   ❌ POST /api/signals ({response.status_code}): {response.get_json().get('message')}")
        tests_failed += 1
        all_passed = False
    
    print(f"\n   API Test Results: {tests_passed}/{tests_passed + tests_failed} passed")
    
    return all_passed


def test_directory_structure():
    """Verify the directory structure is correct"""
    print_header("Verify Directory Structure")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    expected_dirs = [
        'schemas',
        'routes',
        'services',
        'middleware',
        'utils',
        'data',
    ]
    
    expected_files = [
        '__init__.py',
        'app.py',
        'config.py',
        'database.py',
        'models.py',
        'routes/__init__.py',
        'routes/auth.py',
        'routes/signals.py',
        'routes/notifications.py',
        'routes/market.py',
        'routes/users.py',
        'services/__init__.py',
        'services/auth_service.py',
        'services/signal_service.py',
        'services/notification_service.py',
        'services/market_service.py',
        'middleware/__init__.py',
        'middleware/auth.py',
        'middleware/error_handler.py',
        'utils/__init__.py',
        'utils/security.py',
        'utils/helpers.py',
    ]
    
    all_passed = True
    
    print("\n   Directories:")
    for dir_name in expected_dirs:
        dir_path = os.path.join(base_dir, dir_name)
        if os.path.isdir(dir_path):
            print(f"   ✅ {dir_name}/")
        else:
            print(f"   ❌ {dir_name}/ - MISSING")
            all_passed = False
    
    print("\n   Files:")
    for file_path in expected_files:
        full_path = os.path.join(base_dir, file_path)
        if os.path.isfile(full_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - MISSING")
            all_passed = False
    
    return all_passed


def main():
    print("\n" + "=" * 70)
    print("MODULAR ARCHITECTURE TEST SUITE")
    print("=" * 70)
    print(f"\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    start_time = datetime.now()
    
    tests = [
        ("Directory Structure", test_directory_structure),
        ("Module Imports", test_module_imports),
        ("Configuration Module", test_config_module),
        ("Database Connection", test_database_connection),
        ("Utility Functions", test_utils_module),
        ("Service Layer", test_services),
        ("API Endpoints", test_api_endpoints),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            if not result:
                print(f"\n❌ Test failed at: {test_name}")
                break
        except Exception as e:
            print(f"\n❌ Exception in test '{test_name}': {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
            break
    
    elapsed = datetime.now() - start_time
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total time: {elapsed}")
    print("\nResults:")
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        if not result:
            all_passed = False
        print(f"   {status} - {test_name}")
    
    if all_passed and len(results) == len(tests):
        print("\n🎉 MODULAR ARCHITECTURE TEST PASSED!")
        print("\nThe backend has been successfully refactored into a modular structure:")
        print("   - config.py: Centralized configuration management")
        print("   - models.py: SQLAlchemy ORM models (16 tables)")
        print("   - database.py: Database connection and session management")
        print("   - routes/: API route blueprints (5 modules)")
        print("   - services/: Business logic layer (4 modules)")
        print("   - middleware/: Authentication and error handling")
        print("   - utils/: Security and helper functions")
        print("   - app.py: Flask application factory")
        print("\nBenefits:")
        print("   ✅ Separation of concerns")
        print("   ✅ Improved code maintainability")
        print("   ✅ Easier testing")
        print("   ✅ Better team collaboration")
        print("   ✅ Scalable architecture")
        return 0
    else:
        print("\n❌ MODULAR ARCHITECTURE TEST FAILED")
        print("Please review the errors above and fix them.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
