"""Bug Triage Agent for analyzing and prioritizing bug reports.

This agent analyzes bug reports to classify severity, priority, root cause,
and provide recommendations for reproduction and assignment.
"""

from __future__ import annotations

from mirascope import llm
from pydantic import BaseModel, Field
from typing import Literal, Optional

# Make lilypad optional
try:
    from lilypad import trace
    LILYPAD_AVAILABLE = True
except ImportError:
    # Fallback no-op decorator if lilypad not available
    def trace():
        def decorator(func):
            return func
        return decorator
    LILYPAD_AVAILABLE = False


class ComponentIdentification(BaseModel):
    """Identification of affected component/module."""

    component_name: str = Field(..., description="Name of the affected component or module")
    component_type: str = Field(..., description="Type of component (e.g., 'frontend', 'backend', 'database', 'api')")
    subcomponent: Optional[str] = Field(None, description="Specific subcomponent if applicable")
    file_paths: list[str] = Field(default_factory=list, description="Likely affected file paths or modules")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in component identification")


class SeverityClassification(BaseModel):
    """Bug severity classification."""

    severity: Literal["critical", "high", "medium", "low", "trivial"] = Field(
        ..., description="Severity level of the bug"
    )
    priority: Literal["urgent", "high", "medium", "low", "backlog"] = Field(
        ..., description="Priority for fixing the bug"
    )
    severity_reasoning: str = Field(..., description="Explanation of why this severity was assigned")
    priority_reasoning: str = Field(..., description="Explanation of why this priority was assigned")
    impact_scope: Literal["system_wide", "module_specific", "feature_specific", "edge_case"] = Field(
        ..., description="Scope of the bug's impact"
    )
    user_impact: str = Field(..., description="How this bug affects users")
    business_impact: str = Field(..., description="Potential business impact")


class RootCauseAnalysis(BaseModel):
    """Analysis of potential root causes."""

    likely_cause: str = Field(..., description="Most likely root cause of the bug")
    cause_category: Literal[
        "logic_error",
        "null_pointer",
        "race_condition",
        "memory_leak",
        "configuration",
        "integration",
        "dependency",
        "data_validation",
        "security",
        "performance",
        "ui_ux",
        "other"
    ] = Field(..., description="Category of the root cause")
    contributing_factors: list[str] = Field(
        default_factory=list, description="Other factors contributing to the bug"
    )
    similar_issues: list[str] = Field(
        default_factory=list, description="Similar issues or patterns observed"
    )
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in root cause analysis")


class ReproductionSteps(BaseModel):
    """Suggested steps to reproduce the bug."""

    steps: list[str] = Field(..., description="Step-by-step reproduction instructions")
    preconditions: list[str] = Field(default_factory=list, description="Required preconditions or setup")
    expected_behavior: str = Field(..., description="What should happen")
    actual_behavior: str = Field(..., description="What actually happens")
    reproducibility: Literal["always", "often", "sometimes", "rarely", "unable"] = Field(
        ..., description="How reliably the bug can be reproduced"
    )
    environment_details: list[str] = Field(
        default_factory=list, description="Relevant environment details (OS, browser, version, etc.)"
    )


class BugTriageResult(BaseModel):
    """Complete bug triage analysis result."""

    summary: str = Field(..., description="Executive summary of the bug")
    severity_classification: SeverityClassification = Field(..., description="Severity and priority assessment")
    component: ComponentIdentification = Field(..., description="Affected component identification")
    root_cause: RootCauseAnalysis = Field(..., description="Root cause analysis")
    reproduction: ReproductionSteps = Field(..., description="Reproduction steps")
    recommended_assignee: Optional[str] = Field(
        None, description="Recommended team or person to handle this bug"
    )
    estimated_effort: Literal["trivial", "small", "medium", "large", "extra_large"] = Field(
        ..., description="Estimated effort to fix"
    )
    dependencies: list[str] = Field(
        default_factory=list, description="Dependencies or blockers for fixing this bug"
    )
    related_bugs: list[str] = Field(
        default_factory=list, description="Related or duplicate bugs"
    )
    recommendations: list[str] = Field(
        default_factory=list, description="Recommendations for fixing and preventing similar bugs"
    )
    tags: list[str] = Field(default_factory=list, description="Relevant tags for categorization")


