"""
Signals Routes

API endpoints for trading signals, comments, and participants.
"""

from flask import Blueprint, request, jsonify

from services.signal_service import (
    get_signals, get_signal_detail, get_signal_replies,
    get_signal_participants, get_signal_quality, add_reply,
    toggle_follow, get_follow_status, like_signal, like_reply, create_signal
)
from middleware.auth import require_auth

signals_bp = Blueprint('signals', __name__, url_prefix='/api/signals')


@signals_bp.route('/feed', methods=['GET'])
def signals_feed_route():
    limit = int(request.args.get('limit', 20))
    message_type = request.args.get('message_type', '')
    market = request.args.get('market', '')
    
    result, status = get_signals(limit, message_type, market)
    return jsonify(result), status


@signals_bp.route('/<int:signal_id>', methods=['GET'])
def signal_detail_route(signal_id):
    result, status = get_signal_detail(signal_id)
    return jsonify(result), status


@signals_bp.route('/<int:signal_id>/replies', methods=['GET'])
def signal_replies_route(signal_id):
    result, status = get_signal_replies(signal_id)
    return jsonify(result), status


@signals_bp.route('/<int:signal_id>/replies', methods=['POST'])
@require_auth
def add_reply_route(signal_id):
    data = request.get_json()
    content = data.get('content', '').strip()
    parent_id = data.get('parent_id')
    user_id = request.current_user_id
    
    result, status = add_reply(signal_id, user_id, content, parent_id)
    return jsonify(result), status


@signals_bp.route('/<int:signal_id>/participants', methods=['GET'])
def signal_participants_route(signal_id):
    result, status = get_signal_participants(signal_id)
    return jsonify(result), status


@signals_bp.route('/<int:signal_id>/quality-detail', methods=['GET'])
def signal_quality_route(signal_id):
    result, status = get_signal_quality(signal_id)
    return jsonify(result), status


@signals_bp.route('/<int:signal_id>/follow', methods=['GET'])
@require_auth
def get_follow_status_route(signal_id):
    user_id = request.current_user_id
    result, status = get_follow_status(signal_id, user_id)
    return jsonify(result), status


@signals_bp.route('/<int:signal_id>/follow', methods=['POST'])
@require_auth
def toggle_follow_route(signal_id):
    user_id = request.current_user_id
    result, status = toggle_follow(signal_id, user_id)
    return jsonify(result), status


@signals_bp.route('/<int:signal_id>/like', methods=['POST'])
@require_auth
def like_signal_route(signal_id):
    user_id = request.current_user_id
    result, status = like_signal(signal_id, user_id)
    return jsonify(result), status


@signals_bp.route('/<int:signal_id>/replies/<int:reply_id>/like', methods=['POST'])
@require_auth
def like_reply_route(signal_id, reply_id):
    result, status = like_reply(signal_id, reply_id)
    return jsonify(result), status


@signals_bp.route('', methods=['POST'])
@require_auth
def create_signal_route():
    data = request.get_json()
    user_id = request.current_user_id
    
    result, status = create_signal(
        user_id=user_id,
        title=data.get('title', '').strip(),
        content=data.get('content', '').strip(),
        message_type=data.get('type', data.get('message_type', 'operation')),
        market=data.get('market', 'us-stock'),
        symbol=data.get('symbol', ''),
        direction=data.get('direction', ''),
        entry_price=data.get('entry_price'),
        stop_loss=data.get('stop_loss'),
        take_profit=data.get('take_profit')
    )
    return jsonify(result), status
