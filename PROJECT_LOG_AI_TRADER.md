# AI-Trader 项目定制化记录

## 项目概述

本项目记录了对 [HKUDS/AI-Trader](https://github.com/HKUDS/AI-Trader) 开源项目的本地部署、功能增强和性能优化工作。

## 完成的工作

### 1. 本地部署

#### 1.1 环境配置
- **操作系统**: macOS
- **Python 版本**: 3.9.6
- **Node.js 版本**: 22.14.0
- **数据库**: SQLite (默认) / PostgreSQL (可选)

#### 1.2 环境变量配置
创建了 `.env` 配置文件：

```env
# 基础环境
ENVIRONMENT=development

# 数据库
DB_PATH=service/server/data/clawtrader.db

# API 密钥
ALPHA_VANTAGE_API_KEY=SRE8D1YI42AJAVMJ

# 前端刷新间隔
VITE_REFRESH_INTERVAL=60000

# CORS 配置
CLAWTRADER_CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# 价格更新间隔
POSITION_REFRESH_INTERVAL=60

# 价格缓存 TTL
PRICE_CACHE_TTL_SECONDS=30
PRICE_FAILURE_CACHE_TTL_SECONDS=15

# Redis 缓存
REDIS_ENABLED=true
REDIS_URL=redis://localhost:6379
REDIS_PREFIX=ai_trader
```

#### 1.3 服务启动
- **前端**: http://localhost:3001/
- **后端 API**: http://localhost:9004/
- **Redis**: localhost:6379

---

### 2. Python 3.9 兼容性修复

#### 2.1 问题
项目使用了 Python 3.10+ 的类型注解语法（`int | None`），但系统只有 Python 3.9。

#### 2.2 解决方案

**修改文件**: `service/server/routes_agent.py`

```python
# 添加到文件顶部
from __future__ import annotations
```

**安装依赖**:
```bash
python3 -m pip install eval_type_backport
```

---

### 3. 价格获取功能增强

#### 3.1 问题
Alpha Vantage 免费 API 密钥无法访问 `TIME_SERIES_INTRADAY`（高级端点）。

#### 3.2 解决方案
修改 `service/server/price_fetcher.py`，添加免费端点回退机制：

```python
def _get_us_stock_price(symbol: str, executed_at: str) -> Optional[float]:
    # 先尝试 TIME_SERIES_INTRADAY（高级端点）
    price = _try_intraday_price(symbol, dt_et)
    if price is not None:
        return price
    
    # 回退到 GLOBAL_QUOTE（免费端点）
    return _try_global_quote_price(symbol)
```

#### 3.3 新增函数
- `_try_intraday_price()` - 尝试高级端点
- `_try_global_quote_price()` - 使用免费端点

---

### 4. 测试数据创建

#### 4.1 代理账户
创建了 10 个测试代理账户：
- test_agent_1 到 test_agent_10
- 每个代理初始资金 $100,000

#### 4.2 持仓数据
创建了 54 个持仓，覆盖 21 只股票：
- 科技股: AAPL, MSFT, NVDA, AMZN, META, TSLA, GOOGL, GOOG, AMD, INTC
- 金融股: JPM, BAC, V, MA
- 消费股: WMT, COST, TGT, HD
- 医疗股: JNJ, PFE, MRK
- 其他: DIS, NFLX, CRM

---

### 5. 手动刷新功能

#### 5.1 后端 API
新增端点: `POST /api/refresh-prices`

**修改文件**: `service/server/routes_market.py`

```python
@app.post('/api/refresh-prices')
async def refresh_prices():
    result = await refresh_prices_once()
    return result
```

#### 5.2 一次性刷新函数
新增函数: `service/server/tasks.py`

```python
async def refresh_prices_once() -> dict:
    """手动刷新价格一次并返回结果"""
    # ... 实现逻辑
    return {
        "success": True,
        "total": total_count,
        "updated": success_count,
        "failed": failed_count,
        "results": results
    }
```

#### 5.3 前端按钮
修改 `service/frontend/src/AppPages.tsx`，在 `TrendingSidebar` 组件中添加：

- 刷新状态管理
- 刷新按钮 UI
- 刷新结果显示
- 中英文双语支持

**按钮功能**:
- 点击触发手动刷新
- 显示刷新状态（刷新中/完成）
- 显示刷新结果统计
- 5 秒后自动清除消息

---

### 6. Redis 缓存系统

#### 6.1 Redis 安装
```bash
brew install redis
/opt/homebrew/opt/redis/bin/redis-server --daemonize yes
```

#### 6.2 缓存架构
实现了两级缓存系统：

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

#### 6.3 缓存键格式
```
price:{market}:{symbol}[:{token_id}]
```

示例:
- `price:us-stock:AAPL`
- `price:polymarket:BTC:12345`

#### 6.4 缓存 TTL 配置
- **成功价格缓存**: 30 秒（可配置）
- **失败请求缓存**: 15 秒（可配置）
- **最小 TTL**: 5 秒

---

### 7. 价格缓存实现

#### 7.1 新增缓存函数
修改 `service/server/price_fetcher.py`：

```python
# 缓存配置
_PRICE_CACHE_TTL_SECONDS = max(5, int(os.environ.get("PRICE_CACHE_TTL_SECONDS", "60")))
_PRICE_FAILURE_CACHE_TTL_SECONDS = max(5, int(os.environ.get("PRICE_FAILURE_CACHE_TTL_SECONDS", "30")))

# 缓存键生成
def _price_cache_key(symbol: str, market: str, token_id: Optional[str] = None) -> str:
    token_part = f":{token_id}" if token_id else ""
    return f"price:{market}:{symbol}{token_part}"

# 缓存读取
def _price_cache_get(symbol: str, market: str, token_id: Optional[str] = None) -> Optional[float]:
    # 先查本地缓存
    # 再查 Redis 缓存
    # 未命中返回 None

# 缓存写入
def _price_cache_set(symbol: str, market: str, price: Optional[float], token_id: Optional[str] = None) -> None:
    # 写入本地缓存
    # 写入 Redis 缓存（如果启用）
```

#### 7.2 缓存流程
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

---

### 8. 单元测试

#### 8.1 测试文件
创建了 `service/server/tests/test_price_cache.py`

#### 8.2 测试覆盖范围

**PriceCacheKeyTests (8 个测试)**:
- `test_cache_key_generation` - 缓存键生成
- `test_cache_key_with_token_id` - 带 token_id 的缓存键
- `test_local_cache_hit` - 本地缓存命中
- `test_local_cache_miss` - 本地缓存未命中
- `test_local_cache_expiration` - 本地缓存过期
- `test_failure_cache` - 失败请求缓存
- `test_different_markets` - 不同市场缓存隔离
- `test_cache_overwrite` - 缓存覆盖

**PriceCacheTTLTests (2 个测试)**:
- `test_success_cache_ttl` - 成功价格缓存 TTL
- `test_failure_cache_ttl` - 失败请求缓存 TTL

**RedisCacheTests (4 个测试)**:
- `test_redis_cache_hit` - Redis 缓存命中
- `test_redis_cache_miss` - Redis 缓存未命中
- `test_redis_cache_expired` - Redis 缓存过期
- `test_redis_cache_set` - Redis 缓存设置

**PriceCacheIntegrationTests (3 个测试)**:
- `test_multiple_symbols` - 多股票缓存
- `test_cache_local_priority` - 本地缓存优先级
- `test_redis_to_local_sync` - Redis 到本地同步

#### 8.3 测试结果
```
======================== 17 passed, 1 warning in 0.32s ========================
```

**所有 17 个测试全部通过！**

---

### 9. 测试报告

创建了 `docs/TEST_REPORT_PRICE_CACHE.md`，包含：

- 测试环境信息
- 测试结果摘要
- 详细的测试覆盖说明
- 配置指南
- 缓存架构说明
- 性能优势分析
- 测试执行方法
- 故障排除指南
- 未来改进建议

---

## 性能提升

### API 调用减少
- **之前**: 每次刷新都调用外部 API
- **之后**: 仅在缓存过期时调用 API
- **预计减少**: 80-90% 的 API 调用

### 响应时间改进
- **缓存命中**: < 1ms（本地内存）
- **Redis 命中**: ~1-5ms
- **API 调用**: ~500-2000ms

### 速率限制保护
- Alpha Vantage 免费版: 25 次请求/天
- 使用缓存后: 可支持更多价格更新
- 失败缓存避免重复调用不可用的符号

---

## 修改的文件清单

### 后端修改
1. **service/server/routes_agent.py**
   - 添加 `from __future__ import annotations`

2. **service/server/price_fetcher.py**
   - 添加 Redis 缓存导入
   - 添加两级缓存系统
   - 添加免费 API 端点回退
   - 从环境变量读取缓存 TTL

3. **service/server/routes_market.py**
   - 新增 `POST /api/refresh-prices` 端点

4. **service/server/tasks.py**
   - 新增 `refresh_prices_once()` 函数

5. **service/requirements.txt**
   - 修复 `openrouter` 版本问题

### 前端修改
1. **service/frontend/src/AppPages.tsx**
   - 添加手动刷新按钮
   - 添加刷新状态管理
   - 添加刷新结果显示

2. **service/frontend/vite.config.mts**
   - 更新 API 代理配置

### 新增文件
1. **service/server/tests/test_price_cache.py**
   - 17 个单元测试

2. **docs/TEST_REPORT_PRICE_CACHE.md**
   - 详细的测试报告文档

3. **.env**
   - 完整的环境变量配置

---

## 部署指南

### 前置要求
- Python 3.9+
- Node.js 18+
- Redis（可选，推荐）

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/HKUDS/AI-Trader.git
cd AI-Trader
```

2. **安装后端依赖**
```bash
cd service
python3 -m pip install -r requirements.txt
python3 -m pip install email-validator eval_type_backport
```

3. **安装前端依赖**
```bash
cd frontend
npm install
```

4. **安装 Redis（可选）**
```bash
brew install redis
redis-server --daemonize yes
```

5. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件
```

6. **启动服务**
```bash
# 后端
cd service/server
python3 -m uvicorn main:app --host 0.0.0.0 --port 9004 --reload

# 前端
cd service/frontend
npm run dev

# Worker（价格更新）
cd service/server
python3 worker.py
```

---

## 常用命令

### 运行测试
```bash
cd service/server
python3 -m pytest tests/test_price_cache.py -v
```

### 检查 Redis
```bash
redis-cli ping
redis-cli FLUSHALL  # 清除所有缓存
```

### 查看缓存键
```bash
redis-cli KEYS "ai_trader:price:*"
```

---

## 未来改进建议

### 1. 缓存统计
- 跟踪缓存命中率
- 监控平均响应时间
- 记录缓存性能指标

### 2. 自适应 TTL
- 波动性大的股票 = 更短的 TTL
- 稳定的股票 = 更长的 TTL
- 交易时间 = 更短的 TTL

### 3. 缓存失效
- 手动清除缓存 API
- 交易执行触发缓存刷新
- 市场事件触发缓存刷新

### 4. 分布式缓存
- Redis 集群支持
- 缓存复制
- 高可用性

---

## 相关链接

- **原项目**: https://github.com/HKUDS/AI-Trader
- **Alpha Vantage**: https://www.alphavantage.co/
- **Redis**: https://redis.io/

---

**记录日期**: 2026-05-11
**状态**: ✅ 所有功能已完成并测试通过
