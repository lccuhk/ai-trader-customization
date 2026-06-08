from flask import Blueprint, request, jsonify
from middleware.auth import require_auth
from services import trading_service

trading_bp = Blueprint('trading', __name__, url_prefix='/api/trading')


@trading_bp.route('/orders', methods=['POST'])
@require_auth
def create_order():
    user_id = request.current_user_id
    data = request.get_json()
    result = trading_service.create_order(user_id, data)
    return jsonify(result), result.get('code', 200)


@trading_bp.route('/orders/<int:order_id>/cancel', methods=['POST'])
@require_auth
def cancel_order(order_id):
    user_id = request.current_user_id
    result = trading_service.cancel_order(user_id, order_id)
    return jsonify(result), result.get('code', 200)


@trading_bp.route('/orders', methods=['GET'])
@require_auth
def get_orders():
    user_id = request.current_user_id
    params = request.args.to_dict()
    result = trading_service.get_orders(user_id, params)
    return jsonify(result), result.get('code', 200)


@trading_bp.route('/orders/<int:order_id>', methods=['GET'])
@require_auth
def get_order_detail(order_id):
    user_id = request.current_user_id
    result = trading_service.get_order_detail(user_id, order_id)
    return jsonify(result), result.get('code', 200)


@trading_bp.route('/positions', methods=['GET'])
@require_auth
def get_positions():
    user_id = request.current_user_id
    params = request.args.to_dict()
    result = trading_service.get_positions(user_id, params)
    return jsonify(result), result.get('code', 200)


@trading_bp.route('/trades', methods=['GET'])
@require_auth
def get_trades():
    user_id = request.current_user_id
    params = request.args.to_dict()
    result = trading_service.get_trades(user_id, params)
    return jsonify(result), result.get('code', 200)


@trading_bp.route('/portfolio', methods=['GET'])
@require_auth
def get_portfolio():
    user_id = request.current_user_id
    is_simulation = request.args.get('is_simulation', 'true').lower() == 'true'
    result = trading_service.get_portfolio(user_id, is_simulation)
    return jsonify(result), result.get('code', 200)


@trading_bp.route('/exchange-accounts', methods=['GET'])
@require_auth
def get_exchange_accounts():
    user_id = request.current_user_id
    result = trading_service.get_exchange_accounts(user_id)
    return jsonify(result), result.get('code', 200)


@trading_bp.route('/exchange-accounts', methods=['POST'])
@require_auth
def create_exchange_account():
    user_id = request.current_user_id
    data = request.get_json()
    result = trading_service.create_exchange_account(user_id, data)
    return jsonify(result), result.get('code', 200)


@trading_bp.route('/exchange-accounts/<int:account_id>', methods=['DELETE'])
@require_auth
def delete_exchange_account(account_id):
    user_id = request.current_user_id
    result = trading_service.delete_exchange_account(user_id, account_id)
    return jsonify(result), result.get('code', 200)


@trading_bp.route('/market/price/<symbol>', methods=['GET'])
def get_market_price(symbol):
    result = trading_service.get_market_price(symbol)
    return jsonify(result), result.get('code', 200)


@trading_bp.route('/market/prices', methods=['GET'])
def get_all_market_prices():
    result = trading_service.get_all_market_prices()
    return jsonify(result), result.get('code', 200)
