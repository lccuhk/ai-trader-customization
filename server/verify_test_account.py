#!/usr/bin/env python3
"""
Verify the test account is working correctly
"""

import sys
import os

# Add the server directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_db_session
from models import User
from utils.security import hash_password


def verify_test_account():
    """Verify the test account"""
    db = get_db_session()
    try:
        print("🔍 Verifying test account...")
        
        # Get user 1
        user = db.query(User).filter(User.id == 1).first()
        
        if not user:
            print(f"❌ No user with ID 1 found!")
            return
        
        print(f"\n✅ User found:")
        print(f"  ID: {user.id}")
        print(f"  Username: {user.username}")
        print(f"  Email: {user.email}")
        print(f"  Display Name: {user.display_name}")
        
        # Verify password
        test_hash = hash_password('demo123456')
        password_match = (test_hash == user.password_hash)
        print(f"\n🔑 Password verification:")
        print(f"  Expected hash: {test_hash}")
        print(f"  Actual hash:   {user.password_hash}")
        print(f"  Password 'demo123456' matches: {password_match}")
        
        if password_match:
            print(f"\n🎉 SUCCESS! You can now login with:")
            print(f"   Username: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Password: demo123456")
        else:
            print(f"\n❌ Password does NOT match!")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == '__main__':
    verify_test_account()
