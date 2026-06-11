"""
Flask Application Factory

Main entry point for the Flask application with modular architecture and WebSocket support.
"""

import os
import sys
from datetime import datetime

from flask import Flask, jsonify
from flask_cors import CORS

from config import settings
from database import init_db, get_db_session
from middleware.error_handler import register_error_handlers
from utils.security import hash_password
import websocket

from routes.auth import auth_bp
from routes.signals import signals_bp
from routes.notifications import notifications_bp
from routes.market import market_bp
from routes.users import users_bp
from routes.trading import trading_bp
from routes.social import social_bp
from routes.ai import ai_bp
from routes.health import health_bp
from routes.security import security_bp
from routes.admin import admin_bp
from routes.analytics import analytics_bp
from simulation.engine import simulation_engine


def init_test_account():
    """
    Initialize a test account. Update password if account already exists.
    """
    from models import User
    from sqlalchemy import or_

    db = get_db_session()
    try:
        existing_user = db.query(User).filter(
            or_(User.username == 'demo', User.email == 'demo@example.com', User.email == 'demo')
        ).first()

        if not existing_user:
            test_user = User(
                username='demo',
                email='demo@example.com',
                password_hash=hash_password('demo123456'),
                display_name='Demo User'
            )
            db.add(test_user)
            db.commit()
            print("[OK] Test account created successfully!")
        else:
            # Always update password hash to ensure PBKDF2 format
            existing_user.password_hash = hash_password('demo123456')
            if not existing_user.username:
                existing_user.username = 'demo'
            if not existing_user.display_name:
                existing_user.display_name = 'Demo User'
            db.commit()
            print("[OK] Test account password updated!")

        print("   Username: demo")
        print("   Password: demo123456")
    except Exception as e:
        db.rollback()
        print(f"[WARN] Error creating test account: {str(e)}")
    finally:
        db.close()


def create_app() -> Flask:
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = settings.secret_key
    app.config['DEBUG'] = settings.FLASK_DEBUG
    app.config['ENV'] = settings.FLASK_ENV
    
    CORS(app, resources={
        r"/api/*": {
            "origins": settings.ALLOWED_ORIGINS,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    register_error_handlers(app)
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(signals_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(market_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(trading_bp)
    app.register_blueprint(social_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(security_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(analytics_bp)
    
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'environment': settings.FLASK_ENV,
            'database': 'postgresql' if settings.is_postgresql else 'sqlite',
            'websocket': 'enabled'
        })
    
    @app.route('/api/')
    def api_root():
        return jsonify({
            'name': 'Trading Agent API',
            'version': '2.0.0',
            'features': ['REST API', 'WebSocket Real-time'],
            'endpoints': {
                'auth': '/api/auth/*',
                'signals': '/api/signals/*',
                'notifications': '/api/notifications/*',
                'market': '/api/market/*',
                'strategies': '/api/strategies/*',
                'users': '/api/users/*',
                'websocket': '/socket.io/'
            }
        })
    
    with app.app_context():
        init_db()
        init_test_account()
    
    websocket.init_socketio(app)
    
    return app


app = create_app()


def run_server():
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8001))
    debug = settings.FLASK_DEBUG
    
    print(f"🚀 Starting server on {host}:{port}")
    print(f"📡 WebSocket enabled at /socket.io/")
    print(f"🔧 Environment: {settings.FLASK_ENV}")
    print(f"💾 Database: {'PostgreSQL' if settings.is_postgresql else 'SQLite'}")
    
    websocket.price_updater.start()
    simulation_engine.start()
    print(f"🤖 Simulation engine started")
    
    websocket.socketio.run(
        app,
        host=host,
        port=port,
        debug=debug,
        use_reloader=debug
    )


if __name__ == '__main__':
    run_server()
