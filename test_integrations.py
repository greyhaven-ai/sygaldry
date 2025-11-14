"""Simple integration test to verify agent-tool integrations."""

import sys
from pathlib import Path

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent / "packages"))

def test_bug_triage_imports():
    """Test bug_triage_agent with github_issues integration."""
    try:
        from sygaldry_registry.components.agents.bug_triage.agent import (
            triage_bug,
            GITHUB_AVAILABLE
        )
        print("✓ bug_triage_agent imports successfully")
        print(f"  - GitHub Issues tool available: {GITHUB_AVAILABLE}")
        return True
    except Exception as e:
        print(f"✗ bug_triage_agent import failed: {e}")
        return False


def test_code_review_imports():
    """Test code_review_agent with static_analysis and github_issues integration."""
    try:
        from sygaldry_registry.components.agents.code_review.agent import (
            review_code,
            STATIC_ANALYSIS_AVAILABLE,
            GITHUB_AVAILABLE
        )
        print("✓ code_review_agent imports successfully")
        print(f"  - Static Analysis tool available: {STATIC_ANALYSIS_AVAILABLE}")
        print(f"  - GitHub Issues tool available: {GITHUB_AVAILABLE}")
        return True
    except Exception as e:
        print(f"✗ code_review_agent import failed: {e}")
        return False


def test_financial_statement_analyzer_imports():
    """Test financial_statement_analyzer with sec_edgar integration."""
    try:
        from sygaldry_registry.components.agents.financial_statement_analyzer.agent import (
            analyze_financial_statements,
            fetch_sec_edgar_data,
            SEC_EDGAR_AVAILABLE
        )
        print("✓ financial_statement_analyzer imports successfully")
        print(f"  - SEC EDGAR tool available: {SEC_EDGAR_AVAILABLE}")
        return True
    except Exception as e:
        print(f"✗ financial_statement_analyzer import failed: {e}")
        return False


def test_customer_support_imports():
    """Test customer_support_agent with helpdesk_integration."""
    try:
        from sygaldry_registry.components.agents.customer_support.agent import (
            analyze_support_ticket,
            analyze_and_create_ticket,
            analyze_and_respond,
            update_ticket_from_analysis,
            HELPDESK_AVAILABLE
        )
        print("✓ customer_support_agent imports successfully")
        print(f"  - Helpdesk Integration tool available: {HELPDESK_AVAILABLE}")
        return True
    except Exception as e:
        print(f"✗ customer_support_agent import failed: {e}")
        return False


def test_tool_imports():
    """Test tool imports."""
    results = []

    # Test github_issues tool
    try:
        from sygaldry_registry.components.tools.github_issues.tool import (
            search_issues,
            get_issue,
            create_issue
        )
        print("✓ github_issues tool imports successfully")
        results.append(True)
    except Exception as e:
        print(f"✗ github_issues tool import failed: {e}")
        results.append(False)

    # Test static_analysis tool
    try:
        from sygaldry_registry.components.tools.static_analysis.tool import (
            analyze_code,
            run_pylint
        )
        print("✓ static_analysis tool imports successfully")
        results.append(True)
    except Exception as e:
        print(f"✗ static_analysis tool import failed: {e}")
        results.append(False)

    # Test sec_edgar tool
    try:
        from sygaldry_registry.components.tools.sec_edgar.tool import (
            get_company_info,
            get_company_filings
        )
        print("✓ sec_edgar tool imports successfully")
        results.append(True)
    except Exception as e:
        print(f"✗ sec_edgar tool import failed: {e}")
        results.append(False)

    # Test helpdesk_integration tool
    try:
        from sygaldry_registry.components.tools.helpdesk_integration.tool import (
            create_ticket,
            get_ticket,
            update_ticket
        )
        print("✓ helpdesk_integration tool imports successfully")
        results.append(True)
    except Exception as e:
        print(f"✗ helpdesk_integration tool import failed: {e}")
        results.append(False)

    return all(results)


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Agent-Tool Integrations")
    print("=" * 60)

    print("\n--- Testing Tools ---")
    tools_ok = test_tool_imports()

    print("\n--- Testing Agent Integrations ---")
    bug_triage_ok = test_bug_triage_imports()
    code_review_ok = test_code_review_imports()
    financial_ok = test_financial_statement_analyzer_imports()
    customer_support_ok = test_customer_support_imports()

    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)

    all_passed = all([
        tools_ok,
        bug_triage_ok,
        code_review_ok,
        financial_ok,
        customer_support_ok
    ])

    if all_passed:
        print("✓ All integrations passed!")
        sys.exit(0)
    else:
        print("✗ Some integrations failed")
        sys.exit(1)
