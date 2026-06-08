from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone, timedelta
import random
from sqlalchemy import and_, or_, desc, func

from database import get_db
from models import AISignal, AIAnalysis, AIRiskAlert, AIStrategy, User, Trade, Position, Signal
from simulation import simulation_engine
from websocket import push_service
from middleware.error_handler import success_response, error_response


def generate_ai_signal(user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    symbol = data.get('symbol')
    strategy = data.get('strategy', 'technical')
    risk_level = data.get('risk_level', 'medium')

    if not symbol:
        return error_response('缺少交易对参数', 400)

    db = next(get_db())
    try:
        current_price = simulation_engine.get_price(symbol)
        if not current_price:
            return error_response('不支持的交易对', 400)

        direction, confidence, reasoning = _generate_signal_logic(symbol, current_price, strategy, risk_level)

        entry_price = current_price
        if direction == 'long':
            take_profit = round(entry_price * 1.05, 2)
            stop_loss = round(entry_price * 0.97, 2)
        else:
            take_profit = round(entry_price * 0.95, 2)
            stop_loss = round(entry_price * 1.03, 2)

        ai_signal = AISignal(
            user_id=user_id,
            symbol=symbol,
            direction=direction,
            entry_price=entry_price,
            take_profit=take_profit,
            stop_loss=stop_loss,
            confidence=confidence,
            reasoning=reasoning,
            strategy=strategy,
            risk_level=risk_level,
            status='active'
        )

        db.add(ai_signal)
        db.commit()
        db.refresh(ai_signal)

        signal_dict = _ai_signal_to_dict(ai_signal)

        try:
            push_service.push_ai_signal(user_id, signal_dict)
        except Exception as e:
            print(f"[AI] Failed to push AI signal: {e}")

        return success_response(signal_dict)

    except Exception as e:
        db.rollback()
        return error_response(f'生成AI信号失败: {str(e)}', 500)
    finally:
        db.close()


def _generate_signal_logic(symbol: str, current_price: float, strategy: str, risk_level: str) -> Tuple[str, float, str]:
    volatility = random.uniform(0.01, 0.05)
    trend = random.choice(['up', 'down', 'sideways'])

    if strategy == 'technical':
        rsi = random.uniform(20, 80)
        ma_short = current_price * (1 + random.uniform(-0.02, 0.02))
        ma_long = current_price * (1 + random.uniform(-0.03, 0.03))

        if rsi < 30 and ma_short > ma_long:
            direction = 'long'
            confidence = min(95, 70 + (30 - rsi))
        elif rsi > 70 and ma_short < ma_long:
            direction = 'short'
            confidence = min(95, 70 + (rsi - 70))
        else:
            direction = random.choice(['long', 'short'])
            confidence = random.uniform(55, 75)

        reasoning = f"技术分析: RSI={rsi:.1f}, 短期均线={ma_short:.2f}, 长期均线={ma_long:.2f}"

    elif strategy == 'trend':
        if trend == 'up':
            direction = 'long'
            confidence = random.uniform(70, 90)
        elif trend == 'down':
            direction = 'short'
            confidence = random.uniform(70, 90)
        else:
            direction = random.choice(['long', 'short'])
            confidence = random.uniform(55, 65)

        reasoning = f"趋势分析: 当前趋势为{trend}, 波动率={volatility:.2%}"

    elif strategy == 'mean_reversion':
        deviation = random.uniform(-0.05, 0.05)
        if deviation < -0.03:
            direction = 'long'
            confidence = min(90, 70 + abs(deviation) * 500)
        elif deviation > 0.03:
            direction = 'short'
            confidence = min(90, 70 + abs(deviation) * 500)
        else:
            direction = random.choice(['long', 'short'])
            confidence = random.uniform(55, 65)

        reasoning = f"均值回归分析: 当前价格偏离均值{deviation:.2%}"

    else:
        direction = random.choice(['long', 'short'])
        confidence = random.uniform(60, 80)
        reasoning = "综合多因子模型分析结果"

    if risk_level == 'low':
        confidence = min(confidence, 85)
    elif risk_level == 'high':
        confidence = min(98, confidence + 5)

    return direction, round(confidence, 2), reasoning


def analyze_user_trading(user_id: int, analysis_type: str = 'comprehensive') -> Dict[str, Any]:
    db = next(get_db())
    try:
        trades = db.query(Trade).filter(
            Trade.user_id == user_id,
            Trade.is_simulation == True
        ).order_by(desc(Trade.created_at)).all()

        positions = db.query(Position).filter(
            Position.user_id == user_id,
            Position.is_simulation == True
        ).all()

        if not trades and not positions:
            return error_response('没有足够的交易数据进行分析', 400)

        analysis_result = _analyze_trading_patterns(trades, positions, analysis_type)

        ai_analysis = AIAnalysis(
            user_id=user_id,
            analysis_type=analysis_type,
            summary=analysis_result['summary'],
            strengths=analysis_result['strengths'],
            weaknesses=analysis_result['weaknesses'],
            recommendations=analysis_result['recommendations'],
            risk_score=analysis_result['risk_score'],
            performance_metrics=analysis_result['metrics']
        )

        db.add(ai_analysis)
        db.commit()
        db.refresh(ai_analysis)

        return success_response({
            'id': ai_analysis.id,
            'analysis_type': ai_analysis.analysis_type,
            'summary': ai_analysis.summary,
            'strengths': ai_analysis.strengths,
            'weaknesses': ai_analysis.weaknesses,
            'recommendations': ai_analysis.recommendations,
            'risk_score': ai_analysis.risk_score,
            'performance_metrics': ai_analysis.performance_metrics,
            'created_at': ai_analysis.created_at.isoformat() if ai_analysis.created_at else None
        })

    except Exception as e:
        db.rollback()
        return error_response(f'分析失败: {str(e)}', 500)
    finally:
        db.close()


def _analyze_trading_patterns(trades: List[Trade], positions: List[Position], analysis_type: str) -> Dict[str, Any]:
    total_trades = len(trades)
    winning_trades = [t for t in trades if t.pnl > 0]
    losing_trades = [t for t in trades if t.pnl < 0]

    win_rate = len(winning_trades) / total_trades * 100 if total_trades > 0 else 0
    total_pnl = sum(t.pnl for t in trades)
    avg_win = sum(t.pnl for t in winning_trades) / len(winning_trades) if winning_trades else 0
    avg_loss = sum(t.pnl for t in losing_trades) / len(losing_trades) if losing_trades else 0
    profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0

    total_position_value = sum(
        (pos.current_price or 0) * pos.quantity for pos in positions
    )
    total_unrealized_pnl = sum(pos.unrealized_pnl for pos in positions)

    risk_score = _calculate_risk_score(trades, positions, total_position_value)

    strengths = []
    weaknesses = []
    recommendations = []

    if win_rate >= 55:
        strengths.append(f'胜率表现良好，达到{win_rate:.1f}%')
    else:
        weaknesses.append(f'胜率偏低，当前为{win_rate:.1f}%，建议提高入场准确性')
        recommendations.append('考虑增加技术指标过滤，提高入场信号质量')

    if profit_factor >= 1.5:
        strengths.append(f'盈亏比优秀，达到{profit_factor:.2f}')
    elif profit_factor < 1:
        weaknesses.append(f'盈亏比不理想，当前为{profit_factor:.2f}')
        recommendations.append('建议扩大盈利空间，严格设置止损')

    if risk_score <= 40:
        strengths.append('风险控制良好，仓位管理得当')
    elif risk_score >= 70:
        weaknesses.append('风险敞口较大，需要加强风险管理')
        recommendations.append('建议降低单笔交易仓位，设置更严格的止损')

    if total_trades >= 30:
        strengths.append('交易经验丰富，样本量充足')
    elif total_trades < 10:
        recommendations.append('建议增加交易次数，积累更多数据以便更准确的分析')

    symbols_traded = set(t.symbol for t in trades)
    if len(symbols_traded) <= 3:
        strengths.append('专注于少数交易对，有利于深入研究')
    else:
        recommendations.append('考虑减少交易对数量，专注于你最熟悉的品种')

    summary_parts = []
    if total_trades > 0:
        summary_parts.append(f'你已完成{total_trades}笔交易')
        summary_parts.append(f'总盈亏: {"+" if total_pnl >= 0 else ""}${total_pnl:.2f}')
        summary_parts.append(f'胜率: {win_rate:.1f}%')
    if total_position_value > 0:
        summary_parts.append(f'当前持仓价值: ${total_position_value:.2f}')
        summary_parts.append(f'未实现盈亏: {"+" if total_unrealized_pnl >= 0 else ""}${total_unrealized_pnl:.2f}')

    summary = ' '.join(summary_parts) if summary_parts else '暂无足够交易数据'

    return {
        'summary': summary,
        'strengths': strengths,
        'weaknesses': weaknesses,
        'recommendations': recommendations,
        'risk_score': risk_score,
        'metrics': {
            'total_trades': total_trades,
            'win_rate': round(win_rate, 2),
            'total_pnl': round(total_pnl, 2),
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2),
            'profit_factor': round(profit_factor, 2),
            'total_position_value': round(total_position_value, 2),
            'total_unrealized_pnl': round(total_unrealized_pnl, 2),
            'symbols_traded': list(symbols_traded)
        }
    }


