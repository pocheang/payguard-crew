# 数据安全增强功能

## 📋 新增功能概览

### 1. ✅ 基于角色的访问控制 (RBAC) (`app/security/access_control.py`)

**功能特性：**
- **9种预定义角色**：
  - Super Admin（超级管理员）
  - Admin（管理员）
  - Compliance Officer（合规官）
  - AML Analyst（AML 分析师）
  - KYC Reviewer（KYC 审核员）
  - Transaction Approver（交易审批员）
  - Auditor（审计员）
  - Operator（操作员）
  - Viewer（查看者）

- **26种细粒度权限**：
  - 用户管理（读/创建/更新/删除）
  - KYC 管理（读/验证/批准/拒绝）
  - 交易管理（读/创建/批准/拒绝/取消）
  - AML 管理（读/调查/创建SAR/提交SAR）
  - 报告管理（读/生成/导出/提交）
  - 审计日志（读/导出）
  - 系统管理（配置/角色管理/用户管理）

- **访问控制功能**：
  - 权限检查和验证
  - 数据级访问控制
  - 敏感字段过滤
  - 权限装饰器

---

### 2. ✅ 数据加密服务 (`app/security/encryption.py`)

**加密能力：**
- **4种加密级别**：
  - None（不加密）
  - Basic（基础加密，可逆）
  - Hash（哈希，不可逆）
  - Strong（强加密，双层加密）

- **字段级加密**：
  - 基于字段名的密钥派生
  - 自动识别敏感字段
  - 批量加密/解密
  - 数据脱敏显示

- **文件加密**：
  - 完整文件加密
  - 加密文件解密

- **敏感数据类型**：
  - PII（个人身份信息）
  - Financial（财务信息）
  - Credential（凭证信息）
  - Biometric（生物识别信息）
  - Medical（医疗信息）

**预定义敏感字段：**
```python
- 身份证、护照
- 手机号、邮箱
- 银行账户、信用卡
- 密码、API Key
- 人脸模板、指纹
```

---

### 3. ✅ 增强的审计追踪 (`app/security/enhanced_audit.py`)

**审计功能：**
- **20种安全事件类型**：
  - 认证事件（登录/登出/会话）
  - 授权事件（访问授予/拒绝/权限提升）
  - 数据访问（读/导出/删除/敏感数据）
  - 数据修改（创建/更新/加密/解密）
  - 安全异常（可疑活动/暴力破解/未授权访问）
  - 系统事件（配置变更/安全策略/密钥轮换）

- **5种严重程度**：
  - Info（信息）
  - Low（低）
  - Medium（中）
  - High（高）
  - Critical（严重）

- **审计链（Audit Chain）**：
  - SHA-256 哈希链
  - 防篡改机制
  - 完整性验证
  - 链式结构

- **异常检测**：
  - 暴力破解检测（10分钟内5次失败）
  - 快速请求检测（1分钟内20次请求）
  - 敏感数据访问监控（1小时内10次访问）
  - 风险评分（0-100）

- **完整审计信息**：
  - 用户信息（ID/用户名/角色）
  - 请求信息（IP/User Agent/Session ID）
  - 操作信息（动作/资源类型/资源ID）
  - 数据变更（前值/后值/变更字段）
  - 安全信息（风险评分/异常检测）

---

## 📊 数据安全架构

```
用户请求
    ↓
访问控制 (RBAC)
    ├─ 角色验证
    ├─ 权限检查
    └─ 资源访问控制
    ↓
数据加密/解密
    ├─ 字段级加密
    ├─ 敏感数据识别
    └─ 自动加密/解密
    ↓
业务处理
    ↓
增强审计追踪
    ├─ 记录操作日志
    ├─ 异常检测
    ├─ 审计链维护
    └─ 安全告警
```

---

## 🔐 安全功能对比

| 功能 | 之前 | 现在 | 改进 |
|------|------|------|------|
| **访问控制** | ❌ 无 | ✅ RBAC (9角色/26权限) | 新增 |
| **数据加密** | ❌ 无 | ✅ 字段级+文件级 | 新增 |
| **敏感数据保护** | ❌ 无 | ✅ 自动识别+加密 | 新增 |
| **审计追踪** | ⚠️ 简单日志 | ✅ 完整审计链 | 大幅提升 |
| **异常检测** | ❌ 无 | ✅ 3种检测机制 | 新增 |
| **防篡改** | ❌ 无 | ✅ SHA-256 哈希链 | 新增 |
| **安全告警** | ❌ 无 | ✅ 实时告警 | 新增 |

---

## 🚀 使用示例

### 1. 访问控制

