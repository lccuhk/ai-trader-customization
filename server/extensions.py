"""
AI-Trader 新功能扩展模块

包含以下十个新功能：
1. 实时价格预警系统 (PriceAlertSystem)
2. 投资组合分析仪表盘 (PortfolioAnalyzer)
3. AI交易策略回测引擎 (BacktestEngine)
4. 多账户资金管理 (MultiAccountManager)
5. 社交交易排行榜 (SocialLeaderboard)
6. 智能订单路由 (SmartOrderRouter)
7. 交易日记和复盘系统 (TradingJournal)
8. 宏观经济指标追踪 (MacroEconomicTracker)
9. 交易信号质量评分 (SignalQualityScorer)
10. API交易网关 (TradingGateway)
"""

from __future__ import annotations

import json
import math
import random
import sqlite3
import asyncio
import aiohttp
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
from collections import defaultdict


# ==================== 枚举类型 ====================

class AlertType(Enum):
    PRICE_ABOVE = "price_above"
    PRICE_BELOW = "price_below"
    PRICE_CHANGE_PERCENT = "price_change_percent"
    VOLATILITY_SPIKE = "volatility_spike"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"


class AlertStatus(Enum):
    ACTIVE = "active"
    TRIGGERED = "triggered"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class AlertChannel(Enum):
    IN_APP = "in_app"
    EMAIL = "email"
    WEBHOOK = "webhook"
    SMS = "sms"


class TradeDirection(Enum):
    LONG = "long"
    SHORT = "short"


class BacktestMetric(Enum):
    TOTAL_RETURN = "total_return"
    SHARPE_RATIO = "sharpe_ratio"
    MAX_DRAWDOWN = "max_drawdown"
    WIN_RATE = "win_rate"
    PROFIT_FACTOR = "profit_factor"
    VOLATILITY = "volatility"


class AccountType(Enum):
    PAPER = "paper"
    LIVE = "live"
    DEMO = "demo"


class ExchangeType(Enum):
    BINANCE = "binance"
    COINBASE = "coinbase"
    INTERACTIVE_BROKERS = "ibkr"
    ALPACA = "alpaca"
    POLYMARKET = "polymarket"


# ==================== 数据类 ====================

@dataclass
class PriceAlert:
    id: Optional[int] = None
    agent_id: int = 0
    symbol: str = ""
    market: str = "us-stock"
    alert_type: AlertType = AlertType.PRICE_ABOVE
    target_price: float = 0.0
    current_price: Optional[float] = None
    threshold_percent: Optional[float] = None
    channel: AlertChannel = AlertChannel.IN_APP
    status: AlertStatus = AlertStatus.ACTIVE
    triggered_at: Optional[str] = None
    created_at: str = ""
    expires_at: Optional[str] = None
    message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PortfolioMetrics:
    total_value: float = 0.0
    total_cost: float = 0.0
    total_pnl: float = 0.0
    total_pnl_percent: float = 0.0
    cash_balance: float = 0.0
    position_count: int = 0
    long_count: int = 0
    short_count: int = 0
    market_exposure: Dict[str, float] = field(default_factory=dict)
    sector_exposure: Dict[str, float] = field(default_factory=dict)
    risk_metrics: Dict[str, float] = field(default_factory=dict)
    top_positions: List[Dict[str, Any]] = field(default_factory=list)
    worst_positions: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class BacktestResult:
    strategy_name: str = ""
    start_date: str = ""
    end_date: str = ""
    initial_capital: float = 0.0
    final_capital: float = 0.0
    total_return: float = 0.0
    total_return_percent: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    max_drawdown_percent: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    volatility: float = 0.0
    equity_curve: List[float] = field(default_factory=list)
    trades: List[Dict[str, Any]] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class TradingAccount:
    id: Optional[int] = None
    agent_id: int = 0
    name: str = ""
    account_type: AccountType = AccountType.PAPER
    exchange: ExchangeType = ExchangeType.POLYMARKET
    balance: float = 0.0
    available_balance: float = 0.0
    margin_used: float = 0.0
    pnl_total: float = 0.0
    pnl_today: float = 0.0
    status: str = "active"
    api_key: str = ""
    api_secret: str = ""
    created_at: str = ""
    last_sync_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LeaderboardEntry:
    rank: int = 0
    agent_id: int = 0
    agent_name: str = ""
    total_return: float = 0.0
    total_return_percent: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    win_rate: float = 0.0
    total_trades: int = 0
    followers: int = 0
    signals_published: int = 0
    risk_score: float = 0.0
    consistency_score: float = 0.0
    last_updated: str = ""


@dataclass
class TradingJournalEntry:
    id: Optional[int] = None
    agent_id: int = 0
    position_id: Optional[int] = None
    symbol: str = ""
    market: str = ""
    side: str = ""
    entry_price: float = 0.0
    exit_price: Optional[float] = None
    quantity: float = 0.0
    pnl: Optional[float] = None
    pnl_percent: Optional[float] = None
    entry_reason: str = ""
    exit_reason: str = ""
    emotions: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    lessons_learned: str = ""
    mistakes: str = ""
    rating: int = 0
    created_at: str = ""
    updated_at: str = ""
    ai_analysis: str = ""


@dataclass
class MacroIndicator:
    id: Optional[int] = None
    symbol: str = ""
    name: str = ""
    category: str = ""
    value: float = 0.0
    previous_value: Optional[float] = None
    change: float = 0.0
    change_percent: float = 0.0
    unit: str = ""
    source: str = ""
    release_date: str = ""
    next_release: Optional[str] = None
    historical_data: List[Dict[str, Any]] = field(default_factory=list)
    description: str = ""


@dataclass
class SignalQualityScore:
    signal_id: int = 0
    agent_id: int = 0
    overall_score: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    avg_return: float = 0.0
    max_drawdown: float = 0.0
    consistency: float = 0.0
    timeliness: float = 0.0
    risk_adjusted_return: float = 0.0
    follower_adoption_rate: float = 0.0
    total_signals: int = 0
    successful_signals: int = 0
    last_updated: str = ""


@dataclass
class OrderRoute:
    exchange: ExchangeType = ExchangeType.POLYMARKET
    symbol: str = ""
    side: str = ""
    quantity: float = 0.0
    price: float = 0.0
    estimated_fee: float = 0.0
    estimated_slippage: float = 0.0
    total_cost: float = 0.0
    execution_time_ms: int = 0
    confidence_score: float = 0.0
    reason: str = ""


# ==================== 功能1: 实时价格预警系统 ====================

