"""
AI-Trader 新功能 API 路由

包含以下十个新功能的 API 端点：
1. 实时价格预警系统
2. 投资组合分析仪表盘
3. AI交易策略回测引擎
4. 多账户资金管理
5. 社交交易排行榜
6. 智能订单路由
7. 交易日记和复盘系统
8. 宏观经济指标追踪
9. 交易信号质量评分
10. API交易网关
"""

from __future__ import annotations

import json
import random
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field

from extensions import (
    AlertType, AlertStatus, AlertChannel,
    AccountType, ExchangeType,
    PriceAlert, TradingAccount, TradingJournalEntry,
    get_price_alert_system, get_portfolio_analyzer,
    get_backtest_engine, get_multi_account_manager,
    get_social_leaderboard, get_smart_order_router,
    get_trading_journal, get_macro_economic_tracker,
    get_signal_quality_scorer, get_trading_gateway
)


router = APIRouter(prefix="/api/extensions", tags=["extensions"])


# ==================== 请求/响应模型 ====================

class CreateAlertRequest(BaseModel):
    symbol: str
    market: str = "us-stock"
    alert_type: str
    target_price: float
    threshold_percent: Optional[float] = None
    channel: str = "in_app"
    message: str = ""
    expires_at: Optional[str] = None


class CreateAccountRequest(BaseModel):
    name: str
    account_type: str = "paper"
    exchange: str = "polymarket"
    balance: float = 0.0
    api_key: str = ""
    api_secret: str = ""


class CreateJournalEntryRequest(BaseModel):
    position_id: Optional[int] = None
    symbol: str
    market: str = "us-stock"
    side: str
    entry_price: float
    exit_price: Optional[float] = None
    quantity: float
    pnl: Optional[float] = None
    pnl_percent: Optional[float] = None
    entry_reason: str = ""
    exit_reason: str = ""
    emotions: List[str] = []
    tags: List[str] = []
    lessons_learned: str = ""
    mistakes: str = ""
    rating: int = 0


class BacktestRequest(BaseModel):
    strategy_name: str
    initial_capital: float = 100000.0
    symbol: str = "AAPL"
    start_date: str
    end_date: str
    strategy_params: Dict[str, Any] = {}


class CapitalAllocationRequest(BaseModel):
    allocations: Dict[int, float]


class PlaceOrderRequest(BaseModel):
    symbol: str
    side: str
    quantity: float
    order_type: str = "market"
    price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    exchange: Optional[str] = None


class SmartOrderRequest(BaseModel):
    symbol: str
    side: str
    quantity: float
    available_exchanges: List[str]
    order_type: str = "market"


# ==================== 功能1: 实时价格预警系统 ====================

@router.post("/alerts", summary="创建价格预警")
async def create_alert(request: Request, data: CreateAlertRequest):
    agent_id = request.state.agent_id if hasattr(request.state, "agent_id") else 1
    
    alert = PriceAlert(
        agent_id=agent_id,
        symbol=data.symbol,
        market=data.market,
        alert_type=AlertType(data.alert_type),
        target_price=data.target_price,
        threshold_percent=data.threshold_percent,
        channel=AlertChannel(data.channel),
        message=data.message,
        expires_at=data.expires_at
    )
    
    alert_id = get_price_alert_system().create_alert(alert)
    return {"success": True, "alert_id": alert_id}


@router.get("/alerts", summary="获取代理的所有预警")
async def get_alerts(
    request: Request,
    status: Optional[str] = Query(None, description="预警状态: active, triggered, expired, cancelled")
):
    agent_id = request.state.agent_id if hasattr(request.state, "agent_id") else 1
    
    alert_status = AlertStatus(status) if status else None
    alerts = get_price_alert_system().get_agent_alerts(agent_id, alert_status)
    
    return {
        "success": True,
        "alerts": [
            {
                "id": a.id,
                "symbol": a.symbol,
                "market": a.market,
                "alert_type": a.alert_type.value,
                "target_price": a.target_price,
                "current_price": a.current_price,
                "status": a.status.value,
                "triggered_at": a.triggered_at,
                "created_at": a.created_at,
                "message": a.message
            }
            for a in alerts
        ]
    }


