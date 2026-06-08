from flask import Blueprint, request, jsonify
from middleware.auth import require_auth
from services import admin_service, analytics_service

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


@admin_bp.route('/stats', methods=['GET'])
@require_auth
def get_admin_stats():
    user_id = request.current_user_id
    result = admin_service.get_admin_stats(user_id)
    return jsonify(result), result.get('code', 200)


@admin_bp.route('/users', methods=['GET'])
@require_auth
def get_users():
    user_id = request.current_user_id
    params = request.args.to_dict()
    result = admin_service.get_users(user_id, params)
    return jsonify(result), result.get('code', 200)


@admin_bp.route('/users/<int:user_id>/status', methods=['PUT'])
@require_auth
def update_user_status(user_id):
    admin_user_id = request.current_user_id
    data = request.get_json() or {}
    result = admin_service.update_user_status(admin_user_id, user_id, data)
    return jsonify(result), result.get('code', 200)


@admin_bp.route('/signals', methods=['GET'])
@require_auth
def get_signals():
    user_id = request.current_user_id
    params = request.args.to_dict()
    result = admin_service.get_signals(user_id, params)
    return jsonify(result), result.get('code', 200)


@admin_bp.route('/signals/<int:signal_id>/moderate', methods=['POST'])
@require_auth
def moderate_signal(signal_id):
    user_id = request.current_user_id
    data = request.get_json() or {}
    result = admin_service.moderate_signal(user_id, signal_id, data)
    return jsonify(result), result.get('code', 200)


@admin_bp.route('/notifications/send', methods=['POST'])
@require_auth
def send_system_notification():
    user_id = request.current_user_id
    data = request.get_json() or {}
    result = admin_service.send_system_notification(user_id, data)
    return jsonify(result), result.get('code', 200)


@admin_bp.route('/actions', methods=['GET'])
@require_auth
def get_admin_actions():
    user_id = request.current_user_id
    params = request.args.to_dict()
    result = admin_service.get_admin_actions(user_id, params)
    return jsonify(result), result.get('code', 200)


@admin_bp.route('/analytics/platform', methods=['GET'])
@require_auth
def get_platform_analytics():
    user_id = request.current_user_id
    params = request.args.to_dict()
    result = analytics_service.get_platform_analytics(params)
    return jsonify(result), result.get('code', 200)


@admin_bp.route('/analytics/funnel', methods=['GET'])
@require_auth
def get_funnel_analysis():
    user_id = request.current_user_id
    params = request.args.to_dict()
    result = analytics_service.get_funnel_analysis(params)
    return jsonify(result), result.get('code', 200)


@admin_bp.route('/analytics/retention', methods=['GET'])
@require_auth
def get_retention_analysis():
    user_id = request.current_user_id
    params = request.args.to_dict()
    result = analytics_service.get_retention_analysis(params)
    return jsonify(result), result.get('code', 200)


@admin_bp.route('/ab-tests', methods=['GET'])
@require_auth
def get_ab_tests():
    user_id = request.current_user_id
    params = request.args.to_dict()
    result = analytics_service.get_ab_tests(params)
    return jsonify(result), result.get('code', 200)


@admin_bp.route('/ab-tests', methods=['POST'])
@require_auth
def create_ab_test():
    user_id = request.current_user_id
    data = request.get_json() or {}
    result = analytics_service.create_ab_test(user_id, data)
    return jsonify(result), result.get('code', 200)
