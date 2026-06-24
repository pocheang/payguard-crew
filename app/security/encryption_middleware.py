"""
数据库字段加密中间件
自动加密/解密数据库字段
"""
from typing import Any, Dict, List, Optional, Set
from sqlalchemy import event, inspect
from sqlalchemy.orm import Session
from .advanced_encryption import EnhancedEncryptionService, KeyManagementService
from .encryption import EncryptionLevel


class DatabaseEncryptionMiddleware:
    """数据库加密中间件"""

    def __init__(
        self,
        encryption_service: EnhancedEncryptionService,
        encrypted_fields: Dict[str, Dict[str, EncryptionLevel]]
    ):
        """
        初始化数据库加密中间件

        Args:
            encryption_service: 加密服务
            encrypted_fields: 加密字段配置
                格式: {
                    "table_name": {
                        "field_name": EncryptionLevel.STRONG,
                        ...
                    },
                    ...
                }
        """
        self.encryption = encryption_service
        self.encrypted_fields = encrypted_fields

    def encrypt_before_insert(self, mapper, connection, target):
        """插入前加密"""
        table_name = mapper.mapped_table.name
        if table_name not in self.encrypted_fields:
            return

        for field_name, encryption_level in self.encrypted_fields[table_name].items():
            if hasattr(target, field_name):
                value = getattr(target, field_name)
                if value is not None:
                    encrypted = self._encrypt_value(value, field_name, encryption_level)
                    setattr(target, field_name, encrypted)

    def encrypt_before_update(self, mapper, connection, target):
        """更新前加密"""
        self.encrypt_before_insert(mapper, connection, target)

    def decrypt_after_load(self, target, context):
        """加载后解密"""
        table_name = target.__tablename__
        if table_name not in self.encrypted_fields:
            return

        for field_name, encryption_level in self.encrypted_fields[table_name].items():
            if hasattr(target, field_name):
                encrypted_value = getattr(target, field_name)
                if encrypted_value is not None:
                    try:
                        decrypted = self._decrypt_value(
                            encrypted_value,
                            field_name,
                            encryption_level
                        )
                        setattr(target, field_name, decrypted)
                    except Exception as e:
                        print(f"解密失败 {table_name}.{field_name}: {e}")

    def _encrypt_value(self, value: str, field_name: str, level: EncryptionLevel) -> str:
        """加密值"""
        if level == EncryptionLevel.NONE:
            return value
        elif level == EncryptionLevel.HASH:
            # 哈希不可逆
            import hashlib
            return hashlib.sha256(value.encode()).hexdigest()
        else:
            # 使用信封加密
            encrypted = self.encryption.encrypt_field_with_rotation(value, field_name)
            import json
            return json.dumps(encrypted)

    def _decrypt_value(self, encrypted: str, field_name: str, level: EncryptionLevel) -> str:
        """解密值"""
        if level == EncryptionLevel.NONE:
            return encrypted
        elif level == EncryptionLevel.HASH:
            # 哈希值不能解密
            return encrypted
        else:
            import json
            encrypted_data = json.loads(encrypted)
            return self.encryption.decrypt_field_with_rotation(encrypted_data)

    def register_model(self, model_class):
        """注册模型到加密中间件"""
        event.listen(model_class, 'before_insert', self.encrypt_before_insert)
        event.listen(model_class, 'before_update', self.encrypt_before_update)
        event.listen(model_class, 'load', self.decrypt_after_load)


class EncryptionPerformanceOptimizer:
    """加密性能优化器"""

    def __init__(self, encryption_service: EnhancedEncryptionService):
        self.encryption = encryption_service
        self.cache: Dict[str, Any] = {}
        self.cache_hits = 0
        self.cache_misses = 0

    def encrypt_with_cache(
        self,
        plaintext: str,
        field_name: str,
        ttl_seconds: int = 300
    ) -> Dict:
        """
        带缓存的加密（用于重复加密相同数据）

        Args:
            plaintext: 明文
            field_name: 字段名
            ttl_seconds: 缓存TTL

        Returns:
            加密结果
        """
        cache_key = f"{field_name}:{plaintext}"

        if cache_key in self.cache:
            self.cache_hits += 1
            return self.cache[cache_key]

        self.cache_misses += 1
        encrypted = self.encryption.encrypt_field_with_rotation(plaintext, field_name)
        self.cache[cache_key] = encrypted

        return encrypted

    def batch_encrypt(
        self,
        items: List[Dict[str, str]],
        field_mappings: Dict[str, str]
    ) -> List[Dict]:
        """
        批量加密（提高性能）

        Args:
            items: 数据项列表
            field_mappings: 字段映射 {field_name: encryption_field_name}

        Returns:
            加密后的数据列表
        """
        encrypted_items = []

        for item in items:
            encrypted_item = item.copy()
            for field_name, enc_field_name in field_mappings.items():
                if field_name in item:
                    encrypted = self.encryption.encrypt_field_with_rotation(
                        item[field_name],
                        field_name
                    )
                    encrypted_item[enc_field_name] = encrypted

            encrypted_items.append(encrypted_item)

        return encrypted_items

    def get_cache_stats(self) -> Dict:
        """获取缓存统计"""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = self.cache_hits / total_requests if total_requests > 0 else 0

        return {
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate": hit_rate,
            "cache_size": len(self.cache)
        }

    def clear_cache(self):
        """清空缓存"""
        self.cache.clear()
        self.cache_hits = 0
        self.cache_misses = 0


