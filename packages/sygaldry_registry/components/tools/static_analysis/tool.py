"""Static Analysis Tool for Python code quality and security analysis.

This tool provides functions to run various static analysis tools including
pylint, flake8, mypy, bandit, and semgrep for comprehensive code analysis.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Literal, Optional


class CodeIssue(BaseModel):
    """Code quality issue from static analysis."""

    file_path: str = Field(..., description="File path where issue was found")
    line: Optional[int] = Field(None, description="Line number")
    column: Optional[int] = Field(None, description="Column number")
    severity: Literal["error", "warning", "info", "convention", "refactor"] = Field(
        ..., description="Issue severity level"
    )
    category: str = Field(..., description="Issue category/rule code")
    message: str = Field(..., description="Issue description")
    tool: Literal["pylint", "flake8", "mypy", "bandit", "semgrep"] = Field(
        ..., description="Tool that detected the issue"
    )


class SecurityIssue(BaseModel):
    """Security vulnerability from security analysis."""

    file_path: str = Field(..., description="File path where vulnerability was found")
    line: Optional[int] = Field(None, description="Line number")
    severity: Literal["high", "medium", "low"] = Field(
        ..., description="Vulnerability severity"
    )
    confidence: Literal["high", "medium", "low"] = Field(
        ..., description="Confidence level"
    )
    cwe_id: Optional[str] = Field(None, description="CWE identifier")
    issue_id: str = Field(..., description="Issue identifier/rule ID")
    message: str = Field(..., description="Vulnerability description")
    code_snippet: Optional[str] = Field(None, description="Vulnerable code snippet")


class AnalysisResult(BaseModel):
    """Complete analysis result from all tools."""

    target: str = Field(..., description="Analyzed file or directory path")
    tools_run: list[str] = Field(..., description="Tools successfully executed")
    tools_failed: list[str] = Field(default_factory=list, description="Tools that failed")
    code_issues: list[CodeIssue] = Field(
        default_factory=list, description="Code quality issues"
    )
    security_issues: list[SecurityIssue] = Field(
        default_factory=list, description="Security vulnerabilities"
    )
    total_issues: int = Field(..., description="Total number of issues found")
    summary: dict[str, int] = Field(
        ..., description="Summary statistics by severity/tool"
    )


def _check_tool_available(tool_name: str) -> bool:
    """Check if a static analysis tool is available."""
    try:
        result = subprocess.run(
            [tool_name, "--version"],
            capture_output=True,
            text=True,
            timeout=5.0
        )
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def run_pylint(file_path: str) -> list[CodeIssue]:
    """
    Run pylint analysis on a Python file or directory.

    Args:
        file_path: Path to Python file or directory to analyze

    Returns:
        List of CodeIssue objects from pylint analysis

    Example:
        ```python
        issues = run_pylint("myproject/main.py")
        for issue in issues:
            print(f"{issue.severity}: {issue.message}")
        ```
    """
    if not _check_tool_available("pylint"):
        raise RuntimeError(
            "pylint is not available. Install with: pip install pylint"
        )

    try:
        result = subprocess.run(
            ["pylint", "--output-format=json", file_path],
            capture_output=True,
            text=True,
            timeout=60.0
        )

        # pylint returns non-zero if issues found, which is expected
        if result.stdout:
            data = json.loads(result.stdout)
        else:
            return []

        issues = []
        for item in data:
            # Map pylint types to our severity levels
            severity_map = {
                "error": "error",
                "warning": "warning",
                "convention": "convention",
                "refactor": "refactor",
                "fatal": "error",
                "info": "info"
            }

            issue = CodeIssue(
                file_path=item.get("path", file_path),
                line=item.get("line"),
                column=item.get("column"),
                severity=severity_map.get(item.get("type", "warning"), "warning"),
                category=item.get("message-id", "unknown"),
                message=item.get("message", ""),
                tool="pylint"
            )
            issues.append(issue)

        return issues

    except subprocess.TimeoutExpired:
        raise RuntimeError(f"pylint analysis timed out for {file_path}")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse pylint output: {e}")
    except Exception as e:
        raise RuntimeError(f"pylint analysis failed: {e}")


def run_flake8(file_path: str) -> list[CodeIssue]:
    """
    Run flake8 analysis on a Python file or directory.

    Args:
        file_path: Path to Python file or directory to analyze

    Returns:
        List of CodeIssue objects from flake8 analysis

    Example:
        ```python
        issues = run_flake8("myproject/")
        print(f"Found {len(issues)} style issues")
        ```
    """
    if not _check_tool_available("flake8"):
        raise RuntimeError(
            "flake8 is not available. Install with: pip install flake8"
        )

    try:
        result = subprocess.run(
            ["flake8", "--format=json", file_path],
            capture_output=True,
            text=True,
            timeout=60.0
        )

        # flake8 with json formatter
        if result.stdout:
            data = json.loads(result.stdout)
        else:
            return []

        issues = []
        for file_key, file_issues in data.items():
            for item in file_issues:
                # Map flake8 codes to severity
                code = item.get("code", "")
                if code.startswith("E"):
                    severity = "error"
                elif code.startswith("W"):
                    severity = "warning"
                elif code.startswith("F"):
                    severity = "error"
                else:
                    severity = "info"

                issue = CodeIssue(
                    file_path=file_key,
                    line=item.get("line_number"),
                    column=item.get("column_number"),
                    severity=severity,
                    category=code,
                    message=item.get("text", ""),
                    tool="flake8"
                )
                issues.append(issue)

        return issues

    except subprocess.TimeoutExpired:
        raise RuntimeError(f"flake8 analysis timed out for {file_path}")
    except json.JSONDecodeError:
        # Fallback to parsing plain output
        return _parse_flake8_plain_output(result.stdout, file_path)
    except Exception as e:
        raise RuntimeError(f"flake8 analysis failed: {e}")


def _parse_flake8_plain_output(output: str, file_path: str) -> list[CodeIssue]:
    """Parse flake8 plain text output as fallback."""
    issues = []
    for line in output.strip().split("\n"):
        if not line:
            continue

        # Format: path:line:col: code message
        parts = line.split(":", 3)
        if len(parts) >= 4:
            file_part = parts[0]
            line_num = int(parts[1]) if parts[1].isdigit() else None
            col_num = int(parts[2]) if parts[2].isdigit() else None
            message_part = parts[3].strip()

            # Extract code and message
            code = message_part.split()[0] if message_part else "unknown"
            message = message_part[len(code):].strip() if len(message_part) > len(code) else message_part

            severity = "error" if code.startswith(("E", "F")) else "warning"

            issues.append(CodeIssue(
                file_path=file_part,
                line=line_num,
                column=col_num,
                severity=severity,
                category=code,
                message=message,
                tool="flake8"
            ))

    return issues


def run_mypy(file_path: str) -> list[CodeIssue]:
    """
    Run mypy type checking on a Python file or directory.

    Args:
        file_path: Path to Python file or directory to analyze

    Returns:
        List of CodeIssue objects from mypy analysis

    Example:
        ```python
        issues = run_mypy("myproject/")
        type_errors = [i for i in issues if i.severity == "error"]
        print(f"Found {len(type_errors)} type errors")
        ```
    """
    if not _check_tool_available("mypy"):
        raise RuntimeError(
            "mypy is not available. Install with: pip install mypy"
        )

    try:
        result = subprocess.run(
            ["mypy", "--show-column-numbers", "--no-error-summary", file_path],
            capture_output=True,
            text=True,
            timeout=60.0
        )

        issues = []
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue

            # Format: path:line:col: severity: message
            parts = line.split(":", 4)
            if len(parts) >= 4:
                file_part = parts[0]
                line_num = int(parts[1]) if parts[1].isdigit() else None
                col_num = int(parts[2]) if parts[2].isdigit() else None
                severity_part = parts[3].strip().lower()
                message = parts[4].strip() if len(parts) > 4 else parts[3].strip()

                # Map mypy severity
                if severity_part in ("error", "warning", "note"):
                    severity = "error" if severity_part == "error" else "warning"
                else:
                    severity = "error"
                    message = severity_part + " " + message if len(parts) > 4 else severity_part

                issue = CodeIssue(
                    file_path=file_part,
                    line=line_num,
                    column=col_num,
                    severity=severity,
                    category="type-check",
                    message=message,
                    tool="mypy"
                )
                issues.append(issue)

        return issues

    except subprocess.TimeoutExpired:
        raise RuntimeError(f"mypy analysis timed out for {file_path}")
    except Exception as e:
        raise RuntimeError(f"mypy analysis failed: {e}")


def run_bandit(file_path: str) -> list[SecurityIssue]:
    """
    Run bandit security scanning on a Python file or directory.

    Args:
        file_path: Path to Python file or directory to analyze

    Returns:
        List of SecurityIssue objects from bandit analysis

    Example:
        ```python
        issues = run_bandit("myproject/")
        high_severity = [i for i in issues if i.severity == "high"]
        print(f"Found {len(high_severity)} high-severity vulnerabilities")
        ```
    """
    if not _check_tool_available("bandit"):
        raise RuntimeError(
            "bandit is not available. Install with: pip install bandit"
        )

    try:
        # Check if path is a directory or file
        path_obj = Path(file_path)
        if path_obj.is_dir():
            cmd = ["bandit", "-r", "-f", "json", file_path]
        else:
            cmd = ["bandit", "-f", "json", file_path]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60.0
        )

        # bandit returns non-zero if issues found
        if result.stdout:
            data = json.loads(result.stdout)
        else:
            return []

        issues = []
        for item in data.get("results", []):
            # Map bandit severity and confidence
            severity_map = {"HIGH": "high", "MEDIUM": "medium", "LOW": "low"}
            confidence_map = {"HIGH": "high", "MEDIUM": "medium", "LOW": "low"}

            issue = SecurityIssue(
                file_path=item.get("filename", file_path),
                line=item.get("line_number"),
                severity=severity_map.get(
                    item.get("issue_severity", "MEDIUM"), "medium"
                ),
                confidence=confidence_map.get(
                    item.get("issue_confidence", "MEDIUM"), "medium"
                ),
                cwe_id=item.get("issue_cwe", {}).get("id") if isinstance(item.get("issue_cwe"), dict) else None,
                issue_id=item.get("test_id", "unknown"),
                message=item.get("issue_text", ""),
                code_snippet=item.get("code", "").strip()
            )
            issues.append(issue)

        return issues

    except subprocess.TimeoutExpired:
        raise RuntimeError(f"bandit analysis timed out for {file_path}")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse bandit output: {e}")
    except Exception as e:
        raise RuntimeError(f"bandit analysis failed: {e}")


def run_semgrep(file_path: str, config: str = "auto") -> list[SecurityIssue]:
    """
    Run semgrep security and pattern scanning.

    Args:
        file_path: Path to Python file or directory to analyze
        config: Semgrep config (auto, p/security-audit, p/owasp-top-ten, etc.)

    Returns:
        List of SecurityIssue objects from semgrep analysis

    Example:
        ```python
        issues = run_semgrep("myproject/", config="p/security-audit")
        print(f"Found {len(issues)} security patterns")
        ```
    """
    if not _check_tool_available("semgrep"):
        raise RuntimeError(
            "semgrep is not available. Install with: pip install semgrep"
        )

    try:
        result = subprocess.run(
            ["semgrep", "--config", config, "--json", file_path],
            capture_output=True,
            text=True,
            timeout=120.0
        )

        if result.stdout:
            data = json.loads(result.stdout)
        else:
            return []

        issues = []
        for item in data.get("results", []):
            # Map semgrep severity
            severity_map = {
                "ERROR": "high",
                "WARNING": "medium",
                "INFO": "low"
            }

            severity_str = item.get("extra", {}).get("severity", "WARNING")

            issue = SecurityIssue(
                file_path=item.get("path", file_path),
                line=item.get("start", {}).get("line"),
                severity=severity_map.get(severity_str, "medium"),
                confidence="high",  # semgrep patterns are generally high confidence
                cwe_id=None,  # semgrep doesn't always map to CWE
                issue_id=item.get("check_id", "unknown"),
                message=item.get("extra", {}).get("message", ""),
                code_snippet=item.get("extra", {}).get("lines", "").strip()
            )
            issues.append(issue)

        return issues

    except subprocess.TimeoutExpired:
        raise RuntimeError(f"semgrep analysis timed out for {file_path}")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse semgrep output: {e}")
    except Exception as e:
        raise RuntimeError(f"semgrep analysis failed: {e}")


def analyze_code(
    file_path: str,
    tools: list[str] = ["all"],
    include_security: bool = True
) -> AnalysisResult:
    """
    Run comprehensive code analysis with multiple tools.

    Args:
        file_path: Path to Python file or directory to analyze
        tools: List of tools to run (["all"], ["pylint", "flake8"], etc.)
        include_security: Whether to run security tools (bandit, semgrep)

    Returns:
        AnalysisResult with all findings

    Example:
        ```python
        # Run all tools
        result = analyze_code("myproject/")
        print(f"Total issues: {result.total_issues}")
        print(f"Tools run: {', '.join(result.tools_run)}")

        # Run specific tools only
        result = analyze_code(
            "myproject/main.py",
            tools=["pylint", "mypy"],
            include_security=False
        )

        # Check for high-severity security issues
        high_security = [
            i for i in result.security_issues
            if i.severity == "high"
        ]
        ```
    """
    # Normalize tools list
    if "all" in tools:
        code_tools = ["pylint", "flake8", "mypy"]
        security_tools = ["bandit"] if include_security else []
    else:
        available_code_tools = {"pylint", "flake8", "mypy"}
        available_security_tools = {"bandit", "semgrep"}

        code_tools = [t for t in tools if t in available_code_tools]
        security_tools = [
            t for t in tools
            if t in available_security_tools and include_security
        ]

    code_issues = []
    security_issues = []
    tools_run = []
    tools_failed = []

    # Run code quality tools
    for tool in code_tools:
        try:
            if tool == "pylint":
                issues = run_pylint(file_path)
                code_issues.extend(issues)
                tools_run.append("pylint")
            elif tool == "flake8":
                issues = run_flake8(file_path)
                code_issues.extend(issues)
                tools_run.append("flake8")
            elif tool == "mypy":
                issues = run_mypy(file_path)
                code_issues.extend(issues)
                tools_run.append("mypy")
        except Exception as e:
            tools_failed.append(f"{tool}: {str(e)}")

    # Run security tools
    for tool in security_tools:
        try:
            if tool == "bandit":
                issues = run_bandit(file_path)
                security_issues.extend(issues)
                tools_run.append("bandit")
            elif tool == "semgrep":
                issues = run_semgrep(file_path)
                security_issues.extend(issues)
                tools_run.append("semgrep")
        except Exception as e:
            tools_failed.append(f"{tool}: {str(e)}")

    # Calculate summary statistics
    total_issues = len(code_issues) + len(security_issues)

    summary = {
        "total": total_issues,
        "code_issues": len(code_issues),
        "security_issues": len(security_issues),
    }

    # Count by severity
    for issue in code_issues:
        key = f"code_{issue.severity}"
        summary[key] = summary.get(key, 0) + 1

    for issue in security_issues:
        key = f"security_{issue.severity}"
        summary[key] = summary.get(key, 0) + 1

    # Count by tool
    for tool in tools_run:
        tool_issues = [i for i in code_issues if i.tool == tool]
        summary[f"{tool}_issues"] = len(tool_issues)

    return AnalysisResult(
        target=file_path,
        tools_run=tools_run,
        tools_failed=tools_failed,
        code_issues=code_issues,
        security_issues=security_issues,
        total_issues=total_issues,
        summary=summary
    )
