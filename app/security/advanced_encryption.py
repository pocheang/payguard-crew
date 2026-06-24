"""
高级加密服务
提供密钥管理、密钥轮换、多层加密等企业级功能
"""
from cryptography.fernet import Fernet, MultiFernet
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import secrets


class KeyType(str, Enum):
    """密钥类型"""
    MASTER = "master"  # 主密钥
    DATA = "data"  # 数据加密密钥
    FIELD = "field"  # 字段加密密钥
    FILE = "file"  # 文件加密密钥
    BACKUP = "backup"  # 备份密钥


class KeyStatus(str, Enum):
    """密钥状态"""
    ACTIVE = "active"  # 活跃
    INACTIVE = "inactive"  # 非活跃
    ROTATED = "rotated"  # 已轮换
    REVOKED = "revoked"  # 已撤销


class EncryptionKey:
    """加密密钥模型"""
    def __init__(
        self,
        key_id: str,
        key_type: KeyType,
        key_material: bytes,
        created_at: datetime,
        expires_at: Optional[datetime] = None,
        status: KeyStatus = KeyStatus.ACTIVE,
        version: int = 1
    ):
        self.key_id = key_id
        self.key_type = key_type
        self.key_material = key_material
        self.created_at = created_at
        self.expires_at = expires_at
        self.status = status
        self.version = version


class KeyManagementService:
    """密钥管理服务"""

    def __init__(self, storage_path: Optional[str] = None):
        """
        初始化密钥管理服务

        Args:
            storage_path: 密钥存储路径（生产环境应使用 KMS）
        """
        self.storage_path = storage_path or ".keys"
        self.keys: Dict[str, EncryptionKey] = {}
        self.current_master_key: Optional[EncryptionKey] = None

        # 创建密钥存储目录
        os.makedirs(self.storage_path, exist_ok=True)

        # 加载或生成主密钥
        self._initialize_master_key()

    def _initialize_master_key(self):
        """初始化或加载主密钥"""
        master_key_path = os.path.join(self.storage_path, "master.key")

        if os.path.exists(master_key_path):
            # 加载现有主密钥
            with open(master_key_path, 'rb') as f:
                key_data = f.read()
                self.current_master_key = EncryptionKey(
                    key_id="master-001",
                    key_type=KeyType.MASTER,
                    key_material=key_data,
                    created_at=datetime.utcnow()
                )
        else:
            # 生成新的主密钥
            key_material = Fernet.generate_key()
            self.current_master_key = EncryptionKey(
                key_id="master-001",
                key_type=KeyType.MASTER,
                key_material=key_material,
                created_at=datetime.utcnow()
            )

            # 保存主密钥（生产环境应使用 KMS）
            with open(master_key_path, 'wb') as f:
                f.write(key_material)

            print(f"⚠️ 新主密钥已生成: {master_key_path}")
            print("⚠️ 请妥善保管此密钥文件！")

    def generate_data_key(
        self,
        key_id: Optional[str] = None,
        expiry_days: Optional[int] = 365
    ) -> EncryptionKey:
        """
        生成数据加密密钥（DEK）

        Args:
            key_id: 密钥ID，如不提供则自动生成
            expiry_days: 过期天数
        """
        if key_id is None:
            key_id = f"dek-{secrets.token_hex(8)}"

        key_material = Fernet.generate_key()
        expires_at = None
        if expiry_days:
            expires_at = datetime.utcnow() + timedelta(days=expiry_days)

        data_key = EncryptionKey(
            key_id=key_id,
            key_type=KeyType.DATA,
            key_material=key_material,
            created_at=datetime.utcnow(),
            expires_at=expires_at
        )

        self.keys[key_id] = data_key
        return data_key

    def wrap_key(self, data_key: EncryptionKey) -> bytes:
        """
        使用主密钥包装（加密）数据密钥

        Args:
            data_key: 要包装的数据密钥

        Returns:
            加密后的密钥材料
        """
        master_fernet = Fernet(self.current_master_key.key_material)
        wrapped = master_fernet.encrypt(data_key.key_material)
        return wrapped

    def unwrap_key(self, wrapped_key: bytes) -> bytes:
        """
        使用主密钥解包（解密）数据密钥

        Args:
            wrapped_key: 包装的密钥材料

        Returns:
            解密后的密钥材料
        """
        master_fernet = Fernet(self.current_master_key.key_material)
        unwrapped = master_fernet.decrypt(wrapped_key)
        return unwrapped

    def rotate_master_key(self) -> EncryptionKey:
        """
        轮换主密钥

        Returns:
            新的主密钥
        """
        # 标记旧主密钥为已轮换
        if self.current_master_key:
            self.current_master_key.status = KeyStatus.ROTATED

        # 生成新主密钥
        new_key_material = Fernet.generate_key()
        new_master_key = EncryptionKey(
            key_id=f"master-{int(datetime.utcnow().timestamp())}",
            key_type=KeyType.MASTER,
            key_material=new_key_material,
            created_at=datetime.utcnow(),
            version=self.current_master_key.version + 1 if self.current_master_key else 1
        )

        # 保存新主密钥
        master_key_path = os.path.join(self.storage_path, f"{new_master_key.key_id}.key")
        with open(master_key_path, 'wb') as f:
            f.write(new_key_material)

        self.current_master_key = new_master_key
        return new_master_key

    def get_active_key(self, key_type: KeyType) -> Optional[EncryptionKey]:
        """获取活跃的指定类型密钥"""
        for key in self.keys.values():
            if key.key_type == key_type and key.status == KeyStatus.ACTIVE:
                # 检查是否过期
                if key.expires_at and key.expires_at < datetime.utcnow():
                    key.status = KeyStatus.INACTIVE
                    continue
                return key
        return None


