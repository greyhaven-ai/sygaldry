"""Verify Python syntax for integrated agents."""

import ast
from pathlib import Path


def verify_syntax(file_path: Path) -> tuple[bool, str]:
    """Verify Python file syntax."""
    try:
        with open(file_path, 'r') as f:
            code = f.read()
        ast.parse(code)
        return True, "OK"
    except SyntaxError as e:
        return False, f"Syntax error: {e}"
    except Exception as e:
        return False, f"Error: {e}"


def main():
    """Verify syntax of all integrated agents and tools."""
    base_path = Path(__file__).parent / "packages" / "sygaldry_registry" / "components"

    files_to_check = [
        # Agents
        "agents/bug_triage/agent.py",
        "agents/code_review/agent.py",
        "agents/financial_statement_analyzer/agent.py",
        "agents/customer_support/agent.py",
        # Tools
        "tools/github_issues/tool.py",
        "tools/static_analysis/tool.py",
        "tools/sec_edgar/tool.py",
        "tools/helpdesk_integration/tool.py",
    ]

    print("=" * 60)
    print("Verifying Python Syntax")
    print("=" * 60)

    all_ok = True
    for file_rel in files_to_check:
        file_path = base_path / file_rel
        ok, message = verify_syntax(file_path)
        status = "✓" if ok else "✗"
        print(f"{status} {file_rel}: {message}")
        all_ok = all_ok and ok

    print("\n" + "=" * 60)
    if all_ok:
        print("✓ All files have valid Python syntax!")
    else:
        print("✗ Some files have syntax errors")
    print("=" * 60)

    return 0 if all_ok else 1


if __name__ == "__main__":
    exit(main())
