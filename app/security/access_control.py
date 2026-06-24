"""
基于角色的访问控制 (RBAC)
"""
from enum import Enum
from typing import List, Set, Optional, Dict
from pydantic import BaseModel
from datetime import datetime


class Permission(str, Enum):
    """权限枚举"""
    # 用户管理
    USER_READ = "user:read"
    USER_CREATE = "user:create"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"

    # KYC 管理
    KYC_READ = "kyc:read"
    KYC_VERIFY = "kyc:verify"
    KYC_APPROVE = "kyc:approve"
    KYC_REJECT = "kyc:reject"

    # 交易管理
    TRANSACTION_READ = "transaction:read"
    TRANSACTION_CREATE = "transaction:create"
    TRANSACTION_APPROVE = "transaction:approve"
    TRANSACTION_REJECT = "transaction:reject"
    TRANSACTION_CANCEL = "transaction:cancel"

    # AML 管理
    AML_READ = "aml:read"
    AML_INVESTIGATE = "aml:investigate"
    SAR_CREATE = "sar:create"
    SAR_FILE = "sar:file"

    # 报告管理
    REPORT_READ = "report:read"
    REPORT_GENERATE = "report:generate"
    REPORT_EXPORT = "report:export"
    REPORT_SUBMIT = "report:submit"

    # 审计日志
    AUDIT_READ = "audit:read"
    AUDIT_EXPORT = "audit:export"

    # 系统管理
    SYSTEM_CONFIG = "system:config"
    ROLE_MANAGE = "role:manage"
    USER_MANAGE = "user:manage"


class Role(str, Enum):
    """角色枚举"""
    SUPER_ADMIN = "super_admin"  # 超级管理员
    ADMIN = "admin"  # 管理员
    COMPLIANCE_OFFICER = "compliance_officer"  # 合规官
    AML_ANALYST = "aml_analyst"  # AML 分析师
    KYC_REVIEWER = "kyc_reviewer"  # KYC 审核员
    TRANSACTION_APPROVER = "transaction_approver"  # 交易审批员
    AUDITOR = "auditor"  # 审计员
    OPERATOR = "operator"  # 操作员
    VIEWER = "viewer"  # 查看者


class RolePermissions(BaseModel):
    """角色权限配置"""
    role: Role
    permissions: Set[Permission]
    description: str


# 角色权限映射
ROLE_PERMISSIONS_MAP: Dict[Role, Set[Permission]] = {
    Role.SUPER_ADMIN: {p for p in Permission},  # 所有权限

    Role.ADMIN: {
        Permission.USER_READ, Permission.USER_CREATE, Permission.USER_UPDATE,
        Permission.KYC_READ, Permission.KYC_VERIFY, Permission.KYC_APPROVE, Permission.KYC_REJECT,
        Permission.TRANSACTION_READ, Permission.TRANSACTION_APPROVE, Permission.TRANSACTION_REJECT,
        Permission.AML_READ, Permission.AML_INVESTIGATE,
        Permission.REPORT_READ, Permission.REPORT_GENERATE, Permission.REPORT_EXPORT,
        Permission.AUDIT_READ,
        Permission.SYSTEM_CONFIG,
    },

    Role.COMPLIANCE_OFFICER: {
        Permission.USER_READ,
        Permission.KYC_READ, Permission.KYC_VERIFY, Permission.KYC_APPROVE, Permission.KYC_REJECT,
        Permission.TRANSACTION_READ, Permission.TRANSACTION_APPROVE, Permission.TRANSACTION_REJECT,
        Permission.AML_READ, Permission.AML_INVESTIGATE, Permission.SAR_CREATE, Permission.SAR_FILE,
        Permission.REPORT_READ, Permission.REPORT_GENERATE, Permission.REPORT_EXPORT, Permission.REPORT_SUBMIT,
        Permission.AUDIT_READ,
    },

    Role.AML_ANALYST: {
        Permission.USER_READ,
        Permission.TRANSACTION_READ,
        Permission.AML_READ, Permission.AML_INVESTIGATE, Permission.SAR_CREATE,
        Permission.REPORT_READ,
        Permission.AUDIT_READ,
    },

    Role.KYC_REVIEWER: {
        Permission.USER_READ,
        Permission.KYC_READ, Permission.KYC_VERIFY,
        Permission.AUDIT_READ,
    },

    Role.TRANSACTION_APPROVER: {
        Permission.USER_READ,
        Permission.TRANSACTION_READ, Permission.TRANSACTION_APPROVE, Permission.TRANSACTION_REJECT,
        Permission.AUDIT_READ,
    },

    Role.AUDITOR: {
        Permission.USER_READ,
        Permission.KYC_READ,
        Permission.TRANSACTION_READ,
        Permission.AML_READ,
        Permission.REPORT_READ, Permission.REPORT_EXPORT,
        Permission.AUDIT_READ, Permission.AUDIT_EXPORT,
    },

    Role.OPERATOR: {
        Permission.USER_READ,
        Permission.KYC_READ,
        Permission.TRANSACTION_READ, Permission.TRANSACTION_CREATE,
        Permission.REPORT_READ,
    },

    Role.VIEWER: {
        Permission.USER_READ,
        Permission.KYC_READ,
        Permission.TRANSACTION_READ,
        Permission.REPORT_READ,
    },
}