@router.post("/alerts/check", summary="检查并触发预警")
async def check_alerts(symbol: str, current_price: float, market: str = "us-stock"):
    triggered = get_price_alert_system().check_alerts(symbol, current_price, market)
    return {
        "success": True,
        "triggered_count": len(triggered),
        "triggered_alerts": [
            {"id": a.id, "symbol": a.symbol, "message": a.message}
            for a in triggered
        ]
    }


# ==================== 功能2: 投资组合分析仪表盘 ====================

@router.get("/portfolio/analysis", summary="分析投资组合")
async def analyze_portfolio(request: Request):
    agent_id = request.state.agent_id if hasattr(request.state, "agent_id") else 1
    
    metrics = get_portfolio_analyzer().analyze_portfolio(agent_id)
    
    return {
        "success": True,
        "portfolio": {
            "total_value": metrics.total_value,
            "total_cost": metrics.total_cost,
            "total_pnl": metrics.total_pnl,
            "total_pnl_percent": metrics.total_pnl_percent,
            "cash_balance": metrics.cash_balance,
            "position_count": metrics.position_count,
            "long_count": metrics.long_count,
            "short_count": metrics.short_count,
            "market_exposure": metrics.market_exposure,
            "risk_metrics": metrics.risk_metrics,
            "top_positions": metrics.top_positions,
            "worst_positions": metrics.worst_positions
        }
    }


@router.get("/portfolio/history", summary="获取投资组合历史")
async def get_portfolio_history(
    request: Request,
    days: int = Query(30, ge=1, le=365)
):
    agent_id = request.state.agent_id if hasattr(request.state, "agent_id") else 1
    
    history = get_portfolio_analyzer().get_portfolio_history(agent_id, days)
    return {"success": True, "history": history}


# ==================== 功能3: AI交易策略回测引擎 ====================

@router.post("/backtest/run", summary="运行策略回测")
async def run_backtest(data: BacktestRequest):
    engine = get_backtest_engine()
    
    historical_data = []
    start = datetime.fromisoformat(data.start_date.replace("Z", "+00:00"))
    end = datetime.fromisoformat(data.end_date.replace("Z", "+00:00"))
    current = start
    price = 100.0
    
    while current <= end:
        change = (random.random() - 0.5) * 0.04
        price *= (1 + change)
        historical_data.append({
            "date": current.isoformat().replace("+00:00", "Z"),
            "open": price * 0.995,
            "high": price * 1.01,
            "low": price * 0.99,
            "close": price,
            "volume": random.randint(100000, 1000000)
        })
        current += timedelta(days=1)
    
    def simple_strategy(data, **params):
        if random.random() > 0.7:
            return {"side": "long" if random.random() > 0.5 else "short"}
        if random.random() > 0.8:
            return {"action": "close"}
        return None
    
    result = engine.run_backtest(
        strategy_name=data.strategy_name,
        historical_data=historical_data,
        strategy_func=simple_strategy,
        initial_capital=data.initial_capital
    )
    
    return {
        "success": True,
        "result": {
            "strategy_name": result.strategy_name,
            "start_date": result.start_date,
            "end_date": result.end_date,
            "initial_capital": result.initial_capital,
            "final_capital": result.final_capital,
            "total_return": result.total_return,
            "total_return_percent": result.total_return_percent,
            "sharpe_ratio": result.sharpe_ratio,
            "max_drawdown_percent": result.max_drawdown_percent,
            "win_rate": result.win_rate,
            "profit_factor": result.profit_factor,
            "total_trades": result.total_trades,
            "winning_trades": result.winning_trades,
            "losing_trades": result.losing_trades,
            "volatility": result.volatility,
            "metrics": result.metrics
        }
    }


# ==================== 功能4: 多账户资金管理 ====================

@router.post("/accounts", summary="创建交易账户")
async def create_account(request: Request, data: CreateAccountRequest):
    agent_id = request.state.agent_id if hasattr(request.state, "agent_id") else 1
    
    account = TradingAccount(
        agent_id=agent_id,
        name=data.name,
        account_type=AccountType(data.account_type),
        exchange=ExchangeType(data.exchange),
        balance=data.balance,
        available_balance=data.balance,
        api_key=data.api_key,
        api_secret=data.api_secret
    )
    
    account_id = get_multi_account_manager().create_account(account)
    return {"success": True, "account_id": account_id}


