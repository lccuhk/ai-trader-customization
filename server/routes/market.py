"""
Market Routes

API endpoints for market news and strategies.
"""

from flask import Blueprint, request, jsonify

from services.market_service import (
    get_market_news, get_news_detail, get_strategies,
    get_strategy_detail, create_strategy
)

market_bp = Blueprint('market', __name__, url_prefix='/api')


@market_bp.route('/market/news', methods=['GET'])
def market_news_route():
    limit = int(request.args.get('limit', 10))
    category = request.args.get('category', '')
    
    result, status = get_market_news(limit, category)
    return jsonify(result), status


@market_bp.route('/market/news/<int:news_id>', methods=['GET'])
def market_news_detail_route(news_id):
    result, status = get_news_detail(news_id)
    return jsonify(result), status


@market_bp.route('/strategies', methods=['GET'])
def strategies_route():
    result, status = get_strategies()
    return jsonify(result), status


@market_bp.route('/strategies/<int:strategy_id>', methods=['GET'])
def strategy_detail_route(strategy_id):
    result, status = get_strategy_detail(strategy_id)
    return jsonify(result), status


@market_bp.route('/strategies', methods=['POST'])
def create_strategy_route():
    data = request.get_json()
    
    result, status = create_strategy(
        name=data.get('name', ''),
        description=data.get('description', ''),
        strategy_type=data.get('strategy_type', 'custom'),
        code=data.get('code', ''),
        parameters=data.get('parameters', {})
    )
    return jsonify(result), status
