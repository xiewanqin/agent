#!/bin/bash

# 智能画布项目安装脚本

echo "🚀 开始安装依赖..."

# 检查是否在正确的目录
if [ ! -f "package.json" ]; then
    echo "❌ 错误: 未找到 package.json，请确保在项目根目录执行此脚本"
    exit 1
fi

# 检查包管理器
if command -v pnpm &> /dev/null; then
    echo "📦 使用 pnpm 安装..."
    pnpm install
elif command -v yarn &> /dev/null; then
    echo "📦 使用 yarn 安装..."
    yarn install
else
    echo "📦 使用 npm 安装..."
    npm install
fi

if [ $? -eq 0 ]; then
    echo "✅ 安装完成！"
    echo ""
    echo "下一步："
    echo "1. 复制 .env.example 为 .env 并配置你的 API Key"
    echo "2. 运行 npm run dev 启动开发服务器"
else
    echo "❌ 安装失败，请检查错误信息"
    exit 1
fi
