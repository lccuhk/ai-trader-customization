#!/usr/bin/env python3
"""
Debug script to check if test account exists and manually create it
"""

import sys
import os

# Add the server directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_db_session
from models import User
from utils.security import hash_password


def check_test_account():
    """Check if test account exists"""
    db = get_db_session()
    try:
        print("🔍 Checking test account...")
        
        # Check if user exists
        user = db.query(User).filter(User.username == 'demo').first()
        
        if user:
            print(f"✅ Test account found!")
            print(f"   ID: {user.id}")
            print(f"   Username: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Display name: {user.display_name}")
            print(f"   Password hash: {user.password_hash}")
            
            # Verify password hash
            test_hash = hash_password('demo123456')
            print(f"\n🔐 Testing password verification...")
            print(f"   Expected hash: {test_hash}")
            print(f"   Database hash: {user.password_hash}")
            print(f"   Match: {test_hash == user.password_hash}")
        else:
            print(f"❌ Test account NOT found!")
            
            # Create the test account
            print(f"\n🔧 Creating test account...")
            test_user = User(
                username='demo',
                email='demo@example.com',
                password_hash=hash_password('demo123456'),
                display_name='Demo User'
            )
            db.add(test_user)
            db.commit()
            print(f"✅ Test account created successfully!")
            print(f"   Username: demo")
            print(f"   Password: demo123456")
            
            # List all users
            print(f"\n📋 All users in database:")
            all_users = db.query(User).all()
            for u in all_users:
                print(f"  - ID: {u.id}, Username: {u.username}, Email: {u.email}")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == '__main__':
    check_test_account()
