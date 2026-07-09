"""
数据加密服务
提供字段级和文件级加密功能
"""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import base64
import hashlib
import os
from typing import Optional, Dict, Any
from enum import Enum


class EncryptionLevel(str, Enum):
    """加密级别"""
    NONE = "none"  # 不加密
    BASIC = "basic"  # 基础加密（可逆）
    HASH = "hash"  # 哈希（不可逆）
    STRONG = "strong"  # 强加密（双层加密）


class SensitiveFieldType(str, Enum):
    """敏感字段类型"""
    PII = "pii"  # 个人身份信息
    FINANCIAL = "financial"  # 财务信息
    CREDENTIAL = "credential"  # 凭证信息
    BIOMETRIC = "biometric"  # 生物识别信息
    MEDICAL = "medical"  # 医疗信息


class EncryptionService:
    """加密服务"""

    def __init__(self, master_key: Optional[bytes] = None):
        """
        初始化加密服务

        Args:
            master_key: 主密钥，如果不提供则从环境变量读取

        Raises:
            ValueError: 如果未配置 ENCRYPTION_MASTER_KEY
        """
        if master_key is None:
            # 从环境变量读取（必需）
            master_key_str = os.getenv("ENCRYPTION_MASTER_KEY")
            if not master_key_str:
                raise ValueError(
                    "ENCRYPTION_MASTER_KEY is required for data encryption.\n"
                    "Generate with:\n"
                    "python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\"\n"
                    "Then set in .env file: ENCRYPTION_MASTER_KEY=<generated_key>"
                )
            master_key = master_key_str.encode()

        self.master_key = master_key
        self.fernet = Fernet(master_key)

        # 字段加密密钥派生
        self.field_keys: Dict[str, Fernet] = {}

    def generate_key(self) -> bytes:
        """生成新的加密密钥"""
        return Fernet.generate_key()

    def derive_field_key(self, field_name: str, salt: Optional[bytes] = None) -> Fernet:
        """
        为特定字段派生加密密钥

        Args:
            field_name: 字段名称
            salt: 盐值，如果不提供则使用字段名生成
        """
        if field_name in self.field_keys:
            return self.field_keys[field_name]

        if salt is None:
            salt = hashlib.sha256(field_name.encode()).digest()[:16]

        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key))
        self.field_keys[field_name] = Fernet(key)
        return self.field_keys[field_name]

    def encrypt_field(self, value: str, field_name: str) -> str:
        """
        加密字段值

        Args:
            value: 要加密的值
            field_name: 字段名称

        Returns:
            加密后的值（Base64编码）
        """
        if not value:
            return value

        fernet = self.derive_field_key(field_name)
        encrypted = fernet.encrypt(value.encode())
        return base64.urlsafe_b64encode(encrypted).decode()

    def decrypt_field(self, encrypted_value: str, field_name: str) -> str:
        """
        解密字段值

        Args:
            encrypted_value: 加密的值
            field_name: 字段名称

        Returns:
            解密后的值
        """
        if not encrypted_value:
            return encrypted_value

        try:
            fernet = self.derive_field_key(field_name)
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_value.encode())
            decrypted = fernet.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"解密失败: {str(e)}")

    def hash_value(self, value: str, algorithm: str = "sha256") -> str:
        """
        对值进行哈希（不可逆）

        Args:
            value: 要哈希的值
            algorithm: 哈希算法（sha256, sha512）

        Returns:
            哈希值（十六进制）
        """
        if algorithm == "sha256":
            return hashlib.sha256(value.encode()).hexdigest()
        elif algorithm == "sha512":
            return hashlib.sha512(value.encode()).hexdigest()
        else:
            raise ValueError(f"不支持的哈希算法: {algorithm}")

    def encrypt_file(self, file_path: str, output_path: Optional[str] = None) -> str:
        """
        加密文件

        Args:
            file_path: 源文件路径
            output_path: 输出文件路径，如果不提供则覆盖原文件

        Returns:
            加密后的文件路径
        """
        with open(file_path, 'rb') as f:
            data = f.read()

        encrypted_data = self.fernet.encrypt(data)

        if output_path is None:
            output_path = file_path

        with open(output_path, 'wb') as f:
            f.write(encrypted_data)

        return output_path

    def decrypt_file(self, file_path: str, output_path: Optional[str] = None) -> str:
        """
        解密文件

        Args:
            file_path: 加密的文件路径
            output_path: 输出文件路径，如果不提供则覆盖原文件

        Returns:
            解密后的文件路径
        """
        with open(file_path, 'rb') as f:
            encrypted_data = f.read()

        decrypted_data = self.fernet.decrypt(encrypted_data)

        if output_path is None:
            output_path = file_path

        with open(output_path, 'wb') as f:
            f.write(decrypted_data)

        return output_path

    def encrypt_sensitive_data(
        self,
        data: Dict[str, Any],
        sensitive_fields: Dict[str, EncryptionLevel]
    ) -> Dict[str, Any]:
        """
        加密敏感数据字典

        Args:
            data: 数据字典
            sensitive_fields: 敏感字段及其加密级别

        Returns:
            加密后的数据字典
        """
        encrypted_data = data.copy()

        for field_name, encryption_level in sensitive_fields.items():
            if field_name not in data:
                continue

            value = data[field_name]
            if value is None:
                continue

            value_str = str(value)

            if encryption_level == EncryptionLevel.NONE:
                continue
            elif encryption_level == EncryptionLevel.BASIC:
                encrypted_data[field_name] = self.encrypt_field(value_str, field_name)
            elif encryption_level == EncryptionLevel.HASH:
                encrypted_data[field_name] = self.hash_value(value_str)
            elif encryption_level == EncryptionLevel.STRONG:
                # 双层加密：先用字段密钥，再用主密钥
                encrypted_once = self.encrypt_field(value_str, field_name)
                encrypted_data[field_name] = base64.urlsafe_b64encode(
                    self.fernet.encrypt(encrypted_once.encode())
                ).decode()

        return encrypted_data

    def decrypt_sensitive_data(
        self,
        encrypted_data: Dict[str, Any],
        sensitive_fields: Dict[str, EncryptionLevel]
    ) -> Dict[str, Any]:
        """
        解密敏感数据字典

        Args:
            encrypted_data: 加密的数据字典
            sensitive_fields: 敏感字段及其加密级别

        Returns:
            解密后的数据字典
        """
        decrypted_data = encrypted_data.copy()

        for field_name, encryption_level in sensitive_fields.items():
            if field_name not in encrypted_data:
                continue

            value = encrypted_data[field_name]
            if value is None:
                continue

            if encryption_level == EncryptionLevel.NONE:
                continue
            elif encryption_level == EncryptionLevel.HASH:
                # 哈希值不能解密
                continue
            elif encryption_level == EncryptionLevel.BASIC:
                decrypted_data[field_name] = self.decrypt_field(value, field_name)
            elif encryption_level == EncryptionLevel.STRONG:
                # 双层解密
                decrypted_once = self.fernet.decrypt(
                    base64.urlsafe_b64decode(value.encode())
                ).decode()
                decrypted_data[field_name] = self.decrypt_field(decrypted_once, field_name)

        return decrypted_data

    def mask_sensitive_data(self, value: str, mask_char: str = "*", show_last: int = 4) -> str:
        """
        脱敏显示敏感数据

        Args:
            value: 原始值
            mask_char: 掩码字符
            show_last: 显示最后几位

        Returns:
            脱敏后的值
        """
        if not value or len(value) <= show_last:
            return mask_char * len(value) if value else ""

        masked_length = len(value) - show_last
        return mask_char * masked_length + value[-show_last:]