class EnhancedEncryptionService:
    """增强的加密服务"""

    def __init__(self, key_manager: KeyManagementService):
        """
        初始化增强加密服务

        Args:
            key_manager: 密钥管理服务
        """
        self.key_manager = key_manager
        self.backend = default_backend()

    def encrypt_with_aes_gcm(
        self,
        plaintext: bytes,
        associated_data: Optional[bytes] = None
    ) -> Dict:
        """
        使用 AES-GCM 加密（带认证的加密）

        Args:
            plaintext: 明文
            associated_data: 关联数据（AAD）

        Returns:
            包含密文、nonce和tag的字典
        """
        # 生成随机密钥和 nonce
        key = AESGCM.generate_key(bit_length=256)
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)  # GCM 推荐 96-bit nonce

        # 加密
        ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data)

        return {
            "ciphertext": base64.b64encode(ciphertext).decode(),
            "nonce": base64.b64encode(nonce).decode(),
            "key": base64.b64encode(key).decode(),
            "algorithm": "AES-256-GCM"
        }

    def decrypt_with_aes_gcm(
        self,
        encrypted_data: Dict,
        associated_data: Optional[bytes] = None
    ) -> bytes:
        """
        使用 AES-GCM 解密

        Args:
            encrypted_data: 加密数据字典
            associated_data: 关联数据（AAD）

        Returns:
            明文
        """
        ciphertext = base64.b64decode(encrypted_data["ciphertext"])
        nonce = base64.b64decode(encrypted_data["nonce"])
        key = base64.b64decode(encrypted_data["key"])

        aesgcm = AESGCM(key)
        plaintext = aesgcm.decrypt(nonce, ciphertext, associated_data)

        return plaintext

    def encrypt_with_envelope(
        self,
        plaintext: bytes,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        信封加密（Envelope Encryption）
        数据使用 DEK 加密，DEK 使用 KEK 加密

        Args:
            plaintext: 明文
            metadata: 元数据

        Returns:
            信封加密结果
        """
        # 生成数据加密密钥（DEK）
        dek = self.key_manager.generate_data_key()

        # 使用 DEK 加密数据
        fernet = Fernet(dek.key_material)
        ciphertext = fernet.encrypt(plaintext)

        # 使用主密钥包装 DEK
        wrapped_dek = self.key_manager.wrap_key(dek)

        return {
            "ciphertext": base64.b64encode(ciphertext).decode(),
            "wrapped_key": base64.b64encode(wrapped_dek).decode(),
            "key_id": dek.key_id,
            "algorithm": "Fernet-Envelope",
            "metadata": metadata or {}
        }

    def decrypt_with_envelope(self, envelope_data: Dict) -> bytes:
        """
        解密信封加密的数据

        Args:
            envelope_data: 信封加密数据

        Returns:
            明文
        """
        # 解包 DEK
        wrapped_dek = base64.b64decode(envelope_data["wrapped_key"])
        dek_material = self.key_manager.unwrap_key(wrapped_dek)

        # 使用 DEK 解密数据
        fernet = Fernet(dek_material)
        ciphertext = base64.b64decode(envelope_data["ciphertext"])
        plaintext = fernet.decrypt(ciphertext)

        return plaintext

    def encrypt_with_rsa(self, plaintext: bytes, public_key: rsa.RSAPublicKey) -> bytes:
        """
        使用 RSA 公钥加密（非对称加密）

        Args:
            plaintext: 明文
            public_key: RSA 公钥

        Returns:
            密文
        """
        ciphertext = public_key.encrypt(
            plaintext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return ciphertext

    def decrypt_with_rsa(self, ciphertext: bytes, private_key: rsa.RSAPrivateKey) -> bytes:
        """
        使用 RSA 私钥解密

        Args:
            ciphertext: 密文
            private_key: RSA 私钥

        Returns:
            明文
        """
        plaintext = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return plaintext

    def generate_rsa_keypair(self, key_size: int = 2048) -> Tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
        """
        生成 RSA 密钥对

        Args:
            key_size: 密钥大小（位）

        Returns:
            (私钥, 公钥)
        """
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=self.backend
        )
        public_key = private_key.public_key()

        return private_key, public_key

    def encrypt_field_with_rotation(
        self,
        value: str,
        field_name: str,
        enable_rotation: bool = True
    ) -> Dict:
        """
        字段加密（支持密钥轮换）

        Args:
            value: 字段值
            field_name: 字段名
            enable_rotation: 是否启用密钥轮换

        Returns:
            加密结果（包含版本信息）
        """
        # 使用信封加密
        envelope = self.encrypt_with_envelope(
            value.encode(),
            metadata={
                "field_name": field_name,
                "encrypted_at": datetime.utcnow().isoformat()
            }
        )

        envelope["version"] = self.key_manager.current_master_key.version
        envelope["rotation_enabled"] = enable_rotation

        return envelope

    def decrypt_field_with_rotation(self, encrypted_data: Dict) -> str:
        """
        解密字段（支持密钥轮换）

        Args:
            encrypted_data: 加密数据

        Returns:
            解密后的值
        """
        # 检查密钥版本
        data_version = encrypted_data.get("version", 1)
        current_version = self.key_manager.current_master_key.version

        if data_version < current_version:
            print(f"⚠️ 检测到旧版本密钥({data_version})，当前版本({current_version})")

        plaintext = self.decrypt_with_envelope(encrypted_data)
        return plaintext.decode()

    def multi_layer_encrypt(self, data: bytes, layers: int = 2) -> Dict:
        """
        多层加密（增强安全性）

        Args:
            data: 要加密的数据
            layers: 加密层数

        Returns:
            多层加密结果
        """
        encrypted = data
        keys = []

        for i in range(layers):
            dek = self.key_manager.generate_data_key(key_id=f"layer-{i}-{secrets.token_hex(4)}")
            fernet = Fernet(dek.key_material)
            encrypted = fernet.encrypt(encrypted)
            keys.append(self.key_manager.wrap_key(dek))

        return {
            "ciphertext": base64.b64encode(encrypted).decode(),
            "wrapped_keys": [base64.b64encode(k).decode() for k in keys],
            "layers": layers,
            "algorithm": "Multi-Layer-Fernet"
        }

    def multi_layer_decrypt(self, encrypted_data: Dict) -> bytes:
        """
        解密多层加密数据

        Args:
            encrypted_data: 多层加密数据

        Returns:
            明文
        """
        ciphertext = base64.b64decode(encrypted_data["ciphertext"])
        wrapped_keys = [base64.b64decode(k) for k in encrypted_data["wrapped_keys"]]

        # 逆序解密
        decrypted = ciphertext
        for wrapped_key in reversed(wrapped_keys):
            dek_material = self.key_manager.unwrap_key(wrapped_key)
            fernet = Fernet(dek_material)
            decrypted = fernet.decrypt(decrypted)

        return decrypted

    def secure_delete(self, file_path: str, passes: int = 3):
        """
        安全删除文件（多次覆写）

        Args:
            file_path: 文件路径
            passes: 覆写次数
        """
        if not os.path.exists(file_path):
            return

        file_size = os.path.getsize(file_path)

        # 多次覆写
        with open(file_path, 'r+b') as f:
            for _ in range(passes):
                f.seek(0)
                f.write(os.urandom(file_size))
                f.flush()
                os.fsync(f.fileno())

        # 删除文件
        os.remove(file_path)