class User(BaseModel):
    """用户模型"""
    user_id: str
    username: str
    email: str
    roles: List[Role]
    is_active: bool = True
    created_at: datetime
    last_login: Optional[datetime] = None


class AccessControl:
    """访问控制服务"""

    @staticmethod
    def get_role_permissions(role: Role) -> Set[Permission]:
        """获取角色的所有权限"""
        return ROLE_PERMISSIONS_MAP.get(role, set())

    @staticmethod
    def get_user_permissions(user: User) -> Set[Permission]:
        """获取用户的所有权限（合并所有角色的权限）"""
        all_permissions = set()
        for role in user.roles:
            all_permissions.update(AccessControl.get_role_permissions(role))
        return all_permissions

    @staticmethod
    def has_permission(user: User, required_permission: Permission) -> bool:
        """检查用户是否有指定权限"""
        if not user.is_active:
            return False

        user_permissions = AccessControl.get_user_permissions(user)
        return required_permission in user_permissions

    @staticmethod
    def has_any_permission(user: User, required_permissions: List[Permission]) -> bool:
        """检查用户是否有任意一个权限"""
        if not user.is_active:
            return False

        user_permissions = AccessControl.get_user_permissions(user)
        return any(perm in user_permissions for perm in required_permissions)

    @staticmethod
    def has_all_permissions(user: User, required_permissions: List[Permission]) -> bool:
        """检查用户是否有所有权限"""
        if not user.is_active:
            return False

        user_permissions = AccessControl.get_user_permissions(user)
        return all(perm in user_permissions for perm in required_permissions)

    @staticmethod
    def require_permission(required_permission: Permission):
        """权限装饰器（用于函数）"""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                # 从参数中获取 user
                user = kwargs.get('user') or (args[0] if args else None)

                if not isinstance(user, User):
                    raise ValueError("无法获取用户信息")

                if not AccessControl.has_permission(user, required_permission):
                    raise PermissionError(f"缺少权限: {required_permission}")

                return await func(*args, **kwargs)
            return wrapper
        return decorator

    @staticmethod
    def check_resource_access(
        user: User,
        resource_type: str,
        resource_id: str,
        action: str
    ) -> bool:
        """
        检查用户对特定资源的访问权限

        Args:
            user: 用户
            resource_type: 资源类型（如 transaction, kyc_profile）
            resource_id: 资源ID
            action: 操作（read, update, delete）
        """
        # 构造权限字符串
        permission_str = f"{resource_type}:{action}"

        try:
            permission = Permission(permission_str)
            return AccessControl.has_permission(user, permission)
        except ValueError:
            # 如果权限不存在，默认拒绝
            return False


class DataAccessControl:
    """数据级访问控制"""

    @staticmethod
    def filter_sensitive_fields(
        data: Dict,
        user: User,
        sensitive_fields: Set[str]
    ) -> Dict:
        """
        根据用户权限过滤敏感字段

        Args:
            data: 原始数据
            user: 用户
            sensitive_fields: 敏感字段集合

        Returns:
            过滤后的数据
        """
        # 检查用户是否有查看敏感信息的权限
        can_view_sensitive = AccessControl.has_any_permission(user, [
            Permission.SUPER_ADMIN,
            Permission.COMPLIANCE_OFFICER,
            Permission.AUDITOR
        ])

        if can_view_sensitive:
            return data

        # 过滤敏感字段
        filtered_data = data.copy()
        for field in sensitive_fields:
            if field in filtered_data:
                filtered_data[field] = "***REDACTED***"

        return filtered_data

    @staticmethod
    def can_export_data(user: User) -> bool:
        """检查用户是否可以导出数据"""
        return AccessControl.has_any_permission(user, [
            Permission.REPORT_EXPORT,
            Permission.AUDIT_EXPORT
        ])

    @staticmethod
    def can_delete_data(user: User, data_type: str) -> bool:
        """检查用户是否可以删除数据"""
        delete_permissions = {
            "user": Permission.USER_DELETE,
            "transaction": Permission.TRANSACTION_DELETE,
        }

        required_permission = delete_permissions.get(data_type)
        if not required_permission:
            return False

        return AccessControl.has_permission(user, required_permission)
