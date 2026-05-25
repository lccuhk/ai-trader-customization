# 部署指南

## 前置要求

- Python 3.9+
- Node.js 18+
- Redis（可选，推荐用于生产环境）

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/HKUDS/AI-Trader.git
cd AI-Trader
```

### 2. 安装依赖

#### 后端

```bash
cd service
python3 -m pip install -r requirements.txt
python3 -m pip install email-validator eval_type_backport
```

#### 前端

```bash
cd frontend
npm install
```

#### Redis（可选）

```bash
# macOS
brew install redis
redis-server --daemonize yes

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis-server
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env` 并配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，至少配置以下内容：

```env
# API 密钥
ALPHA_VANTAGE_API_KEY=your_api_key_here

# Redis 配置（可选）
REDIS_ENABLED=true
REDIS_URL=redis://localhost:6379
REDIS_PREFIX=ai_trader

# 价格缓存 TTL
PRICE_CACHE_TTL_SECONDS=30
PRICE_FAILURE_CACHE_TTL_SECONDS=15
```

### 4. 启动服务

#### 后端

```bash
cd service/server
python3 -m uvicorn main:app --host 0.0.0.0 --port 9004 --reload
```

#### 前端

```bash
cd service/frontend
npm run dev
```

#### Worker（后台任务）

```bash
cd service/server
python3 worker.py
```

## 配置说明

### 价格缓存配置

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `PRICE_CACHE_TTL_SECONDS` | 60 | 成功价格缓存 TTL（秒） |
| `PRICE_FAILURE_CACHE_TTL_SECONDS` | 30 | 失败请求缓存 TTL（秒） |
| `REDIS_ENABLED` | false | 是否启用 Redis 缓存 |
| `REDIS_URL` | "" | Redis 连接 URL |
| `REDIS_PREFIX` | "ai_trader" | Redis 键前缀 |

### 缓存架构

```
Level 1: Local Memory Cache (最快)
  - 进程内缓存
  - 自动从 Redis 同步
  - 优先级最高

Level 2: Redis Cache (共享)
  - 跨进程共享
  - 持久化存储
  - 本地缓存未命中时使用
```

### 缓存流程

```
1. 检查本地内存缓存
   ├─ 命中 → 返回缓存值
   └─ 未命中 → 检查 Redis 缓存

2. 检查 Redis 缓存（如果启用）
   ├─ 命中 → 同步到本地缓存，返回值
   └─ 未命中 → 调用外部 API

3. 调用外部 API
   ├─ 成功 → 缓存结果（TTL: 30s）
   └─ 失败 → 缓存失败（TTL: 15s）
```

## API 端点

### 手动刷新价格

**POST** `/api/refresh-prices`

请求：

```bash
curl -X POST http://localhost:9004/api/refresh-prices
```

响应：

```json
{
  "success": true,
  "total": 10,
  "updated": 8,
  "failed": 2,
  "results": [
    {
      "symbol": "AAPL",
      "market": "us-stock",
      "price": 150.50,
      "success": true
    }
  ]
}
```

## 故障排除

### 价格获取失败

1. 检查 Alpha Vantage API 密钥是否有效
2. 检查网络连接
3. 查看日志中的错误信息
4. 检查是否触发了速率限制

### Redis 连接失败

1. 检查 Redis 服务是否运行
2. 检查 `REDIS_URL` 配置
3. 检查防火墙设置

### 前端无法连接后端

1. 检查后端服务是否运行
2. 检查 API 代理配置
3. 检查 CORS 配置

## 性能优化建议

### 缓存优化

1. **启用 Redis**：生产环境强烈建议启用 Redis 缓存
2. **调整 TTL**：根据实际需求调整缓存 TTL
3. **监控缓存命中率**：定期检查缓存命中率

### 并发优化

1. **调整并行请求数**：通过 `MAX_PARALLEL_PRICE_FETCH` 配置
2. **使用连接池**：确保数据库连接池配置合理

## 升级指南

### 从旧版本升级

1. 拉取最新代码
2. 更新依赖
3. 运行数据库迁移（如果有）
4. 重启服务

## 生产环境部署

### 使用 Docker（推荐）

```bash
# 构建镜像
docker build -t ai-trader .

# 运行容器
docker run -d \
  --name ai-trader \
  -p 9004:9004 \
  -v $(pwd)/.env:/app/.env \
  ai-trader
```

### 使用 systemd

创建服务文件：

```ini
[Unit]
Description=AI-Trader Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/ai-trader/service/server
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 9004
Restart=always

[Install]
WantedBy=multi-user.target
```

## 监控和日志

### 日志位置

- 后端日志：标准输出/错误
- 前端日志：浏览器控制台
- Redis 日志：`/var/log/redis/redis-server.log`

### 监控指标

- 缓存命中率
- API 响应时间
- 错误率
- 系统资源使用情况