# Step 1: Classify severity and priority
@llm.call(
    provider="openai:completions",
    model_id="gpt-4o-mini",
    format=SeverityClassification,
)
async def classify_severity(bug_report: str, context: Optional[str] = None) -> str:
    """Classify bug severity and priority."""
    context_info = f"\n\nAdditional Context:\n{context}" if context else ""

    return f"""You are an expert software engineer performing bug triage.

Bug Report:
{bug_report}
{context_info}

Classify the severity and priority of this bug:

**Severity Levels:**
- **Critical**: System crash, data loss, security vulnerability, complete feature failure
- **High**: Major functionality broken, significant user impact, no workaround
- **Medium**: Feature partially broken, moderate user impact, workaround exists
- **Low**: Minor issue, cosmetic problem, minimal user impact
- **Trivial**: Typos, minor UI issues, negligible impact

**Priority Levels:**
- **Urgent**: Needs immediate attention, production down, critical security issue
- **High**: Should be fixed in next sprint, significant impact
- **Medium**: Should be fixed soon, moderate impact
- **Low**: Can wait, minor impact
- **Backlog**: Nice to have, minimal impact

**Impact Scope:**
- **system_wide**: Affects entire system
- **module_specific**: Affects specific module
- **feature_specific**: Affects specific feature
- **edge_case**: Only affects unusual scenarios

Provide detailed reasoning for your classification, explaining:
1. Why you chose this severity level
2. Why you chose this priority level
3. The scope of impact
4. How it affects users
5. Potential business impact"""


# Step 2: Identify affected component
@llm.call(
    provider="openai:completions",
    model_id="gpt-4o-mini",
    format=ComponentIdentification,
)
async def identify_component(bug_report: str, codebase_structure: Optional[str] = None) -> str:
    """Identify affected component or module."""
    structure_info = f"\n\nCodebase Structure:\n{codebase_structure}" if codebase_structure else ""

    return f"""You are an expert software engineer analyzing bug reports.

Bug Report:
{bug_report}
{structure_info}

Identify which component or module is affected by this bug:

1. **Component Name**: Identify the main component (e.g., "User Authentication", "Payment Processing", "Search Engine")
2. **Component Type**: Classify the type (frontend, backend, database, api, infrastructure, etc.)
3. **Subcomponent**: Identify specific subcomponent if applicable
4. **File Paths**: Suggest likely file paths or modules that may be affected
5. **Confidence**: Rate your confidence in this identification (0.0 to 1.0)

Consider:
- Stack traces or error messages
- Feature descriptions
- User actions leading to the bug
- System components mentioned
- Common architectural patterns"""


# Step 3: Analyze root cause
@llm.call(
    provider="openai:completions",
    model_id="gpt-4o-mini",
    format=RootCauseAnalysis,
)
async def analyze_root_cause(bug_report: str, component_info: str, severity_info: str) -> str:
    """Analyze potential root causes."""
    return f"""You are an expert software engineer analyzing root causes of bugs.

Bug Report:
{bug_report}

Component Information:
{component_info}

Severity Information:
{severity_info}

Analyze the potential root cause of this bug:

**Root Cause Categories:**
- **logic_error**: Incorrect business logic or algorithm
- **null_pointer**: Null/undefined reference errors
- **race_condition**: Concurrency or timing issues
- **memory_leak**: Memory management problems
- **configuration**: Configuration or settings issues
- **integration**: Problems with external systems or APIs
- **dependency**: Issues with third-party libraries or dependencies
- **data_validation**: Input validation or data handling issues
- **security**: Security vulnerabilities
- **performance**: Performance or scalability issues
- **ui_ux**: User interface or experience issues
- **other**: Other categories

Provide:
1. **Likely Cause**: Describe the most probable root cause
2. **Category**: Select the appropriate category
3. **Contributing Factors**: List other factors that may contribute
4. **Similar Issues**: Identify patterns or similar issues
5. **Confidence**: Rate your confidence in this analysis (0.0 to 1.0)

Base your analysis on:
- Error messages and stack traces
- User actions and triggers
- System behavior descriptions
- Known patterns and common issues"""


