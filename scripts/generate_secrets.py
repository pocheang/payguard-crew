#!/usr/bin/env python3
"""
安全密钥生成脚本

生成生产环境所需的所有密钥
用法: python scripts/generate_secrets.py
"""
import secrets
from cryptography.fernet import Fernet


def generate_jwt_secret(length: int = 64) -> str:
    """生成JWT密钥"""
    return secrets.token_urlsafe(length)


def generate_encryption_key() -> str:
    """生成Fernet加密密钥"""
    return Fernet.generate_key().decode()


def generate_api_keys(count: int = 3) -> str:
    """生成多个API密钥"""
    return ",".join([secrets.token_urlsafe(32) for _ in range(count)])


def main():
    print("=" * 60)
    print("PayGuard Crew - Security Keys Generator")
    print("=" * 60)
    print()

    # 生成所有密钥
    jwt_secret = generate_jwt_secret()
    encryption_key = generate_encryption_key()
    api_keys = generate_api_keys()

    # 输出到控制台
    print("🔐 Generated Security Keys:")
    print()
    print("# Add these to your .env file:")
    print()
    print("# JWT Configuration")
    print(f"JWT_SECRET_KEY={jwt_secret}")
    print()
    print("# Encryption Configuration")
    print(f"ENCRYPTION_MASTER_KEY={encryption_key}")
    print()
    print("# API Keys (3 keys generated)")
    print(f"API_KEYS={api_keys}")
    print()

    # 写入到 .env.secrets 文件
    output_file = ".env.secrets"
    with open(output_file, "w") as f:
        f.write("# Generated Security Keys\n")
        f.write("# DO NOT COMMIT THIS FILE TO VERSION CONTROL\n")
        f.write(f"# Generated at: {__import__('datetime').datetime.now().isoformat()}\n\n")
        f.write("# JWT Configuration\n")
        f.write(f"JWT_SECRET_KEY={jwt_secret}\n\n")
        f.write("# Encryption Configuration\n")
        f.write(f"ENCRYPTION_MASTER_KEY={encryption_key}\n\n")
        f.write("# API Keys\n")
        f.write(f"API_KEYS={api_keys}\n")

    print(f"✅ Keys also saved to: {output_file}")
    print()
    print("⚠️  IMPORTANT:")
    print("   1. Copy these keys to your .env file")
    print("   2. Keep .env.secrets secure and never commit it to Git")
    print("   3. For production, use a secrets manager (HashiCorp Vault, AWS Secrets Manager)")
    print("   4. Store these keys in a secure password manager")
    print()


if __name__ == "__main__":
    main()
