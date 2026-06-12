# 后端部署指南

## 前端部署状态 ✅

前端已成功部署到: **https://trading-agent-for-dscourse.surge.sh**

## 后端部署方案

### 方案一: Render.com (推荐，免费额度)

Render 是最适合部署 FastAPI 应用的平台之一，有免费额度。

#### 部署步骤:

1. **准备代码**
   ```bash
   cd /Users/bytedance/Documents/trae_projects/trading_agent_for_dscourse/AI-Trader/service/server
   ```

2. **创建 Git 仓库并推送**
   ```bash
   git init
   git add .
   git commit -m "Initial backend deployment"
   git branch -M main
   git remote add origin <你的-git-仓库地址>
   git push -u origin main
   ```

3. **在 Render.com 上部署**
   - 访问 https://render.com 并注册账号
   - 点击 "New" -> "Web Service"
   - 连接你的 GitHub 仓库
   - 配置如下:
     - **Name**: `ai-trader-customization`
     - **Runtime**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn simple_server:app --host 0.0.0.0 --port $PORT`
     - **Plan**: Free (或选择适合的付费方案)
   - 点击 "Create Web Service"

4. **配置环境变量 (可选)**
   - 在 Render 控制面板的 "Environment" 中添加:
     - `PORT`: 10000 (Render 会自动设置)

5. **部署完成后**
   - 你会得到一个 URL，例如: `https://ai-trader-customization.onrender.com`
   - 更新前端代码中的 API 地址（已配置为这个地址）

---

### 方案二: Railway.app (有免费试用额度)

Railway 提供 $5 免费额度，适合小型应用。

#### 部署步骤:

1. 访问 https://railway.app 并注册
2. 点击 "New Project" -> "Deploy from GitHub repo"
3. 选择你的仓库
4. 配置:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn simple_server:app --host 0.0.0.0 --port $PORT`
5. 部署后获取 URL，更新前端配置

---

### 方案三: Fly.io (有免费额度)

Fly.io 适合部署全球分布的应用。

#### 部署步骤:

1. 安装 Fly CLI:
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. 登录并初始化:
   ```bash
   fly auth login
   fly launch
   ```

3. 按照提示配置，部署后获取 URL

---

### 方案四: Heroku (需要信用卡验证)

#### 部署步骤:

1. 安装 Heroku CLI:
   ```bash
   brew tap heroku/brew && brew install heroku
   ```

2. 登录并创建应用:
   ```bash
   heroku login
   heroku create ai-trader-customization
   ```

3. 推送代码:
   ```bash
   git push heroku main
   ```

---

## 部署后的配置

### 1. 更新前端 API 地址

如果你的后端 URL 不是 `https://ai-trader-customization.onrender.com`，需要更新前端代码:

编辑 `AI-Trader/service/frontend/dist/index.html`，找到:
```javascript
if (hostname === 'trading-agent-for-dscourse.surge.sh') {
    return 'https://ai-trader-customization.onrender.com';
}
```

修改为你的实际后端 URL，然后重新部署前端:
```bash
cd AI-Trader/service/frontend/dist
surge .
```

### 2. 生产环境配置建议

#### 数据库
- SQLite 适合开发和小型应用
- 如果需要更高性能，建议迁移到 PostgreSQL 或 MySQL
- 可以使用 Render 提供的托管数据库服务

#### CORS 配置
当前已配置为只允许以下域名访问:
- `http://localhost:8080`
- `http://localhost:3000`
- `https://trading-agent-for-dscourse.surge.sh`

如需添加更多域名，编辑 `simple_server.py` 中的 `allowed_origins` 列表。

#### 安全建议
1. 添加环境变量管理敏感配置
2. 考虑添加 HTTPS（Render 等平台会自动提供）
3. 实现速率限制防止 API 滥用
4. 定期备份数据库

---

## 本地测试部署

在部署前，可以先在本地测试生产环境配置:

```bash
cd AI-Trader/service/server
pip install -r requirements.txt
PORT=8001 uvicorn simple_server:app --host 0.0.0.0 --port 8001
```

访问 http://localhost:8001/docs 查看 API 文档。

---

## 演示账户

- **邮箱**: `demo@example.com`
- **密码**: `demo123`

---

## 常见问题

### Q: 部署后 API 无法访问?
A: 检查以下几点:
1. 后端服务是否正常运行
2. CORS 配置是否包含前端域名
3. 端口是否正确配置

### Q: 数据库数据丢失?
A: SQLite 数据库文件在容器重启时会丢失。如果需要持久化数据:
1. 使用 Render 的磁盘挂载功能
2. 或迁移到 PostgreSQL 等托管数据库

### Q: 如何添加真实的 AI 对话功能?
A: 需要接入 OpenAI 或其他 LLM API，在 `simple_server.py` 中的 `ai_chat` 函数中实现真实的 API 调用。
