#!/usr/bin/env python3
"""
安全配置检查脚本

在应用启动前验证所有安全配置
用法: python scripts/security_check.py
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def check_jwt_config() -> list[str]:
    """检查JWT配置"""
    errors = []

    jwt_key = os.getenv("JWT_SECRET_KEY")
    if not jwt_key:
        errors.append("❌ JWT_SECRET_KEY is not configured")
    elif len(jwt_key) < 32:
        errors.append(f"❌ JWT_SECRET_KEY too short (length: {len(jwt_key)}, minimum: 32)")
    elif jwt_key == "CHANGE_THIS_IN_PRODUCTION":
        errors.append("❌ JWT_SECRET_KEY is using default value")

    return errors


def check_encryption_config() -> list[str]:
    """检查加密配置"""
    errors = []

    enc_key = os.getenv("ENCRYPTION_MASTER_KEY")
    if not enc_key:
        errors.append("❌ ENCRYPTION_MASTER_KEY is not configured")
    elif len(enc_key) < 32:
        errors.append(f"❌ ENCRYPTION_MASTER_KEY too short (length: {len(enc_key)})")

    return errors


def check_api_keys() -> list[str]:
    """检查API密钥"""
    errors = []

    api_keys = os.getenv("API_KEYS")
    if not api_keys:
        errors.append("❌ API_KEYS is not configured (API will be unprotected)")
    else:
        keys = [k.strip() for k in api_keys.split(",") if k.strip()]
        if not keys:
            errors.append("❌ API_KEYS is empty after parsing")
        elif len(keys) < 2:
            errors.append(f"⚠️  Only {len(keys)} API key configured. Recommend at least 2 for rotation.")

    return errors


def check_environment() -> list[str]:
    """检查环境配置"""
    errors = []

    app_env = os.getenv("APP_ENV", "dev")
    valid_envs = ["dev", "development", "local", "staging", "prod", "production"]

    if app_env not in valid_envs:
        errors.append(f"❌ Invalid APP_ENV: '{app_env}'. Valid: {', '.join(valid_envs)}")

    # 生产环境额外检查
    if app_env in ["prod", "production"]:
        if os.getenv("CORS_ORIGINS") == "*":
            errors.append("❌ CORS_ORIGINS set to wildcard '*' in production")

        if not os.getenv("REDIS_URL"):
            errors.append("⚠️  REDIS_URL not configured. Rate limiting will use memory (not recommended for prod)")

    return errors


def check_dangerous_defaults() -> list[str]:
    """检查危险的默认值"""
    errors = []

    dangerous_patterns = [
        ("JWT_SECRET_KEY", ["test", "demo", "example", "CHANGE_THIS"]),
        ("ENCRYPTION_MASTER_KEY", ["test", "demo", "example"]),
        ("API_KEYS", ["test-key", "demo-key", "your-key"]),
    ]

    for env_var, patterns in dangerous_patterns:
        value = os.getenv(env_var, "")
        for pattern in patterns:
            if pattern in value:
                errors.append(f"❌ {env_var} contains dangerous pattern: '{pattern}'")

    return errors


def main():
    print("=" * 60)
    print("PayGuard Crew - Security Configuration Check")
    print("=" * 60)
    print()

    # 加载环境变量
    from dotenv import load_dotenv
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ Loaded environment from: {env_file}")
    else:
        print(f"⚠️  No .env file found at: {env_file}")

    print()

    # 运行所有检查
    all_errors = []

    checks = [
        ("JWT Configuration", check_jwt_config),
        ("Encryption Configuration", check_encryption_config),
        ("API Keys", check_api_keys),
        ("Environment", check_environment),
        ("Dangerous Defaults", check_dangerous_defaults),
    ]

    for check_name, check_func in checks:
        print(f"Checking {check_name}...")
        errors = check_func()
        all_errors.extend(errors)

        if errors:
            for error in errors:
                print(f"  {error}")
        else:
            print(f"  ✅ All checks passed")

        print()

    # 汇总结果
    print("=" * 60)
    if all_errors:
        print(f"❌ Security check FAILED with {len(all_errors)} issue(s)")
        print()
        print("To fix:")
        print("  1. Run: python scripts/generate_secrets.py")
        print("  2. Copy generated keys to your .env file")
        print("  3. Run this check again")
        print()
        sys.exit(1)
    else:
        print("✅ All security checks PASSED")
        print()
        print("Your application is properly configured for secure operation.")
        print()
        sys.exit(0)


if __name__ == "__main__":
    main()
