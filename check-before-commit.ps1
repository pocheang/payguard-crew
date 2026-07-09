# PayGuard GitHub 提交安全检查脚本 (PowerShell)

Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                           ║" -ForegroundColor Cyan
Write-Host "║          🔒 GitHub 提交安全检查                            ║" -ForegroundColor Cyan
Write-Host "║                                                           ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$issuesFound = 0

# 检查 .env 文件
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "1. 检查环境变量文件" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

$envFiles = git status --short | Select-String -Pattern '\.env$|\.env\.local|\.env\.production' | Where-Object { $_ -notmatch '\.example' }
if ($envFiles) {
    Write-Host "❌ 发现 .env 文件在暂存区！" -ForegroundColor Red
    Write-Host "   以下文件不应提交："
    $envFiles
    $issuesFound++
} else {
    Write-Host "✓ 未发现 .env 文件" -ForegroundColor Green
}

# 检查数据库文件
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "2. 检查数据库文件" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

$dbFiles = git status --short | Select-String -Pattern '\.db$|\.sqlite'
if ($dbFiles) {
    Write-Host "❌ 发现数据库文件在暂存区！" -ForegroundColor Red
    $dbFiles
    $issuesFound++
} else {
    Write-Host "✓ 未发现数据库文件" -ForegroundColor Green
}

# 检查日志文件
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "3. 检查日志文件" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

$logFiles = git status --short | Select-String -Pattern '\.log$|logs/'
if ($logFiles) {
    Write-Host "⚠️  发现日志文件在暂存区" -ForegroundColor Yellow
    $logFiles
    Write-Host "   建议：日志文件通常不应提交"
}

# 检查 node_modules
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "4. 检查 node_modules" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

$nodeModules = git status --short | Select-String -Pattern 'node_modules'
if ($nodeModules) {
    Write-Host "❌ node_modules 在暂存区！" -ForegroundColor Red
    Write-Host "   这会导致仓库体积巨大"
    $issuesFound++
} else {
    Write-Host "✓ node_modules 未被追踪" -ForegroundColor Green
}

# 扫描敏感关键词
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "5. 扫描敏感关键词" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

$keywords = @('api_key', 'api-key', 'apikey', 'secret', 'password', 'passwd', 'token', 'auth_token', 'private_key', 'sk-[a-zA-Z0-9]{32,}')
$foundSensitive = $false

foreach ($keyword in $keywords) {
    $matches = git diff --cached | Select-String -Pattern $keyword -CaseSensitive:$false | Where-Object { $_ -notmatch '\.example|your-.*-here|GITHUB_GUIDE' }
    if ($matches) {
        if (-not $foundSensitive) {
            Write-Host "❌ 发现可能的敏感信息：" -ForegroundColor Red
            $foundSensitive = $true
            $issuesFound++
        }
        Write-Host "   关键词: $keyword" -ForegroundColor Yellow
    }
}

if (-not $foundSensitive) {
    Write-Host "✓ 未发现敏感关键词" -ForegroundColor Green
}

# 总结
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "检查完成" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

if ($issuesFound -eq 0) {
    Write-Host "✓ 安全检查通过！可以提交到 GitHub" -ForegroundColor Green
    Write-Host ""
    Write-Host "建议的提交命令："
    Write-Host "  git commit -m `"your commit message`""
    Write-Host "  git push origin main"
    exit 0
} else {
    Write-Host "✗ 发现 $issuesFound 个问题，请修复后再提交" -ForegroundColor Red
    Write-Host ""
    Write-Host "修复建议："
    Write-Host "  1. 移除敏感文件：git reset HEAD <file>"
    Write-Host "  2. 添加到 .gitignore"
    Write-Host "  3. 使用环境变量替代硬编码密钥"
    Write-Host ""
    exit 1
}
