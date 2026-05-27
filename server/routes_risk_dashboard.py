from __future__ import annotations

import sqlite3
import time
from datetime import datetime, timedelta
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from database import _SQLITE_DB_PATH

router = APIRouter()


class RiskSettings(BaseModel):
    max_position_size: float = 5.0
    max_daily_loss: float = 5.0
    max_drawdown: float = 20.0
    risk_per_trade: float = 1.0
    stop_loss_percent: float = 5.0
    take_profit_percent: float = 10.0


def _init_risk_db():
    conn = sqlite3.connect(_SQLITE_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS risk_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id INTEGER DEFAULT 0,
            max_position_size REAL DEFAULT 5.0,
            max_daily_loss REAL DEFAULT 5.0,
            max_drawdown REAL DEFAULT 20.0,
            risk_per_trade REAL DEFAULT 1.0,
            stop_loss_percent REAL DEFAULT 5.0,
            take_profit_percent REAL DEFAULT 10.0,
            updated_at TEXT NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS risk_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alert_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            message TEXT NOT NULL,
            details TEXT,
            timestamp INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            resolved INTEGER DEFAULT 0
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_pnl (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL UNIQUE,
            start_balance REAL,
            end_balance REAL,
            pnl REAL,
            pnl_percent REAL,
            trades_count INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)
    
    cursor.execute("SELECT COUNT(*) as count FROM risk_settings")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO risk_settings (
                agent_id, max_position_size, max_daily_loss, max_drawdown,
                risk_per_trade, stop_loss_percent, take_profit_percent, updated_at
            ) VALUES (0, 5.0, 5.0, 20.0, 1.0, 5.0, 10.0, ?)
        """, (datetime.now().isoformat(),))
    
    conn.commit()
    conn.close()


def _calculate_risk_metrics():
    _init_risk_db()
    
    conn = sqlite3.connect(_SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM positions")
    positions = [dict(row) for row in cursor.fetchall()]
    
    total_value = 0
    total_cost = 0
    total_pnl = 0
    position_values = []
    
    for pos in positions:
        current_price = pos.get("current_price") or pos.get("entry_price") or 0
        qty = pos.get("quantity") or 0
        cost = pos.get("entry_price") or 0
        
        value = current_price * qty
        cost_basis = cost * qty
        pnl = (current_price - cost) * qty * (1 if pos.get("side") == "long" else -1)
        
        total_value += value
        total_cost += cost_basis
        total_pnl += pnl
        position_values.append({
            "symbol": pos.get("symbol"),
            "value": value,
            "pnl": pnl,
            "side": pos.get("side")
        })
    
    cursor.execute("SELECT * FROM risk_settings ORDER BY id DESC LIMIT 1")
    settings = dict(cursor.fetchone()) if cursor.fetchone() else {}
    
    cursor.execute("""
        SELECT * FROM daily_pnl 
        ORDER BY date DESC 
        LIMIT 30
    """)
    daily_pnl = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    if total_value == 0:
        total_value = 100000
    
    concentration_risk = 0
    if position_values:
        max_position = max(pv["value"] for pv in position_values)
        concentration_risk = (max_position / total_value * 100) if total_value > 0 else 0
    
    long_count = sum(1 for pv in position_values if pv["side"] == "long")
    short_count = sum(1 for pv in position_values if pv["side"] == "short")
    net_exposure = (long_count - short_count) / max(len(position_values), 1) * 100
    
    winning_positions = sum(1 for pv in position_values if pv["pnl"] > 0)
    losing_positions = sum(1 for pv in position_values if pv["pnl"] < 0)
    win_rate = (winning_positions / max(len(position_values), 1)) * 100
    
    max_drawdown = 0
    peak = total_value
    for dp in daily_pnl:
        if dp.get("end_balance", 0) > peak:
            peak = dp.get("end_balance", peak)
        if peak > 0:
            dd = (peak - dp.get("end_balance", peak)) / peak * 100
            max_drawdown = max(max_drawdown, dd)
    
    daily_pnl_values = [dp.get("pnl", 0) for dp in daily_pnl if dp.get("pnl") is not None]
    avg_daily_pnl = sum(daily_pnl_values) / len(daily_pnl_values) if daily_pnl_values else 0
    max_daily_loss = min(daily_pnl_values) if daily_pnl_values else 0
    
    return {
        "total_value": total_value,
        "total_pnl": total_pnl,
        "position_count": len(position_values),
        "concentration_risk": concentration_risk,
        "net_exposure": net_exposure,
        "win_rate": win_rate,
        "max_drawdown": max_drawdown,
        "avg_daily_pnl": avg_daily_pnl,
        "max_daily_loss": max_daily_loss,
        "settings": settings,
        "daily_pnl": daily_pnl,
        "positions": position_values
    }


@router.get("/api/risk/dashboard")
async def get_risk_dashboard():
    metrics = _calculate_risk_metrics()
    
    alerts = []
    settings = metrics.get("settings", {})
    
    if metrics.get("concentration_risk", 0) > settings.get("max_position_size", 5):
        alerts.append({
            "type": "concentration",
            "severity": "warning",
            "message": f"持仓集中度风险: {metrics['concentration_risk']:.1f}% 超过阈值 {settings.get('max_position_size', 5)}%",
            "timestamp": int(time.time())
        })
    
    if metrics.get("max_drawdown", 0) > settings.get("max_drawdown", 20):
        alerts.append({
            "type": "drawdown",
            "severity": "danger",
            "message": f"最大回撤: {metrics['max_drawdown']:.1f}% 超过阈值 {settings.get('max_drawdown', 20)}%",
            "timestamp": int(time.time())
        })
    
    if metrics.get("win_rate", 0) < 40:
        alerts.append({
            "type": "win_rate",
            "severity": "warning",
            "message": f"胜率偏低: {metrics['win_rate']:.1f}%，建议复盘交易策略",
            "timestamp": int(time.time())
        })
    
    return JSONResponse({
        "success": True,
        "metrics": metrics,
        "alerts": alerts,
        "risk_score": _calculate_risk_score(metrics, settings)
    })


def _calculate_risk_score(metrics, settings):
    score = 100
    
    if metrics.get("concentration_risk", 0) > settings.get("max_position_size", 5):
        score -= 15
    
    if metrics.get("max_drawdown", 0) > settings.get("max_drawdown", 20):
        score -= 25
    
    if metrics.get("win_rate", 0) < 40:
        score -= 10
    
    if metrics.get("net_exposure", 0) > 80 or metrics.get("net_exposure", 0) < -80:
        score -= 10
    
    if metrics.get("position_count", 0) < 3:
        score -= 10
    
    return max(0, min(100, score))


@router.get("/api/risk/settings")
async def get_risk_settings():
    _init_risk_db()
    
    conn = sqlite3.connect(_SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM risk_settings ORDER BY id DESC LIMIT 1")
    settings = dict(cursor.fetchone()) if cursor.fetchone() else {}
    
    conn.close()
    
    return JSONResponse({
        "success": True,
        "settings": settings
    })


@router.post("/api/risk/settings")
async def update_risk_settings(request: RiskSettings):
    _init_risk_db()
    
    conn = sqlite3.connect(_SQLITE_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO risk_settings (
            agent_id, max_position_size, max_daily_loss, max_drawdown,
            risk_per_trade, stop_loss_percent, take_profit_percent, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        0,
        request.max_position_size,
        request.max_daily_loss,
        request.max_drawdown,
        request.risk_per_trade,
        request.stop_loss_percent,
        request.take_profit_percent,
        datetime.now().isoformat()
    ))
    
    conn.commit()
    conn.close()
    
    return JSONResponse({
        "success": True,
        "message": "Risk settings updated"
    })


@router.get("/api/risk/alerts")
async def get_risk_alerts(limit: int = Query(20, ge=1, le=100)):
    _init_risk_db()
    
    conn = sqlite3.connect(_SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM risk_alerts 
        ORDER BY timestamp DESC 
        LIMIT ?
    """, (limit,))
    
    alerts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return JSONResponse({
        "success": True,
        "alerts": alerts
    })


@router.post("/api/risk/calculate-position-size")
async def calculate_position_size(request: Request):
    data = await request.json()
    
    account_balance = data.get("account_balance", 100000)
    risk_percent = data.get("risk_percent", 1.0)
    entry_price = data.get("entry_price", 100)
    stop_loss_price = data.get("stop_loss_price", 95)
    
    if entry_price <= 0 or stop_loss_price <= 0:
        return JSONResponse({
            "success": False,
            "error": "Invalid prices"
        })
    
    risk_amount = account_balance * (risk_percent / 100)
    price_risk = abs(entry_price - stop_loss_price)
    shares = int(risk_amount / price_risk) if price_risk > 0 else 0
    position_value = shares * entry_price
    position_percent = (position_value / account_balance * 100) if account_balance > 0 else 0
    
    return JSONResponse({
        "success": True,
        "calculation": {
            "account_balance": account_balance,
            "risk_percent": risk_percent,
            "risk_amount": risk_amount,
            "entry_price": entry_price,
            "stop_loss_price": stop_loss_price,
            "price_risk": price_risk,
            "recommended_shares": shares,
            "position_value": position_value,
            "position_percent": position_percent
        }
    })


def init_risk_dashboard_routes(app):
    app.include_router(router)