class SecureDataTransfer:
    """安全数据传输"""

    def __init__(self, encryption_service: EnhancedEncryptionService):
        self.encryption = encryption_service

    def encrypt_for_transit(self, data: Dict) -> Dict:
        """
        为传输加密数据（使用临时密钥）

        Args:
            data: 要传输的数据

        Returns:
            加密的数据包
        """
        import json

        # 序列化数据
        json_data = json.dumps(data).encode()

        # 使用 AES-GCM 加密
        encrypted = self.encryption.encrypt_with_aes_gcm(
            json_data,
            associated_data=b"transit-v1"
        )

        return {
            "encrypted_payload": encrypted,
            "version": "1.0",
            "algorithm": "AES-256-GCM"
        }

    def decrypt_from_transit(self, encrypted_package: Dict) -> Dict:
        """
        解密传输的数据

        Args:
            encrypted_package: 加密的数据包

        Returns:
            解密后的数据
        """
        import json

        decrypted_bytes = self.encryption.decrypt_with_aes_gcm(
            encrypted_package["encrypted_payload"],
            associated_data=b"transit-v1"
        )

        return json.loads(decrypted_bytes)

    def sign_data(self, data: bytes, private_key) -> bytes:
        """
        数字签名

        Args:
            data: 要签名的数据
            private_key: RSA 私钥

        Returns:
            签名
        """
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import padding

        signature = private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        return signature

    def verify_signature(self, data: bytes, signature: bytes, public_key) -> bool:
        """
        验证数字签名

        Args:
            data: 原始数据
            signature: 签名
            public_key: RSA 公钥

        Returns:
            签名是否有效
        """
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import padding
        from cryptography.exceptions import InvalidSignature

        try:
            public_key.verify(
                signature,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except InvalidSignature:
            return False


class EncryptionAuditLogger:
    """加密审计日志"""

    def __init__(self):
        self.audit_log: List[Dict] = []

    def log_encryption(
        self,
        operation: str,
        field_name: str,
        user_id: Optional[str] = None,
        success: bool = True,
        metadata: Optional[Dict] = None
    ):
        """记录加密操作"""
        from datetime import datetime

        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "operation": operation,
            "field_name": field_name,
            "user_id": user_id,
            "success": success,
            "metadata": metadata or {}
        }

        self.audit_log.append(log_entry)

    def log_key_operation(
        self,
        operation: str,
        key_id: str,
        key_type: str,
        user_id: Optional[str] = None,
        success: bool = True
    ):
        """记录密钥操作"""
        self.log_encryption(
            operation=f"key_{operation}",
            field_name=key_id,
            user_id=user_id,
            success=success,
            metadata={"key_type": key_type}
        )

    def get_logs(
        self,
        operation: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """获取审计日志"""
        filtered = self.audit_log

        if operation:
            filtered = [log for log in filtered if log["operation"] == operation]

        if user_id:
            filtered = [log for log in filtered if log["user_id"] == user_id]

        return filtered[-limit:]

    def generate_report(self) -> Dict:
        """生成审计报告"""
        from collections import Counter

        operations = Counter(log["operation"] for log in self.audit_log)
        success_rate = sum(1 for log in self.audit_log if log["success"]) / len(self.audit_log) if self.audit_log else 0

        return {
            "total_operations": len(self.audit_log),
            "operation_counts": dict(operations),
            "success_rate": success_rate,
            "generated_at": datetime.utcnow().isoformat()
        }