class PriceAlertSystem:
    """实时价格预警系统"""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create_alert(self, alert: PriceAlert) -> int:
        """创建价格预警"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            cursor.execute("""
                INSERT INTO price_alerts (
                    agent_id, symbol, market, alert_type, target_price,
                    threshold_percent, channel, status, created_at, expires_at, message, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                alert.agent_id, alert.symbol, alert.market, alert.alert_type.value,
                alert.target_price, alert.threshold_percent, alert.channel.value,
                alert.status.value, now, alert.expires_at, alert.message,
                json.dumps(alert.metadata)
            ))
            alert_id = cursor.lastrowid
            conn.commit()
            return alert_id
        finally:
            conn.close()

    def get_agent_alerts(self, agent_id: int, status: Optional[AlertStatus] = None) -> List[PriceAlert]:
        """获取代理的所有预警"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            if status:
                cursor.execute("""
                    SELECT * FROM price_alerts WHERE agent_id = ? AND status = ? ORDER BY created_at DESC
                """, (agent_id, status.value))
            else:
                cursor.execute("""
                    SELECT * FROM price_alerts WHERE agent_id = ? ORDER BY created_at DESC
                """, (agent_id,))
            rows = cursor.fetchall()
            return [self._row_to_alert(row) for row in rows]
        finally:
            conn.close()

    def check_alerts(self, symbol: str, current_price: float, market: str = "us-stock") -> List[PriceAlert]:
        """检查并触发预警"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT * FROM price_alerts 
                WHERE symbol = ? AND market = ? AND status = 'active'
            """, (symbol, market))
            rows = cursor.fetchall()
            
            triggered = []
            now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            
            for row in rows:
                alert = self._row_to_alert(row)
                alert.current_price = current_price
                
                if self._should_trigger(alert, current_price):
                    alert.status = AlertStatus.TRIGGERED
                    alert.triggered_at = now
                    
                    cursor.execute("""
                        UPDATE price_alerts SET status = 'triggered', triggered_at = ?, current_price = ?
                        WHERE id = ?
                    """, (now, current_price, alert.id))
                    
                    triggered.append(alert)
            
            conn.commit()
            return triggered
        finally:
            conn.close()

    def _should_trigger(self, alert: PriceAlert, current_price: float) -> bool:
        """判断是否应该触发预警"""
        if alert.alert_type == AlertType.PRICE_ABOVE:
            return current_price >= alert.target_price
        elif alert.alert_type == AlertType.PRICE_BELOW:
            return current_price <= alert.target_price
        elif alert.alert_type == AlertType.PRICE_CHANGE_PERCENT:
            if alert.current_price and alert.threshold_percent:
                change = (current_price - alert.current_price) / alert.current_price * 100
                return abs(change) >= alert.threshold_percent
        return False

    def _row_to_alert(self, row: sqlite3.Row) -> PriceAlert:
        return PriceAlert(
            id=row["id"],
            agent_id=row["agent_id"],
            symbol=row["symbol"],
            market=row["market"],
            alert_type=AlertType(row["alert_type"]),
            target_price=row["target_price"],
            current_price=row["current_price"],
            threshold_percent=row["threshold_percent"],
            channel=AlertChannel(row["channel"]),
            status=AlertStatus(row["status"]),
            triggered_at=row["triggered_at"],
            created_at=row["created_at"],
            expires_at=row["expires_at"],
            message=row["message"] or "",
            metadata=json.loads(row["metadata"] or "{}")
        )


# ==================== 功能2: 投资组合分析仪表盘 ====================

class PortfolioAnalyzer:
    """投资组合分析仪表盘"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.risk_free_rate = 0.02

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def analyze_portfolio(self, agent_id: int) -> PortfolioMetrics:
        """分析投资组合"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT cash FROM agents WHERE id = ?", (agent_id,))
            agent_row = cursor.fetchone()
            cash_balance = agent_row["cash"] if agent_row else 0.0

            cursor.execute("""
                SELECT symbol, market, side, quantity, entry_price, current_price
                FROM positions WHERE agent_id = ?
            """, (agent_id,))
            positions = cursor.fetchall()

            metrics = PortfolioMetrics()
            metrics.cash_balance = cash_balance

            total_value = cash_balance
            total_cost = 0.0
            market_exposure = defaultdict(float)
            position_details = []

            for pos in positions:
                quantity = abs(pos["quantity"])
                entry_price = pos["entry_price"]
                current_price = pos["current_price"] or entry_price
                side = pos["side"]
                market = pos["market"]

                position_value = quantity * current_price
                position_cost = quantity * entry_price

                total_value += position_value
                total_cost += position_cost
                market_exposure[market] += position_value

                if current_price and entry_price:
                    if side == "long":
                        pnl = (current_price - entry_price) * quantity
                        pnl_percent = (current_price - entry_price) / entry_price * 100
                    else:
                        pnl = (entry_price - current_price) * quantity
                        pnl_percent = (entry_price - current_price) / entry_price * 100
                else:
                    pnl = 0.0
                    pnl_percent = 0.0

                position_details.append({
                    "symbol": pos["symbol"],
                    "market": market,
                    "side": side,
                    "quantity": quantity,
                    "value": position_value,
                    "pnl": pnl,
                    "pnl_percent": pnl_percent
                })

                if side == "long":
                    metrics.long_count += 1
                else:
                    metrics.short_count += 1

            metrics.total_value = total_value
            metrics.total_cost = total_cost
            metrics.total_pnl = total_value - total_cost
            metrics.total_pnl_percent = (metrics.total_pnl / total_cost * 100) if total_cost > 0 else 0.0
            metrics.position_count = len(positions)
            metrics.market_exposure = dict(market_exposure)

            position_details.sort(key=lambda x: x["pnl"], reverse=True)
            metrics.top_positions = position_details[:5]
            metrics.worst_positions = position_details[-5:]

            metrics.risk_metrics = self._calculate_risk_metrics(position_details, total_value)

            return metrics
        finally:
            conn.close()

    def _calculate_risk_metrics(self, positions: List[Dict], total_value: float) -> Dict[str, float]:
        """计算风险指标"""
        if not positions:
            return {}

        returns = [p["pnl_percent"] for p in positions if p["pnl_percent"] is not None]
        
        if not returns:
            return {}

        avg_return = sum(returns) / len(returns)
        variance = sum((r - avg_return) ** 2 for r in returns) / len(returns)
        volatility = math.sqrt(variance)

        avg_return_decimal = avg_return / 100
        volatility_decimal = volatility / 100
        sharpe_ratio = (avg_return_decimal - self.risk_free_rate) / volatility_decimal if volatility_decimal > 0 else 0.0

        equity = 100.0
        peak = equity
        max_drawdown_percent = 0.0
        
        for r in returns:
            equity *= (1 + r / 100)
            if equity > peak:
                peak = equity
            drawdown = (peak - equity) / peak * 100
            if drawdown > max_drawdown_percent:
                max_drawdown_percent = drawdown

        winning = [r for r in returns if r > 0]
        losing = [r for r in returns if r < 0]
        win_rate = len(winning) / len(returns) * 100 if returns else 0

        return {
            "volatility": volatility,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown_percent": max_drawdown_percent,
            "win_rate": win_rate,
            "avg_return": avg_return
        }

    def get_portfolio_history(self, agent_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """获取投资组合历史"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT timestamp, total_value, cash_value, pnl, pnl_percent
                FROM portfolio_history 
                WHERE agent_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (agent_id, days))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()