@router.get("/accounts", summary="获取代理的所有账户")
async def get_accounts(request: Request):
    agent_id = request.state.agent_id if hasattr(request.state, "agent_id") else 1
    
    accounts = get_multi_account_manager().get_agent_accounts(agent_id)
    return {
        "success": True,
        "accounts": [
            {
                "id": a.id,
                "name": a.name,
                "account_type": a.account_type.value,
                "exchange": a.exchange.value,
                "balance": a.balance,
                "available_balance": a.available_balance,
                "pnl_total": a.pnl_total,
                "status": a.status
            }
            for a in accounts
        ]
    }


@router.get("/accounts/summary", summary="获取账户汇总")
async def get_account_summary(request: Request):
    agent_id = request.state.agent_id if hasattr(request.state, "agent_id") else 1
    
    summary = get_multi_account_manager().get_account_summary(agent_id)
    return {"success": True, "summary": summary}


@router.post("/accounts/allocate", summary="资金分配")
async def allocate_capital(request: Request, data: CapitalAllocationRequest):
    agent_id = request.state.agent_id if hasattr(request.state, "agent_id") else 1
    
    success = get_multi_account_manager().allocate_capital(agent_id, data.allocations)
    return {"success": success}


# ==================== 功能5: 社交交易排行榜 ====================

@router.get("/leaderboard", summary="获取排行榜")
async def get_leaderboard(
    metric: str = Query("total_return", description="排序指标: total_return, sharpe_ratio, win_rate, followers"),
    period: str = Query("all", description="时间周期: day, week, month, year, all"),
    limit: int = Query(50, ge=1, le=200)
):
    entries = get_social_leaderboard().get_leaderboard(metric, period, limit)
    
    return {
        "success": True,
        "leaderboard": [
            {
                "rank": e.rank,
                "agent_id": e.agent_id,
                "agent_name": e.agent_name,
                "total_return": e.total_return,
                "total_return_percent": e.total_return_percent,
                "sharpe_ratio": e.sharpe_ratio,
                "max_drawdown": e.max_drawdown,
                "win_rate": e.win_rate,
                "total_trades": e.total_trades,
                "followers": e.followers,
                "signals_published": e.signals_published,
                "risk_score": e.risk_score,
                "consistency_score": e.consistency_score
            }
            for e in entries
        ]
    }


@router.get("/leaderboard/rank/{agent_id}", summary="获取代理排名")
async def get_agent_rank(
    agent_id: int,
    metric: str = Query("total_return")
):
    rank = get_social_leaderboard().get_agent_rank(agent_id, metric)
    return {"success": True, "agent_id": agent_id, "rank": rank}


# ==================== 功能6: 智能订单路由 ====================

@router.post("/router/best-route", summary="寻找最优订单路由")
async def find_best_route(
    symbol: str,
    side: str,
    quantity: float,
    price: float,
    exchanges: List[str] = Query(...)
):
    available_exchanges = [ExchangeType(e) for e in exchanges]
    route = get_smart_order_router().find_best_route(
        symbol, side, quantity, price, available_exchanges
    )
    
    return {
        "success": True,
        "route": {
            "exchange": route.exchange.value,
            "symbol": route.symbol,
            "side": route.side,
            "quantity": route.quantity,
            "price": route.price,
            "estimated_fee": route.estimated_fee,
            "estimated_slippage": route.estimated_slippage,
            "total_cost": route.total_cost,
            "execution_time_ms": route.execution_time_ms,
            "confidence_score": route.confidence_score,
            "reason": route.reason
        }
    }


@router.get("/router/exchange-comparison", summary="交易所对比")
async def get_exchange_comparison(symbol: str, quantity: float, price: float):
    comparisons = get_smart_order_router().get_exchange_comparison(symbol, quantity, price)
    return {"success": True, "comparisons": comparisons}


# ==================== 功能7: 交易日记和复盘系统 ====================

