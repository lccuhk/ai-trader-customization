from flask import Blueprint, request, jsonify
from middleware.auth import require_auth, get_current_user_id
from services import analytics_service

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')


@analytics_bp.route('/track', methods=['POST'])
def track_event():
    data = request.get_json() or {}
    event_type = data.get('event_type')
    event_name = data.get('event_name')
    properties = data.get('properties')
    session_id = data.get('session_id')

    user_id = None
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        user_id = get_current_user_id()

    if not event_type or not event_name:
        return jsonify({'success': False, 'message': '缺少事件参数', 'code': 400}), 400

    analytics_service.track_event(user_id, event_type, event_name, properties, session_id)
    return jsonify({'success': True, 'code': 200, 'data': {'message': '事件已记录'}})


@analytics_bp.route('/user', methods=['GET'])
@require_auth
def get_user_analytics():
    user_id = request.current_user_id
    params = request.args.to_dict()
    result = analytics_service.get_user_analytics(user_id, params)
    return jsonify(result), result.get('code', 200)


@analytics_bp.route('/ab/variant', methods=['GET'])
@require_auth
def get_user_ab_variant():
    user_id = request.current_user_id
    feature_name = request.args.get('feature_name', '')
    if not feature_name:
        return jsonify({'success': False, 'message': '缺少feature_name参数', 'code': 400}), 400
    
    result = analytics_service.get_user_ab_variant(user_id, feature_name)
    return jsonify(result), result.get('code', 200)


@analytics_bp.route('/ab/conversion', methods=['POST'])
@require_auth
def track_ab_conversion():
    user_id = request.current_user_id
    data = request.get_json() or {}
    test_id = data.get('test_id')
    variant = data.get('variant')
    conversion_type = data.get('conversion_type')

    if not test_id or not variant or not conversion_type:
        return jsonify({'success': False, 'message': '缺少必要参数', 'code': 400}), 400

    result = analytics_service.track_ab_conversion(test_id, user_id, variant, conversion_type)
    return jsonify(result), result.get('code', 200)