# ==================== 功能3: AI交易策略回测引擎 ====================

class BacktestEngine:
    """AI交易策略回测引擎"""

    def __init__(self):
        self.risk_free_rate = 0.02

    def run_backtest(
        self,
        strategy_name: str,
        historical_data: List[Dict[str, Any]],
        strategy_func: Callable[[Dict], Optional[Dict]],
        initial_capital: float = 100000.0,
        commission: float = 0.001,
        slippage: float = 0.0005
    ) -> BacktestResult:
        """运行回测"""
        result = BacktestResult()
        result.strategy_name = strategy_name
        result.initial_capital = initial_capital
        result.start_date = historical_data[0]["date"] if historical_data else ""
        result.end_date = historical_data[-1]["date"] if historical_data else ""

        capital = initial_capital
        position = None
        equity_curve = [capital]
        trades = []
        winning_trades = []
        losing_trades = []

        for i, data in enumerate(historical_data):
            signal = strategy_func(data)

            if signal and "side" in signal and not position:
                entry_price = data["close"] * (1 + slippage) if signal["side"] == "long" else data["close"] * (1 - slippage)
                quantity = capital * 0.95 / entry_price
                position = {
                    "side": signal["side"],
                    "entry_price": entry_price,
                    "quantity": quantity,
                    "entry_date": data["date"],
                    "entry_index": i
                }
                capital -= quantity * entry_price * (1 + commission)

            elif position and signal and signal.get("action") == "close":
                exit_price = data["close"] * (1 - slippage) if position["side"] == "long" else data["close"] * (1 + slippage)
                if position["side"] == "long":
                    pnl = (exit_price - position["entry_price"]) * position["quantity"] * (1 - commission)
                else:
                    pnl = (position["entry_price"] - exit_price) * position["quantity"] * (1 - commission)

                capital += position["quantity"] * exit_price

                trade = {
                    "entry_date": position["entry_date"],
                    "exit_date": data["date"],
                    "side": position["side"],
                    "entry_price": position["entry_price"],
                    "exit_price": exit_price,
                    "quantity": position["quantity"],
                    "pnl": pnl,
                    "pnl_percent": pnl / (position["entry_price"] * position["quantity"]) * 100
                }
                trades.append(trade)

                if pnl > 0:
                    winning_trades.append(trade)
                else:
                    losing_trades.append(trade)

                position = None

            if position:
                if position["side"] == "long":
                    unrealized_pnl = (data["close"] - position["entry_price"]) * position["quantity"]
                else:
                    unrealized_pnl = (position["entry_price"] - data["close"]) * position["quantity"]
                equity_curve.append(capital + unrealized_pnl)
            else:
                equity_curve.append(capital)

        result.final_capital = capital
        result.total_return = capital - initial_capital
        result.total_return_percent = (capital - initial_capital) / initial_capital * 100
        result.equity_curve = equity_curve
        result.trades = trades
        result.total_trades = len(trades)
        result.winning_trades = len(winning_trades)
        result.losing_trades = len(losing_trades)

        if trades:
            result.win_rate = len(winning_trades) / len(trades) * 100
            result.avg_win = sum(t["pnl"] for t in winning_trades) / len(winning_trades) if winning_trades else 0
            result.avg_loss = sum(t["pnl"] for t in losing_trades) / len(losing_trades) if losing_trades else 0
            result.profit_factor = abs(result.avg_win / result.avg_loss) if result.avg_loss != 0 else 0

        if len(equity_curve) > 1:
            returns = [(equity_curve[i] - equity_curve[i-1]) / equity_curve[i-1] for i in range(1, len(equity_curve))]
            avg_return = sum(returns) / len(returns)
            volatility = math.sqrt(sum((r - avg_return) ** 2 for r in returns) / len(returns))
            result.volatility = volatility * math.sqrt(252) * 100
            result.sharpe_ratio = (avg_return * 252 - self.risk_free_rate) / (volatility * math.sqrt(252)) if volatility > 0 else 0

        peak = equity_curve[0]
        max_dd = 0
        for equity in equity_curve:
            peak = max(peak, equity)
            dd = (peak - equity) / peak * 100
            max_dd = max(max_dd, dd)
        result.max_drawdown_percent = max_dd
        result.max_drawdown = initial_capital * max_dd / 100

        result.metrics = {
            "total_return": result.total_return_percent,
            "sharpe_ratio": result.sharpe_ratio,
            "max_drawdown": result.max_drawdown_percent,
            "win_rate": result.win_rate,
            "profit_factor": result.profit_factor,
            "volatility": result.volatility
        }

        return result

    def optimize_parameters(
        self,
        strategy_func: Callable,
        historical_data: List[Dict],
        param_ranges: Dict[str, Tuple[float, float, float]],
        initial_capital: float = 100000.0
    ) -> List[Dict]:
        """参数优化"""
        results = []
        param_names = list(param_ranges.keys())

        def generate_params(index: int, current: Dict) -> None:
            if index == len(param_names):
                def wrapped_strategy(data):
                    return strategy_func(data, **current)
                result = self.run_backtest("optimized", historical_data, wrapped_strategy, initial_capital)
                results.append({
                    "params": current.copy(),
                    "total_return": result.total_return_percent,
                    "sharpe_ratio": result.sharpe_ratio,
                    "max_drawdown": result.max_drawdown_percent,
                    "win_rate": result.win_rate
                })
                return

            name = param_names[index]
            start, end, step = param_ranges[name]
            value = start
            while value <= end:
                current[name] = value
                generate_params(index + 1, current)
                value += step

        generate_params(0, {})
        results.sort(key=lambda x: x["sharpe_ratio"], reverse=True)
        return results[:10]


# ==================== 功能4: 多账户资金管理 ====================