@router.post("/journal", summary="创建交易日记条目")
async def create_journal_entry(request: Request, data: CreateJournalEntryRequest):
    agent_id = request.state.agent_id if hasattr(request.state, "agent_id") else 1
    
    entry = TradingJournalEntry(
        agent_id=agent_id,
        position_id=data.position_id,
        symbol=data.symbol,
        market=data.market,
        side=data.side,
        entry_price=data.entry_price,
        exit_price=data.exit_price,
        quantity=data.quantity,
        pnl=data.pnl,
        pnl_percent=data.pnl_percent,
        entry_reason=data.entry_reason,
        exit_reason=data.exit_reason,
        emotions=data.emotions,
        tags=data.tags,
        lessons_learned=data.lessons_learned,
        mistakes=data.mistakes,
        rating=data.rating
    )
    
    entry_id = get_trading_journal().create_entry(entry)
    return {"success": True, "entry_id": entry_id}


@router.get("/journal", summary="获取交易日记")
async def get_journal(
    request: Request,
    limit: int = Query(100, ge=1, le=500)
):
    agent_id = request.state.agent_id if hasattr(request.state, "agent_id") else 1
    
    entries = get_trading_journal().get_agent_journal(agent_id, limit)
    return {
        "success": True,
        "entries": [
            {
                "id": e.id,
                "symbol": e.symbol,
                "market": e.market,
                "side": e.side,
                "entry_price": e.entry_price,
                "exit_price": e.exit_price,
                "quantity": e.quantity,
                "pnl": e.pnl,
                "pnl_percent": e.pnl_percent,
                "entry_reason": e.entry_reason,
                "emotions": e.emotions,
                "tags": e.tags,
                "rating": e.rating,
                "created_at": e.created_at
            }
            for e in entries
        ]
    }


@router.get("/journal/analysis", summary="分析交易日记")
async def analyze_journal(request: Request):
    agent_id = request.state.agent_id if hasattr(request.state, "agent_id") else 1
    
    analysis = get_trading_journal().analyze_journal(agent_id)
    return {"success": True, "analysis": analysis}


# ==================== 功能8: 宏观经济指标追踪 ====================

@router.get("/macro/indicators", summary="获取所有宏观指标")
async def get_all_indicators(category: Optional[str] = None):
    if category:
        indicators = get_macro_economic_tracker().get_indicators_by_category(category)
    else:
        indicators = get_macro_economic_tracker().get_all_indicators()
    
    return {
        "success": True,
        "indicators": [
            {
                "id": i.id,
                "symbol": i.symbol,
                "name": i.name,
                "category": i.category,
                "value": i.value,
                "previous_value": i.previous_value,
                "change": i.change,
                "change_percent": i.change_percent,
                "unit": i.unit,
                "source": i.source,
                "release_date": i.release_date,
                "next_release": i.next_release,
                "description": i.description
            }
            for i in indicators
        ]
    }


@router.get("/macro/indicators/{symbol}", summary="获取单个指标")
async def get_indicator(symbol: str):
    indicator = get_macro_economic_tracker().get_indicator(symbol)
    if not indicator:
        raise HTTPException(status_code=404, detail="Indicator not found")
    
    return {
        "success": True,
        "indicator": {
            "symbol": indicator.symbol,
            "name": indicator.name,
            "category": indicator.category,
            "value": indicator.value,
            "previous_value": indicator.previous_value,
            "change": indicator.change,
            "change_percent": indicator.change_percent,
            "unit": indicator.unit,
            "historical_data": indicator.historical_data
        }
    }


@router.get("/macro/calendar", summary="获取经济日历")
async def get_economic_calendar(days: int = Query(30, ge=1, le=90)):
    calendar = get_macro_economic_tracker().get_economic_calendar(days)
    return {"success": True, "calendar": calendar}


# ==================== 功能9: 交易信号质量评分 ====================