class SensitiveDataHandler:
    """敏感数据处理器"""

    # 预定义的敏感字段配置
    SENSITIVE_FIELDS_CONFIG = {
        # 个人身份信息
        "id_card": (SensitiveFieldType.PII, EncryptionLevel.STRONG),
        "passport": (SensitiveFieldType.PII, EncryptionLevel.STRONG),
        "phone_number": (SensitiveFieldType.PII, EncryptionLevel.BASIC),
        "email": (SensitiveFieldType.PII, EncryptionLevel.BASIC),
        "full_name": (SensitiveFieldType.PII, EncryptionLevel.BASIC),
        "address": (SensitiveFieldType.PII, EncryptionLevel.BASIC),
        "date_of_birth": (SensitiveFieldType.PII, EncryptionLevel.BASIC),

        # 财务信息
        "bank_account": (SensitiveFieldType.FINANCIAL, EncryptionLevel.STRONG),
        "credit_card": (SensitiveFieldType.FINANCIAL, EncryptionLevel.STRONG),
        "cvv": (SensitiveFieldType.FINANCIAL, EncryptionLevel.HASH),

        # 凭证信息
        "password": (SensitiveFieldType.CREDENTIAL, EncryptionLevel.HASH),
        "api_key": (SensitiveFieldType.CREDENTIAL, EncryptionLevel.STRONG),
        "access_token": (SensitiveFieldType.CREDENTIAL, EncryptionLevel.STRONG),

        # 生物识别
        "face_template": (SensitiveFieldType.BIOMETRIC, EncryptionLevel.STRONG),
        "fingerprint": (SensitiveFieldType.BIOMETRIC, EncryptionLevel.STRONG),
    }

    def __init__(self, encryption_service: EncryptionService):
        self.encryption = encryption_service

    def identify_sensitive_fields(self, data: Dict[str, Any]) -> Dict[str, EncryptionLevel]:
        """识别数据中的敏感字段"""
        sensitive_fields = {}

        for field_name in data.keys():
            if field_name in self.SENSITIVE_FIELDS_CONFIG:
                _, encryption_level = self.SENSITIVE_FIELDS_CONFIG[field_name]
                sensitive_fields[field_name] = encryption_level

        return sensitive_fields

    def encrypt_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """自动识别并加密敏感数据"""
        sensitive_fields = self.identify_sensitive_fields(data)
        return self.encryption.encrypt_sensitive_data(data, sensitive_fields)

    def decrypt_data(self, encrypted_data: Dict[str, Any]) -> Dict[str, Any]:
        """自动识别并解密敏感数据"""
        sensitive_fields = self.identify_sensitive_fields(encrypted_data)
        return self.encryption.decrypt_sensitive_data(encrypted_data, sensitive_fields)

    def mask_for_display(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """为显示目的脱敏数据"""
        masked_data = data.copy()

        for field_name in data.keys():
            if field_name in self.SENSITIVE_FIELDS_CONFIG:
                value = data[field_name]
                if value:
                    masked_data[field_name] = self.encryption.mask_sensitive_data(str(value))

        return masked_data
