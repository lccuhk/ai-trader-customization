"""
Users Routes

API endpoints for user-related operations.
"""

from flask import Blueprint, request, jsonify

from services.auth_service import get_current_user_info
from middleware.auth import require_auth

users_bp = Blueprint('users', __name__, url_prefix='/api/users')


@users_bp.route('/me', methods=['GET'])
@require_auth
def get_me_route():
    user_id = request.current_user_id
    result, status = get_current_user_info(user_id)
    return jsonify(result), status