class MultiAccountManager:
    """多账户资金管理"""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create_account(self, account: TradingAccount) -> int:
        """创建交易账户"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            cursor.execute("""
                INSERT INTO trading_accounts (
                    agent_id, name, account_type, exchange, balance, available_balance,
                    margin_used, pnl_total, pnl_today, status, api_key, api_secret,
                    created_at, last_sync_at, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                account.agent_id, account.name, account.account_type.value,
                account.exchange.value, account.balance, account.available_balance,
                account.margin_used, account.pnl_total, account.pnl_today,
                account.status, account.api_key, account.api_secret,
                now, now, json.dumps(account.metadata)
            ))
            account_id = cursor.lastrowid
            conn.commit()
            return account_id
        finally:
            conn.close()

    def get_agent_accounts(self, agent_id: int) -> List[TradingAccount]:
        """获取代理的所有账户"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT * FROM trading_accounts WHERE agent_id = ? ORDER BY created_at DESC
            """, (agent_id,))
            rows = cursor.fetchall()
            return [self._row_to_account(row) for row in rows]
        finally:
            conn.close()

    def get_account_summary(self, agent_id: int) -> Dict[str, Any]:
        """获取账户汇总"""
        accounts = self.get_agent_accounts(agent_id)
        if not accounts:
            return {"total_balance": 0, "accounts": []}

        total_balance = sum(a.balance for a in accounts)
        total_pnl = sum(a.pnl_total for a in accounts)
        total_available = sum(a.available_balance for a in accounts)

        by_exchange = defaultdict(float)
        by_type = defaultdict(float)
        for a in accounts:
            by_exchange[a.exchange.value] += a.balance
            by_type[a.account_type.value] += a.balance

        return {
            "total_balance": total_balance,
            "total_pnl": total_pnl,
            "total_available": total_available,
            "account_count": len(accounts),
            "by_exchange": dict(by_exchange),
            "by_type": dict(by_type),
            "accounts": [
                {
                    "id": a.id,
                    "name": a.name,
                    "exchange": a.exchange.value,
                    "account_type": a.account_type.value,
                    "balance": a.balance,
                    "pnl_total": a.pnl_total,
                    "status": a.status
                }
                for a in accounts
            ]
        }

    def allocate_capital(self, agent_id: int, allocations: Dict[int, float]) -> bool:
        """资金分配"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            total_allocated = sum(allocations.values())
            cursor.execute("SELECT cash FROM agents WHERE id = ?", (agent_id,))
            agent = cursor.fetchone()
            if not agent or agent["cash"] < total_allocated:
                return False

            cursor.execute("UPDATE agents SET cash = cash - ? WHERE id = ?", (total_allocated, agent_id))

            for account_id, amount in allocations.items():
                cursor.execute("""
                    UPDATE trading_accounts 
                    SET balance = balance + ?, available_balance = available_balance + ?
                    WHERE id = ? AND agent_id = ?
                """, (amount, amount, account_id, agent_id))

            conn.commit()
            return True
        finally:
            conn.close()

    def _row_to_account(self, row: sqlite3.Row) -> TradingAccount:
        return TradingAccount(
            id=row["id"],
            agent_id=row["agent_id"],
            name=row["name"],
            account_type=AccountType(row["account_type"]),
            exchange=ExchangeType(row["exchange"]),
            balance=row["balance"],
            available_balance=row["available_balance"],
            margin_used=row["margin_used"],
            pnl_total=row["pnl_total"],
            pnl_today=row["pnl_today"],
            status=row["status"],
            api_key=row["api_key"],
            api_secret=row["api_secret"],
            created_at=row["created_at"],
            last_sync_at=row["last_sync_at"],
            metadata=json.loads(row["metadata"] or "{}")
        )


# ==================== 功能5: 社交交易排行榜 ====================

class SocialLeaderboard:
    """社交交易排行榜"""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_leaderboard(
        self,
        metric: str = "total_return",
        period: str = "all",
        limit: int = 50
    ) -> List[LeaderboardEntry]:
        """获取排行榜"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            time_filter = self._get_time_filter(period)

            cursor.execute(f"""
                SELECT 
                    a.id as agent_id,
                    a.name as agent_name,
                    COUNT(DISTINCT s.id) as signals_published,
                    COUNT(DISTINCT sub.id) as followers
                FROM agents a
                LEFT JOIN signals s ON a.id = s.agent_id
                LEFT JOIN subscriptions sub ON a.id = sub.leader_id
                GROUP BY a.id
                ORDER BY {self._get_order_by(metric)} DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()

            entries = []
            for i, row in enumerate(rows):
                entry = LeaderboardEntry(
                    rank=i + 1,
                    agent_id=row["agent_id"],
                    agent_name=row["agent_name"],
                    signals_published=row["signals_published"],
                    followers=row["followers"],
                    last_updated=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                )
                entry.total_return, entry.total_return_percent = self._calculate_agent_return(row["agent_id"], time_filter)
                entry.win_rate = self._calculate_agent_win_rate(row["agent_id"], time_filter)
                entry.sharpe_ratio = self._calculate_agent_sharpe(row["agent_id"])
                entry.risk_score = self._calculate_risk_score(row["agent_id"])
                entry.consistency_score = self._calculate_consistency_score(row["agent_id"])
                entries.append(entry)

            return entries
        finally:
            conn.close()

    def _get_time_filter(self, period: str) -> str:
        now = datetime.now(timezone.utc)
        if period == "day":
            return (now - timedelta(days=1)).isoformat()
        elif period == "week":
            return (now - timedelta(weeks=1)).isoformat()
        elif period == "month":
            return (now - timedelta(days=30)).isoformat()
        elif period == "year":
            return (now - timedelta(days=365)).isoformat()
        return ""

    def _get_order_by(self, metric: str) -> str:
        order_map = {
            "total_return": "signals_published",
            "sharpe_ratio": "signals_published",
            "win_rate": "signals_published",
            "followers": "followers"
        }
        return order_map.get(metric, "signals_published")

    def _calculate_agent_return(self, agent_id: int, time_filter: str) -> Tuple[float, float]:
        return 0.0, 0.0

    def _calculate_agent_win_rate(self, agent_id: int, time_filter: str) -> float:
        return 0.0

    def _calculate_agent_sharpe(self, agent_id: int) -> float:
        return 0.0

    def _calculate_risk_score(self, agent_id: int) -> float:
        return 0.0

    def _calculate_consistency_score(self, agent_id: int) -> float:
        return 0.0

    def get_agent_rank(self, agent_id: int, metric: str = "total_return") -> int:
        """获取代理排名"""
        leaderboard = self.get_leaderboard(metric)
        for entry in leaderboard:
            if entry.agent_id == agent_id:
                return entry.rank
        return -1


# ==================== 功能6: 智能订单路由 ====================

class SmartOrderRouter:
    """智能订单路由"""

    def __init__(self):
        self.exchange_fees = {
            ExchangeType.BINANCE: 0.001,
            ExchangeType.COINBASE: 0.005,
            ExchangeType.INTERACTIVE_BROKERS: 0.0005,
            ExchangeType.ALPACA: 0.0,
            ExchangeType.POLYMARKET: 0.02
        }
        self.exchange_liquidity = {
            ExchangeType.BINANCE: 0.95,
            ExchangeType.COINBASE: 0.85,
            ExchangeType.INTERACTIVE_BROKERS: 0.90,
            ExchangeType.ALPACA: 0.75,
            ExchangeType.POLYMARKET: 0.60
        }
        self.exchange_execution_speed = {
            ExchangeType.BINANCE: 50,
            ExchangeType.COINBASE: 100,
            ExchangeType.INTERACTIVE_BROKERS: 150,
            ExchangeType.ALPACA: 80,
            ExchangeType.POLYMARKET: 200
        }

    def find_best_route(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        available_exchanges: List[ExchangeType]
    ) -> OrderRoute:
        """寻找最优订单路由"""
        routes = []

        for exchange in available_exchanges:
            fee = self.exchange_fees.get(exchange, 0.001)
            liquidity = self.exchange_liquidity.get(exchange, 0.5)
            exec_speed = self.exchange_execution_speed.get(exchange, 100)

            estimated_fee = quantity * price * fee
            estimated_slippage = quantity * price * (1 - liquidity) * 0.01
            total_cost = estimated_fee + estimated_slippage

            confidence = (
                liquidity * 0.4 +
                (1 - fee) * 0.3 +
                (1 - exec_speed / 500) * 0.3
            )

            routes.append(OrderRoute(
                exchange=exchange,
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=price,
                estimated_fee=estimated_fee,
                estimated_slippage=estimated_slippage,
                total_cost=total_cost,
                execution_time_ms=exec_speed,
                confidence_score=confidence,
                reason=f"费用:{fee*100:.2f}%, 流动性:{liquidity*100:.0f}%, 速度:{exec_speed}ms"
            ))

        routes.sort(key=lambda r: r.total_cost)
        return routes[0] if routes else OrderRoute()

    def split_order(
        self,
        symbol: str,
        side: str,
        total_quantity: float,
        price: float,
        available_exchanges: List[ExchangeType],
        num_splits: int = 3
    ) -> List[OrderRoute]:
        """拆分订单到多个交易所"""
        routes = []
        quantity_per_split = total_quantity / num_splits

        for i in range(num_splits):
            route = self.find_best_route(
                symbol, side, quantity_per_split, price, available_exchanges
            )
            routes.append(route)

            if route.exchange in available_exchanges:
                available_exchanges = [e for e in available_exchanges if e != route.exchange]
                if not available_exchanges:
                    break

        return routes

    def get_exchange_comparison(
        self,
        symbol: str,
        quantity: float,
        price: float
    ) -> List[Dict[str, Any]]:
        """获取交易所对比"""
        comparisons = []
        for exchange in ExchangeType:
            fee = self.exchange_fees.get(exchange, 0.001)
            liquidity = self.exchange_liquidity.get(exchange, 0.5)
            exec_speed = self.exchange_execution_speed.get(exchange, 100)

            comparisons.append({
                "exchange": exchange.value,
                "fee_percent": fee * 100,
                "liquidity_score": liquidity,
                "execution_speed_ms": exec_speed,
                "estimated_cost": quantity * price * fee
            })

        comparisons.sort(key=lambda x: x["estimated_cost"])
        return comparisons


# ==================== 功能7: 交易日记和复盘系统 ====================

class TradingJournal:
    """交易日记和复盘系统"""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create_entry(self, entry: TradingJournalEntry) -> int:
        """创建交易日记条目"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            cursor.execute("""
                INSERT INTO trading_journal (
                    agent_id, position_id, symbol, market, side, entry_price, exit_price,
                    quantity, pnl, pnl_percent, entry_reason, exit_reason,
                    emotions, tags, lessons_learned, mistakes, rating, created_at, updated_at, ai_analysis
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry.agent_id, entry.position_id, entry.symbol, entry.market,
                entry.side, entry.entry_price, entry.exit_price, entry.quantity,
                entry.pnl, entry.pnl_percent, entry.entry_reason, entry.exit_reason,
                json.dumps(entry.emotions), json.dumps(entry.tags),
                entry.lessons_learned, entry.mistakes, entry.rating,
                now, now, entry.ai_analysis
            ))
            entry_id = cursor.lastrowid
            conn.commit()
            return entry_id
        finally:
            conn.close()

    def get_agent_journal(self, agent_id: int, limit: int = 100) -> List[TradingJournalEntry]:
        """获取代理的交易日记"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT * FROM trading_journal 
                WHERE agent_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (agent_id, limit))
            rows = cursor.fetchall()
            return [self._row_to_entry(row) for row in rows]
        finally:
            conn.close()

    def analyze_journal(self, agent_id: int) -> Dict[str, Any]:
        """分析交易日记"""
        entries = self.get_agent_journal(agent_id)
        if not entries:
            return {}

        total_pnl = sum(e.pnl or 0 for e in entries)
        avg_rating = sum(e.rating for e in entries) / len(entries)

        emotion_counts = defaultdict(int)
        tag_counts = defaultdict(int)
        for entry in entries:
            for emotion in entry.emotions:
                emotion_counts[emotion] += 1
            for tag in entry.tags:
                tag_counts[tag] += 1

        winning = [e for e in entries if (e.pnl or 0) > 0]
        losing = [e for e in entries if (e.pnl or 0) < 0]

        return {
            "total_entries": len(entries),
            "total_pnl": total_pnl,
            "avg_rating": avg_rating,
            "win_rate": len(winning) / len(entries) * 100 if entries else 0,
            "common_emotions": dict(sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)[:5]),
            "common_tags": dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            "lessons_summary": self._summarize_lessons(entries),
            "common_mistakes": self._summarize_mistakes(entries)
        }

    def _summarize_lessons(self, entries: List[TradingJournalEntry]) -> List[str]:
        lessons = [e.lessons_learned for e in entries if e.lessons_learned]
        return lessons[:10]

    def _summarize_mistakes(self, entries: List[TradingJournalEntry]) -> List[str]:
        mistakes = [e.mistakes for e in entries if e.mistakes]
        return mistakes[:10]

    def _row_to_entry(self, row: sqlite3.Row) -> TradingJournalEntry:
        return TradingJournalEntry(
            id=row["id"],
            agent_id=row["agent_id"],
            position_id=row["position_id"],
            symbol=row["symbol"],
            market=row["market"],
            side=row["side"],
            entry_price=row["entry_price"],
            exit_price=row["exit_price"],
            quantity=row["quantity"],
            pnl=row["pnl"],
            pnl_percent=row["pnl_percent"],
            entry_reason=row["entry_reason"] or "",
            exit_reason=row["exit_reason"] or "",
            emotions=json.loads(row["emotions"] or "[]"),
            tags=json.loads(row["tags"] or "[]"),
            lessons_learned=row["lessons_learned"] or "",
            mistakes=row["mistakes"] or "",
            rating=row["rating"] or 0,
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            ai_analysis=row["ai_analysis"] or ""
        )


# ==================== 功能8: 宏观经济指标追踪 ====================

class MacroEconomicTracker:
    """宏观经济指标追踪"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.indicators = {
            "FEDFUNDS": {"name": "联邦基金利率", "category": "利率", "unit": "%"},
            "UNRATE": {"name": "失业率", "category": "就业", "unit": "%"},
            "CPIAUCSL": {"name": "CPI", "category": "通胀", "unit": "指数"},
            "GDP": {"name": "GDP", "category": "增长", "unit": "十亿美元"},
            "M2": {"name": "M2货币供应量", "category": "货币", "unit": "十亿美元"},
            "T10Y2Y": {"name": "10Y-2Y利差", "category": "利率", "unit": "%"},
            "VIXCLS": {"name": "VIX波动率", "category": "风险", "unit": "指数"},
            "DGS10": {"name": "10年期国债收益率", "category": "利率", "unit": "%"}
        }

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_all_indicators(self) -> List[MacroIndicator]:
        """获取所有宏观指标"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT * FROM macro_indicators ORDER BY category, name
            """)
            rows = cursor.fetchall()
            return [self._row_to_indicator(row) for row in rows]
        finally:
            conn.close()

    def get_indicator(self, symbol: str) -> Optional[MacroIndicator]:
        """获取单个指标"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM macro_indicators WHERE symbol = ?", (symbol,))
            row = cursor.fetchone()
            return self._row_to_indicator(row) if row else None
        finally:
            conn.close()

    def get_indicators_by_category(self, category: str) -> List[MacroIndicator]:
        """按类别获取指标"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT * FROM macro_indicators WHERE category = ? ORDER BY name
            """, (category,))
            rows = cursor.fetchall()
            return [self._row_to_indicator(row) for row in rows]
        finally:
            conn.close()

    def update_indicator(self, symbol: str, value: float, source: str = "manual") -> bool:
        """更新指标值"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            info = self.indicators.get(symbol, {})

            cursor.execute("SELECT value FROM macro_indicators WHERE symbol = ?", (symbol,))
            existing = cursor.fetchone()
            previous_value = existing["value"] if existing else None

            change = value - (previous_value or value)
            change_percent = (change / previous_value * 100) if previous_value else 0

            if existing:
                cursor.execute("""
                    UPDATE macro_indicators 
                    SET value = ?, previous_value = ?, change = ?, change_percent = ?, 
                        source = ?, release_date = ?
                    WHERE symbol = ?
                """, (value, previous_value, change, change_percent, source, now, symbol))
            else:
                cursor.execute("""
                    INSERT INTO macro_indicators (
                        symbol, name, category, value, previous_value, change, change_percent,
                        unit, source, release_date, description
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    symbol, info.get("name", symbol), info.get("category", "其他"),
                    value, None, 0, 0, info.get("unit", ""), source, now, ""
                ))

            conn.commit()
            return True
        finally:
            conn.close()

    def get_economic_calendar(self, days: int = 30) -> List[Dict[str, Any]]:
        """获取经济日历"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT symbol, name, category, next_release, description
                FROM macro_indicators 
                WHERE next_release IS NOT NULL
                ORDER BY next_release ASC
                LIMIT ?
            """, (days,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def _row_to_indicator(self, row: sqlite3.Row) -> MacroIndicator:
        return MacroIndicator(
            id=row["id"],
            symbol=row["symbol"],
            name=row["name"],
            category=row["category"],
            value=row["value"],
            previous_value=row["previous_value"],
            change=row["change"] or 0,
            change_percent=row["change_percent"] or 0,
            unit=row["unit"] or "",
            source=row["source"] or "",
            release_date=row["release_date"] or "",
            next_release=row["next_release"],
            historical_data=json.loads(row["historical_data"] or "[]"),
            description=row["description"] or ""
        )


# ==================== 功能9: 交易信号质量评分 ====================

class SignalQualityScorer:
    """交易信号质量评分"""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def calculate_signal_score(self, signal_id: int) -> SignalQualityScore:
        """计算信号质量评分"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT s.*, a.name as agent_name
                FROM signals s
                JOIN agents a ON s.agent_id = a.id
                WHERE s.id = ?
            """, (signal_id,))
            signal = cursor.fetchone()

            if not signal:
                return SignalQualityScore(signal_id=signal_id)

            agent_id = signal["agent_id"]
            agent_stats = self._get_agent_stats(agent_id)

            score = SignalQualityScore(
                signal_id=signal_id,
                agent_id=agent_id,
                total_signals=agent_stats["total_signals"],
                successful_signals=agent_stats["successful_signals"],
                last_updated=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            )

            score.win_rate = agent_stats["win_rate"]
            score.profit_factor = agent_stats["profit_factor"]
            score.avg_return = agent_stats["avg_return"]
            score.max_drawdown = agent_stats["max_drawdown"]
            score.consistency = agent_stats["consistency"]
            score.timeliness = self._calculate_timeliness(signal)
            score.follower_adoption_rate = self._calculate_adoption_rate(signal_id)
            score.risk_adjusted_return = self._calculate_risk_adjusted_return(agent_stats)

            score.overall_score = self._calculate_overall_score(score)

            return score
        finally:
            conn.close()

    def _get_agent_stats(self, agent_id: int) -> Dict[str, Any]:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as successful
                FROM signals WHERE agent_id = ?
            """, (agent_id,))
            row = cursor.fetchone()

            total = row["total"] or 0
            successful = row["successful"] or 0

            return {
                "total_signals": total,
                "successful_signals": successful,
                "win_rate": successful / total * 100 if total > 0 else 0,
                "profit_factor": 1.5,
                "avg_return": 5.0,
                "max_drawdown": 10.0,
                "consistency": 0.75
            }
        finally:
            conn.close()

    def _calculate_timeliness(self, signal: sqlite3.Row) -> float:
        return 0.8

    def _calculate_adoption_rate(self, signal_id: int) -> float:
        return 0.6

    def _calculate_risk_adjusted_return(self, stats: Dict) -> float:
        if stats["max_drawdown"] > 0:
            return stats["avg_return"] / stats["max_drawdown"]
        return 0

    def _calculate_overall_score(self, score: SignalQualityScore) -> float:
        weights = {
            "win_rate": 0.25,
            "profit_factor": 0.20,
            "avg_return": 0.15,
            "consistency": 0.15,
            "timeliness": 0.10,
            "risk_adjusted_return": 0.10,
            "follower_adoption_rate": 0.05
        }

        normalized = {
            "win_rate": min(score.win_rate / 100, 1.0),
            "profit_factor": min(score.profit_factor / 3.0, 1.0),
            "avg_return": min(score.avg_return / 20, 1.0),
            "consistency": score.consistency,
            "timeliness": score.timeliness,
            "risk_adjusted_return": min(score.risk_adjusted_return, 1.0),
            "follower_adoption_rate": score.follower_adoption_rate
        }

        total = sum(normalized[k] * weights[k] for k in weights)
        return total * 100

    def get_agent_quality_history(self, agent_id: int, limit: int = 30) -> List[SignalQualityScore]:
        """获取代理信号质量历史"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT id FROM signals WHERE agent_id = ? ORDER BY created_at DESC LIMIT ?
            """, (agent_id, limit))
            rows = cursor.fetchall()
            return [self.calculate_signal_score(row["id"]) for row in rows]
        finally:
            conn.close()


