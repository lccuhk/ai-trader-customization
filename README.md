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

### 3. 配置环境