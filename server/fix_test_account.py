#!/usr/bin/env python3
"""
Debug script to check all users and fix the test account
"""

import sys
import os

# Add the server directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_db_session
from models import User
from utils.security import hash_password


def check_all_users():
    """Check all users and fix the test account"""
    db = get_db_session()
    try:
        print("🔍 Checking all users...")
        
        # Get all users
        all_users = db.query(User).all()
        
        if not all_users:
            print(f"❌ No users found!")
            # Create test user
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
        else:
            print(f"\n📋 Found {len(all_users)} user(s):")
            for user in all_users:
                print(f"\n  ID: {user.id}")
                print(f"  Username: {user.username}")
                print(f"  Email: {user.email}")
                print(f"  Display Name: {user.display_name}")
                
                # Check if password matches
                test_hash = hash_password('demo123456')
                password_match = (test_hash == user.password_hash)
                print(f"  Password 'demo123456' matches: {password_match}")
                
                # If this is a user we can use, update password
                if not password_match:
                    print(f"\n  🔧 Updating password to 'demo123456'...")
                    user.password_hash = hash_password('demo123456')
                    db.commit()
                    print(f"  ✅ Password updated!")
                    print(f"  ✅ You can now login with:")
                    print(f"     Username/Email: {user.username or user.email}")
                    print(f"     Password: demo123456")
                    
                # If username is not demo, rename it
                if user.username != 'demo':
                    print(f"\n  🔧 Setting username to 'demo'...")
                    user.username = 'demo'
                    db.commit()
                    print(f"  ✅ Username updated!")
    
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == '__main__':
    check_all_users()
