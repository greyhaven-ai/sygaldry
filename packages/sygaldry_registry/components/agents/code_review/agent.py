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


class CodeIssue(BaseModel):
    """A code issue found during review."""

    severity: Literal["critical", "high", "medium", "low", "info"] = Field(..., description="Issue severity")
    category: str = Field(..., description="Category (e.g., 'security', 'performance', 'style')")
    description: str = Field(..., description="Description of the issue")
    line_number: Optional[int] = Field(None, description="Line number where issue occurs")
    suggestion: str = Field(..., description="Suggested fix or improvement")
    code_snippet: Optional[str] = Field(None, description="Relevant code snippet")


class CodeReviewResult(BaseModel):
    """Complete code review result."""

    issues: list[CodeIssue] = Field(..., description="List of issues found")
    summary: str = Field(..., description="Review summary")
    overall_quality: Literal["excellent", "good", "fair", "needs_improvement", "poor"] = Field(
        ..., description="Overall code quality rating"
    )
    security_score: int = Field(..., ge=0, le=100, description="Security score (0-100)")
    maintainability_score: int = Field(..., ge=0, le=100, description="Maintainability score")
    performance_score: int = Field(..., ge=0, le=100, description="Performance score")
    recommendations: list[str] = Field(..., description="General recommendations")


@llm.call(provider="openai:completions", model_id="gpt-4o-mini", format=CodeReviewResult)
async def review_code(
    code: str,
    language: str = "python",
    review_focus: Optional[list[str]] = None,
    strict_mode: bool = False
) -> str:
    """
    Review code for security, performance, and best practices.

    Args:
        code: Code to review
        language: Programming language
        review_focus: Specific areas to focus on (e.g., ['security', 'performance'])
        strict_mode: Whether to apply strict review standards

    Returns:
        CodeReviewResult with issues and recommendations
    """
    focus = f"\nFocus areas: {', '.join(review_focus)}" if review_focus else ""
    strictness = "Apply strict standards and flag even minor issues." if strict_mode else "Focus on significant issues."

    return f"""You are an expert code reviewer. Review this {language} code thoroughly.

Code:
```{language}
{code}
```
{focus}

{strictness}

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
async def quick_security_check(code: str, language: str = "python") -> list[dict]:
    """Quick security-focused code review."""
    result = await review_code(code, language, review_focus=["security"], strict_mode=True)
    return [
        {"severity": issue.severity, "description": issue.description, "suggestion": issue.suggestion}
        for issue in result.issues
        if issue.category.lower() == "security"
    ]
