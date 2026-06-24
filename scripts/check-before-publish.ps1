# GitHub 发布前检查脚本（PowerShell 版本）
# 用于检查是否有不应该上传的敏感文件

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🔍 GitHub 发布前安全检查" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$ERRORS = 0
$WARNINGS = 0

# 1. 检查敏感文件
Write-Host "1️⃣ 检查敏感文件..." -ForegroundColor Yellow
Write-Host ""

if (Test-Path ".env") {
    Write-Host "❌ 发现 .env 文件 - 不应上传！" -ForegroundColor Red
    $ERRORS++
} else {
    Write-Host "✅ 未发现 .env 文件" -ForegroundColor Green
}

if (Test-Path ".env.example") {
    Write-Host "✅ .env.example 存在" -ForegroundColor Green
} else {
    Write-Host "⚠️  .env.example 不存在 - 建议创建" -ForegroundColor Yellow
    $WARNINGS++
}

# 2. 检查数据库文件
Write-Host ""
Write-Host "2️⃣ 检查数据库文件..." -ForegroundColor Yellow
Write-Host ""

$dbFiles = @(Get-ChildItem -Path . -Filter "*.db" -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.FullName -notlike "*\.git\*" })
if ($dbFiles.Count -gt 0) {
    Write-Host "❌ 发现 $($dbFiles.Count) 个数据库文件：" -ForegroundColor Red
    foreach ($file in $dbFiles) {
        Write-Host "   - $($file.FullName)" -ForegroundColor Red
    }
    $ERRORS++
} else {
    Write-Host "✅ 未发现数据库文件" -ForegroundColor Green
}

# 3. 检查日志文件
Write-Host ""
Write-Host "3️⃣ 检查日志文件..." -ForegroundColor Yellow
Write-Host ""

$logFiles = @(Get-ChildItem -Path . -Filter "*.log" -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.FullName -notlike "*\.git\*" })
if ($logFiles.Count -gt 0) {
    Write-Host "⚠️  发现 $($logFiles.Count) 个日志文件：" -ForegroundColor Yellow
    foreach ($file in $logFiles) {
        Write-Host "   - $($file.FullName)" -ForegroundColor Yellow
    }
    $WARNINGS++
} else {
    Write-Host "✅ 未发现日志文件" -ForegroundColor Green
}

# 4. 检查 ChromaDB
Write-Host ""
Write-Host "4️⃣ 检查 ChromaDB 向量库..." -ForegroundColor Yellow
Write-Host ""

if (Test-Path ".chroma") {
    Write-Host "⚠️  发现 .chroma 目录" -ForegroundColor Yellow
    $WARNINGS++
} else {
    Write-Host "✅ 未发现 .chroma 目录" -ForegroundColor Green
}

# 5. 检查缓存
Write-Host ""
Write-Host "5️⃣ 检查 __pycache__ 缓存..." -ForegroundColor Yellow
Write-Host ""

$cacheDirs = @(Get-ChildItem -Path . -Filter "__pycache__" -Directory -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.FullName -notlike "*\.git\*" })
if ($cacheDirs.Count -gt 0) {
    Write-Host "⚠️  发现 $($cacheDirs.Count) 个 __pycache__ 目录" -ForegroundColor Yellow
    $WARNINGS++
} else {
    Write-Host "✅ 未发现 __pycache__ 目录" -ForegroundColor Green
}

# 6. 检查 .gitignore
Write-Host ""
Write-Host "6️⃣ 检查 .gitignore..." -ForegroundColor Yellow
Write-Host ""

if (Test-Path ".gitignore") {
    Write-Host "✅ .gitignore 存在" -ForegroundColor Green
} else {
    Write-Host "❌ .gitignore 不存在！" -ForegroundColor Red
    $ERRORS++
}

# 显示结果
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "📊 检查结果" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

if ($ERRORS -eq 0 -and $WARNINGS -eq 0) {
    Write-Host "✅ 所有检查通过！可以安全发布到 GitHub" -ForegroundColor Green
    Write-Host ""
    exit 0
} elseif ($ERRORS -eq 0) {
    Write-Host "⚠️  发现 $WARNINGS 个警告" -ForegroundColor Yellow
    Write-Host "建议清理后再发布" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "清理命令：" -ForegroundColor Yellow
    Write-Host "  Remove-Item -Recurse -Force .chroma" -ForegroundColor White
    Write-Host "  Get-ChildItem -Directory -Recurse -Filter '__pycache__' | Remove-Item -Recurse -Force" -ForegroundColor White
    Write-Host "  Remove-Item logs\*.log -Force" -ForegroundColor White
    Write-Host ""
    exit 1
} else {
    Write-Host "❌ 发现 $ERRORS 个错误和 $WARNINGS 个警告" -ForegroundColor Red
    Write-Host "请修复错误后再发布！" -ForegroundColor Red
    Write-Host ""
    Write-Host "修复建议：" -ForegroundColor Yellow
    Write-Host "  1. 删除 .env 文件（或将其添加到 .gitignore）" -ForegroundColor White
    Write-Host "  2. 删除所有 .db 文件" -ForegroundColor White
    Write-Host "  3. 检查并移除真实的 API Key" -ForegroundColor White
    Write-Host "  4. 创建 .env.example 模板文件" -ForegroundColor White
    Write-Host ""
    exit 1
}
