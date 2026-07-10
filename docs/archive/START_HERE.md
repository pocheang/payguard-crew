# PayGuard Crew - 立即启动

## 问题说明

你的电脑上有两个Python环境：
- Anaconda Python（已安装所有依赖）✅
- Python 3.13（缺少email-validator）❌

## 解决方案

### 方式1：使用start_server.bat（推荐）

1. 打开命令提示符（CMD）
2. 运行：
```
cd c:\Users\pocheang\Downloads\payguard_crew_starter\payguard_crew_starter
start_server.bat
```

### 方式2：手动启动

1. 打开命令提示符（CMD）
2. 运行以下命令：

```bash
cd c:\Users\pocheang\Downloads\payguard_crew_starter\payguard_crew_starter
pip install email-validator
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

3. 看到 "Application startup complete" 后
4. 打开浏览器：http://127.0.0.1:8000/docs

---

## 一键测试

启动后，在浏览器中：

1. 访问：http://127.0.0.1:8000/docs
2. 找到：`POST /api/audit/transaction`
3. 点击 "Try it out"
4. 使用这个数据：

```json
{
  "transaction_id": "DEMO_001",
  "user_id": "USER_001",  
  "merchant_id": "MERCHANT_001",
  "amount": 500,
  "currency": "USD",
  "account_age_days": 365,
  "transaction_frequency_1h": 1,
  "ip_location_status": "normal",
  "device_status": "normal",
  "kyc_status": "verified",
  "merchant_risk_level": "low",
  "is_blacklisted": false,
  "timestamp": "2026-07-07T10:00:00"
}
```

5. 添加 Header：`x-api-key: demo-test-key-12345`
6. 点击 Execute
7. 查看结果！

---

## 已准备好的功能

✅ 服务器配置完成
✅ 数据库已初始化（payguard_crew.db）
✅ 环境配置完成（.env）
✅ 测试数据准备好
✅ Demo脚本可用（run_demo.py）
✅ 完整API文档

---

## 其他启动方式

### 使用Python脚本测试
```bash
python run_demo.py
```

### 查看健康状态
```bash
curl http://127.0.0.1:8000/api/health/health
```

---

**一切都准备好了！只需要启动服务器即可。**
