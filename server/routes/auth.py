"""
Authentication Routes

API endpoints for user authentication.
"""

from flask import Blueprint, request, jsonify

from services.auth_service import login, register, get_current_user_info
from middleware.auth import require_auth

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/login', methods=['POST'])
def login_route():
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')
    
    result, status = login(username, password)
    return jsonify(result), status


@auth_bp.route('/register', methods=['POST'])
def register_route():
    data = request.get_json()
    username = data.get('username', '')
    email = data.get('email', '')
    password = data.get('password', '')
    
    result, status = register(username, email, password)
    return jsonify(result), status


@auth_bp.route('/me', methods=['GET'])
@require_auth
def get_me_route():
    user_id = request.current_user_id
    result, status = get_current_user_info(user_id)
    return jsonify(result), status