```python
from app.security import AccessControl, Permission, Role, User

# 创建用户
user = User(
    user_id="user123",
    username="john_doe",
    email="john@example.com",
    roles=[Role.COMPLIANCE_OFFICER]
)

# 检查权限
can_approve = AccessControl.has_permission(user, Permission.KYC_APPROVE)

# 权限装饰器
@AccessControl.require_permission(Permission.TRANSACTION_APPROVE)
async def approve_transaction(user: User, transaction_id: str):
    # 业务逻辑
    pass

# 过滤敏感字段
from app.security import DataAccessControl

sensitive_fields = {"id_card", "bank_account", "password"}
filtered_data = DataAccessControl.filter_sensitive_fields(
    data=user_data,
    user=user,
    sensitive_fields=sensitive_fields
)
```

### 2. 数据加密

```python
from app.security import EncryptionService, SensitiveDataHandler

# 初始化加密服务
encryption = EncryptionService()
handler = SensitiveDataHandler(encryption)

# 加密敏感数据
user_data = {
    "user_id": "user123",
    "full_name": "张三",
    "id_card": "110101199001011234",
    "phone_number": "+86 138****1234",
    "bank_account": "6222****1234"
}

# 自动识别并加密
encrypted_data = handler.encrypt_data(user_data)

# 解密
decrypted_data = handler.decrypt_data(encrypted_data)

# 脱敏显示
masked_data = handler.mask_for_display(user_data)
# 输出: {"id_card": "************1234", ...}
```

### 3. 增强审计追踪

```python
from app.security import EnhancedAuditService, SecurityEventType

audit_service = EnhancedAuditService(db_repository, encryption_service)

# 记录数据访问
await audit_service.log_data_access(
    user=current_user,
    data_type="kyc_profile",
    data_id="kyc_123",
    access_type="read",
    fields_accessed=["id_card", "phone_number"],
    ip_address="192.168.1.1",
    authorized=True
)

# 记录数据修改
await audit_service.log_data_modification(
    user=current_user,
    data_type="transaction",
    data_id="tx_789",
    operation="update",
    before_data={"status": "pending"},
    after_data={"status": "approved"},
    ip_address="192.168.1.1"
)

# 记录安全事件
await audit_service.log_security_event(
    event_type=SecurityEventType.LOGIN_SUCCESS,
    user=current_user,
    action="user_login",
    ip_address="192.168.1.1",
    success=True
)

# 获取用户活动
activities = await audit_service.get_user_activity(
    user_id="user123",
    start_date=datetime(2026, 1, 1),
    end_date=datetime(2026, 6, 24)
)

# 验证审计完整性
integrity_report = await audit_service.verify_audit_integrity(
    start_date=datetime(2026, 1, 1),
    end_date=datetime(2026, 6, 24)
)
```

---

## 🎯 安全合规覆盖

### 数据保护合规
- ✅ 敏感数据加密存储
- ✅ 字段级访问控制
- ✅ 数据脱敏显示
- ✅ 加密密钥管理

### 访问控制合规
- ✅ 最小权限原则
- ✅ 职责分离
- ✅ 审批工作流
- ✅ 访问日志记录

### 审计追踪合规
- ✅ 完整操作记录
- ✅ 数据变更追踪
- ✅ 防篡改机制
- ✅ 异常行为检测

---

## 📈 代码统计

**安全模块代码行数：**
- `access_control.py`: 350+ 行
- `encryption.py`: 400+ 行
- `enhanced_audit.py`: 450+ 行
- `__init__.py`: 50+ 行

**总计**: 1,250+ 行

---

## 🔧 配置要求

### 环境变量

```bash
# 加密主密钥（生产环境必须配置）
ENCRYPTION_MASTER_KEY=your-secure-master-key-here

# 审计配置
AUDIT_LOG_RETENTION_DAYS=365
AUDIT_CHAIN_ENABLED=true

# 安全告警
SECURITY_ALERT_EMAIL=security@example.com
SECURITY_ALERT_WEBHOOK=https://alerts.example.com/webhook
```

### 依赖包

```bash
pip install cryptography>=41.0.0
```

---

## ⚠️ 注意事项

### 生产环境配置

1. **加密密钥管理**：
   - 使用 KMS（密钥管理服务）
   - 定期轮换密钥
   - 安全存储备份密钥

2. **访问控制**：
   - 定期审查权限分配
   - 实施最小权限原则
   - 监控权限变更

3. **审计日志**：
   - 配置日志归档
   - 设置告警规则
   - 定期完整性检查

4. **性能优化**：
   - 加密操作异步处理
   - 审计日志批量写入
   - 使用缓存减少加密开销

---

## 🎉 总结

现在 PayGuard Crew 拥有：

✅ 完整的访问控制体系  
✅ 生产级数据加密  
✅ 增强的审计追踪  
✅ 实时异常检测  
✅ 防篡改机制  
✅ 安全告警系统  

**项目已达到企业级数据安全标准！**