# Step 4: Generate reproduction steps
@llm.call(
    provider="openai:completions",
    model_id="gpt-4o-mini",
    format=ReproductionSteps,
)
async def generate_reproduction_steps(bug_report: str, component_info: str) -> str:
    """Generate detailed reproduction steps."""
    return f"""You are an expert QA engineer creating reproduction steps for bugs.

Bug Report:
{bug_report}

Component Information:
{component_info}

Create detailed steps to reproduce this bug:

**Reproduction Steps should include:**
1. **Steps**: Clear, numbered, step-by-step instructions
2. **Preconditions**: Any required setup or prerequisites
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Reproducibility**: How reliably the bug can be reproduced
   - always: 100% reproducible
   - often: >75% reproducible
   - sometimes: 25-75% reproducible
   - rarely: <25% reproducible
   - unable: Cannot determine from the report
6. **Environment Details**: OS, browser, version, configuration, etc.

Make steps:
- Clear and unambiguous
- Easy to follow
- Include specific values and inputs
- Note any important observations
- Include environment-specific details

If information is missing from the bug report, note what additional details are needed."""


# Main bug triage function
@trace()
async def triage_bug(
    bug_report: str,
    context: Optional[str] = None,
    codebase_structure: Optional[str] = None,
    include_recommendations: bool = True,
    llm_provider: str = "openai",
    model: str = "gpt-4o-mini",
) -> BugTriageResult:
    """
    Analyze and triage a bug report.

    This agent performs comprehensive bug analysis including:
    - Severity and priority classification
    - Component/module identification
    - Root cause analysis
    - Reproduction step generation
    - Effort estimation and recommendations

    Args:
        bug_report: The bug report text to analyze
        context: Optional additional context (product info, recent changes, etc.)
        codebase_structure: Optional codebase structure information
        include_recommendations: Whether to include fixing recommendations
        llm_provider: LLM provider to use
        model: Specific model to use

    Returns:
        BugTriageResult with complete analysis

    Example:
        ```python
        result = await triage_bug(
            bug_report="Users getting 500 error when logging in with Google OAuth",
            context="Recent deployment to production yesterday",
            include_recommendations=True
        )

        print(f"Severity: {result.severity_classification.severity}")
        print(f"Priority: {result.severity_classification.priority}")
        print(f"Component: {result.component.component_name}")
        print(f"Root Cause: {result.root_cause.likely_cause}")
        ```
    """
    # Step 1: Classify severity and priority
    severity_classification = await classify_severity(bug_report, context)

    # Step 2: Identify component
    component_identification = await identify_component(bug_report, codebase_structure)

    # Prepare info for root cause analysis
    component_summary = f"Component: {component_identification.component_name} ({component_identification.component_type})"
    severity_summary = f"Severity: {severity_classification.severity}, Priority: {severity_classification.priority}"

    # Step 3: Analyze root cause
    root_cause_analysis = await analyze_root_cause(bug_report, component_summary, severity_summary)

    # Step 4: Generate reproduction steps
    reproduction_steps = await generate_reproduction_steps(bug_report, component_summary)

    # Step 5: Generate summary and additional insights
    @llm.call(
        provider="openai:completions",
        model_id="gpt-4o-mini",
    )
    async def generate_summary_and_insights(
        bug_report: str,
        severity: str,
        priority: str,
        component: str,
        root_cause_category: str,
    ) -> str:
        """Generate executive summary."""
        return f"""You are an expert engineering manager reviewing a bug triage.

Bug Report:
{bug_report}

Triage Results:
- Severity: {severity}
- Priority: {priority}
- Component: {component}
- Root Cause Category: {root_cause_category}

Provide a concise executive summary (2-3 sentences) that:
1. Summarizes the issue in business/user terms
2. Highlights the key impact
3. States the urgency level

Keep it clear and suitable for non-technical stakeholders."""

    summary_text = await generate_summary_and_insights(
        bug_report=bug_report,
        severity=severity_classification.severity,
        priority=severity_classification.priority,
        component=component_identification.component_name,
        root_cause_category=root_cause_analysis.cause_category,
    )

    # Determine estimated effort
    effort = "medium"
    if severity_classification.severity == "critical":
        effort = "large"
    elif severity_classification.severity == "trivial":
        effort = "trivial"
    elif root_cause_analysis.cause_category in ["race_condition", "memory_leak", "security"]:
        effort = "large"
    elif root_cause_analysis.cause_category in ["configuration", "data_validation"]:
        effort = "small"

    # Determine recommended assignee
    assignee_mapping = {
        "frontend": "Frontend Team",
        "backend": "Backend Team",
        "database": "Database Team",
        "api": "API Team",
        "security": "Security Team",
        "infrastructure": "DevOps Team",
        "ui": "UI/UX Team",
    }
    recommended_assignee = assignee_mapping.get(
        component_identification.component_type.lower(),
        f"{component_identification.component_name} Team"
    )

    # Generate recommendations
    recommendations = []
    if include_recommendations:
        if severity_classification.severity in ["critical", "high"]:
            recommendations.append(f"Address immediately - {severity_classification.severity} severity bug affecting {severity_classification.impact_scope}")

        if root_cause_analysis.cause_category == "security":
            recommendations.append("Security review required before deploying fix")

        if reproduction_steps.reproducibility in ["rarely", "unable"]:
            recommendations.append("Gather more information to improve reproducibility - add logging or monitoring")

        if root_cause_analysis.similar_issues:
            recommendations.append("Review similar issues to identify systematic problems and prevent recurrence")

        recommendations.append(f"Estimated effort: {effort} - plan accordingly in sprint")

        # Add preventive recommendations
        if root_cause_analysis.cause_category == "data_validation":
            recommendations.append("Add input validation and error handling to prevent similar issues")
        elif root_cause_analysis.cause_category == "race_condition":
            recommendations.append("Review concurrency controls and add synchronization where needed")
        elif root_cause_analysis.cause_category == "null_pointer":
            recommendations.append("Add null checks and defensive programming practices")

    # Generate tags
    tags = [
        severity_classification.severity,
        severity_classification.priority,
        component_identification.component_type,
        root_cause_analysis.cause_category,
    ]
    if severity_classification.severity in ["critical", "high"]:
        tags.append("needs_attention")
    if root_cause_analysis.cause_category == "security":
        tags.append("security")

    return BugTriageResult(
        summary=summary_text,
        severity_classification=severity_classification,
        component=component_identification,
        root_cause=root_cause_analysis,
        reproduction=reproduction_steps,
        recommended_assignee=recommended_assignee,
        estimated_effort=effort,
        dependencies=[],
        related_bugs=[],
        recommendations=recommendations if include_recommendations else [],
        tags=tags,
    )


