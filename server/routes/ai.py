from flask import Blueprint, request, jsonify
from middleware.auth import require_auth
from services import ai_service

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')


@ai_bp.route('/signals/generate', methods=['POST'])
@require_auth
def generate_ai_signal():
    user_id = request.current_user_id
    data = request.get_json()
    result = ai_service.generate_ai_signal(user_id, data)
    return jsonify(result), result.get('code', 200)


@ai_bp.route('/signals', methods=['GET'])
@require_auth
def get_ai_signals():
    user_id = request.current_user_id
    params = request.args.to_dict()
    result = ai_service.get_ai_signals(user_id, params)
    return jsonify(result), result.get('code', 200)


@ai_bp.route('/analyze/trading', methods=['POST'])
@require_auth
def analyze_user_trading():
    user_id = request.current_user_id
    data = request.get_json() or {}
    analysis_type = data.get('type', 'comprehensive')
    result = ai_service.analyze_user_trading(user_id, analysis_type)
    return jsonify(result), result.get('code', 200)


@ai_bp.route('/alerts/check', methods=['POST'])
@require_auth
def check_risk_alerts():
    user_id = request.current_user_id
    result = ai_service.check_risk_alerts(user_id)
    return jsonify(result), result.get('code', 200)


@ai_bp.route('/alerts', methods=['GET'])
@require_auth
def get_risk_alerts():
    user_id = request.current_user_id
    params = request.args.to_dict()
    result = ai_service.get_risk_alerts(user_id, params)
    return jsonify(result), result.get('code', 200)


@ai_bp.route('/alerts/<int:alert_id>/acknowledge', methods=['POST'])
@require_auth
def acknowledge_risk_alert(alert_id):
    user_id = request.current_user_id
    result = ai_service.acknowledge_risk_alert(user_id, alert_id)
    return jsonify(result), result.get('code', 200)


@ai_bp.route('/strategies/generate', methods=['POST'])
@require_auth
def generate_strategy():
    user_id = request.current_user_id
    data = request.get_json()
    result = ai_service.generate_strategy(user_id, data)
    return jsonify(result), result.get('code', 200)


@ai_bp.route('/strategies/<int:strategy_id>/backtest', methods=['POST'])
@require_auth
def backtest_strategy(strategy_id):
    user_id = request.current_user_id
    data = request.get_json() or {}
    result = ai_service.backtest_strategy(user_id, strategy_id, data)
    return jsonify(result), result.get('code', 200)


@ai_bp.route('/strategies', methods=['GET'])
@require_auth
def get_strategies():
    user_id = request.current_user_id
    params = request.args.to_dict()
    result = ai_service.get_strategies(user_id, params)
    return jsonify(result), result.get('code', 200)


@ai_bp.route('/chat', methods=['POST'])
@require_auth
def ai_chat():
    user_id = request.current_user_id
    data = request.get_json()
    message = data.get('message', '')
    context = data.get('context')
    
    if not message:
        return jsonify({'success': False, 'message': '消息内容不能为空', 'code': 400}), 400
    
    result = ai_service.ai_chat(user_id, message, context)
    return jsonify(result), result.get('code', 200)
