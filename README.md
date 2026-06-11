# AI-Trader — 智能交易助手

一个功能完整的 AI 交易助手平台，支持**加密货币**（BTC/USDT、ETH/USDT 等）市场，包含 AI 对话、风险控制、市场情报、策略编辑、DL 价格预测等功能。

## 功能特性

### AI Agent 对话看板
- 多角色 AI 助手（市场分析师、交易教练、投资组合经理、量化研究员）
- 对话历史记录与快捷提问模板
- 自然语言下单（输入"买入 1 BTC"即可创建订单）
- 下单确认卡片（交易对/方向/数量/价格/模式）

### DL 价格预测（LSTM 深度学习）
- 基于 TensorFlow/Keras LSTM 模型的加密货币价格预测
- 多交易对支持（BTC、ETH、SOL、BNB、XRP、ADA、DOT、LINK、AVAX、MATIC）
- 可配置训练轮数（epochs），实时训练进度
- 训练指标展示（MAE、MSE、样本数）
- 最近预测样本对比表

### 风险仪表盘
- 实时风险指标监控（集中度风险、净敞口、最大回撤、胜率、夏普比率）
- 风险预警系统与仓位计算器

### 市场情报中心
- 加密货币市场总览（总市值、BTC 占比、24h 成交量）
- Top 10 加密货币实时行情
- 多数据源支持：**Binance API**（加密货币）

### 策略编辑器
- 策略创建与管理
- 策略模板库与代码编辑器

### 信号市场
- 实时交易信号流
- 多类型信号（交易操作、分析报告、讨论）
- 信号质量评分与互动统计

### 通知系统
- 实时通知中心与邮件配置

## 技术栈

### 后端
| 技术 | 用途 |
|------|------|
| **Flask 3.0** | Web 框架 |
| **Flask-SocketIO** | WebSocket 实时通信 |
| **SQLAlchemy 2.0** | ORM 数据库层 |
| **TensorFlow / Keras** | LSTM 深度学习价格预测 |
| **Binance API** | 加密货币行情与历史 K 线数据 |
| **SQLite / PostgreSQL** | 数据库（开发/生产） |
| **eventlet** | 异步协程支持 |

### 前端
| 技术 | 用途 |
|------|------|
| **Vue 3** (Composition API) | UI 框架 |
| **TypeScript** | 类型安全 |
| **Vite 5** | 构建工具 |
| **Pinia** | 状态管理 |
| **Vue Router 4** | 路由 |
| **vue-i18n** | 国际化（中/英） |
| **Axios** | HTTP 请求 |
| **Socket.IO Client** | WebSocket 客户端 |

## 快速开始

### 本地开发

#### 1. 克隆项目
```bash
git clone https://github.com/lccuhk/ai-trader-customization.git
cd ai-trader-customization
```

#### 2. 安装后端依赖
```bash
pip install -r server/requirements.txt
```

完整依赖（含 DL 预测）：
```bash
pip install flask flask-cors flask-socketio sqlalchemy python-dotenv eventlet tensorflow pandas numpy scikit-learn requests
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

#### 5. 启动后端服务
```bash
python main.py
```

后端将在 `http://localhost:8001` 启动。如遇端口冲突可指定端口：
```bash
PORT=8002 python main.py
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

### 前端（Vercel）
前端已部署在 Vercel，配置见 `vercel.json`：
- **生产地址**: [https://ai-trader-customization.vercel.app](https://ai-trader-customization.vercel.app)

> 注意：Vercel 部署为纯静态页面，AI 预测、交易等功能需要本地运行后端并通过 `localhost:3000` 访问。

### 后端（Render.com）
1. 在 Render.com 创建 Web Service
2. **Build Command**: `pip install -r server/requirements.txt`
3. **Start Command**: `python main.py`

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
GET  /api/ai/agents
POST /api/ai/chat              # AI 对话
POST /api/ai/signals/generate  # 生成 AI 交易信号
POST /api/ai/analysis          # 交易行为分析
POST /api/ai/strategies        # 策略生成
```

### ML 预测接口
```http
GET  /api/ml/status/{symbol}     # 模型训练状态（如 /api/ml/status/BTCUSDT）
GET  /api/ml/predict/{symbol}    # 获取预测价格
POST /api/ml/train/{symbol}      # 训练模型（body: { epochs: 30 }）
```