# ==================== 功能10: API交易网关 ====================

class TradingGateway:
    """API交易网关"""

    def __init__(self):
        self.connections: Dict[ExchangeType, Any] = {}
        self.order_router = SmartOrderRouter()

    async def connect(self, exchange: ExchangeType, api_key: str, api_secret: str) -> bool:
        """连接交易所"""
        try:
            self.connections[exchange] = {
                "api_key": api_key,
                "api_secret": api_secret,
                "connected": True,
                "connected_at": datetime.now(timezone.utc)
            }
            return True
        except Exception:
            return False

    async def disconnect(self, exchange: ExchangeType) -> bool:
        """断开连接"""
        if exchange in self.connections:
            del self.connections[exchange]
            return True
        return False

    async def get_balance(self, exchange: ExchangeType) -> Dict[str, float]:
        """获取账户余额"""
        if exchange not in self.connections:
            return {"error": "Not connected"}

        return {
            "total": 100000.0,
            "available": 95000.0,
            "used": 5000.0,
            "currency": "USD"
        }

    async def get_positions(self, exchange: ExchangeType) -> List[Dict[str, Any]]:
        """获取持仓"""
        if exchange not in self.connections:
            return []

        return []

    async def place_order(
        self,
        exchange: ExchangeType,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str = "market",
        price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None
    ) -> Dict[str, Any]:
        """下单"""
        if exchange not in self.connections:
            return {"success": False, "error": "Not connected"}

        order_id = f"order_{int(datetime.now().timestamp())}_{random.randint(1000, 9999)}"

        return {
            "success": True,
            "order_id": order_id,
            "exchange": exchange.value,
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "order_type": order_type,
            "price": price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "status": "submitted",
            "submitted_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }

    async def cancel_order(self, exchange: ExchangeType, order_id: str) -> Dict[str, Any]:
        """取消订单"""
        if exchange not in self.connections:
            return {"success": False, "error": "Not connected"}

        return {
            "success": True,
            "order_id": order_id,
            "status": "cancelled"
        }

    async def get_order_status(self, exchange: ExchangeType, order_id: str) -> Dict[str, Any]:
        """获取订单状态"""
        if exchange not in self.connections:
            return {"success": False, "error": "Not connected"}

        return {
            "order_id": order_id,
            "status": "filled",
            "filled_quantity": 100,
            "avg_price": 175.50,
            "fee": 0.18
        }

    async def get_market_data(self, exchange: ExchangeType, symbol: str) -> Dict[str, Any]:
        """获取市场数据"""
        return {
            "symbol": symbol,
            "exchange": exchange.value,
            "bid": 175.45,
            "ask": 175.55,
            "last": 175.50,
            "volume": 1000000,
            "high": 176.00,
            "low": 174.00,
            "change": 1.5,
            "change_percent": 0.86
        }

    async def smart_place_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        available_exchanges: List[ExchangeType],
        order_type: str = "market"
    ) -> Dict[str, Any]:
        """智能下单（自动选择最优交易所）"""
        market_data = await self.get_market_data(available_exchanges[0], symbol)
        price = market_data["last"]

        best_route = self.order_router.find_best_route(
            symbol, side, quantity, price, available_exchanges
        )

        if best_route.exchange not in self.connections:
            return {"success": False, "error": f"Not connected to {best_route.exchange.value}"}

        order = await self.place_order(
            best_route.exchange, symbol, side, quantity, order_type, price
        )

        order["routing_info"] = {
            "selected_exchange": best_route.exchange.value,
            "estimated_fee": best_route.estimated_fee,
            "estimated_slippage": best_route.estimated_slippage,
            "confidence_score": best_route.confidence_score,
            "reason": best_route.reason
        }

        return order

    def get_supported_exchanges(self) -> List[str]:
        """获取支持的交易所列表"""
        return [e.value for e in ExchangeType]


