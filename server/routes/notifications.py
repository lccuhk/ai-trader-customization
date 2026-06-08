"""
Notifications Routes

API endpoints for notifications.
"""

from flask import Blueprint, request, jsonify

from services.notification_service import (
    get_notifications, mark_notification_read, mark_all_read
)
from middleware.auth import require_auth

notifications_bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')


@notifications_bp.route('', methods=['GET'])
@require_auth
def get_notifications_route():
    user_id = request.current_user_id
    limit = int(request.args.get('limit', 20))
    
    result, status = get_notifications(user_id, limit)
    return jsonify(result), status


@notifications_bp.route('/<int:notification_id>/read', methods=['PUT'])
@require_auth
def mark_read_route(notification_id):
    user_id = request.current_user_id
    result, status = mark_notification_read(notification_id, user_id)
    return jsonify(result), status


@notifications_bp.route('/read-all', methods=['PUT'])
@require_auth
def mark_all_read_route():
    user_id = request.current_user_id
    result, status = mark_all_read(user_id)
    return jsonify(result), status
