"""
Error Handler Middleware

Global error handling and response formatting.
"""

import traceback
import sys
from typing import Any, Dict

from flask import jsonify


def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'message': '资源不存在',
            'error': str(error)
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'message': '请求方法不允许',
            'error': str(error)
        }), 405
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'message': '请求参数错误',
            'error': str(error)
        }), 400
    
    @app.errorhandler(500)
    def internal_error(error):
        print(f"[ERROR] 500 Internal Error: {error}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return jsonify({
            'success': False,
            'message': '服务器内部错误',
            'error': str(error) if app.debug else None
        }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        print(f"[ERROR] Unhandled Exception: {error}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return jsonify({
            'success': False,
            'message': '服务器内部错误',
            'error': str(error) if app.debug else None
        }), 500


def success_response(data: Any = None, message: str = '操作成功') -> Dict[str, Any]:
    return {
        'success': True,
        'message': message,
        'data': data
    }


def error_response(message: str, error: Any = None, code: int = 400) -> Dict[str, Any]:
    return {
        'success': False,
        'message': message,
        'error': str(error) if error else None
    }, code
