# Deta Space 部署指南

## 🚀 快速开始

### 方法一：使用自动化部署脚本（推荐）

```bash
cd AI-Trader/service/server
./deploy.sh
```

### 方法二：手动部署

#### 1. 安装 Deta Space CLI

```bash
curl -fsSL https://get.deta.dev/space-cli.sh | sh
```

安装完成后，重新打开终端或运行：
```bash
source ~/.zshrc  # 或 source ~/.bashrc
```

#### 2. 登录 Deta Space

```bash
space login
```

按照提示在浏览器中登录。

#### 3. 初始化项目

```bash
cd AI-Trader/service/server
space new --name trading-agent-backend
```

#### 4. 部署

```bash
space push
```

#### 5. 获取应用 URL

```bash
space info
```

你会看到类似这样的输出：
```
App URL: https://trading-agent-backend.deta.app
```

---

## 📁 项目文件说明

| 文件 | 说明 |
|------|------|
| `Spacefile` | Deta Space 配置文件 |
| `main.py` | 应用入口文件 |
| `simple_server.py` | FastAPI 应用主文件 |
| `requirements.txt` | Python 依赖列表 |
| `.spaceignore` | 部署时忽略的文件 |
| `deploy.sh` | 自动化部署脚本 |
| `data/clawtrader.db` | SQLite 数据库文件 |

---

## 🔧 配置说明

### Spacefile 配置

```yaml
v: 0
micros:
  - name: trading-agent-backend
    src: .
    engine: python3.9
    run: uvicorn main:app --host 0.0.0.0 --port 8080
    primary: true
```

- `engine: python3.9` - 使用 Python 3.9 运行时
- `run` - 启动命令，Deta Space 要求使用 8080 端口

---

## 🌐 部署后的配置

### 1. 更新前端 API 地址

部署完成后，你会得到一个 URL，例如 `https://trading-agent-backend.deta.app`。

前端已经配置为使用这个地址。如果你的 URL 不同，请编辑 `AI-Trader/service/frontend/dist/index.html`：

```javascript
if (hostname === 'trading-agent-for-dscourse.surge.sh') {
    return 'https://trading-agent-backend.deta.app';  // 修改为你的 URL
}
```

然后重新部署前端：
```bash
cd AI-Trader/service/frontend/dist
surge .
```

### 2. CORS 配置

后端已配置为允许以下域名访问：
- `http://localhost:8080`
- `http://localhost:3000`
- `https://trading-agent-for-dscourse.surge.sh`
- `https://trading-agent-backend.deta.app`
- 所有 `*.deta.app` 和 `*.deta.dev` 域名

如需添加更多域名，编辑 `simple_server.py` 中的 `allowed_origins` 列表。

---

## 💾 数据库说明

### SQLite 数据库

Deta Space 支持 SQLite 数据库，但需要注意：
- 数据库文件存储在 `data/clawtrader.db`
- 每次重新部署时，数据库会被重置为初始状态
- 如果需要持久化数据，建议使用 Deta Base 或 Deta Collections

### 迁移到 Deta Base（可选）

如果需要更可靠的持久化存储，可以使用 Deta Base：

```python
from deta import Deta

deta = Deta("your_project_key")
db = deta.Base("users")
```

---

## 🔍 查看日志

```bash
space logs
```

或在 Deta Space 控制台中查看：
https://deta.space/

---

## 🧪 本地测试

在部署前，可以先在本地测试：

```bash
cd AI-Trader/service/server
pip install -r requirements.txt
python main.py
```

访问 http://localhost:8080/docs 查看 API 文档。

---

## ❓ 常见问题

### Q: 部署失败怎么办？

A: 查看详细日志：
```bash
space push --verbose
```

### Q: 如何更新应用？

A: 修改代码后，重新部署：
```bash
space push
```

### Q: 如何删除应用？

A:
```bash
space delete
```

### Q: 数据库数据会丢失吗？

A: 每次重新部署时，SQLite 数据库会被重置。如果需要持久化数据：
1. 使用 Deta Base 替代 SQLite
2. 或定期备份数据库文件

### Q: 如何添加环境变量？

A: 在 Deta Space 控制台中：
1. 进入你的应用
2. 点击 "Settings"
3. 在 "Environment Variables" 中添加

---

## 📱 演示账户

- **邮箱**: `demo@example.com`
- **密码**: `demo123`

---

## 🎯 下一步

1. ✅ 部署后端到 Deta Space
2. ✅ 更新前端 API 地址（如果需要）
3. ✅ 重新部署前端到 surge.sh
4. 🚀 访问 https://trading-agent-for-dscourse.surge.sh 测试

---

## 📚 更多资源

- Deta Space 文档: https://deta.space/docs
- FastAPI 文档: https://fastapi.tiangolo.com
- Deta Discord: https://discord.gg/deta
