# Deta Space 登录指南

## 🔐 获取访问令牌

### 方法一：使用浏览器登录（推荐）

1. 访问 https://deta.space 并注册/登录账号
2. 登录后，点击右上角的头像
3. 选择 "Settings"
4. 在 "Access Tokens" 部分，点击 "Create new token"
5. 输入 token 名称（例如：`trading-agent`）
6. 复制生成的 token（只显示一次，请保存好）

### 方法二：直接访问令牌页面

登录后直接访问：https://deta.space/settings/tokens

---

## 🚀 使用令牌登录

### 方法一：使用部署脚本

```bash
cd AI-Trader/service/server
export PATH="/Users/bytedance/Documents/trae_projects/trading_agent_for_dscourse/bin:$PATH"
echo "你的-token" | space login --with-token
```

### 方法二：手动登录

```bash
# 设置 PATH
export PATH="/Users/bytedance/Documents/trae_projects/trading_agent_for_dscourse/bin:$PATH"

# 登录（将 YOUR_TOKEN 替换为你的实际 token）
echo "YOUR_TOKEN" | space login --with-token

# 验证登录
space version
```

---

## 📝 完整部署流程

```bash
# 1. 进入后端目录
cd /Users/bytedance/Documents/trae_projects/trading_agent_for_dscourse/AI-Trader/service/server

# 2. 设置 PATH
export PATH="/Users/bytedance/Documents/trae_projects/trading_agent_for_dscourse/bin:$PATH"

# 3. 登录（替换为你的 token）
echo "你的-access-token" | space login --with-token

# 4. 初始化项目（首次部署）
space new --name trading-agent-backend

# 5. 部署
space push

# 6. 查看应用信息
# 登录 https://deta.space 查看你的应用 URL
```

---

## 💡 常见问题

### Q: 忘记了 token 怎么办？
A: 可以在 https://deta.space/settings/tokens 创建新的 token。

### Q: 如何永久设置 PATH？
A: 将以下内容添加到 `~/.zshrc` 或 `~/.bashrc`：
```bash
export PATH="/Users/bytedance/Documents/trae_projects/trading_agent_for_dscourse/bin:$PATH"
```

### Q: 部署失败怎么办？
A: 使用详细日志查看错误：
```bash
space push --verbose
```

---

## 📱 部署完成后

部署成功后，你会在 Deta Space 控制台看到你的应用 URL，例如：
`https://trading-agent-backend.deta.app`

然后需要：
1. 如果 URL 不是 `https://trading-agent-backend.deta.app`，更新前端代码中的 API 地址
2. 重新部署前端到 surge.sh

---

## 🔐 演示账户

- **邮箱**: `demo@example.com`
- **密码**: `demo123`