@router.get("/signals/quality/{signal_id}", summary="计算信号质量评分")
async def get_signal_quality(signal_id: int):
    score = get_signal_quality_scorer().calculate_signal_score(signal_id)
    
    return {
        "success": True,
        "quality": {
            "signal_id": score.signal_id,
            "agent_id": score.agent_id,
            "overall_score": score.overall_score,
            "win_rate": score.win_rate,
            "profit_factor": score.profit_factor,
            "avg_return": score.avg_return,
            "max_drawdown": score.max_drawdown,
            "consistency": score.consistency,
            "timeliness": score.timeliness,
            "risk_adjusted_return": score.risk_adjusted_return,
            "follower_adoption_rate": score.follower_adoption_rate,
            "total_signals": score.total_signals,
            "successful_signals": score.successful_signals
        }
    }


@router.get("/signals/quality/history/{agent_id}", summary="获取代理信号质量历史")
async def get_agent_quality_history(
    agent_id: int,
    limit: int = Query(30, ge=1, le=100)
):
    history = get_signal_quality_scorer().get_agent_quality_history(agent_id, limit)
    return {
        "success": True,
        "history": [
            {
                "signal_id": h.signal_id,
                "overall_score": h.overall_score,
                "win_rate": h.win_rate,
                "profit_factor": h.profit_factor
            }
            for h in history
        ]
    }


# ==================== 功能10: API交易网关 ====================

@router.post("/gateway/connect", summary="连接交易所")
async def connect_exchange(exchange: str, api_key: str, api_secret: str):
    gateway = get_trading_gateway()
    success = await gateway.connect(ExchangeType(exchange), api_key, api_secret)
    return {"success": success}


@router.post("/gateway/disconnect", summary="断开连接")
async def disconnect_exchange(exchange: str):
    gateway = get_trading_gateway()
    success = await gateway.disconnect(ExchangeType(exchange))
    return {"success": success}


@router.get("/gateway/balance", summary="获取账户余额")
async def get_balance(exchange: str):
    gateway = get_trading_gateway()
    balance = await gateway.get_balance(ExchangeType(exchange))
    return {"success": True, "balance": balance}


@router.get("/gateway/positions", summary="获取持仓")
async def get_positions(exchange: str):
    gateway = get_trading_gateway()
    positions = await gateway.get_positions(ExchangeType(exchange))
    return {"success": True, "positions": positions}


@router.post("/gateway/order", summary="下单")
async def place_order(data: PlaceOrderRequest):
    gateway = get_trading_gateway()
    
    if not data.exchange:
        raise HTTPException(status_code=400, detail="Exchange is required")
    
    order = await gateway.place_order(
        exchange=ExchangeType(data.exchange),
        symbol=data.symbol,
        side=data.side,
        quantity=data.quantity,
        order_type=data.order_type,
        price=data.price,
        stop_loss=data.stop_loss,
        take_profit=data.take_profit
    )
    return order


@router.post("/gateway/order/smart", summary="智能下单")
async def smart_place_order(data: SmartOrderRequest):
    gateway = get_trading_gateway()
    available_exchanges = [ExchangeType(e) for e in data.available_exchanges]
    
    order = await gateway.smart_place_order(
        symbol=data.symbol,
        side=data.side,
        quantity=data.quantity,
        available_exchanges=available_exchanges,
        order_type=data.order_type
    )
    return order


@router.delete("/gateway/order/{order_id}", summary="取消订单")
async def cancel_order(exchange: str, order_id: str):
    gateway = get_trading_gateway()
    result = await gateway.cancel_order(ExchangeType(exchange), order_id)
    return result


@router.get("/gateway/order/{order_id}", summary="获取订单状态")
async def get_order_status(exchange: str, order_id: str):
    gateway = get_trading_gateway()
    status = await gateway.get_order_status(ExchangeType(exchange), order_id)
    return {"success": True, "status": status}


@router.get("/gateway/market/{symbol}", summary="获取市场数据")
async def get_market_data(exchange: str, symbol: str):
    gateway = get_trading_gateway()
    data = await gateway.get_market_data(ExchangeType(exchange), symbol)
    return {"success": True, "market_data": data}


@router.get("/gateway/exchanges", summary="获取支持的交易所列表")
async def get_supported_exchanges():
    gateway = get_trading_gateway()
    exchanges = gateway.get_supported_exchanges()
    return {"success": True, "exchanges": exchanges}
