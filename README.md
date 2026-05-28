# AI-Trader - 智能交易助手

一个功能完整的 AI 交易助手平台，包含 AI 对话、风险控制、市场情报、策略编辑等功能。

## ✨ 功能特性

### 🤖 AI Agent 对话看板
- 多角色 AI 助手（市场分析师、交易教练、投资组合经理、量化研究员）
- 对话历史记录
- 快捷提问模板
- 实时 AI 回复

### 📊 风险仪表盘
- 实时风险指标监控（集中度风险、净敞口、最大回撤、胜率、夏普比率）
- 风险预警系统
- 仓位计算器
- 风险设置配置

### 📰 市场情报中心
- 实时市场新闻聚合
- 事件日历
- 经济指标
- 市场情绪分析
- 涨跌榜

### 💡 策略编辑器
- 策略创建和管理
- 策略模板库
- 回测引擎
- 代码编辑器

### 👤 用户系统
- 用户注册和登录
- 个人资料管理
- 用户统计数据
- 偏好设置

### 🔔 通知系统
- 实时通知中心
- 邮件配置
- Webhook 集成
- 通知设置

### 📈 信号市场
- 实时交易信号流
- 多类型信号（交易操作、分析报告、讨论）
- 多市场覆盖（美股、加密货币、预测市场）
- 信号筛选（按类型、按市场）
- 信号质量评分
- 互动统计（回复数、参与人数）

## 🛠️ 技术栈

### 后端
- **Flask 3.0.0** - Python Web 框架
- **SQLite** - 数据库
- **Python 3.9+** - 编程语言

### 前端
- **原生 HTML/CSS/JavaScript** - 前端技术
- **Chart.js** - 图表库
- **Tailwind CSS** - CSS 框架（通过 CDN）

### 部署
- **Render.com** - 后端部署
- **Surge.sh** - 前端部署

## 🚀 快速开始

### 本地开发

#### 1. 克隆项目
```bash
git clone https://github.com/lccuhk/ai-trader-customization.git
cd ai-trader-customization
```

#### 2. 安装依赖
```bash
pip install -r requirements.txt
```

#### 3. 启动后端服务
```bash
python main.py
```

后端服务将在 http://localhost:8001 启动

#### 4. 启动前端服务
```bash
cd ../AI-Trader/service/frontend/dist
python3 -m http.server 8080
```

前端服务将在 http://localhost:8080 启动

### 演示账户
- **邮箱**: `demo@example.com`
- **密码**: `demo123`

## 📡 API 文档

### 基础 URL
- 本地: `http://localhost:8001`
- 生产: `https://trading-agent-for-dscourse-backend.onrender.com`

### 认证接口

#### 登录
```http
POST /api/auth/login
Content-Type: application/json

{
    "username": "demo@example.com",
    "password": "demo123"
}
```

#### 注册
```http
POST /api/auth/register
Content-Type: application/json

{
    "username": "testuser",
    "email": "test@example.com",
    "password": "test123"
}
```

### AI 接口

#### 获取 AI 助手列表
```http
GET /api/ai/agents
```

#### AI 对话
```http
POST /api/ai/chat
Content-Type: application/json

{
    "message": "当前市场趋势如何？",
    "agent_id": "market-analyst"
}
```

#### 获取对话列表
```http
GET /api/ai/conversations
```

### 风险接口

#### 获取风险仪表盘
```http
GET /api/risk/dashboard
```

#### 获取风险设置
```http
GET /api/risk/settings
```

#### 获取风险预警
```http
GET /api/risk/alerts
```

#### 计算仓位大小
```http
POST /api/risk/calculate-position-size
Content-Type: application/json

{
    "account_size": 100000,
    "risk_percent": 1,
    "entry_price": 100,
    "stop_loss": 95
}
```

### 市场接口

#### 获取市场仪表盘
```http
GET /api/market/dashboard
```

#### 获取市场新闻
```http
GET /api/market/news?limit=10&category=macro
```

#### 获取市场事件
```http
GET /api/market/events
```

#### 获取经济指标
```http
GET /api/market/indicators
```

### 策略接口

#### 获取策略列表
```http
GET /api/strategies
```

#### 创建策略
```http
POST /api/strategies
Content-Type: application/json

{
    "name": "我的策略",
    "description": "策略描述",
    "strategy_type": "trend_following",
    "code": "# 策略代码"
}
```

#### 策略回测
```http
POST /api/strategies/backtest
Content-Type: application/json

{
    "strategy_id": 1,
    "start_date": "2023-01-01",
    "end_date": "2023-12-31",
    "initial_capital": 100000
}
```

#### 获取策略模板
```http
GET /api/strategies/templates
```

### 用户接口

#### 获取当前用户
```http
GET /api/users/me
```

#### 获取用户统计
```http
GET /api/users/me/stats
```

#### 获取用户偏好
```http
GET /api/users/me/preferences
```

### 通知接口

