# AI-Trader 定制化项目

本项目记录了对 [HKUDS/AI-Trader](https://github.com/HKUDS/AI-Trader) 开源项目的本地部署、功能增强和性能优化工作。

## 项目概述

AI-Trader 是一个基于 AI 的自动化交易系统。本项目对其进行了以下定制化改进：

- ✅ Python 3.9 兼容性修复
- ✅ 价格获取功能增强（免费 API 端点回退）
- ✅ 手动刷新功能（前后端）
- ✅ Redis 两级缓存系统
- ✅ 17 个单元测试（全部通过）
- ✅ 完整的测试报告文档

## 快速开始

### 1. 克隆原项目

```bash
git clone https://github.com/HKUDS/AI-Trader.git
cd AI-Trader
```

### 2. 安装依赖

```bash
# 后端
cd service
python3 -m pip install -r requirements.txt
python3 -m pip install email-validator eval_type_backport

# 前端
cd frontend
npm install

# Redis（可选，推荐）
brew install redis
redis-server --daemonize yes
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env` 并配置：

```env
ALPHA_VANTAGE_API_KEY=your_api_key
REDIS_ENABLED=true
REDIS_URL=redis://localhost:6379
PRICE_CACHE_TTL_SECONDS=30
```

### 4. 启动服务

```bash
# 后端
cd service/server
python3 -m uvicorn main:app --host 0.0.0.0 --port 9004 --reload

# 前端
cd service/frontend
npm run dev

# Worker
cd service/server
python3 worker.py
```

## 主要改进

### 1. Python 3.9 兼容性

- 添加 `from __future__ import annotations`
- 安装 `eval_type_backport` 依赖

### 2. 价格获取增强

- 支持 Alpha Vantage 免费 API 端点回退
- 从 `TIME_SERIES_INTRADAY`（高级）回退到 `GLOBAL_QUOTE`（免费）

### 3. 手动刷新功能

- 后端 API: `POST /api/refresh-prices`
- 前端按钮：在 TrendingSidebar 中添加刷新按钮
- 显示刷新状态和结果统计

### 4. Redis 缓存系统

两级缓存架构：
- **Level 1**: 本地内存缓存（最快，< 1ms）
- **Level 2**: Redis 缓存（共享，~1-5ms）

缓存 TTL 可配置：
- 成功价格缓存：默认 30 秒
- 失败请求缓存：默认 15 秒

### 5. 性能提升

- API 调用减少：80-90%
- 响应时间：从 500-2000ms 降至 < 5ms（缓存命中）

## 测试

运行单元测试：

```bash
cd service/server
python3 -m pytest tests/test_price_cache.py -v
```

测试结果：**17 passed**

## 文档

- [项目完整记录](./PROJECT_LOG_AI_TRADER.md)
- [测试报告](./TEST_REPORT_PRICE_CACHE.md)
- [环境配置示例](./.env.example)

## 修改的文件

### 后端
- `service/server/routes_agent.py` - Python 3.9 兼容性
- `service/server/price_fetcher.py` - 缓存系统和 API 回退
- `service/server/routes_market.py` - 手动刷新 API
- `service/server/tasks.py` - 一次性刷新函数

### 前端
- `service/frontend/src/AppPages.tsx` - 手动刷新按钮
- `service/frontend/vite.config.mts` - API 代理配置

### 新增文件
- `service/server/tests/test_price_cache.py` - 17 个单元测试
- `docs/TEST_REPORT_PRICE_CACHE.md` - 测试报告

## 相关链接

- 原项目: https://github.com/HKUDS/AI-Trader
- Alpha Vantage: https://www.alphavantage.co/
- Redis: https://redis.io/

## 许可证

与原项目保持一致。
