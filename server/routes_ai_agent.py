from __future__ import annotations

import json
import sqlite3
import time
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from database import _SQLITE_DB_PATH, get_db_connection

router = APIRouter()

AI_AGENT_PROMPTS = {
    "market_analyst": """你是一位专业的市场分析师，擅长技术分析和基本面分析。
请用简洁专业的语言回答用户的问题，包括：
- 技术指标分析（RSI、MACD、布林带等）
- 基本面分析（财报、估值、行业趋势）
- 市场情绪和资金流向
- 风险提示和建议""",
    
    "trading_coach": """你是一位经验丰富的交易教练，专注于交易心理和风险管理。
请帮助用户：
- 分析交易心理和情绪管理
- 制定交易计划和纪律
- 复盘历史交易
- 提供改进建议""",
    
    "portfolio_manager": """你是一位投资组合经理，擅长资产配置和风险分散。
请帮助用户：
- 分析当前投资组合
- 提供资产配置建议
- 评估风险收益比
- 推荐再平衡策略""",
    
    "quant_researcher": """你是一位量化研究员，擅长策略开发和回测分析。
请帮助用户：
- 解释量化策略原理
- 分析回测结果
- 优化策略参数
- 识别策略风险"""
}

MOCK_RESPONSES = {
    "default": [
        "基于当前市场环境，我建议保持谨慎乐观的态度。",
        "从技术面来看，RSI指标显示当前处于中性区域。",
        "建议关注成交量变化和资金流向。",
        "风险管理永远是第一位的，请确保设置合理的止损。",
        "这个位置可以考虑分批建仓，控制好仓位。"
    ],
    "market": [
        "当前市场处于震荡整理阶段，建议等待明确方向。",
        "从宏观角度看，美联储政策是关键变量。",
        "科技板块近期表现强势，但需警惕估值压力。",
        "建议关注财报季的业绩表现。",
        "市场情绪指标显示投资者情绪偏谨慎。"
    ],
    "stock": [
        "从技术面分析，该股处于上升趋势中。",
        "基本面稳健，营收和利润增长符合预期。",
        "建议关注支撑位和阻力位的突破情况。",
        "可以考虑设置追踪止损来保护利润。",
        "行业对比来看，该股估值相对合理。"
    ],
    "crypto": [
        "加密货币市场波动性较大，建议控制仓位。",
        "BTC 作为数字黄金，长期配置价值依然存在。",
        "关注链上数据和交易所资金流向。",
        "监管政策是重要的风险因素。",
        "DeFi 生态持续发展，值得关注。"
    ],
    "portfolio": [
        "当前组合集中度偏高，建议适当分散。",
        "可以考虑增加债券或黄金来对冲风险。",
        "定期再平衡是保持组合健康的好习惯。",
        "建议根据风险承受能力调整资产配置。",
        "全球配置可以降低单一市场风险。"
    ],
    "risk": [
        "单笔交易风险建议控制在总资金的 1-2%。",
        "最大回撤超过 20% 时应考虑降低仓位。",
        "止损不是认输，而是保护资金的必要手段。",
        "建议使用凯利公式或固定比例来确定仓位。",
        "黑天鹅事件无法预测，但可以通过分散来降低影响。"
    ]
}


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    agent_type: str = "market_analyst"
    conversation_id: Optional[str] = None
    context: Optional[dict[str, Any]] = None


class ConversationCreate(BaseModel):
    title: str = "新对话"
    agent_type: str = "market_analyst"