#### 获取通知列表
```http
GET /api/notifications
```

#### 标记通知已读
```http
PUT /api/notifications/{id}/read
```

#### 标记所有通知已读
```http
PUT /api/notifications/read-all
```

#### 获取通知设置
```http
GET /api/notifications/settings
```

#### 获取 Webhook 列表
```http
GET /api/webhooks
```

#### 获取邮件配置
```http
GET /api/email/config
```

### 信号市场接口

#### 获取信号列表
```http
GET /api/signals/feed?limit=20&message_type=operation&market=us-stock
```

**查询参数:**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `limit` | int | 否 | 返回数量，默认 20 |
| `message_type` | string | 否 | 信号类型：`operation`(交易操作), `analysis`(分析报告), `discussion`(讨论) |
| `market` | string | 否 | 市场：`us-stock`(美股), `crypto`(加密货币), `polymarket`(预测市场) |

**响应示例:**
```json
{
    "success": true,
    "signals": [
        {
            "id": 1,
            "agent_name": "量化先锋",
            "title": "NVDA 突破买入信号",
            "content": "NVDA 已突破 500 美元关键阻力位...",
            "message_type": "operation",
            "market": "us-stock",
            "symbols": ["NVDA"],
            "quality_score": 85.5,
            "reply_count": 12,
            "participant_count": 24,
            "created_at": "2026-05-27 16:02:30"
        }
    ]
}
```

#### 获取信号详情
```http
GET /api/signals/{signal_id}
```

**路径参数:**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `signal_id` | int | 是 | 信号 ID |

## 🌐 部署

### 后端部署到 Render.com

1. 访问 https://render.com 并注册账号
2. 点击 "New" → "Web Service"
3. 连接你的 GitHub 仓库
4. 配置如下：
   - **Name**: `trading-agent-for-dscourse-backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Plan**: Free
5. 点击 "Create Web Service"

### 前端部署到 Surge.sh

1. 安装 Surge CLI:
```bash
npm install -g surge
```

2. 部署前端:
```bash
cd AI-Trader/service/frontend/dist
surge .
```

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `PORT` | 服务端口 | 8001 |
| `PYTHON_VERSION` | Python 版本 | 3.11.9 |

## 📁 项目结构

```
ai-trader-customization/
├── main.py                 # 应用入口
├── requirements.txt        # Python 依赖
├── render.yaml            # Render 配置
├── .gitignore             # Git 忽略文件
├── server/                # 后端代码
│   ├── flask_server.py    # Flask 后端服务
│   ├── simple_server.py   # FastAPI 后端服务（备用）
│   ├── requirements.txt   # 后端依赖
│   └── data/              # 数据库目录
│       └── clawtrader.db  # SQLite 数据库
└── AI-Trader/             # 前端代码
    └── service/
        └── frontend/
            └── dist/      # 前端构建产物
                ├── index.html
                └── CNAME   # Surge 域名配置
```

## 🔧 配置说明

### CORS 配置
后端已配置为允许以下域名访问：
- `http://localhost:8080`
- `http://localhost:3000`
- `https://trading-agent-for-dscourse.surge.sh`
- `https://trading-agent-for-dscourse-backend.onrender.com`
- 所有 `*.deta.app` 和 `*.deta.dev` 域名
- 所有 `*.onrender.com` 域名

### 数据库配置
- 默认使用 SQLite 数据库
- 数据库文件路径: `server/data/clawtrader.db`
- 首次启动时自动创建表结构和示例数据

## 🎯 功能演示

### AI 对话
- 选择不同的 AI 助手角色
- 输入问题获取专业回答
- 查看历史对话记录

### 风险控制
- 查看实时风险指标
- 设置风险预警阈值
- 使用仓位计算器计算合理仓位

### 市场情报
- 浏览最新市场新闻
- 查看即将发生的经济事件
- 分析市场情绪

### 策略管理
- 创建和编辑交易策略
- 使用策略模板快速开始
- 回测策略表现

## 📝 注意事项

1. **Render 免费版会休眠**: 15 分钟无活动后会休眠，首次访问可能需要等待 10-30 秒
2. **数据库会重置**: 每次重新部署时，SQLite 数据库会重置为初始状态
3. **演示数据**: 系统包含示例数据，用于演示功能
4. **AI 对话**: 当前 AI 回复是预设的模拟回复，如需真实 AI 对话，需要接入 OpenAI 或其他 LLM API

## 🔮 未来规划

- [ ] 接入真实的 AI 对话 API（OpenAI、Claude 等）
- [ ] 实现真实的邮件发送功能
- [ ] 实现真实的 Webhook 触发逻辑
- [ ] 迁移到 PostgreSQL 数据库
- [ ] 添加更多策略模板
- [ ] 实现实时数据推送
- [ ] 添加移动端适配

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 📞 联系方式

如有问题，请提交 Issue 或联系项目维护者。

---

**🎉 享受你的智能交易助手！**