def _calculate_risk_score(trades: List[Trade], positions: List[Position], total_position_value: float) -> float:
    score = 50.0

    if trades:
        max_single_loss = min((t.pnl for t in trades if t.pnl < 0), default=0)
        if max_single_loss < -500:
            score += 20
        elif max_single_loss < -200:
            score += 10

        pnl_values = [t.pnl for t in trades]
        if len(pnl_values) > 1:
            variance = sum((x - sum(pnl_values)/len(pnl_values))**2 for x in pnl_values) / len(pnl_values)
            if variance > 10000:
                score += 15

    if total_position_value > 50000:
        score += 15
    elif total_position_value > 20000:
        score += 5

    if len(positions) > 5:
        score += 10

    return min(100, max(0, score))


def check_risk_alerts(user_id: int) -> Dict[str, Any]:
    db = next(get_db())
    try:
        positions = db.query(Position).filter(
            Position.user_id == user_id,
            Position.is_simulation == True
        ).all()

        alerts = []

        for position in positions:
            unrealized_pnl_percent = (
                (position.current_price - position.avg_price) / position.avg_price * 100
                if position.avg_price else 0
            )

            if unrealized_pnl_percent <= -10:
                alert = _create_risk_alert(
                    user_id,
                    'high',
                    f'{position.symbol} 持仓亏损超过10%',
                    f'当前{position.symbol}持仓亏损{unrealized_pnl_percent:.2f}%，建议评估是否需要止损',
                    '考虑止损或减仓以控制风险'
                )
                alerts.append(alert)
                db.add(alert)

            elif unrealized_pnl_percent <= -5:
                alert = _create_risk_alert(
                    user_id,
                    'medium',
                    f'{position.symbol} 持仓亏损超过5%',
                    f'当前{position.symbol}持仓亏损{unrealized_pnl_percent:.2f}%，请关注风险',
                    '关注价格走势，必要时调整仓位'
                )
                alerts.append(alert)
                db.add(alert)

        recent_trades = db.query(Trade).filter(
            Trade.user_id == user_id,
            Trade.is_simulation == True,
            Trade.created_at >= datetime.now(timezone.utc) - timedelta(days=1)
        ).all()

        if len(recent_trades) >= 10:
            alert = _create_risk_alert(
                user_id,
                'medium',
                '交易频率过高',
                f'过去24小时内已完成{len(recent_trades)}笔交易，可能存在过度交易风险',
                '建议降低交易频率，提高每笔交易的质量'
            )
            alerts.append(alert)
            db.add(alert)

        daily_pnl = sum(t.pnl for t in recent_trades)
        if daily_pnl <= -1000:
            alert = _create_risk_alert(
                user_id,
                'high',
                '单日亏损过大',
                f'今日已亏损${abs(daily_pnl):.2f}，超过风险阈值',
                '建议暂停交易，调整心态和策略'
            )
            alerts.append(alert)
            db.add(alert)

        db.commit()

        for alert in alerts:
            try:
                push_service.push_ai_alert(user_id, {
                    'id': alert.id,
                    'severity': alert.severity,
                    'title': alert.title,
                    'message': alert.message,
                    'suggested_action': alert.suggested_action,
                    'created_at': alert.created_at.isoformat() if alert.created_at else None
                })
            except Exception as e:
                print(f"[AI] Failed to push risk alert: {e}")

        return success_response([_risk_alert_to_dict(a) for a in alerts])

    except Exception as e:
        db.rollback()
        return error_response(f'检查风险预警失败: {str(e)}', 500)
    finally:
        db.close()