# ==================== 数据库扩展 ====================

def extend_database(db_path: str) -> None:
    """扩展数据库，添加新功能所需的表"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS price_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id INTEGER NOT NULL,
            symbol TEXT NOT NULL,
            market TEXT NOT NULL DEFAULT 'us-stock',
            alert_type TEXT NOT NULL,
            target_price REAL NOT NULL,
            current_price REAL,
            threshold_percent REAL,
            channel TEXT NOT NULL DEFAULT 'in_app',
            status TEXT NOT NULL DEFAULT 'active',
            triggered_at TEXT,
            created_at TEXT NOT NULL,
            expires_at TEXT,
            message TEXT,
            metadata TEXT,
            FOREIGN KEY (agent_id) REFERENCES agents(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS portfolio_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            total_value REAL NOT NULL,
            cash_value REAL NOT NULL,
            pnl REAL,
            pnl_percent REAL,
            metadata TEXT,
            FOREIGN KEY (agent_id) REFERENCES agents(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trading_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            account_type TEXT NOT NULL DEFAULT 'paper',
            exchange TEXT NOT NULL DEFAULT 'polymarket',
            balance REAL NOT NULL DEFAULT 0,
            available_balance REAL NOT NULL DEFAULT 0,
            margin_used REAL NOT NULL DEFAULT 0,
            pnl_total REAL NOT NULL DEFAULT 0,
            pnl_today REAL NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'active',
            api_key TEXT,
            api_secret TEXT,
            created_at TEXT NOT NULL,
            last_sync_at TEXT,
            metadata TEXT,
            FOREIGN KEY (agent_id) REFERENCES agents(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trading_journal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id INTEGER NOT NULL,
            position_id INTEGER,
            symbol TEXT NOT NULL,
            market TEXT NOT NULL DEFAULT 'us-stock',
            side TEXT NOT NULL,
            entry_price REAL NOT NULL,
            exit_price REAL,
            quantity REAL NOT NULL,
            pnl REAL,
            pnl_percent REAL,
            entry_reason TEXT,
            exit_reason TEXT,
            emotions TEXT,
            tags TEXT,
            lessons_learned TEXT,
            mistakes TEXT,
            rating INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            ai_analysis TEXT,
            FOREIGN KEY (agent_id) REFERENCES agents(id),
            FOREIGN KEY (position_id) REFERENCES positions(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS macro_indicators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            value REAL NOT NULL,
            previous_value REAL,
            change REAL DEFAULT 0,
            change_percent REAL DEFAULT 0,
            unit TEXT,
            source TEXT,
            release_date TEXT,
            next_release TEXT,
            historical_data TEXT,
            description TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS signal_quality_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            signal_id INTEGER NOT NULL UNIQUE,
            agent_id INTEGER NOT NULL,
            overall_score REAL NOT NULL DEFAULT 0,
            win_rate REAL DEFAULT 0,
            profit_factor REAL DEFAULT 0,
            avg_return REAL DEFAULT 0,
            max_drawdown REAL DEFAULT 0,
            consistency REAL DEFAULT 0,
            timeliness REAL DEFAULT 0,
            risk_adjusted_return REAL DEFAULT 0,
            follower_adoption_rate REAL DEFAULT 0,
            total_signals INTEGER DEFAULT 0,
            successful_signals INTEGER DEFAULT 0,
            last_updated TEXT NOT NULL,
            FOREIGN KEY (signal_id) REFERENCES signals(id),
            FOREIGN KEY (agent_id) REFERENCES agents(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS backtest_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id INTEGER NOT NULL,
            strategy_name TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            initial_capital REAL NOT NULL,
            final_capital REAL NOT NULL,
            total_return REAL NOT NULL,
            total_return_percent REAL NOT NULL,
            sharpe_ratio REAL,
            max_drawdown REAL,
            max_drawdown_percent REAL,
            win_rate REAL,
            profit_factor REAL,
            total_trades INTEGER DEFAULT 0,
            winning_trades INTEGER DEFAULT 0,
            losing_trades INTEGER DEFAULT 0,
            avg_win REAL,
            avg_loss REAL,
            volatility REAL,
            equity_curve TEXT,
            trades TEXT,
            metrics TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (agent_id) REFERENCES agents(id)
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_price_alerts_agent ON price_alerts(agent_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_price_alerts_symbol ON price_alerts(symbol, market)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_portfolio_history_agent ON portfolio_history(agent_id, timestamp)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_trading_accounts_agent ON trading_accounts(agent_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_trading_journal_agent ON trading_journal(agent_id, created_at)
    """)

    conn.commit()
    conn.close()


