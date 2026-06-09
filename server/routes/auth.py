"""
Authentication Routes

API endpoints for user authentication.
"""

from flask import Blueprint, request, jsonify

from services.auth_service import login, register, get_current_user_info
from middleware.auth import require_auth
from middleware.rate_limit import (
    ip_restriction_required,
    ip_ban_required,
    rate_limit,
    record_failed_attempt,
    reset_failed_attempts,
    get_client_ip,
    LOGIN_RATE_LIMIT,
    LOGIN_RATE_WINDOW,
    ME_RATE_LIMIT,
    ME_RATE_WINDOW,
    BAN_DURATION
)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/login', methods=['POST'])
@ip_restriction_required
@ip_ban_required
@rate_limit('auth', by_user=False, check_ban=False)
def login_route():
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')
    
    result, status = login(username, password)
    ip = get_client_ip()
    
    # 记录失败尝试用于IP封禁
    if status == 401:
        is_banned = record_failed_attempt(ip)
        if is_banned:
            # 如果达到最大尝试次数，直接返回封禁状态
            return jsonify({
                'success': False,
                'message': f'IP 已被暂时封禁，请 {BAN_DURATION} 秒后再试'
            }), 429
    elif status == 200:
        reset_failed_attempts(ip)
    
    return jsonify(result), status


@auth_bp.route('/register', methods=['POST'])
@ip_restriction_required
def register_route():
    data = request.get_json()
    username = data.get('username', '')
    email = data.get('email', '')
    password = data.get('password', '')
    
    result, status = register(username, email, password)
    return jsonify(result), status


@auth_bp.route('/me', methods=['GET'])
@ip_restriction_required
@require_auth
@rate_limit('strict', by_user=True, check_ban=False)
def get_me_route():
    user_id = request.current_user_id
    result, status = get_current_user_info(user_id)
    return jsonify(result), status
