# AI Trader — 智能交易助手

一个功能完整的 AI 交易助手平台，支持**加密货币**和**美股**市场，集成了 AI 智能对话、深度学习价格预测、风险控制、市场情报、策略编辑、模拟交易引擎、社会化交易等功能。

> 基于 [HKUDS/AI-Trader](https://github.com/HKUDS/AI-Trader) 开源项目进行定制化开发和增强。

## 功能特性

### AI Agent 对话看板
- 多角色 AI 助手（市场分析师、交易教练、投资组合经理、量化研究员）
- 对话历史记录与快捷提问模板
- 自然语言下单（输入"买入 1 BTC"即可创建订单）
- 下单确认卡片（交易对/方向/数量/价格/模式）
- AI 交易信号生成与分析

### DL 价格预测（LSTM 深度学习）
- 基于 TensorFlow/Keras LSTM 模型的加密货币价格预测
- 多交易对支持（BTC、ETH、SOL、BNB、XRP、ADA、DOT、LINK、AVAX、MATIC）
- 可配置训练轮数（epochs），实时训练进度展示
- 训练指标展示（MAE、MSE、样本数）
- 最新预测样本对比表

### 模拟交易引擎
- 自动运行模拟交易，覆盖 14+ 主流交易对
- 支持美股和加密货币市场
- 多交易所接口（Binance、OKX、Alpaca）
- 实时的模拟持仓和订单管理

### 风险仪表盘
- 实时风险指标监控（集中度风险、净敞口、最大回撤、胜率、夏普比率）
- 风险预警系统与仓位计算器
- 风险设置与自定义告警规则

### 市场情报中心
- 加密货币市场总览（总市值、BTC 占比、24h 成交量）
- Top 10 加密货币实时行情
- 市场情绪分析
- 市场新闻聚合
- 多数据源支持：Binance API、Alpha Vantage

### 策略编辑器
- 可视化策略创建与管理
- 策略模板库与代码编辑器
- 策略回测与性能分析

### 信号市场
- 实时交易信号流（交易操作、分析报告、讨论）
- 信号质量评分与互动统计
- 信号收藏与历史追踪
- 社会化评论与互动

### 社会化交易
- 用户个人资料与交易统计展示
- 社区讨论与消息系统
- AI 交易行为分析报告

### 实验与挑战系统
- 交易实验管理与指标追踪
- 团队挑战与评分系统
- 排行榜机制

### 通知系统
- 实时通知中心
- WebSocket 推送
- 邮件通知配置

### 管理后台
- 用户管理与权限控制
- 数据统计与分析看板
- 系统安全监控

### 国际化
- 支持中文 / English 双语切换
- 深色/浅色主题切换

## 技术栈

### 后端
| 技术 | 用途 |
|------|------|
| **Flask 3.0** | Web 框架（主应用） |
| **FastAPI** | 异步 API 服务（简化版后端） |
| **Flask-SocketIO** | WebSocket 实时通信 |
| **SQLAlchemy 2.0** | ORM 数据库层 |
| **Alembic** | 数据库迁移管理 |
| **TensorFlow / Keras** | LSTM 深度学习价格预测 |
| **scikit-learn** | 机器学习辅助 |
| **Binance API** | 加密货币行情与 K 线数据 |
| **Alpha Vantage** | 美股价格数据 |
| **SQLite / PostgreSQL** | 数据库（开发/生产） |
| **Redis** | 价格缓存与性能优化 |
| **eventlet** | 异步协程支持 |

### 前端
| 技术 | 用途 |
|------|------|
| **Vue 3** (Composition API) | UI 框架 |
| **TypeScript** | 类型安全 |
| **Vite 5** | 构建工具 |
| **Pinia** | 状态管理 |
| **Vue Router 4** | 路由 |
| **vue-i18n** | 国际化（中文/English） |
| **Axios** | HTTP 请求 |
| **Socket.IO Client** | WebSocket 客户端 |
| **dayjs** | 日期处理 |

## 快速开始

### 本地开发

#### 1. 克隆项目
```bash
git clone https://github.com/lccuhk/ai-trader-customization.git
cd ai-trader-customization
```

#### 2. 安装后端依赖
```bash
# 基础依赖
pip install -r server/requirements.txt

# 完整依赖（含 DL 预测、ML 等功能）
pip install flask flask-cors flask-socketio sqlalchemy python-dotenv eventlet \
    tensorflow pandas numpy scikit-learn requests fastapi uvicorn \
    websocket-client redis alembic
```

#### 3. 安装前端依赖
```bash
cd frontend
npm install
cd ..
```

#### 4. 配置环境变量
复制 `.env.example` 为 `.env`，根据需要修改配置：
```bash
cp .env.example .env
```

主要配置项：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `PORT` | 服务端口 | 8001 |
| `FLASK_ENV` | 运行环境 | development |
| `FLASK_DEBUG` | 调试模式 | True |
| `SECRET_KEY` | JWT 密钥（生产必填） | - |
| `DATABASE_URL` | 数据库连接 | SQLite 本地文件 |
| `POSTGRESQL_URL` | PostgreSQL 连接（可选） | - |
| `ALLOWED_ORIGINS` | CORS 允许域名 | localhost:3000,localhost:8080,surge.sh |
| `REDIS_ENABLED` | 启用 Redis 缓存 | false |
| `REDIS_URL` | Redis 连接地址 | redis://localhost:6379 |
| `REDIS_PREFIX` | Redis 键前缀 | ai_trader |
| `RATE_LIMIT_PER_MINUTE` | API 速率限制 | 60 |
| `TOKEN_EXPIRE_DAYS` | Token 过期天数 | 30 |

#### 5. 启动后端服务

**方式一：Flask 主应用（推荐）**
```bash
cd server
python app.py
```

**方式二：FastAPI 简化版**
```bash
cd server
python simple_server.py
# 或
uvicorn simple_server:app --host 0.0.0.0 --port 8001 --reload
```

后端将在 `http://localhost:8001` 启动。如遇端口冲突可指定端口：
```bash
PORT=8002 python server/app.py
```

#### 6. 启动前端开发服务器
```bash
cd frontend
npm run dev
```

前端将在 `http://localhost:3000` 启动，Vite 自动代理 `/api` 请求到后端 `http://localhost:8001`。

### 演示账户
- **用户名**: `demo`
- **密码**: `demo123456`

## 部署

### 前端部署

#### Vercel（推荐）
前端已配置 Vercel 一键部署，配置见 `vercel.json`：
- **生产地址**: [https://ai-trader-customization.vercel.app](https://ai-trader-customization.vercel.app)

#### Surge.sh
```bash
cd frontend
npm run build
surge dist/ trading-agent-for-dscourse.surge.sh
```

#### 其他静态托管
```bash
cd frontend
npm run build
# 将 dist/ 目录部署到任意静态文件服务器
```

> **注意**：前端为纯静态页面，AI 预测、交易等全功能需要配合后端使用。本地开发时通过 `localhost:3000` 访问可获得完整体验。

### 后端部署

#### Deta Space
后端支持部署到 Deta Space 平台。详见 `server/DETA_DEPLOYMENT.md`。

#### Render.com
1. 在 Render.com 创建 Web Service
2. **Build Command**: `pip install -r server/requirements.txt`
3. **Start Command**: `cd server && python app.py`

#### 传统服务器
```bash
# 使用 gunicorn（生产环境推荐）
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8001 server.app:app

# 或使用 uvicorn（FastAPI 版）
uvicorn server.simple_server:app --host 0.0.0.0 --port 8001 --workers 4
```

## API 文档

### 基础 URL
- 本地: `http://localhost:8001`

### 认证接口

#### 登录
```http
POST /api/auth/login
Content-Type: application/json

{
    "username": "demo",
    "password": "demo123456"
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
```http
GET   /api/ai/agents               # 获取可用 AI 助手列表
POST  /api/ai/chat                 # AI 对话
POST  /api/ai/signals/generate     # 生成 AI 交易信号
POST  /api/ai/analysis             # 交易行为分析
POST  /api/ai/strategies           # AI 策略生成
```

### ML 预测接口
```http
GET  /api/ml/status/{symbol}        # 模型训练状态（如 /api/ml/status/BTCUSDT）
GET  /api/ml/predict/{symbol}       # 获取预测价格
POST /api/ml/train/{symbol}         # 训练模型（body: { epochs: 30 }）
```

### 加密货币接口
```http
GET /api/crypto/overview            # 市场总览（总市值、BTC 占比、24h 成交量）
GET /api/crypto/top?limit=10        # Top N 加密货币
GET /api/crypto/history/{symbol}    # 历史 K 线数据
```

### 市场接口
```http
GET  /api/market/dashboard          # 市场仪表盘数据
GET  /api/market/news?limit=10      # 市场新闻
GET  /api/market/indicators         # 技术指标
GET  /api/market/trending           # 热门标的
POST /api/refresh-prices            # 手动刷新价格
```

### 风险接口
```http
GET  /api/risk/dashboard            # 风险仪表盘
GET  /api/risk/alerts               # 风险预警
POST /api/risk/calculate-position-size  # 仓位计算器
```

### 交易接口
```http
GET    /api/trading/orders           # 获取订单列表
POST   /api/trading/orders           # 创建订单
DELETE /api/trading/orders/{id}      # 取消订单
GET    /api/trading/portfolio        # 投资组合
```

### 信号接口
```http
GET    /api/signals/feed?limit=20    # 信号流
GET    /api/signals/{signal_id}      # 信号详情
POST   /api/signals                  # 发布信号
```

### 社交接口
```http
GET    /api/social/profile/{user_id} # 用户资料
GET    /api/social/messages          # 消息列表
POST   /api/social/follow            # 关注用户
```

### 通知接口
```http
GET  /api/notifications              # 通知列表
PUT  /api/notifications/{id}/read    # 标记已读
POST /api/notifications/settings     # 通知设置
```

### 管理接口
```http
GET  /api/admin/users                # 用户管理
GET  /api/admin/stats                # 系统统计
GET  /api/admin/audit-log            # 审计日志
```

### 实验与挑战
```http
GET  /api/experiments                # 实验列表
GET  /api/challenges                 # 挑战列表
GET  /api/leaderboard                # 排行榜
```

### 健康检查
```http
GET /api/health                      # 健康检查
```

响应示例：
```json
{
    "status": "healthy",
    "timestamp": "2026-06-12T00:00:00",
    "environment": "development",
    "database": "sqlite",
    "websocket": "enabled"
}
```

## 项目结构

```
ai-trader-customization/
├── vercel.json                 # Vercel 部署配置
├── .env.example                # 环境变量模板
├── alembic.ini                 # 数据库迁移配置
├── alembic/                    # 数据库迁移脚本
│   └── versions/               # 迁移版本文件
├── server/                     # 后端
│   ├── app.py                  # Flask 应用工厂（主应用）
│   ├── simple_server.py        # FastAPI 简化版后端
│   ├── config.py               # 配置管理（Settings 类）
│   ├── database.py             # 数据库初始化 + Schema 修复
│   ├── models.py               # SQLAlchemy ORM 模型
│   ├── websocket.py            # WebSocket 事件处理
│   ├── routes.py               # 旧版路由聚合
│   ├── services.py             # 旧版服务聚合
│   ├── middleware/             # 中间件
│   │   ├── auth.py             # 鉴权中间件
│   │   ├── audit.py            # 审计日志
│   │   └── error_handler.py   # 错误处理
│   ├── routes/                 # Flask Blueprint 路由
│   │   ├── auth.py             # 认证
│   │   ├── ai.py               # AI 对话
│   │   ├── ml.py               # DL 价格预测
│   │   ├── crypto.py           # 加密货币行情
│   │   ├── market.py           # 市场数据
│   │   ├── trading.py          # 交易
│   │   ├── signals.py          # 信号市场
│   │   ├── risk.py             # 风险管理
│   │   ├── admin.py            # 管理后台
│   │   ├── analytics.py        # 数据分析
│   │   ├── security.py         # 安全
│   │   ├── social.py           # 社交
│   │   ├── users.py            # 用户
│   │   ├── notifications.py    # 通知
│   │   └── health.py           # 健康检查
│   ├── routes_*.py             # FastAPI 功能路由模块
│   │   ├── routes_agent.py         # AI Agent
│   │   ├── routes_ai_agent.py      # AI Agent 扩展
│   │   ├── routes_challenges.py    # 挑战系统
│   │   ├── routes_experiments.py   # 实验系统
│   │   ├── routes_extensions.py    # 扩展功能
│   │   ├── routes_market_intelligence.py  # 市场情报
│   │   ├── routes_models.py        # 模型管理
│   │   ├── routes_notification_system.py  # 通知系统
│   │   ├── routes_research.py      # 研究报告
│   │   ├── routes_risk_dashboard.py  # 风险仪表盘
│   │   ├── routes_shared.py        # 共享路由工具
│   │   ├── routes_signals.py       # 信号扩展
│   │   ├── routes_strategy_editor.py # 策略编辑器
│   │   ├── routes_team_missions.py # 团队任务
│   │   ├── routes_trading.py       # 交易扩展
│   │   └── routes_user_system.py   # 用户系统
│   ├── services/               # 业务逻辑层
│   │   ├── ai_service.py       # AI 服务
│   │   ├── admin_service.py    # 管理服务
│   │   ├── analytics_service.py   # 分析服务
│   │   ├── market_service.py   # 市场服务
│   │   ├── notification_service.py  # 通知服务
│   │   ├── security_service.py # 安全服务
│   │   └── social_service.py   # 社交服务
│   ├── exchanges/              # 交易所接口
│   │   ├── base.py             # 基础类
│   │   ├── binance.py          # Binance
│   │   ├── okx.py              # OKX
│   │   └── alpaca.py           # Alpaca（美股）
│   ├── simulation/             # 模拟交易引擎
│   │   └── engine.py           # 引擎核心
│   ├── cache/                  # 缓存系统
│   │   └── redis_cache.py      # Redis 缓存实现
│   ├── schemas/                # 数据验证 Schema
│   ├── scripts/                # 运维脚本
│   │   ├── migrate_sqlite_to_postgres.py  # 数据库迁移
│   │   ├── cleanup_dirty_trade_data.py    # 数据清理
│   │   ├── fix_agent_profit.py            # 盈亏修复
│   │   └── repair_market_alias_positions.py  # 持仓修复
│   └── data/                   # SQLite 数据库存储
├── frontend/                   # 前端
│   ├── index.html              # 入口 HTML
│   ├── package.json            # 依赖配置
│   ├── vite.config.ts          # Vite 构建配置
│   ├── tsconfig.json           # TypeScript 配置
│   └── src/
│       ├── main.ts             # 应用入口
│       ├── App.vue             # 根组件
│       ├── router/             # 路由配置
│       ├── views/              # 页面组件（35+ 页面）
│       │   ├── HomeView.vue        # 首页
│       │   ├── AIView.vue          # AI 对话
│       │   ├── AIChatView.vue      # AI 聊天
│       │   ├── AIAnalysisView.vue  # AI 分析
│       │   ├── AIStrategiesView.vue  # AI 策略
│       │   ├── TradingView.vue     # 交易中心
│       │   ├── MarketView.vue      # 市场总览
│       │   ├── PortfolioView.vue   # 投资组合
│       │   ├── RiskDashboardView.vue  # 风险仪表盘
│       │   ├── StrategiesView.vue     # 策略管理
│       │   ├── AdminView.vue       # 管理后台
│       │   ├── AnalyticsView.vue   # 数据分析
│       │   ├── SettingsView.vue    # 设置
│       │   ├── LoginView.vue       # 登录
│       │   ├── RegisterView.vue    # 注册
│       │   ├── ProfileView.vue     # 个人资料
│       │   └── dashboard/          # 仪表盘组件
│       │       ├── DashboardLayout.vue   # 布局
│       │       ├── AIPredictionView.vue  # AI 预测
│       │       ├── TradingHub.vue        # 交易中心
│       │       ├── RiskCenter.vue        # 风险中心
│       │       ├── SignalSquare.vue      # 信号广场
│       │       ├── MarketIntelligence.vue  # 市场情报
│       │       ├── StrategyCenter.vue    # 策略中心
│       │       └── SettingsPage.vue      # 设置页
│       ├── components/         # 通用组件
│       │   ├── SignalList.vue      # 信号列表
│       │   ├── SearchBar.vue       # 搜索栏
│       │   ├── CommentSection.vue  # 评论区
│       │   ├── NotificationBadge.vue  # 通知徽章
│       │   ├── ThemeToggle.vue     # 主题切换
│       │   ├── LanguageSwitcher.vue  # 语言切换
│       │   └── QuickSettings.vue   # 快速设置
│       ├── stores/             # Pinia 状态管理
│       │   ├── market.ts       # 市场状态
│       │   ├── risk.ts         # 风险状态
│       │   ├── social.ts       # 社交状态
│       │   ├── strategy.ts     # 策略状态
│       │   └── theme.ts        # 主题状态
│       ├── services/           # API 服务层
│       │   ├── trading.ts      # 交易 API
│       │   ├── market.ts       # 市场 API
│       │   ├── strategy.ts     # 策略 API
│       │   ├── risk.ts         # 风险 API
│       │   ├── social.ts       # 社交 API
│       │   ├── security.ts     # 安全 API
│       │   ├── admin.ts        # 管理 API
│       │   └── analytics.ts    # 分析 API
│       └── locales/            # 国际化文件
│           ├── zh-CN.json      # 简体中文
│           └── en-US.json      # 英文
└── docs/                       # 文档
    ├── DEPLOYMENT.md           # 部署指南
    ├── TEST_REPORT_PRICE_CACHE.md  # 缓存测试报告
    └── TEST_REPORT_SMART_TTL.md    # TTL 测试报告
```

## 架构特点

### 双后端架构
项目包含两个后端服务：
- **Flask 应用**（`server/app.py`）：主应用，使用 Blueprint 模块化架构，集成 WebSocket、模拟交易引擎
- **FastAPI 应用**（`server/simple_server.py`）：简化版，异步支持，适合高性能场景

### 数据库设计
- 使用 SQLAlchemy ORM 管理 30+ 数据表
- 支持 SQLite（开发）和 PostgreSQL（生产）
- Alembic 数据库迁移管理
- 启动时自动 Schema 修复（向后兼容旧版本数据库）

### 价格缓存系统
- 两级缓存：本地内存 + Redis
- 智能 TTL 管理（成功/失败差异化 TTL）
- API 调用减少 80-90%，响应时间从 500-2000ms 降至 <5ms
- 支持手动刷新端点和前端刷新按钮

### 模拟交易引擎
- 后端启动后自动运行
- 监控 14+ 主流交易对
- 支持美股和加密货币市场
- 模拟订单创建、执行、盈亏计算

## 注意事项

1. **前端部署为纯静态**：Vercel/Surge 部署仅包含前端，AI 预测、交易等功能需要本地运行后端
2. **DL 模型训练**：首次使用需点击"训练模型"，将从 Binance 拉取历史 K 线数据训练 LSTM 网络
3. **AI 聊天下单**：在 AI 对话中输入自然语言（如"买入 1 BTC"）即可触发下单确认流程
4. **Schema 自动修复**：后端启动时自动检测并修复缺失的数据库列，无需手动迁移
5. **模拟交易引擎**：后端启动后自动运行模拟交易
6. **Redis 可选**：不启用 Redis 时使用纯内存缓存，生产环境推荐启用 Redis
7. **API 速率限制**：默认每分钟 60 次请求，可在 `.env` 中调整

## 相关项目

- 原项目：[HKUDS/AI-Trader](https://github.com/HKUDS/AI-Trader)
- 数据源：[Binance API](https://binance-docs.github.io/apidocs/) | [Alpha Vantage](https://www.alphavantage.co/)

## 许可证

MIT License
