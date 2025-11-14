# Static Analysis Tool

## Overview

Comprehensive Python static analysis tool that runs multiple code quality and security scanning tools to detect issues, type errors, and vulnerabilities. Provides structured results with Pydantic models for easy integration with agents.

## Features

- **Code Quality Analysis**: Run pylint, flake8, and mypy for comprehensive code quality checks
- **Security Scanning**: Detect vulnerabilities with bandit and semgrep
- **Structured Results**: Pydantic models for CodeIssue, SecurityIssue, and AnalysisResult
- **Graceful Degradation**: Missing tools are skipped automatically
- **Flexible Execution**: Run all tools or select specific ones
- **Severity Levels**: Clear severity categorization (error, warning, info, etc.)
- **Detailed Reporting**: Line numbers, categories, and code snippets

## Installation

```bash
sygaldry add static_analysis
```

Install static analysis tools:

```bash
# Core tools
pip install pylint flake8 mypy bandit

# Optional advanced security scanning
pip install semgrep
```

## Quick Start

```python
from static_analysis import analyze_code, run_pylint, run_bandit

# Run all available tools
result = analyze_code("myproject/")
print(f"Total issues: {result.total_issues}")
print(f"Code issues: {len(result.code_issues)}")
print(f"Security issues: {len(result.security_issues)}")

# Run specific tools only
result = analyze_code(
    "myproject/main.py",
    tools=["pylint", "mypy"],
    include_security=False
)

# Check for critical issues
errors = [i for i in result.code_issues if i.severity == "error"]
high_security = [i for i in result.security_issues if i.severity == "high"]

print(f"Errors: {len(errors)}")
print(f"High-severity vulnerabilities: {len(high_security)}")
```

## Functions

### analyze_code()

Run comprehensive code analysis with multiple tools.

**Parameters:**
- `file_path` (str): Path to Python file or directory
- `tools` (list[str]): Tools to run (["all"], ["pylint", "flake8"], etc.)
- `include_security` (bool): Whether to run security tools

**Returns:** `AnalysisResult`

**Example:**
```python
result = analyze_code(
    "myproject/",
    tools=["all"],
    include_security=True
)

# Access results
for issue in result.code_issues:
    print(f"{issue.file_path}:{issue.line} - {issue.message}")

for vuln in result.security_issues:
    print(f"[{vuln.severity}] {vuln.message}")
```

### run_pylint()

Run pylint analysis for comprehensive code quality checks.

**Parameters:**
- `file_path` (str): Path to Python file or directory

**Returns:** `list[CodeIssue]`

**Example:**
```python
issues = run_pylint("myproject/main.py")

# Filter by severity
errors = [i for i in issues if i.severity == "error"]
warnings = [i for i in issues if i.severity == "warning"]
conventions = [i for i in issues if i.severity == "convention"]
```

### run_flake8()

Run flake8 for PEP 8 style checking.

**Parameters:**
- `file_path` (str): Path to Python file or directory

**Returns:** `list[CodeIssue]`

**Example:**
```python
issues = run_flake8("myproject/")

# Group by category
by_category = {}
for issue in issues:
    by_category.setdefault(issue.category, []).append(issue)
```

### run_mypy()

Run mypy for static type checking.

**Parameters:**
- `file_path` (str): Path to Python file or directory

**Returns:** `list[CodeIssue]`

**Example:**
```python
issues = run_mypy("myproject/")

# Find type errors
type_errors = [i for i in issues if "type" in i.message.lower()]
```

### run_bandit()

Run bandit security scanner for vulnerability detection.

**Parameters:**
- `file_path` (str): Path to Python file or directory

**Returns:** `list[SecurityIssue]`

**Example:**
```python
vulnerabilities = run_bandit("myproject/")

# Check high-confidence, high-severity issues
critical = [
    v for v in vulnerabilities
    if v.severity == "high" and v.confidence == "high"
]

for vuln in critical:
    print(f"{vuln.file_path}:{vuln.line}")
    print(f"  Issue: {vuln.message}")
    print(f"  Code: {vuln.code_snippet}")
```

### run_semgrep()

Run semgrep for advanced pattern-based security scanning.

**Parameters:**
- `file_path` (str): Path to Python file or directory
- `config` (str): Semgrep config (auto, p/security-audit, p/owasp-top-ten, etc.)

**Returns:** `list[SecurityIssue]`

**Example:**
```python
# Use OWASP Top 10 rules
vulnerabilities = run_semgrep(
    "myproject/",
    config="p/owasp-top-ten"
)

# Use security audit rules
vulnerabilities = run_semgrep(
    "myproject/",
    config="p/security-audit"
)
```

## Data Models

### CodeIssue

Represents a code quality issue.

**Fields:**
- `file_path` (str): File where issue was found
- `line` (int | None): Line number
- `column` (int | None): Column number
- `severity` (str): error, warning, info, convention, refactor
- `category` (str): Issue category/rule code
- `message` (str): Issue description
- `tool` (str): Tool that detected the issue