# Convenience functions
async def quick_severity_check(bug_report: str) -> dict[str, any]:
    """
    Quick severity assessment of a bug.

    Returns simplified severity information.
    """
    result = await triage_bug(bug_report, include_recommendations=False)

    return {
        "severity": result.severity_classification.severity,
        "priority": result.severity_classification.priority,
        "component": result.component.component_name,
        "impact": result.severity_classification.user_impact,
    }


async def get_reproduction_steps(bug_report: str) -> dict[str, any]:
    """
    Generate reproduction steps only.

    Returns simplified reproduction information.
    """
    result = await triage_bug(bug_report, include_recommendations=False)

    return {
        "steps": result.reproduction.steps,
        "preconditions": result.reproduction.preconditions,
        "expected": result.reproduction.expected_behavior,
        "actual": result.reproduction.actual_behavior,
        "reproducibility": result.reproduction.reproducibility,
    }


async def identify_bug_component(bug_report: str, codebase_structure: Optional[str] = None) -> dict[str, any]:
    """
    Identify affected component only.

    Returns simplified component information.
    """
    result = await triage_bug(bug_report, codebase_structure=codebase_structure, include_recommendations=False)

    return {
        "component": result.component.component_name,
        "type": result.component.component_type,
        "subcomponent": result.component.subcomponent,
        "files": result.component.file_paths,
        "confidence": result.component.confidence,
    }
