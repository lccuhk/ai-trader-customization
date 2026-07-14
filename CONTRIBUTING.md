# 贡献指南

感谢您对 **AI-Trader** 项目的关注！我们欢迎任何形式的贡献，无论是提交 Bug 报告、提出功能建议，还是直接贡献代码。

## 📋 目录

- [行为准则](#行为准则)
- [如何贡献](#如何贡献)
  - [提交 Issue](#提交-issue)
  - [提交 Pull Request](#提交-pull-request)
- [代码规范](#代码规范)
  - [Python 后端](#python-后端)
  - [Vue 前端](#vue-前端)
- [开发环境](#开发环境)
  - [后端开发](#后端开发)
  - [前端开发](#前端开发)
- [测试指南](#测试指南)

## 行为准则

本项目遵循 [Contributor Covenant](.github/CODE_OF_CONDUCT.md) 行为准则。参与项目即表示您同意遵守其条款。

## 如何贡献

### 提交 Issue

如果您发现了 Bug 或有新功能建议，请通过 Issue 告诉我们：

1. **Bug 报告**：请包含以下信息
   - 问题描述（清晰简洁）
   - 复现步骤
   - 预期行为
   - 实际行为
   - 环境信息（操作系统、Python 版本、浏览器版本等）
   - 错误日志或截图（如适用）

2. **功能建议**：请包含以下信息
   - 功能描述
   - 为什么需要这个功能
   - 实现思路（可选）
   - 相关的使用场景

### 提交 Pull Request

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

**PR 规范：**
- 标题清晰描述改动内容，使用中文或英文均可
- 详细说明改动的原因和内容
- 关联相关的 Issue（如 `Fixes #123`）
- 确保代码通过所有测试和代码检查
- 更新相关文档（如 README、CHANGELOG）

## 代码规范

### Python 后端

项目使用以下工具进行代码规范管理：

- **Black** - 代码格式化
- **isort** - 导入排序
- **flake8** - 代码检查
- **pytest** - 单元测试

**代码规范：**
- 使用 4 空格缩进
- 变量和函数使用 snake_case
- 类名使用 PascalCase
- 常量使用 UPPER_SNAKE_CASE
- 函数和类需要 docstring 说明
- 类型注解（Type Hints）是推荐的

**运行代码检查：**
```bash
# 格式化代码
black .
isort .

# 代码检查
flake8 .

# 运行测试
pytest server/tests/ -v
```

### Vue 前端

项目使用以下工具进行代码规范管理：

- **Prettier** - 代码格式化
- **ESLint** - 代码检查
- **TypeScript** - 类型系统

**代码规范：**
- 使用 2 空格缩进
- 组件名使用 PascalCase
- 变量和函数使用 camelCase
- 使用 TypeScript 类型注解
- Vue 组件使用 `<script setup>` 语法

**运行代码检查：**
```bash
cd frontend

# 安装依赖
npm install

# 格式化代码
npm run format

# 代码检查
npm run lint

# 运行开发服务器
npm run dev
```

## 代码风格指南

### Git 提交规范

我们遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**提交类型（type）：**
- `feat` - 新功能
- `fix` - Bug 修复
- `docs` - 文档更新
- `style` - 代码格式（不影响代码运行）
- `refactor` - 重构（既不是新增功能，也不是修改 bug）
- `perf` - 性能优化
- `test` - 增加测试
- `chore` - 构建过程或辅助工具的变动
- `ci` - CI/CD 配置变更
- `revert` - 回退提交

**示例：**
```
feat(auth): add user registration with email verification

- Implement registration form with validation
- Add email verification flow
- Update API documentation

Closes #123
```

**提交规范：**
- 标题不超过 72 个字符
- 使用中文或英文均可，但要保持一致
- 标题使用祈使句（"添加" 而不是 "添加了"）
- 正文详细说明改动的原因和内容
- 关联相关 Issue（如 `Closes #123`、`Fixes #456`）

### 命名约定

#### Python 后端
```python
# 变量名 - snake_case
user_name = "John"
max_retries = 3

# 函数名 - snake_case，动词开头
def get_user_by_id(user_id: int) -> User:
    """根据 ID 获取用户信息"""
    pass

def calculate_portfolio_value(portfolio: Portfolio) -> float:
    """计算投资组合价值"""
    pass

# 类名 - PascalCase
class UserService:
    """用户服务类"""
    pass

class TradingStrategy:
    """交易策略基类"""
    pass

# 常量 - UPPER_SNAKE_CASE
MAX_RETRY_COUNT = 3
DEFAULT_TIMEOUT = 30
API_BASE_URL = "https://api.example.com"

# 私有变量/方法 - 下划线前缀
class User:
    def __init__(self):
        self._internal_state = {}
    
    def _validate_input(self, data):
        """内部验证方法"""
        pass
```

#### Vue 前端
```typescript
// 组件名 - PascalCase，多单词
const UserProfile = defineComponent({ ... })
const TradingDashboard = defineComponent({ ... })

// 组合式函数 - camelCase，use 开头
const useUserStore = defineStore('user', () => { ... })
const useTradingData = () => { ... }

// 变量/函数 - camelCase
const userName = ref('John')
const fetchUserData = async () => { ... }

// 常量 - UPPER_SNAKE_CASE
const MAX_RETRIES = 3
const API_BASE_URL = import.meta.env.VITE_API_URL

// Props - camelCase
defineProps<{
  userId: number
  isLoading: boolean
}>()

// Emits - kebab-case（模板中），camelCase（脚本中）
const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'user-updated', user: User): void
}>()
```

#### 文件命名
```
# Python 文件 - snake_case
user_service.py
trading_strategy.py
__init__.py

# Vue 组件 - PascalCase
UserProfile.vue
TradingDashboard.vue
ApiClient.ts

# 工具函数 - camelCase
formatDate.ts
calculateStats.ts

# 样式文件 - kebab-case
user-profile.css
trading-dashboard.scss
```

### 注释规范

#### Python Docstring
使用 Google 风格的 docstring：

```python
def fetch_market_data(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """获取指定时间范围内的市场数据

    Args:
        symbol: 交易对符号，如 'BTC/USDT'
        start_date: 开始日期，格式 'YYYY-MM-DD'
        end_date: 结束日期，格式 'YYYY-MM-DD'

    Returns:
        包含 OHLCV 数据的 DataFrame，列为：
        - timestamp: 时间戳
        - open: 开盘价
        - high: 最高价
        - low: 最低价
        - close: 收盘价
        - volume: 成交量

    Raises:
        ValueError: 日期格式不正确
        APIError: API 请求失败

    Example:
        >>> df = fetch_market_data('BTC/USDT', '2024-01-01', '2024-01-31')
        >>> print(df.head())
    """
    pass
```

#### JavaScript/TypeScript 注释
使用 JSDoc 风格：

```typescript
/**
 * 计算投资组合的总价值
 * @param holdings - 持仓列表，每个包含 symbol 和 amount
 * @param prices - 当前价格映射
 * @returns 投资组合总价值
 * @example
 * const value = calculatePortfolioValue(
 *   [{ symbol: 'BTC', amount: 1 }],
 *   { BTC: 50000 }
 * )
 */
function calculatePortfolioValue(
  holdings: Holding[],
  prices: Record<string, number>
): number {
  return holdings.reduce((total, h) => {
    return total + (prices[h.symbol] || 0) * h.amount
  }, 0)
}
```

#### 行内注释
```python
# ✅ 好的注释 - 解释为什么这样做
# 使用缓存避免重复计算，提升性能 30%+
result = expensive_calculation(data)

# ❌ 不好的注释 - 重复代码内容
# 计算结果
result = calculate(data)
```

```typescript
// ✅ 好的注释
// 防抖 300ms，避免频繁触发 API 请求
const debouncedSearch = useDebounce(searchQuery, 300)

// ❌ 不好的注释
// 定义防抖搜索
const debouncedSearch = useDebounce(searchQuery, 300)
```

### API 设计规范

#### REST API 规范
```python
# ✅ 好的 API 设计
# GET    /api/users          # 获取用户列表
# GET    /api/users/:id      # 获取单个用户
# POST   /api/users          # 创建用户
# PUT    /api/users/:id      # 更新用户
# DELETE /api/users/:id      # 删除用户

# ✅ 统一响应格式
{
  "code": 0,              # 0 表示成功，非 0 表示错误
  "message": "success",   # 提示信息
  "data": { ... },        # 响应数据
  "timestamp": 1234567890 # 时间戳
}

# ✅ 分页格式
{
  "code": 0,
  "data": {
    "items": [...],       # 数据列表
    "total": 100,         # 总数
    "page": 1,            # 当前页码
    "page_size": 20       # 每页数量
  }
}
```

#### 错误处理
```python
# ✅ 统一错误码
{
  "code": 40001,           # 错误码
  "message": "参数错误",    # 错误信息
  "details": {             # 详细错误信息（可选）
    "field": "email",
    "error": "邮箱格式不正确"
  }
}
```

### 错误处理规范

#### Python 后端
```python
# ✅ 使用自定义异常
class APIError(Exception):
    """API 调用异常"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

# ✅ 捕获具体异常
try:
    result = api_client.fetch_data()
except ConnectionError as e:
    logger.error(f"连接失败: {e}")
    raise APIError("无法连接到服务器", status_code=503)
except TimeoutError as e:
    logger.error(f"请求超时: {e}")
    raise APIError("请求超时，请稍后重试", status_code=504)

# ❌ 不要捕获所有异常
try:
    result = api_client.fetch_data()
except Exception as e:  # 太宽泛
    pass
```

#### 前端错误处理
```typescript
// ✅ 使用 try-catch 处理异步操作
const fetchData = async () => {
  try {
    isLoading.value = true
    const response = await api.get('/users')
    users.value = response.data
  } catch (error) {
    console.error('获取用户数据失败:', error)
    showError('获取数据失败，请稍后重试')
  } finally {
    isLoading.value = false
  }
}

// ✅ 统一错误处理
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // 未授权，跳转到登录页
      router.push('/login')
    }
    return Promise.reject(error)
  }
)
```

### 导入排序规范

#### Python（isort 配置）
```python
# 1. 标准库
import os
import sys
from datetime import datetime

# 2. 第三方库
import pandas as pd
from flask import Flask, request

# 3. 本地库
from server.models import User
from server.utils import format_date
```

#### JavaScript/TypeScript
```typescript
// 1. 第三方库
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

// 2. 本地组件
import UserProfile from '@/components/UserProfile.vue'
import TradingChart from '@/components/TradingChart.vue'

// 3. 工具函数和类型
import { formatNumber } from '@/utils/format'
import type { User, Portfolio } from '@/types'

// 4. 样式
import '@/styles/main.css'
```

## 开发环境

### 后端开发

1. **克隆仓库**
   ```bash
   git clone https://github.com/lccuhk/ai-trader-customization.git
   cd ai-trader-customization
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，填入必要的配置
   ```

5. **初始化数据库**
   ```bash
   python server/migrate_data.py
   ```

6. **启动开发服务器**
   ```bash
   python server/app.py
   ```

   服务器将在 `http://localhost:5000` 运行

### 前端开发

1. **进入前端目录**
   ```bash
   cd frontend
   ```

2. **安装依赖**
   ```bash
   npm install
   ```

3. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，填入必要的配置
   ```

4. **启动开发服务器**
   ```bash
   npm run dev
   ```

   前端将在 `http://localhost:5173` 运行

## 测试指南

### 后端测试

```bash
# 运行所有测试
pytest server/tests/ -v

# 运行特定测试文件
pytest server/tests/test_auth.py -v

# 生成覆盖率报告
pytest server/tests/ --cov=server --cov-report=html
```

### 前端测试

```bash
cd frontend

# 运行单元测试
npm run test:unit

# 运行端到端测试
npm run test:e2e
```

## 问题？

如果您在贡献过程中遇到任何问题，欢迎通过以下方式联系我们：

- 提交 [Issue](https://github.com/lccuhk/ai-trader-customization/issues)
- 查看 [README.md](README.md) 了解更多项目信息
- 查看 [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) 了解部署指南

再次感谢您的贡献！🎉
