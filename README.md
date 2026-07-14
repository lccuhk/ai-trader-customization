# AI-Trader — 智能交易助手

<p align="center">
  <img src="https://img.shields.io/github/stars/lccuhk/ai-trader-customization?style=for-the-badge&color=00D9FF" />
  <img src="https://img.shields.io/github/forks/lccuhk/ai-trader-customization?style=for-the-badge&color=00FF88" />
  <img src="https://img.shields.io/github/issues/lccuhk/ai-trader-customization?style=for-the-badge&color=FF6B6B" />
  <img src="https://img.shields.io/github/license/lccuhk/ai-trader-customization?style=for-the-badge&color=FFD93D" />
  <img src="https://img.shields.io/github/last-commit/lccuhk/ai-trader-customization?style=for-the-badge&color=9B59B6" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Vue-3.x-4FC08D?style=for-the-badge&logo=vue.js&logoColor=white" />
  <img src="https://img.shields.io/badge/Flask-2.x-000000?style=for-the-badge&logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" />
</p>

<p align="center">
  <a href="https://frontend-six-mu-xqj303z2z3.vercel.app">
    <img src="https://img.shields.io/badge/🚀_在线演示-Vercel-00D9FF?style=for-the-badge" />
  </a>
  <a href="https://github.com/lccuhk/ai-trader-customization">
    <img src="https://img.shields.io/badge/📂_查看源码-GitHub-00FF88?style=for-the-badge" />
  </a>
</p>