def _init_ai_agent_db():
    conn = sqlite3.connect(_SQLITE_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT UNIQUE NOT NULL,
            agent_type TEXT NOT NULL,
            title TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (conversation_id) REFERENCES ai_conversations(conversation_id)
        )
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_ai_messages_conversation 
        ON ai_messages(conversation_id)
    """)
    
    conn.commit()
    conn.close()


def _generate_mock_response(user_message: str, agent_type: str) -> str:
    message_lower = user_message.lower()
    
    if any(keyword in message_lower for keyword in ["股票", "stock", "aapl", "tsla", "nvda", "msft"]):
        responses = MOCK_RESPONSES["stock"]
    elif any(keyword in message_lower for keyword in ["加密", "比特币", "btc", "eth", "crypto", "bitcoin"]):
        responses = MOCK_RESPONSES["crypto"]
    elif any(keyword in message_lower for keyword in ["组合", "配置", "portfolio", "资产"]):
        responses = MOCK_RESPONSES["portfolio"]
    elif any(keyword in message_lower for keyword in ["风险", "止损", "risk", "stop"]):
        responses = MOCK_RESPONSES["risk"]
    elif any(keyword in message_lower for keyword in ["市场", "大盘", "market", "行情"]):
        responses = MOCK_RESPONSES["market"]
    else:
        responses = MOCK_RESPONSES["default"]
    
    import random
    base_response = random.choice(responses)
    
    additional_insights = [
        "",
        f"\n\n💡 作为{agent_type.replace('_', ' ')}，我还建议：",
        "\n\n📊 技术指标提示：",
        "\n\n⚠️ 风险提示："
    ]
    
    additional = random.choice(additional_insights)
    if additional:
        if "技术指标" in additional:
            additional += "\n- RSI: 55 (中性)\n- MACD: 金叉信号\n- 布林带: 价格在中轨上方"
        elif "风险提示" in additional:
            additional += "\n- 建议设置止损\n- 控制仓位在 5% 以内\n- 关注市场流动性"
        elif "建议" in additional:
            additional += "\n- 耐心等待确认信号\n- 分批建仓降低风险\n- 保持交易纪律"
    
    return base_response + additional


@router.post("/api/ai/chat")
async def chat_with_ai(request: ChatRequest):
    _init_ai_agent_db()
    
    conn = sqlite3.connect(_SQLITE_DB_PATH)
    cursor = conn.cursor()
    
    conversation_id = request.conversation_id
    if not conversation_id:
        conversation_id = f"conv_{int(time.time() * 1000)}"
        cursor.execute("""
            INSERT INTO ai_conversations (conversation_id, agent_type, title, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            conversation_id,
            request.agent_type,
            request.message[:50] + "..." if len(request.message) > 50 else request.message,
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
    
    cursor.execute("""
        INSERT INTO ai_messages (conversation_id, role, content, timestamp, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        conversation_id,
        "user",
        request.message,
        int(time.time()),
        datetime.now().isoformat()
    ))
    
    ai_response = _generate_mock_response(request.message, request.agent_type)
    
    cursor.execute("""
        INSERT INTO ai_messages (conversation_id, role, content, timestamp, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        conversation_id,
        "assistant",
        ai_response,
        int(time.time()),
        datetime.now().isoformat()
    ))
    
    cursor.execute("""
        UPDATE ai_conversations 
        SET updated_at = ? 
        WHERE conversation_id = ?
    """, (datetime.now().isoformat(), conversation_id))
    
    conn.commit()
    conn.close()
    
    return JSONResponse({
        "success": True,
        "conversation_id": conversation_id,
        "message": {
            "role": "assistant",
            "content": ai_response
        },
        "agent_type": request.agent_type
    })


@router.get("/api/ai/conversations")
async def get_conversations(limit: int = Query(20, ge=1, le=100)):
    _init_ai_agent_db()
    
    conn = sqlite3.connect(_SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM ai_conversations 
        ORDER BY updated_at DESC 
        LIMIT ?
    """, (limit,))
    
    conversations = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return JSONResponse({
        "success": True,
        "conversations": conversations
    })


@router.get("/api/ai/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    _init_ai_agent_db()
    
    conn = sqlite3.connect(_SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM ai_conversations 
        WHERE conversation_id = ?
    """, (conversation_id,))
    
    conversation = cursor.fetchone()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    cursor.execute("""
        SELECT * FROM ai_messages 
        WHERE conversation_id = ? 
        ORDER BY timestamp ASC
    """, (conversation_id,))
    
    messages = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return JSONResponse({
        "success": True,
        "conversation": dict(conversation),
        "messages": messages
    })


@router.post("/api/ai/conversations")
async def create_conversation(request: ConversationCreate):
    _init_ai_agent_db()
    
    conversation_id = f"conv_{int(time.time() * 1000)}"
    
    conn = sqlite3.connect(_SQLITE_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO ai_conversations (conversation_id, agent_type, title, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        conversation_id,
        request.agent_type,
        request.title,
        datetime.now().isoformat(),
        datetime.now().isoformat()
    ))
    
    conn.commit()
    conn.close()
    
    return JSONResponse({
        "success": True,
        "conversation_id": conversation_id,
        "title": request.title,
        "agent_type": request.agent_type
    })


@router.delete("/api/ai/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    _init_ai_agent_db()
    
    conn = sqlite3.connect(_SQLITE_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM ai_messages WHERE conversation_id = ?", (conversation_id,))
    cursor.execute("DELETE FROM ai_conversations WHERE conversation_id = ?", (conversation_id,))
    
    conn.commit()
    conn.close()
    
    return JSONResponse({
        "success": True,
        "message": "Conversation deleted"
    })


@router.get("/api/ai/agents")
async def get_available_agents():
    agents = [
        {
            "id": "market_analyst",
            "name": "市场分析师",
            "icon": "📊",
            "description": "专业的技术分析和基本面分析",
            "specialties": ["技术分析", "基本面分析", "市场情绪"]
        },
        {
            "id": "trading_coach",
            "name": "交易教练",
            "icon": "🎯",
            "description": "交易心理和风险管理指导",
            "specialties": ["交易心理", "风险控制", "交易纪律"]
        },
        {
            "id": "portfolio_manager",
            "name": "投资组合经理",
            "icon": "💼",
            "description": "资产配置和组合优化",
            "specialties": ["资产配置", "风险分散", "再平衡策略"]
        },
        {
            "id": "quant_researcher",
            "name": "量化研究员",
            "icon": "🔬",
            "description": "策略开发和回测分析",
            "specialties": ["量化策略", "回测分析", "参数优化"]
        }
    ]
    
    return JSONResponse({
        "success": True,
        "agents": agents
    })


@router.post("/api/ai/analyze-position")
async def analyze_position(request: Request):
    data = await request.json()
    
    symbol = data.get("symbol", "UNKNOWN")
    entry_price = data.get("entry_price", 0)
    current_price = data.get("current_price", 0)
    quantity = data.get("quantity", 0)
    side = data.get("side", "long")
    
    pnl = (current_price - entry_price) * quantity * (1 if side == "long" else -1)
    pnl_percent = ((current_price - entry_price) / entry_price * 100) * (1 if side == "long" else -1)
    
    analysis = f"""## {symbol} 持仓分析

### 基本信息
- **方向**: {'做多' if side == 'long' else '做空'}
- **数量**: {quantity} 股
- **成本价**: ${entry_price:.2f}
- **当前价**: ${current_price:.2f}

### 盈亏情况
- **浮动盈亏**: ${pnl:.2f}
- **盈亏比例**: {pnl_percent:.2f}%

### AI 分析建议
"""
    
    if pnl_percent > 10:
        analysis += """✅ **表现优秀**
- 建议考虑部分止盈
- 可以设置追踪止损保护利润
- 关注是否有超买信号
"""
    elif pnl_percent > 0:
        analysis += """📈 **小幅盈利**
- 继续持有观察
- 设置保本止损
- 关注成交量变化
"""
    elif pnl_percent > -5:
        analysis += """📉 **小幅亏损**
- 检查止损位是否合理
- 分析基本面是否变化
- 考虑是否需要加仓摊平
"""
    else:
        analysis += """⚠️ **亏损较大**
- 严格执行止损纪律
- 分析错误原因
- 避免情绪化交易
"""
    
    analysis += """
### 技术指标参考
- RSI: 需要实时数据
- MACD: 需要实时数据
- 支撑位: 需要实时数据
- 阻力位: 需要实时数据
"""
    
    return JSONResponse({
        "success": True,
        "symbol": symbol,
        "analysis": analysis,
        "pnl": pnl,
        "pnl_percent": pnl_percent
    })


def init_ai_agent_routes(app):
    app.include_router(router)