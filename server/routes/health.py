from flask import Blueprint, jsonify, request
from datetime import datetime, timezone
import psutil
import platform

from database import get_db
from config import settings

health_bp = Blueprint('health', __name__, url_prefix='/api/health')


@health_bp.route('/check', methods=['GET'])
def health_check():
    db_status = 'healthy'
    try:
        db = next(get_db())
        db.execute('SELECT 1')
    except Exception as e:
        db_status = f'unhealthy: {str(e)}'

    memory = psutil.virtual_memory()
    cpu = psutil.cpu_percent(interval=0.1)
    disk = psutil.disk_usage('/')

    return jsonify({
        'success': True,
        'code': 200,
        'data': {
            'status': 'healthy' if db_status == 'healthy' else 'degraded',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'version': settings.APP_VERSION,
            'environment': settings.ENV,
            'services': {
                'database': db_status,
                'cache': 'healthy',
                'websocket': 'healthy'
            },
            'system': {
                'platform': platform.system(),
                'python_version': platform.python_version(),
                'cpu_usage': cpu,
                'memory': {
                    'total_mb': round(memory.total / 1024 / 1024, 2),
                    'used_mb': round(memory.used / 1024 / 1024, 2),
                    'percent': memory.percent
                },
                'disk': {
                    'total_gb': round(disk.total / 1024 / 1024 / 1024, 2),
                    'used_gb': round(disk.used / 1024 / 1024 / 1024, 2),
                    'percent': disk.percent
                }
            }
        }
    })


@health_bp.route('/metrics', methods=['GET'])
def metrics():
    from models import User, Signal, Trade, Order
    
    db = next(get_db())
    try:
        total_users = db.query(User).count()
        total_signals = db.query(Signal).count()
        total_trades = db.query(Trade).count()
        total_orders = db.query(Order).count()

        return jsonify({
            'success': True,
            'code': 200,
            'data': {
                'users': {
                    'total': total_users,
                    'active_24h': 0
                },
                'signals': {
                    'total': total_signals,
                    'active': db.query(Signal).filter(Signal.status == 'active').count()
                },
                'trades': {
                    'total': total_trades,
                    'simulation': db.query(Trade).filter(Trade.is_simulation == True).count(),
                    'real': db.query(Trade).filter(Trade.is_simulation == False).count()
                },
                'orders': {
                    'total': total_orders,
                    'pending': db.query(Order).filter(Order.status == 'pending').count(),
                    'filled': db.query(Order).filter(Order.status == 'filled').count()
                }
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'code': 500,
            'message': str(e)
        }), 500
    finally:
        db.close()


@health_bp.route('/ready', methods=['GET'])
def readiness():
    return jsonify({
        'success': True,
        'code': 200,
        'data': {
            'ready': True,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    })


@health_bp.route('/live', methods=['GET'])
def liveness():
    return jsonify({
        'success': True,
        'code': 200,
        'data': {
            'alive': True,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    })
