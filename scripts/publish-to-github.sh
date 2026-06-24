#!/bin/bash
# GitHub 快速发布脚本
#
# 使用方法:
#   1. 编辑此脚本，将 YOUR_USERNAME 替换为你的 GitHub 用户名
#   2. 运行: chmod +x publish-to-github.sh
#   3. 运行: ./publish-to-github.sh

# ========================================
# 配置部分 - 请修改以下变量
# ========================================

# 你的 GitHub 用户名
GITHUB_USERNAME="YOUR_USERNAME"

# 仓库名称
REPO_NAME="payguard-crew"

# ========================================
# 以下内容无需修改
# ========================================

echo "=========================================="
echo "🚀 开始发布到 GitHub"
echo "=========================================="
echo ""

# 检查是否已配置用户名
if [ "$GITHUB_USERNAME" = "YOUR_USERNAME" ]; then
    echo "❌ 错误: 请先编辑脚本，将 YOUR_USERNAME 替换为你的 GitHub 用户名"
    echo ""
    echo "编辑命令:"
    echo "  nano publish-to-github.sh"
    echo "  或"
    echo "  vim publish-to-github.sh"
    exit 1
fi

# 检查是否已有远程仓库
if git remote | grep -q "origin"; then
    echo "⚠️  检测到已存在 origin 远程仓库"
    echo "当前远程仓库:"
    git remote -v
    echo ""
    read -p "是否删除并重新添加? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git remote remove origin
        echo "✅ 已删除旧的 origin"
    else
        echo "❌ 取消操作"
        exit 1
    fi
fi

# 添加远程仓库
echo "📡 添加远程仓库..."
REPO_URL="https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"
git remote add origin "$REPO_URL"

if [ $? -eq 0 ]; then
    echo "✅ 远程仓库添加成功: $REPO_URL"
else
    echo "❌ 添加远程仓库失败"
    exit 1
fi

echo ""
echo "🚀 推送代码到 GitHub..."
echo ""

# 推送到 main 分支
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "🎉 发布成功！"
    echo "=========================================="
    echo ""
    echo "📍 你的仓库地址:"
    echo "   https://github.com/${GITHUB_USERNAME}/${REPO_NAME}"
    echo ""
    echo "🌐 在浏览器中打开:"
    echo "   open https://github.com/${GITHUB_USERNAME}/${REPO_NAME}"
    echo ""
    echo "📋 后续步骤:"
    echo "   1. 在 GitHub 上设置仓库描述和 Topics"
    echo "   2. 查看 PUBLISH_NEXT_STEPS.md 了解更多"
    echo ""
else
    echo ""
    echo "=========================================="
    echo "❌ 推送失败"
    echo "=========================================="
    echo ""
    echo "可能的原因:"
    echo "  1. GitHub 仓库尚未创建"
    echo "  2. 用户名或仓库名错误"
    echo "  3. 没有推送权限"
    echo ""
    echo "解决方法:"
    echo "  1. 访问 https://github.com/new 创建仓库"
    echo "  2. 检查用户名和仓库名是否正确"
    echo "  3. 检查 Git 凭据配置"
    echo ""
    exit 1
fi