def _create_risk_alert(user_id: int, severity: str, title: str, message: str, suggested_action: str) -> AIRiskAlert:
    return AIRiskAlert(
        user_id=user_id,
        severity=severity,
        title=title,
        message=message,
        suggested_action=suggested_action,
        is_acknowledged=False
    )


def get_risk_alerts(user_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
    severity = params.get('severity')
    is_acknowledged = params.get('is_acknowledged')
    page = int(params.get('page', 1))
    per_page = int(params.get('per_page', 20))

    db = next(get_db())
    try:
        query = db.query(AIRiskAlert).filter(AIRiskAlert.user_id == user_id)

        if severity:
            query = query.filter(AIRiskAlert.severity == severity)
        if is_acknowledged is not None:
            query = query.filter(AIRiskAlert.is_acknowledged == is_acknowledged)

        total = query.count()
        alerts = query.order_by(desc(AIRiskAlert.created_at)).offset((page - 1) * per_page).limit(per_page).all()

        return success_response({
            'items': [_risk_alert_to_dict(a) for a in alerts],
            'total': total,
            'page': page,
            'per_page': per_page
        })

    except Exception as e:
        return error_response(f'获取风险预警失败: {str(e)}', 500)
    finally:
        db.close()


def acknowledge_risk_alert(user_id: int, alert_id: int) -> Dict[str, Any]:
    db = next(get_db())
    try:
        alert = db.query(AIRiskAlert).filter(
            AIRiskAlert.id == alert_id,
            AIRiskAlert.user_id == user_id
        ).first()

        if not alert:
            return error_response('预警不存在', 404)

        alert.is_acknowledged = True
        db.commit()

        return success_response({'message': '已确认预警'})

    except Exception as e:
        db.rollback()
        return error_response(f'确认预警失败: {str(e)}', 500)
    finally:
        db.close()


def generate_strategy(user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    strategy_type = data.get('type', 'trend_following')
    risk_level = data.get('risk_level', 'medium')
    target_symbols = data.get('symbols', ['BTC', 'ETH'])

    db = next(get_db())
    try:
        strategy_code, description, parameters = _generate_strategy_code(strategy_type, risk_level, target_symbols)

        ai_strategy = AIStrategy(
            user_id=user_id,
            name=f'{strategy_type.replace("_", " ").title()} Strategy',
            description=description,
            strategy_type=strategy_type,
            strategy_code=strategy_code,
            parameters=parameters,
            risk_level=risk_level,
            target_symbols=target_symbols,
            is_active=False
        )

        db.add(ai_strategy)
        db.commit()
        db.refresh(ai_strategy)

        return success_response(_ai_strategy_to_dict(ai_strategy))

    except Exception as e:
        db.rollback()
        return error_response(f'生成策略失败: {str(e)}', 500)
    finally:
        db.close()


def _generate_strategy_code(strategy_type: str, risk_level: str, symbols: List[str]) -> Tuple[str, str, Dict[str, Any]]:
    if strategy_type == 'trend_following':
        code = '''
# 趋势跟踪策略
# 基于移动均线交叉和趋势强度指标

def generate_signal(symbol, price_data):
    short_ma = calculate_ma(price_data, period=20)
    long_ma = calculate_ma(price_data, period=50)
    adx = calculate_adx(price_data, period=14)
    
    if short_ma > long_ma and adx > 25:
        return {'direction': 'long', 'confidence': 75}
    elif short_ma < long_ma and adx > 25:
        return {'direction': 'short', 'confidence': 75}
    return None

def calculate_ma(data, period):
    return sum(data[-period:]) / period

def calculate_adx(data, period):
    # ADX计算逻辑
    return 30  # 示例值
'''
        description = '基于移动均线交叉和ADX指标的趋势跟踪策略，在强趋势市场中表现优秀'
        parameters = {'short_ma_period': 20, 'long_ma_period': 50, 'adx_threshold': 25}

    elif strategy_type == 'mean_reversion':
        code = '''
# 均值回归策略
# 基于布林带和RSI指标的反转交易

def generate_signal(symbol, price_data):
    upper, middle, lower = calculate_bollinger_bands(price_data, period=20, std_dev=2)
    rsi = calculate_rsi(price_data, period=14)
    current_price = price_data[-1]
    
    if current_price < lower and rsi < 30:
        return {'direction': 'long', 'confidence': 80}
    elif current_price > upper and rsi > 70:
        return {'direction': 'short', 'confidence': 80}
    return None

def calculate_bollinger_bands(data, period, std_dev):
    import statistics
    middle = sum(data[-period:]) / period
    std = statistics.stdev(data[-period:])
    return middle + std_dev * std, middle, middle - std_dev * std

def calculate_rsi(data, period):
    # RSI计算逻辑
    return 50  # 示例值
'''
        description = '基于布林带和RSI的均值回归策略，适合震荡市场环境'
        parameters = {'bb_period': 20, 'bb_std': 2, 'rsi_period': 14, 'rsi_oversold': 30, 'rsi_overbought': 70}

    elif strategy_type == 'breakout':
        code = '''
# 突破交易策略
# 基于支撑阻力位突破的交易策略

def generate_signal(symbol, price_data, volume_data):
    resistance = max(price_data[-20:])
    support = min(price_data[-20:])
    current_price = price_data[-1]
    current_volume = volume_data[-1]
    avg_volume = sum(volume_data[-20:]) / 20
    
    volume_confirmation = current_volume > avg_volume * 1.5
    
    if current_price > resistance and volume_confirmation:
        return {'direction': 'long', 'confidence': 85}
    elif current_price < support and volume_confirmation:
        return {'direction': 'short', 'confidence': 85}
    return None
'''
        description = '基于支撑阻力位突破和成交量确认的策略，捕捉价格爆发性行情'
        parameters = {'lookback_period': 20, 'volume_multiplier': 1.5}

    else:
        code = '# 自定义策略\n# 请在此处实现你的交易逻辑'
        description = '自定义策略模板'
        parameters = {}

    if risk_level == 'low':
        parameters['position_size'] = 0.05
        parameters['stop_loss'] = 0.02
        parameters['take_profit'] = 0.04
    elif risk_level == 'high':
        parameters['position_size'] = 0.15
        parameters['stop_loss'] = 0.05
        parameters['take_profit'] = 0.10
    else:
        parameters['position_size'] = 0.10
        parameters['stop_loss'] = 0.03
        parameters['take_profit'] = 0.06

    return code.strip(), description, parameters


def backtest_strategy(user_id: int, strategy_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    initial_capital = data.get('initial_capital', 100000)

    db = next(get_db())
    try:
        strategy = db.query(AIStrategy).filter(
            AIStrategy.id == strategy_id,
            AIStrategy.user_id == user_id
        ).first()

        if not strategy:
            return error_response('策略不存在', 404)

        backtest_result = _run_backtest(strategy, start_date, end_date, initial_capital)

        strategy.backtest_results = backtest_result
        strategy.last_backtest_at = datetime.now(timezone.utc)
        db.commit()

        return success_response({
            'strategy_id': strategy_id,
            'backtest_result': backtest_result
        })

    except Exception as e:
        db.rollback()
        return error_response(f'回测失败: {str(e)}', 500)
    finally:
        db.close()


def _run_backtest(strategy: AIStrategy, start_date: Optional[str], end_date: Optional[str], initial_capital: float) -> Dict[str, Any]:
    random.seed(hash(strategy.id) % 10000)

    total_days = random.randint(60, 365)
    daily_returns = [random.gauss(0.001, 0.02) for _ in range(total_days)]

    cumulative_returns = []
    capital = initial_capital
    peak = initial_capital
    max_drawdown = 0
    winning_days = 0
    losing_days = 0

    for ret in daily_returns:
        capital *= (1 + ret)
        cumulative_returns.append(capital)
        if capital > peak:
            peak = capital
        drawdown = (peak - capital) / peak
        if drawdown > max_drawdown:
            max_drawdown = drawdown
        if ret > 0:
            winning_days += 1
        elif ret < 0:
            losing_days += 1

    total_return = (capital - initial_capital) / initial_capital * 100
    annualized_return = total_return * (365 / total_days)
    sharpe_ratio = (sum(daily_returns) / len(daily_returns)) / (pd.Series(daily_returns).std() if len(daily_returns) > 1 else 1) * (365 ** 0.5)
    win_rate = winning_days / (winning_days + losing_days) * 100 if (winning_days + losing_days) > 0 else 0

    return {
        'initial_capital': initial_capital,
        'final_capital': round(capital, 2),
        'total_return': round(total_return, 2),
        'annualized_return': round(annualized_return, 2),
        'sharpe_ratio': round(sharpe_ratio, 2),
        'max_drawdown': round(max_drawdown * 100, 2),
        'win_rate': round(win_rate, 2),
        'total_days': total_days,
        'winning_days': winning_days,
        'losing_days': losing_days,
        'start_date': start_date,
        'end_date': end_date,
        'equity_curve': [round(v, 2) for v in cumulative_returns[::max(1, len(cumulative_returns) // 100)]]
    }


def get_ai_signals(user_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
    status = params.get('status')
    symbol = params.get('symbol')
    page = int(params.get('page', 1))
    per_page = int(params.get('per_page', 20))

    db = next(get_db())
    try:
        query = db.query(AISignal).filter(AISignal.user_id == user_id)

        if status:
            query = query.filter(AISignal.status == status)
        if symbol:
            query = query.filter(AISignal.symbol == symbol)

        total = query.count()
        signals = query.order_by(desc(AISignal.created_at)).offset((page - 1) * per_page).limit(per_page).all()

        return success_response({
            'items': [_ai_signal_to_dict(s) for s in signals],
            'total': total,
            'page': page,
            'per_page': per_page
        })

    except Exception as e:
        return error_response(f'获取AI信号失败: {str(e)}', 500)
    finally:
        db.close()


def get_strategies(user_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
    is_active = params.get('is_active')
    page = int(params.get('page', 1))
    per_page = int(params.get('per_page', 20))

    db = next(get_db())
    try:
        query = db.query(AIStrategy).filter(AIStrategy.user_id == user_id)

        if is_active is not None:
            query = query.filter(AIStrategy.is_active == is_active)

        total = query.count()
        strategies = query.order_by(desc(AIStrategy.created_at)).offset((page - 1) * per_page).limit(per_page).all()

        return success_response({
            'items': [_ai_strategy_to_dict(s) for s in strategies],
            'total': total,
            'page': page,
            'per_page': per_page
        })

    except Exception as e:
        return error_response(f'获取策略列表失败: {str(e)}', 500)
    finally:
        db.close()


def ai_chat(user_id: int, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if not message or not message.strip():
        return error_response('消息内容不能为空', 400)

    try:
        response = _generate_chat_response(message, context)
        return success_response({
            'response': response,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })

    except Exception as e:
        return error_response(f'AI对话失败: {str(e)}', 500)


def _generate_chat_response(message: str, context: Optional[Dict[str, Any]]) -> str:
    message_lower = message.lower()

    if any(keyword in message_lower for keyword in ['btc', 'bitcoin', '比特币']):
        return '比特币当前处于关键技术位。从长期来看，比特币作为数字黄金的叙事仍然成立，但短期可能受到宏观经济因素影响。建议关注4小时级别MACD和成交量变化。'

    if any(keyword in message_lower for keyword in ['eth', 'ethereum', '以太坊']):
        return '以太坊在合并后进入了新的发展阶段。Layer2生态的蓬勃发展为以太坊带来了更多可能性。技术面上，关注能否站稳关键支撑位。'

    if any(keyword in message_lower for keyword in ['风险', '止损', '仓位', 'risk', 'stop']):
        return '风险管理是交易中最重要的环节。建议：1) 单笔交易风险不超过总资金的2%；2) 每笔交易都设置止损；3) 避免过度交易；4) 定期评估和调整仓位。'

    if any(keyword in message_lower for keyword in ['策略', 'strategy', '系统']):
        return '一个好的交易策略应该包含：入场条件、出场条件（止损/止盈）、仓位管理、风险控制。建议先在模拟账户测试，验证策略有效性后再实盘应用。'

    if any(keyword in message_lower for keyword in ['均线', 'ma', '移动平均']):
        return '移动均线是最常用的技术指标之一。常见用法包括：均线交叉（金叉/死叉）、价格与均线的位置关系、多均线排列。建议结合其他指标使用，避免单一指标的局限性。'

    if any(keyword in message_lower for keyword in ['rsi', '相对强弱']):
        return 'RSI（相对强弱指数）用于衡量价格变动的速度和变化。一般来说，RSI>70视为超买，<30视为超卖。但在强趋势市场中，超买超卖信号可能失效，建议结合趋势分析。'

    default_responses = [
        '这是一个很好的问题。在交易中，保持学习和思考的习惯非常重要。你对哪个具体的交易品种或策略更感兴趣呢？',
        '交易是一场马拉松，不是短跑。建议你建立自己的交易系统，严格执行，并持续优化。有什么具体问题我可以帮你解答吗？',
        '市场永远是对的，我们要做的是适应市场。你目前在交易中遇到的最大挑战是什么？也许我可以给你一些建议。',
        '成功的交易需要：良好的心态、有效的策略、严格的风控。三者缺一不可。你目前更关注哪方面呢？'
    ]

    return random.choice(default_responses)


def _ai_signal_to_dict(signal: AISignal) -> Dict[str, Any]:
    return {
        'id': signal.id,
        'symbol': signal.symbol,
        'direction': signal.direction,
        'entry_price': signal.entry_price,
        'take_profit': signal.take_profit,
        'stop_loss': signal.stop_loss,
        'confidence': signal.confidence,
        'reasoning': signal.reasoning,
        'strategy': signal.strategy,
        'risk_level': signal.risk_level,
        'status': signal.status,
        'pnl': signal.pnl,
        'pnl_percent': signal.pnl_percent,
        'current_price': signal.current_price,
        'created_at': signal.created_at.isoformat() if signal.created_at else None,
        'closed_at': signal.closed_at.isoformat() if signal.closed_at else None
    }


def _risk_alert_to_dict(alert: AIRiskAlert) -> Dict[str, Any]:
    return {
        'id': alert.id,
        'severity': alert.severity,
        'title': alert.title,
        'message': alert.message,
        'suggested_action': alert.suggested_action,
        'is_acknowledged': alert.is_acknowledged,
        'created_at': alert.created_at.isoformat() if alert.created_at else None
    }


def _ai_strategy_to_dict(strategy: AIStrategy) -> Dict[str, Any]:
    return {
        'id': strategy.id,
        'name': strategy.name,
        'description': strategy.description,
        'strategy_type': strategy.strategy_type,
        'strategy_code': strategy.strategy_code,
        'parameters': strategy.parameters,
        'risk_level': strategy.risk_level,
        'target_symbols': strategy.target_symbols,
        'is_active': strategy.is_active,
        'backtest_results': strategy.backtest_results,
        'created_at': strategy.created_at.isoformat() if strategy.created_at else None,
        'last_backtest_at': strategy.last_backtest_at.isoformat() if strategy.last_backtest_at else None
    }


try:
    import pandas as pd
except ImportError:
    class pd:
        class Series:
            def __init__(self, data):
                self._data = data
            def std(self):
                import statistics
                return statistics.stdev(self._data) if len(self._data) > 1 else 1
