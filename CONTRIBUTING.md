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