### SecurityIssue

Represents a security vulnerability.

**Fields:**
- `file_path` (str): File where vulnerability was found
- `line` (int | None): Line number
- `severity` (str): high, medium, low
- `confidence` (str): high, medium, low
- `cwe_id` (str | None): CWE identifier
- `issue_id` (str): Issue identifier/rule ID
- `message` (str): Vulnerability description
- `code_snippet` (str | None): Vulnerable code snippet

### AnalysisResult

Complete analysis result from all tools.

**Fields:**
- `target` (str): Analyzed file or directory path
- `tools_run` (list[str]): Tools successfully executed
- `tools_failed` (list[str]): Tools that failed
- `code_issues` (list[CodeIssue]): Code quality issues
- `security_issues` (list[SecurityIssue]): Security vulnerabilities
- `total_issues` (int): Total number of issues
- `summary` (dict[str, int]): Summary statistics

## Integration Examples

### Code Review Agent

```python
from static_analysis import analyze_code

def review_code(file_path: str) -> str:
    """Automated code review with static analysis."""
    result = analyze_code(file_path)

    if result.total_issues == 0:
        return "Code looks good! No issues found."

    report = [f"Found {result.total_issues} issues:\n"]

    # Report by severity
    if result.summary.get("code_error", 0) > 0:
        report.append(f"- {result.summary['code_error']} errors")
    if result.summary.get("code_warning", 0) > 0:
        report.append(f"- {result.summary['code_warning']} warnings")
    if result.summary.get("security_high", 0) > 0:
        report.append(f"- {result.summary['security_high']} high-severity security issues")

    return "\n".join(report)
```

### CI/CD Integration

```python
from static_analysis import analyze_code
import sys

def ci_check(path: str, fail_on_error: bool = True) -> int:
    """Run static analysis in CI/CD pipeline."""
    result = analyze_code(path)

    print(f"Analysis complete: {result.total_issues} issues found")
    print(f"Tools run: {', '.join(result.tools_run)}")

    if result.tools_failed:
        print(f"Tools failed: {', '.join(result.tools_failed)}")

    # Count critical issues
    errors = [i for i in result.code_issues if i.severity == "error"]
    high_security = [i for i in result.security_issues if i.severity == "high"]

    critical_count = len(errors) + len(high_security)

    if critical_count > 0:
        print(f"\nCRITICAL: {critical_count} blocking issues found")
        for issue in errors[:5]:  # Show first 5
            print(f"  {issue.file_path}:{issue.line} - {issue.message}")
        for issue in high_security[:5]:
            print(f"  {issue.file_path}:{issue.line} - {issue.message}")

        if fail_on_error:
            return 1

    return 0

if __name__ == "__main__":
    sys.exit(ci_check("src/"))
```

### Security Audit

```python
from static_analysis import run_bandit, run_semgrep

def security_audit(path: str):
    """Comprehensive security audit."""
    print("Running security audit...")

    # Run bandit
    bandit_issues = run_bandit(path)
    print(f"\nBandit found {len(bandit_issues)} issues")

    # Run semgrep with multiple rulesets
    configs = ["p/security-audit", "p/owasp-top-ten"]
    all_semgrep_issues = []

    for config in configs:
        try:
            issues = run_semgrep(path, config=config)
            all_semgrep_issues.extend(issues)
            print(f"Semgrep ({config}): {len(issues)} issues")
        except Exception as e:
            print(f"Semgrep ({config}) failed: {e}")

    # Combine and deduplicate
    all_issues = bandit_issues + all_semgrep_issues
    high_severity = [i for i in all_issues if i.severity == "high"]

    print(f"\nTotal security issues: {len(all_issues)}")
    print(f"High severity: {len(high_severity)}")

    return all_issues
```

## Error Handling

Tools handle errors gracefully:

- **Missing tools**: Skipped automatically, reported in `tools_failed`
- **Timeouts**: 60s for code tools, 120s for semgrep
- **Parse errors**: Fallback to plain text parsing where possible
- **Invalid paths**: Raises clear error messages

```python
result = analyze_code("myproject/")

if result.tools_failed:
    print("Some tools failed:")
    for failure in result.tools_failed:
        print(f"  {failure}")

# Still get results from successful tools
print(f"Successful tools: {', '.join(result.tools_run)}")
```

## Best Practices

1. **Start with all tools**: Use `analyze_code()` with default settings
2. **Filter results**: Focus on errors and high-severity issues first
3. **Progressive enhancement**: Add tools as needed (semgrep for advanced security)
4. **CI/CD integration**: Fail builds on errors and high-severity security issues
5. **Regular scanning**: Run analysis on every commit or PR
6. **Tool configuration**: Configure tools via their config files (.pylintrc, setup.cfg, etc.)

## License

MIT