一个功能完整的 AI 交易助手平台，基于 [HKUDS/AI-Trader](https://github.com/HKUDS/AI-Trader) 定制开发，集成了 AI 对话、风险控制、市场情报、策略编辑、信号市场等功能。

## 🖼️ 项目预览

<p align="center">
  <img src="docs/images/preview.svg" alt="AI Trader Preview" width="100%" style="border-radius: 10px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);" />
</p>

## 生产环境

| 组件 | URL | 部署平台 |
|------|-----|---------|
| 前端 | https://frontend-six-mu-xqj303z2z3.vercel.app | Vercel |
| 后端 | https://ai-trader-customization.onrender.com | Render |

## ✨ 功能特性

### 🤖 AI Agent 对话看板
- 多角色 AI 助手（市场分析师、交易教练、投资组合经理、量化研究员）
- 对话历史记录
- 快捷提问模板

### 📊 风险仪表盘
- 实时风险指标监控（集中度风险、净敞口、最大回撤、胜率、夏普比率）
- 风险预警系统
- 仓位计算器

### 📰 市场情报中心
- 实时市场新闻聚合
- 事件日历
- 经济指标
- 市场情绪分析

### 💡 策略编辑器
- 策略创建和管理
- 策略模板库
- 回测引擎

### 👤 用户系统
- 用户注册和登录
- 个人资料管理
- 偏好设置

### 🔔 通知系统
- 实时通知中心
- Webhook 集成

### 📈 信号市场
- 实时交易信号流
- 多类型信号（交易操作、分析报告、讨论）
- 多市场覆盖（美股、加密货币、预测市场）
- 信号质量评分

## 🛠️ 技术栈

### 后端
- **Flask 3.0.0** — Python Web 框架
- **SQLite** — 数据库
- **Python 3.9+**

### 前端
- **Vue 3** + **Vite** + **TypeScript**
- **Pinia** — 状态管理
- **Vue Router** — 路由
- **Axios** — HTTP 请求
- **Chart.js** — 图表

### 部署
- **Render.com** — 后端
- **Vercel** — 前端

## 🚀 快速开始

### 本地开发

#### 1. 克隆项目
```bash
git clone https://github.com/lccuhk/ai-trader-customization.git
cd ai-trader-customization
```

#### 2. 安装后端依赖
```bash
pip install -r requirements.txt
```

#### 3. 启动后端
```bash
cd server && python flask_server.py
```
后端服务将在 http://localhost:8001 启动。

#### 4. 启动前端
```bash
cd frontend
npm install
npm run dev
```
前端开发服务器将在 http://localhost:3000 启动，自动代理 API 请求到后端。

### 演示账户

| 字段 | 值 |
|------|-----|
| 邮箱 | `demo@example.com` |
| 密码 | `demo123456` |

## 📡 API 文档

### 基础 URL
- 本地: `http://localhost:8001`
- 生产: `https://ai-trader-customization.onrender.com`

### 认证接口

#### 登录
```http
POST /api/auth/login
Content-Type: application/json

{
    "username": "demo@example.com",
    "password": "demo123456"
}
```

**响应:**
```json
{
    "success": true,
    "token": "...",
    "user": {
        "id": 1,
        "username": "demo",
        "email": "demo@example.com",
        "display_name": "Demo User"
    }
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
GET  /api/ai/agents          # 获取 AI 助手列表
POST /api/ai/chat            # AI 对话
GET  /api/ai/conversations   # 获取对话列表
```

### 风险接口

```http
GET  /api/risk/dashboard              # 获取风险仪表盘
GET  /api/risk/settings               # 获取风险设置
GET  /api/risk/alerts                 # 获取风险预警
POST /api/risk/calculate-position-size # 计算仓位大小
```

### 市场接口

```http
GET /api/market/dashboard              # 获取市场仪表盘
GET /api/market/news?limit=10          # 获取市场新闻
GET /api/market/events                 # 获取市场事件
GET /api/market/indicators             # 获取经济指标
```

### 策略接口

```http
GET  /api/strategies           # 获取策略列表
POST /api/strategies           # 创建策略
POST /api/strategies/backtest  # 策略回测
GET  /api/strategies/templates # 获取策略模板
```

### 信号市场接口

```http
GET /api/signals/feed?limit=20&message_type=operation&market=us-stock
GET /api/signals/{signal_id}
```

**查询参数:**

| 参数 | 说明 |
|------|------|
| `limit` | 返回数量，默认 20 |
| `message_type` | `operation` / `analysis` / `discussion` |
| `market` | `us-stock` / `crypto` / `polymarket` |

### 通知接口

```http
GET /api/notifications           # 获取通知列表
PUT /api/notifications/{id}/read # 标记已读
PUT /api/notifications/read-all  # 全部已读
```

## 🌐 部署

### 后端 (Render.com)

`render.yaml` 配置：
```yaml
services:
  - type: web
    name: ai-trader-customization
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: cd server && python flask_server.py
```

部署步骤：
1. 将代码推送到 GitHub
2. Render 自动检测 `render.yaml` 并部署
3. 或手动创建 Web Service 关联仓库

### 前端 (Vercel)

```bash
cd frontend
npm run build
vercel --prod
```

Vercel 通过 `vercel.json` 将 `/api/*` 请求代理到 Render 后端。

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `PORT` | 服务端口 | 8001 |
| `PYTHON_VERSION` | Python 版本 | 3.11.9 |
| `FLASK_ENV` | Flask 环境 | production |

## 📁 项目结构

```
ai-trader-customization/
├── main.py                 # 备用应用入口
├── requirements.txt        # Python 依赖
├── render.yaml             # Render 部署配置
├── vercel.json             # Vercel 代理配置
├── server/                 # 后端代码
│   ├── flask_server.py     # Flask 后端服务（主）
│   ├── config.py           # 配置模块
│   ├── requirements.txt   # 后端依赖
│   └── data/               # SQLite 数据库目录
└── frontend/               # Vue 前端
    ├── package.json
    ├── vite.config.ts
    ├── vercel.json         # Vercel 路由配置
    ├── src/
    │   ├── main.ts         # 应用入口
    │   ├── App.vue
    │   ├── router/         # 路由
    │   ├── stores/         # Pinia 状态管理
    │   ├── services/       # API 请求 (axios)
    │   ├── views/          # 页面组件
    │   └── components/     # 通用组件
    └── dist/               # 构建产物
```

## 🔧 配置说明

### CORS 配置
后端通过 `before_request` + `after_request` 处理 CORS，支持所有来源。

### 数据库
- 默认使用 SQLite，路径 `server/data/clawtrader.db`
- 首次启动自动创建表结构和演示数据
- 演示账户密码每次启动自动重置为 `demo123456`

## 📝 注意事项

1. **Render 免费版会休眠**：15 分钟无活动后休眠，首次访问需等 10-30 秒
2. **数据库会重置**：每次重新部署 SQLite 数据库重置为初始状态
3. **演示数据**：系统包含示例数据用于演示

## 🗺️ 路线图 (Roadmap)

### 短期目标 (v1.2.0)
- [ ] 添加更多 AI 助手角色
- [ ] 实现策略回测可视化
- [ ] 添加更多交易信号源
- [ ] 优化移动端体验
- [ ] 支持自定义策略模板

### 中期目标 (v1.3.0)
- [ ] 集成实盘交易接口
- [ ] 添加投资组合管理
- [ ] 实现风险预警通知
- [ ] 支持多账户管理
- [ ] 添加高级图表分析

### 长期目标 (v2.0.0)
- [ ] 实现 AI 自动交易
- [ ] 添加社交交易功能
- [ ] 支持多市场覆盖（股票、加密货币、外汇）
- [ ] 发布移动应用
- [ ] 建立交易社区

### 功能增强
- [ ] 添加更多 API 接口
- [ ] 优化数据库性能
- [ ] 支持插件扩展
- [ ] 添加多语言支持（中文、英文、日文）
- [ ] 集成更多第三方数据源

## 🎯 里程碑规划

我们按以下里程碑推进项目开发：

| 里程碑 | 状态 | 目标 | 预计完成 |
|--------|------|------|---------|
| **v0.x Stabilization** | 🟡 进行中 | Bug 修复与性能优化，提升交易系统稳定性 | 2026 Q3 |
| **Docs & Onboarding** | ⚪ 待办 | 完善文档与示例，降低使用门槛 | 2026 Q3 |
| **Public Release** | ⚪ 待办 | 对外发布与推广，社区建设 | 2026 Q4 |

### 里程碑详情

#### v0.x Stabilization
- [ ] 修复 API 接口稳定性问题
- [ ] 优化前端页面加载速度
- [ ] 提升交易信号准确率
- [ ] 完善单元测试覆盖率至 80%

#### Docs & Onboarding
- [ ] 添加详细的 API 文档
- [ ] 创建部署和配置指南
- [ ] 提供更多策略模板
- [ ] 添加常见问题解答

#### Public Release
- [ ] 发布 v1.0 正式版本
- [ ] 撰写项目介绍博客
- [ ] 提交到相关开源社区
- [ ] 建立贡献者社区

## 📋 项目管理

我们使用 GitHub Projects 进行看板化管理：

### 工作流
```
📥 待办 → 🔄 进行中 → ✅ 完成 → 🚀 已发布
```

### 看板状态
- **📥 待办** - 待处理的 Issue 和 PR
- **🔄 进行中** - 正在开发的任务
- **✅ 完成** - 已完成待合并的任务
- **🚀 已发布** - 已发布到正式版本

### 关联项目
- [📊 项目看板](https://github.com/users/lccuhk/projects) - 查看所有项目进度
- [📝 里程碑](https://github.com/lccuhk/ai-trader-customization/milestones) - 查看里程碑详情

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 如何贡献

1. Fork 本仓库
2. 创建你的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

### 贡献指南

- 请确保代码遵循项目的代码规范
- 提交 PR 前请先运行测试确保功能正常
- 请为新功能添加相应的文档说明
- 如有重大更改，请先开启 Issue 讨论

更多信息请参考 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。
