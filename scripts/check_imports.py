#!/usr/bin/env python3
"""
导入检查脚本

检查所有Python文件的导入是否正确
"""
import ast
import sys
from pathlib import Path
from typing import List, Tuple


def extract_imports(file_path: Path) -> List[str]:
    """提取文件中的所有导入"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=str(file_path))

        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module.split('.')[0])

        return list(set(imports))
    except Exception as e:
        print(f"⚠️  解析失败: {file_path}: {e}")
        return []


def check_app_imports(root_dir: Path) -> Tuple[List[str], List[str]]:
    """检查app目录中的导入问题"""
    issues = []
    checked_files = []

    # 遍历所有Python文件
    for py_file in root_dir.rglob("*.py"):
        if "__pycache__" in str(py_file) or "venv" in str(py_file):
            continue

        checked_files.append(str(py_file.relative_to(root_dir)))

        # 读取文件内容检查已知问题
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 检查旧的导入路径
            if "from app.crew.agents import" in content:
                issues.append(f"❌ {py_file.relative_to(root_dir)}: 使用旧的 app.crew.agents 导入")

            if "from app.db.repository import" in content:
                issues.append(f"❌ {py_file.relative_to(root_dir)}: 使用旧的 app.db.repository 导入")

            if "from app.rules.risk_rules_optimized import" in content:
                issues.append(f"❌ {py_file.relative_to(root_dir)}: 使用旧的 risk_rules_optimized 导入")

            if "from app.crew.schema_validator import" in content:
                issues.append(f"❌ {py_file.relative_to(root_dir)}: 使用旧的 schema_validator 导入")

        except Exception as e:
            issues.append(f"⚠️  无法读取: {py_file.relative_to(root_dir)}: {e}")

    return checked_files, issues


def main():
    """主函数"""
    print("🔍 检查导入问题...")
    print()

    root_dir = Path(__file__).parent
    app_dir = root_dir / "app"

    if not app_dir.exists():
        print("❌ 找不到 app/ 目录")
        sys.exit(1)

    checked_files, issues = check_app_imports(root_dir)

    print(f"✅ 已检查 {len(checked_files)} 个文件")
    print()

    if issues:
        print(f"❌ 发现 {len(issues)} 个问题:")
        print()
        for issue in issues:
            print(f"  {issue}")
        print()
        print("💡 修复建议:")
        print("  - app.crew.agents → app.agents.runners")
        print("  - app.db.repository → app.db.repositories")
        print("  - app.rules.risk_rules_optimized → app.rules.engine")
        print("  - app.crew.schema_validator → app.crew.schemas")
        sys.exit(1)
    else:
        print("✅ 所有导入检查通过!")
        print()
        print("📝 检查项:")
        print("  ✓ 无旧的 app.crew.agents 导入")
        print("  ✓ 无旧的 app.db.repository 导入")
        print("  ✓ 无旧的 risk_rules_optimized 导入")
        print("  ✓ 无旧的 schema_validator 导入")
        sys.exit(0)


if __name__ == "__main__":
    main()
