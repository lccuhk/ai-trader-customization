from flask import Blueprint, request, jsonify
from middleware.auth import require_auth
from services import social_service

social_bp = Blueprint('social', __name__, url_prefix='/api/social')


@social_bp.route('/follow/<int:user_id>', methods=['POST'])
@require_auth
def follow_user(user_id):
    user_id_curr = request.current_user_id
    result = social_service.follow_user(user_id_curr, user_id)
    return jsonify(result), result.get('code', 200)


@social_bp.route('/unfollow/<int:user_id>', methods=['POST'])
@require_auth
def unfollow_user(user_id):
    user_id_curr = request.current_user_id
    result = social_service.unfollow_user(user_id_curr, user_id)
    return jsonify(result), result.get('code', 200)


@social_bp.route('/followers/<int:user_id>', methods=['GET'])
def get_followers(user_id):
    params = request.args.to_dict()
    result = social_service.get_followers(user_id, params)
    return jsonify(result), result.get('code', 200)


@social_bp.route('/following/<int:user_id>', methods=['GET'])
def get_following(user_id):
    params = request.args.to_dict()
    result = social_service.get_following(user_id, params)
    return jsonify(result), result.get('code', 200)


@social_bp.route('/profile/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    current_user_id = None
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        from middleware.auth import get_current_user_id
        current_user_id = get_current_user_id()
    
    result = social_service.get_user_profile(user_id, current_user_id)
    return jsonify(result), result.get('code', 200)


@social_bp.route('/messages', methods=['POST'])
@require_auth
def send_direct_message():
    user_id_curr = request.current_user_id
    data = request.get_json()
    receiver_id = data.get('receiver_id')
    content = data.get('content', '')
    
    if not receiver_id:
        return jsonify({'success': False, 'message': '缺少接收用户ID', 'code': 400}), 400
    
    result = social_service.send_direct_message(user_id_curr, receiver_id, content)
    return jsonify(result), result.get('code', 200)


@social_bp.route('/messages/<int:other_user_id>', methods=['GET'])
@require_auth
def get_direct_messages(other_user_id):
    user_id_curr = request.current_user_id
    params = request.args.to_dict()
    result = social_service.get_direct_messages(user_id_curr, other_user_id, params)
    return jsonify(result), result.get('code', 200)


@social_bp.route('/conversations', methods=['GET'])
@require_auth
def get_conversations():
    user_id_curr = request.current_user_id
    result = social_service.get_conversations(user_id_curr)
    return jsonify(result), result.get('code', 200)


@social_bp.route('/mentions', methods=['GET'])
@require_auth
def get_mentions():
    user_id_curr = request.current_user_id
    params = request.args.to_dict()
    result = social_service.get_mentions(user_id_curr, params)
    return jsonify(result), result.get('code', 200)


@social_bp.route('/share/<int:signal_id>', methods=['POST'])
@require_auth
def share_signal(signal_id):
    user_id_curr = request.current_user_id
    data = request.get_json() or {}
    platform = data.get('platform', 'link')
    result = social_service.share_signal(user_id_curr, signal_id, platform)
    return jsonify(result), result.get('code', 200)


@social_bp.route('/users/search', methods=['GET'])
def search_users():
    query = request.args.get('q', '')
    params = request.args.to_dict()
    
    if not query:
        return jsonify({'success': False, 'message': '搜索关键词不能为空', 'code': 400}), 400
    
    result = social_service.search_users(query, params)
    return jsonify(result), result.get('code', 200)