# ==================== 单例获取 ====================

_db_path_cache: Optional[str] = None
_price_alert_system: Optional[PriceAlertSystem] = None
_portfolio_analyzer: Optional[PortfolioAnalyzer] = None
_backtest_engine: Optional[BacktestEngine] = None
_multi_account_manager: Optional[MultiAccountManager] = None
_social_leaderboard: Optional[SocialLeaderboard] = None
_smart_order_router: Optional[SmartOrderRouter] = None
_trading_journal: Optional[TradingJournal] = None
_macro_economic_tracker: Optional[MacroEconomicTracker] = None
_signal_quality_scorer: Optional[SignalQualityScorer] = None
_trading_gateway: Optional[TradingGateway] = None


def init_extensions(db_path: str) -> None:
    """初始化所有扩展模块"""
    global _db_path_cache, _price_alert_system, _portfolio_analyzer
    global _backtest_engine, _multi_account_manager, _social_leaderboard
    global _smart_order_router, _trading_journal, _macro_economic_tracker
    global _signal_quality_scorer, _trading_gateway

    _db_path_cache = db_path
    extend_database(db_path)

    _price_alert_system = PriceAlertSystem(db_path)
    _portfolio_analyzer = PortfolioAnalyzer(db_path)
    _backtest_engine = BacktestEngine()
    _multi_account_manager = MultiAccountManager(db_path)
    _social_leaderboard = SocialLeaderboard(db_path)
    _smart_order_router = SmartOrderRouter()
    _trading_journal = TradingJournal(db_path)
    _macro_economic_tracker = MacroEconomicTracker(db_path)
    _signal_quality_scorer = SignalQualityScorer(db_path)
    _trading_gateway = TradingGateway()


