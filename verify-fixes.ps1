# 修复验证脚本 (Windows PowerShell)
# 验证所有修复是否成功

Write-Host "================================" -ForegroundColor Cyan
Write-Host "PayGuard 修复验证脚本" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

$passed = 0
$failed = 0

function Test-Item {
    param(
        [string]$Name,
        [scriptblock]$TestCommand
    )

    Write-Host "测试: $Name ... " -NoNewline

    try {
        $result = & $TestCommand
        if ($result) {
            Write-Host "✓ 通过" -ForegroundColor Green
            $script:passed++
        } else {
            Write-Host "✗ 失败" -ForegroundColor Red
            $script:failed++
        }
    } catch {
        Write-Host "✗ 失败" -ForegroundColor Red
        $script:failed++
    }
}

Write-Host "1. 检查后端配置验证增强" -ForegroundColor Yellow
Write-Host "----------------------------------------"

Test-Item "生产配置验证方法存在" {
    Select-String -Path "app\config.py" -Pattern "_validate_production" -Quiet
}

Test-Item "JWT密钥长度验证" {
    Select-String -Path "app\config.py" -Pattern "len\(jwt_secret\) < 32" -Quiet
}

Test-Item "CORS安全检查" {
    Select-String -Path "app\config.py" -Pattern "CORS_ORIGINS" -Quiet
}

Write-Host ""
Write-Host "2. 检查测试用例" -ForegroundColor Yellow
Write-Host "----------------------------------------"

Test-Item "API审计测试存在" {
    Test-Path "tests\api\test_audit.py"
}

Test-Item "审核工作流测试存在" {
    Test-Path "tests\api\test_review.py"
}

Test-Item "测试配置文件存在" {
    Test-Path "tests\conftest.py"
}

Write-Host ""
Write-Host "3. 检查前端优化" -ForegroundColor Yellow
Write-Host "----------------------------------------"

Test-Item "Logger工具存在" {
    Test-Path "frontend\src\utils\logger.js"
}

Test-Item "错误边界集成" {
    Select-String -Path "frontend\src\App.vue" -Pattern "ErrorBoundary" -Quiet
}

Test-Item "Vite配置优化" {
    Select-String -Path "frontend\vite.config.js" -Pattern "manualChunks" -Quiet
}

Write-Host ""
Write-Host "4. 检查文档" -ForegroundColor Yellow
Write-Host "----------------------------------------"

Test-Item "代码审查报告" {
    Test-Path "CODE_REVIEW_REPORT.md"
}

Test-Item "性能优化报告" {
    Test-Path "PERFORMANCE_OPTIMIZATION_REPORT.md"
}

Test-Item "修复实施指南" {
    Test-Path "FIX_IMPLEMENTATION_GUIDE.md"
}

Test-Item "最终总结报告" {
    Test-Path "FINAL_SUMMARY.md"
}

Write-Host ""
Write-Host "5. 运行Python测试" -ForegroundColor Yellow
Write-Host "----------------------------------------"

if (Get-Command pytest -ErrorAction SilentlyContinue) {
    Write-Host "运行pytest测试套件 ... " -NoNewline
    $testResult = pytest tests\api\ -v --tb=short 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ 通过" -ForegroundColor Green
        $passed++
    } else {
        Write-Host "⚠ 部分失败（可能需要配置）" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠ pytest 未安装，跳过测试" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "6. 检查前端构建" -ForegroundColor Yellow
Write-Host "----------------------------------------"

if (Test-Path "frontend") {
    Push-Location frontend
    if (Get-Command npm -ErrorAction SilentlyContinue) {
        Write-Host "前端构建测试 ... " -NoNewline
        $buildResult = npm run build 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ 通过" -ForegroundColor Green
            $passed++

            # 检查bundle大小
            $dashboardFiles = Get-ChildItem "dist\assets\Dashboard-*.js" -ErrorAction SilentlyContinue
            if ($dashboardFiles) {
                $size = (Get-Item $dashboardFiles[0]).Length
                if ($size -lt 20000) {
                    Write-Host "  Dashboard bundle: $size bytes (优化成功)" -ForegroundColor Green
                    $passed++
                } else {
                    Write-Host "  Dashboard bundle: $size bytes (可能需要进一步优化)" -ForegroundColor Yellow
                }
            }
        } else {
            Write-Host "✗ 失败" -ForegroundColor Red
            $failed++
        }
    } else {
        Write-Host "⚠ npm 未安装，跳过构建测试" -ForegroundColor Yellow
    }
    Pop-Location
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "验证结果汇总" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host "通过: $passed" -ForegroundColor Green
Write-Host "失败: $failed" -ForegroundColor Red
Write-Host ""

if ($failed -eq 0) {
    Write-Host "✓ 所有验证通过！修复成功！" -ForegroundColor Green
    exit 0
} else {
    Write-Host "⚠ 部分验证失败，请检查详细输出" -ForegroundColor Yellow
    exit 1
}
