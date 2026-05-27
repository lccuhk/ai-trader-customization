#!/bin/bash

set -e

echo "=========================================="
echo "  AI-Trader Backend Deployment to Deta Space"
echo "=========================================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
BIN_DIR="$PROJECT_ROOT/bin"

export PATH="$BIN_DIR:$PATH"

if ! command -v space &> /dev/null; then
    echo "📦 space CLI 未找到，正在安装..."
    
    mkdir -p "$BIN_DIR"
    
    ARCH="$(uname -m)"
    if [ "$ARCH" = "arm64" ]; then
        ASSET="space-darwin-arm64.zip"
    elif [ "$ARCH" = "x86_64" ]; then
        ASSET="space-darwin-x86_64.zip"
    else
        ASSET="space-linux-amd64.zip"
    fi
    
    echo "📥 下载 $ASSET..."
    cd /tmp && curl -L "https://github.com/deta/space-cli/releases/download/v0.4.2/$ASSET" -o space.zip
    unzip -o space.zip
    cp space "$BIN_DIR/"
    chmod +x "$BIN_DIR/space"
    
    echo "✅ space CLI 已安装到 $BIN_DIR/space"
    echo ""
fi

echo "✅ Deta Space CLI 已安装: $(space version)"
echo ""

echo "🔐 请登录 Deta Space..."
echo "   请在浏览器中打开以下链接并登录："
space login
echo ""

echo "✅ 登录成功！"
echo ""

if [ ! -f ".space" ]; then
    echo "🚀 初始化 Deta Space 项目..."
    space new --name trading-agent-backend
    echo ""
fi

mkdir -p data

if [ -f "data/clawtrader.db" ]; then
    echo "📋 使用现有数据库"
else
    echo "🆕 创建新数据库"
fi

echo ""
echo "📤 正在部署到 Deta Space..."
echo ""

space push

echo ""
echo "🎉 部署完成！"
echo ""
echo "📱 访问以下地址查看你的应用："
echo "   请登录 https://deta.space 查看你的应用"
echo ""
echo "📝 部署完成后，请更新前端代码中的 API 地址"
echo ""
