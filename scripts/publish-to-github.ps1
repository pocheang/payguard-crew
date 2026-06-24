# GitHub 快速发布脚本（PowerShell 版本）
#
# 使用方法:
#   1. 编辑此脚本，将 YOUR_USERNAME 替换为你的 GitHub 用户名
#   2. 运行: .\scripts\publish-to-github.ps1

# ========================================
# 配置部分 - 请修改以下变量
# ========================================

$GITHUB_USERNAME = "YOUR_USERNAME"
$REPO_NAME = "payguard-crew"

# ========================================
# 以下内容无需修改
# ========================================

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🚀 开始发布到 GitHub" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 检查是否已配置用户名
if ($GITHUB_USERNAME -eq "YOUR_USERNAME") {
    Write-Host "❌ 错误: 请先编辑脚本，将 YOUR_USERNAME 替换为你的 GitHub 用户名" -ForegroundColor Red
    Write-Host ""
    Write-Host "编辑方法:" -ForegroundColor Yellow
    Write-Host "  1. 右键点击 publish-to-github.ps1" -ForegroundColor White
    Write-Host "  2. 选择 '编辑'" -ForegroundColor White
    Write-Host "  3. 修改第 8 行的 YOUR_USERNAME" -ForegroundColor White
    exit 1
}

# 检查是否已有远程仓库
$hasOrigin = git remote | Select-String "origin"

if ($hasOrigin) {
    Write-Host "⚠️  检测到已存在 origin 远程仓库" -ForegroundColor Yellow
    Write-Host "当前远程仓库:" -ForegroundColor Yellow
    git remote -v
    Write-Host ""

    $response = Read-Host "是否删除并重新添加? (y/n)"
    if ($response -eq "y" -or $response -eq "Y") {
        git remote remove origin
        Write-Host "✅ 已删除旧的 origin" -ForegroundColor Green
    }
    else {
        Write-Host "❌ 取消操作" -ForegroundColor Red
        exit 1
    }
}

# 添加远程仓库
Write-Host "📡 添加远程仓库..." -ForegroundColor Yellow
$REPO_URL = "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"

try {
    git remote add origin $REPO_URL
    Write-Host "✅ 远程仓库添加成功: $REPO_URL" -ForegroundColor Green
}
catch {
    Write-Host "❌ 添加远程仓库失败" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🚀 推送代码到 GitHub..." -ForegroundColor Yellow
Write-Host ""

# 推送到 main 分支
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "🎉 发布成功！" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📍 你的仓库地址:" -ForegroundColor Yellow
    Write-Host "   https://github.com/$GITHUB_USERNAME/$REPO_NAME" -ForegroundColor White
    Write-Host ""
    Write-Host "🌐 在浏览器中打开:" -ForegroundColor Yellow
    Write-Host "   Start-Process https://github.com/$GITHUB_USERNAME/$REPO_NAME" -ForegroundColor White
    Write-Host ""
    Write-Host "📋 后续步骤:" -ForegroundColor Yellow
    Write-Host "   1. 在 GitHub 上设置仓库描述和 Topics" -ForegroundColor White
    Write-Host "   2. 查看 PUBLISH_NEXT_STEPS.md 了解更多" -ForegroundColor White
    Write-Host ""
}
else {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "❌ 推送失败" -ForegroundColor Red
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "可能的原因:" -ForegroundColor Yellow
    Write-Host "  1. GitHub 仓库尚未创建" -ForegroundColor White
    Write-Host "  2. 用户名或仓库名错误" -ForegroundColor White
    Write-Host "  3. 没有推送权限" -ForegroundColor White
    Write-Host ""
    Write-Host "解决方法:" -ForegroundColor Yellow
    Write-Host "  1. 访问 https://github.com/new 创建仓库" -ForegroundColor White
    Write-Host "  2. 检查用户名和仓库名是否正确" -ForegroundColor White
    Write-Host "  3. 检查 Git 凭据配置" -ForegroundColor White
    Write-Host ""
    exit 1
}
