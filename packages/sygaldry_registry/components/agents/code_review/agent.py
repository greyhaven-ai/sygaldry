"""Code Review Agent - Automated code review with security and best practices."""

from __future__ import annotations

from mirascope import llm
from pydantic import BaseModel, Field
from typing import Literal, Optional

try:
    from lilypad import trace
except ImportError:
    def trace():
        def decorator(func):
            return func
        return decorator

# Import static analysis tool
try:
    from ...tools.static_analysis.tool import analyze_code, run_pylint, run_mypy, run_bandit
    STATIC_ANALYSIS_AVAILABLE = True
except ImportError:
    analyze_code = None
    run_pylint = None
    run_mypy = None
    run_bandit = None
    STATIC_ANALYSIS_AVAILABLE = False

# Import GitHub Issues tool
try:
    from ...tools.github_issues.tool import create_issue, search_issues
    GITHUB_AVAILABLE = True
except ImportError:
    create_issue = None
    search_issues = None
    GITHUB_AVAILABLE = False


class CodeIssue(BaseModel):
    """A code issue found during review."""

    severity: Literal["critical", "high", "medium", "low", "info"] = Field(..., description="Issue severity")
    category: str = Field(..., description="Category (e.g., 'security', 'performance', 'style')")
    description: str = Field(..., description="Description of the issue")
    # Note: All fields must be required for OpenAI schema validation
    line_number: int | None = Field(..., description="Line number where issue occurs (null if not applicable)")
    suggestion: str = Field(..., description="Suggested fix or improvement")
    code_snippet: str | None = Field(..., description="Relevant code snippet (null if not applicable)")


class CodeReviewResult(BaseModel):
    """Complete code review result."""

    # Note: Field(...) without description for nested models to avoid OpenAI schema error
    # OpenAI rejects $ref with additional keywords like 'description'
    issues: list[CodeIssue] = Field(...)
    summary: str = Field(..., description="Review summary")
    overall_quality: Literal["excellent", "good", "fair", "needs_improvement", "poor"] = Field(
        ..., description="Overall code quality rating"
    )
    security_score: int = Field(..., ge=0, le=100, description="Security score (0-100)")
    maintainability_score: int = Field(..., ge=0, le=100, description="Maintainability score")
    performance_score: int = Field(..., ge=0, le=100, description="Performance score")
    recommendations: list[str] = Field(..., description="General recommendations")


# Rebuild models to resolve forward references
CodeIssue.model_rebuild()
CodeReviewResult.model_rebuild()


@llm.call(provider="openai:completions", model_id="gpt-4o-mini", format=CodeReviewResult)
async def _llm_review_code(
    code: str,
    language: str,
    review_focus: Optional[list[str]],
    strict_mode: bool,
    static_analysis_results: Optional[str] = None
) -> str:
    """Internal LLM review function."""
    focus = f"\nFocus areas: {', '.join(review_focus)}" if review_focus else ""
    strictness = "Apply strict standards and flag even minor issues." if strict_mode else "Focus on significant issues."

    static_results = ""
    if static_analysis_results:
        static_results = f"\n\n**Static Analysis Results:**\n{static_analysis_results}\n\nConsider these automated findings in your review."

    return f"""You are an expert code reviewer. Review this {language} code thoroughly.

Code:
```{language}
{code}
```
{focus}

{strictness}
{static_results}

Review for:
1. **Security**: SQL injection, XSS, authentication issues, secrets in code
2. **Performance**: Inefficiencies, N+1 queries, memory leaks
3. **Best Practices**: Code structure, naming, error handling
4. **Maintainability**: Code clarity, documentation, complexity
5. **Bugs**: Potential bugs, edge cases, race conditions

For each issue provide:
- Severity level
- Category
- Clear description
- Line number if applicable
- Specific suggestion for improvement

Also provide:
- Summary of findings
- Overall quality rating
- Security, maintainability, and performance scores (0-100)
- General recommendations"""


@trace()
async def review_code(
    code: str,
    language: str = "python",
    file_path: Optional[str] = None,
    review_focus: Optional[list[str]] = None,
    strict_mode: bool = False,
    run_static_analysis: bool = True,
    repo: Optional[str] = None,
    create_github_issues: bool = False,
) -> CodeReviewResult:
    """
    Review code for security, performance, and best practices.

    Args:
        code: Code to review
        language: Programming language
        file_path: Optional file path (enables static analysis for Python files)
        review_focus: Specific areas to focus on (e.g., ['security', 'performance'])
        strict_mode: Whether to apply strict review standards
        run_static_analysis: Whether to run automated static analysis (Python only)
        repo: Optional GitHub repository (format: "owner/repo") for creating issues
        create_github_issues: Whether to create GitHub issues for critical/high severity findings

    Returns:
        CodeReviewResult with issues and recommendations

    Example:
        ```python
        result = await review_code(
            code=my_code,
            language="python",
            file_path="/path/to/file.py",
            run_static_analysis=True,
            repo="myorg/myrepo",
            create_github_issues=True
        )
        ```
    """
    static_analysis_summary = None

    # Run static analysis for Python code if requested
    if run_static_analysis and STATIC_ANALYSIS_AVAILABLE and language == "python" and file_path:
        try:
            analysis_result = await analyze_code(file_path)

            # Format static analysis results
            issues_summary = []
            if analysis_result.pylint_issues:
                issues_summary.append(f"Pylint: {len(analysis_result.pylint_issues)} issues")
            if analysis_result.security_issues:
                issues_summary.append(f"Security (Bandit): {len(analysis_result.security_issues)} issues")
            if analysis_result.type_errors:
                issues_summary.append(f"Type errors (mypy): {len(analysis_result.type_errors)} type issues")

            if issues_summary:
                static_analysis_summary = "; ".join(issues_summary)
        except Exception:
            # If static analysis fails, continue with LLM review only
            pass

    # Perform LLM code review
    response = await _llm_review_code(
        code=code,
        language=language,
        review_focus=review_focus,
        strict_mode=strict_mode,
        static_analysis_results=static_analysis_summary
    )
    result = response.parse()

    # Optionally create GitHub issues for critical/high severity findings
    if create_github_issues and GITHUB_AVAILABLE and repo:
        critical_high_issues = [
            issue for issue in result.issues
            if issue.severity in ["critical", "high"]
        ]

        for issue in critical_high_issues:
            try:
                issue_title = f"[Code Review] {issue.category}: {issue.description[:80]}"

                # Build code snippet section
                code_snippet_section = ""
                if issue.code_snippet:
                    code_snippet_section = f"### Code Snippet\n```{language}\n{issue.code_snippet}\n```"

                issue_body = f"""## Code Review Finding

**Severity:** {issue.severity}
**Category:** {issue.category}

### Description
{issue.description}

### Location
{f"File: {file_path}, Line: {issue.line_number}" if file_path and issue.line_number else "See code snippet below"}

### Suggestion
{issue.suggestion}

{code_snippet_section}

---
*This issue was automatically created by the Code Review Agent*
"""
                await create_issue(
                    repo=repo,
                    title=issue_title,
                    body=issue_body,
                    labels=["code-review", issue.severity, issue.category.lower()]
                )
            except Exception:
                # If issue creation fails, continue with review
                pass

    return result


@trace()
async def quick_security_check(code: str, language: str = "python") -> list[dict]:
    """Quick security-focused code review."""
    result = await review_code(code, language, review_focus=["security"], strict_mode=True)
    return [
        {"severity": issue.severity, "description": issue.description, "suggestion": issue.suggestion}
        for issue in result.issues
        if issue.category.lower() == "security"
    ]