### 加密货币接口
```http
GET /api/crypto/overview        # 市场总览（总市值、BTC 占比、24h 成交量）
GET /api/crypto/top?limit=10    # Top N 加密货币
```

### 风险接口
```http
GET /api/risk/dashboard
GET /api/risk/alerts
POST /api/risk/calculate-position-size
```

### 市场接口
```http
GET /api/market/dashboard
GET /api/market/news?limit=10
GET /api/market/indicators
```

### 信号接口
```http
GET /api/signals/feed?limit=20
GET /api/signals/{signal_id}
```

### 交易接口
```http
GET  /api/trading/orders         # 获取订单列表
POST /api/trading/orders         # 创建订单
DELETE /api/trading/orders/{id}  # 取消订单
```

## 项目结构

```
ai-trader-customization/
├── main.py                   # 应用入口
├── vercel.json               # Vercel 部署配置
├── .env.example              # 环境变量模板
├── server/                   # 后端
│   ├── app.py                # Flask 应用工厂
│   ├── config.py             # 配置管理
│   ├── database.py           # 数据库初始化 + schema 修复
│   ├── models.py             # ORM 模型
│   ├── routes/               # API 路由
│   │   ├── auth.py           # 认证
│   │   ├── ai.py             # AI 对话
│   │   ├── ml.py             # DL 价格预测
│   │   ├── crypto.py         # 加密货币行情
│   │   ├── market.py         # 市场数据
│   │   ├── trading.py        # 交易
│   │   ├── signals.py        # 信号市场
│   │   ├── risk.py           # 风险管理
│   │   ├── admin.py          # 管理后台
│   │   ├── analytics.py      # 数据分析
│   │   ├── security.py       # 安全
│   │   ├── social.py         # 社交
│   │   ├── users.py          # 用户
│   │   ├── notifications.py  # 通知
│   │   └── health.py         # 健康检查
│   ├── services/             # 业务逻辑层
│   │   ├── ai_service.py     # AI 服务
│   │   ├── trading_service.py
│   │   ├── signal_service.py
│   │   └── ...
│   ├── simulation/           # 交易模拟引擎
│   ├── middleware/           # 中间件（鉴权、限流、错误处理）
│   └── data/                 # SQLite 数据库目录
├── frontend/                 # 前端
│   ├── src/
│   │   ├── views/            # 页面组件
│   │   │   ├── dashboard/    # 仪表盘（AIPrediction、TradingHub 等）
│   │   │   ├── AIView.vue
│   │   │   ├── AIChatView.vue
│   │   │   ├── AIAnalysisView.vue
│   │   │   ├── AIStrategiesView.vue
│   │   │   └── ...
│   │   ├── components/       # 通用组件
│   │   │   ├── AIChatSidebar.vue  # AI 对话侧边栏
│   │   │   └── ...
│   │   ├── stores/           # Pinia 状态管理
│   │   ├── services/         # API 服务层
│   │   ├── router/           # 路由配置
│   │   ├── locales/          # 国际化（zh-CN / en-US）
│   │   └── data/             # Mock 数据
│   ├── package.json
│   └── vite.config.ts
└── docs/                     # 文档
```

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `PORT` | 服务端口 | 8001 |
| `FLASK_ENV` | 运行环境 | development |
| `FLASK_DEBUG` | 调试模式 | True |
| `SECRET_KEY` | JWT 密钥（生产必填） | - |
| `DATABASE_URL` | 数据库连接 | SQLite 本地文件 |
| `ALLOWED_ORIGINS` | CORS 允许域名 | localhost:3000 |

## 注意事项

1. **Vercel 部署为纯前端**：AI 预测、交易等功能需要本地运行后端，通过 `localhost:3000` 访问可获得完整体验
2. **DL 模型训练**：首次使用需点击"训练模型"，将从 Binance 拉取历史 K 线数据训练 LSTM 网络
3. **AI 聊天下单**：在 AI 对话中输入自然语言（如"买入 1 BTC"）即可触发下单确认流程
4. **Schema 自动修复**：后端启动时自动检测并修复缺失的数据库列，无需手动迁移
5. **模拟交易引擎**：后端启动后自动运行模拟交易，监控 14 个主流交易对

## 许可证

MIT License