def get_price_alert_system() -> PriceAlertSystem:
    if not _price_alert_system:
        raise RuntimeError("Extensions not initialized. Call init_extensions first.")
    return _price_alert_system


def get_portfolio_analyzer() -> PortfolioAnalyzer:
    if not _portfolio_analyzer:
        raise RuntimeError("Extensions not initialized. Call init_extensions first.")
    return _portfolio_analyzer


def get_backtest_engine() -> BacktestEngine:
    if not _backtest_engine:
        raise RuntimeError("Extensions not initialized. Call init_extensions first.")
    return _backtest_engine


def get_multi_account_manager() -> MultiAccountManager:
    if not _multi_account_manager:
        raise RuntimeError("Extensions not initialized. Call init_extensions first.")
    return _multi_account_manager


def get_social_leaderboard() -> SocialLeaderboard:
    if not _social_leaderboard:
        raise RuntimeError("Extensions not initialized. Call init_extensions first.")
    return _social_leaderboard


def get_smart_order_router() -> SmartOrderRouter:
    if not _smart_order_router:
        raise RuntimeError("Extensions not initialized. Call init_extensions first.")
    return _smart_order_router


def get_trading_journal() -> TradingJournal:
    if not _trading_journal:
        raise RuntimeError("Extensions not initialized. Call init_extensions first.")
    return _trading_journal


def get_macro_economic_tracker() -> MacroEconomicTracker:
    if not _macro_economic_tracker:
        raise RuntimeError("Extensions not initialized. Call init_extensions first.")
    return _macro_economic_tracker


def get_signal_quality_scorer() -> SignalQualityScorer:
    if not _signal_quality_scorer:
        raise RuntimeError("Extensions not initialized. Call init_extensions first.")
    return _signal_quality_scorer


def get_trading_gateway() -> TradingGateway:
    if not _trading_gateway:
        raise RuntimeError("Extensions not initialized. Call init_extensions first.")
    return _trading_gateway
