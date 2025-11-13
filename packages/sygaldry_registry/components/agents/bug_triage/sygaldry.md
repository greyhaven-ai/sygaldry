# Bug Triage Agent

## Overview

The Bug Triage Agent is a comprehensive bug analysis tool that uses LLMs to analyze bug reports, classify severity and priority, identify affected components, analyze root causes, and generate detailed reproduction steps. It helps engineering teams efficiently triage bugs and make informed decisions about bug fixes.

## Features

- **Severity & Priority Classification**: Automatically classifies bugs from critical to trivial with appropriate priority levels
- **Component Identification**: Identifies affected components, modules, and file paths with confidence scoring
- **Root Cause Analysis**: Analyzes potential root causes across 12+ categories (logic errors, race conditions, security issues, etc.)
- **Reproduction Steps**: Generates detailed, step-by-step reproduction instructions
- **Impact Assessment**: Evaluates user impact, business impact, and scope of the bug
- **Effort Estimation**: Estimates the effort required to fix the bug
- **Team Assignment**: Recommends which team should handle the bug
- **Actionable Recommendations**: Provides specific suggestions for fixing and preventing similar bugs
- **Tag Generation**: Automatically generates relevant tags for bug tracking systems

## Installation

```bash
sygaldry add bug_triage_agent
```

## Quick Start

```python
import asyncio
from bug_triage import triage_bug

async def main():
    bug_report = """
    Users getting 500 error when logging in with Google OAuth.
    Started after yesterday's deployment.
    Error: TypeError: Cannot read property 'email' of undefined
    """

    result = await triage_bug(
        bug_report=bug_report,
        context="Recent OAuth provider updates",
        include_recommendations=True
    )

    print(f"Severity: {result.severity_classification.severity}")
    print(f"Priority: {result.severity_classification.priority}")
    print(f"Component: {result.component.component_name}")
    print(f"Root Cause: {result.root_cause.likely_cause}")

asyncio.run(main())
```

## Core Functions

### `triage_bug()`

Main function for comprehensive bug triage and analysis.

**Parameters:**
- `bug_report` (str): The bug report text to analyze
- `context` (Optional[str]): Additional context (recent changes, product info, etc.)
- `codebase_structure` (Optional[str]): Information about codebase structure to help identify components
- `include_recommendations` (bool): Whether to include actionable recommendations (default: True)
- `llm_provider` (str): LLM provider to use (default: "openai")
- `model` (str): Specific model to use (default: "gpt-4o-mini")

**Returns:** `BugTriageResult`

**Example:**
```python
result = await triage_bug(
    bug_report=bug_text,
    context="Recent deployment to production",
    codebase_structure="Frontend: React SPA, Backend: Node.js/Express, Database: PostgreSQL",
    include_recommendations=True
)

# Access detailed results
print(f"Severity: {result.severity_classification.severity}")
print(f"Component: {result.component.component_name}")
print(f"Root Cause: {result.root_cause.likely_cause}")
print(f"Effort: {result.estimated_effort}")

for step in result.reproduction.steps:
    print(f"  - {step}")
```

### `quick_severity_check()`

Fast severity and priority assessment without full analysis.

**Parameters:**
- `bug_report` (str): Bug report text to assess

**Returns:** Dictionary with simplified severity information

**Example:**
```python
severity_info = await quick_severity_check(bug_report)
print(f"Severity: {severity_info['severity']}")
print(f"Priority: {severity_info['priority']}")
print(f"Component: {severity_info['component']}")
print(f"Impact: {severity_info['impact']}")
```

### `get_reproduction_steps()`

Generate reproduction steps only without full triage.

**Parameters:**
- `bug_report` (str): Bug report text to process

**Returns:** Dictionary with reproduction steps

**Example:**
```python
repro = await get_reproduction_steps(bug_report)
print(f"Reproducibility: {repro['reproducibility']}")
for i, step in enumerate(repro['steps'], 1):
    print(f"{i}. {step}")
print(f"Expected: {repro['expected']}")
print(f"Actual: {repro['actual']}")
```

### `identify_bug_component()`

Identify affected component only.

**Parameters:**
- `bug_report` (str): Bug report text
- `codebase_structure` (Optional[str]): Codebase structure information

**Returns:** Dictionary with component information

**Example:**
```python
component_info = await identify_bug_component(
    bug_report=bug_report,
    codebase_structure="Microservices: auth-service, payment-service, user-service"
)
print(f"Component: {component_info['component']}")
print(f"Type: {component_info['type']}")
print(f"Files: {component_info['files']}")
print(f"Confidence: {component_info['confidence']}")
```

## Response Models

### BugTriageResult

Complete bug triage analysis result.

**Fields:**
- `summary` (str): Executive summary of the bug
- `severity_classification` (SeverityClassification): Severity and priority details
- `component` (ComponentIdentification): Affected component information
- `root_cause` (RootCauseAnalysis): Root cause analysis
- `reproduction` (ReproductionSteps): Reproduction steps
- `recommended_assignee` (Optional[str]): Recommended team or person
- `estimated_effort` (str): Effort estimate ('trivial', 'small', 'medium', 'large', 'extra_large')
- `dependencies` (list[str]): Dependencies or blockers
- `related_bugs` (list[str]): Related or duplicate bugs
- `recommendations` (list[str]): Actionable recommendations
- `tags` (list[str]): Categorization tags

### SeverityClassification

Bug severity and priority classification.

**Fields:**
- `severity` (str): Severity level ('critical', 'high', 'medium', 'low', 'trivial')
- `priority` (str): Priority level ('urgent', 'high', 'medium', 'low', 'backlog')
- `severity_reasoning` (str): Why this severity was assigned
- `priority_reasoning` (str): Why this priority was assigned
- `impact_scope` (str): Scope of impact ('system_wide', 'module_specific', 'feature_specific', 'edge_case')
- `user_impact` (str): How users are affected
- `business_impact` (str): Business impact

### ComponentIdentification

Identification of affected component/module.

**Fields:**
- `component_name` (str): Name of affected component
- `component_type` (str): Type ('frontend', 'backend', 'database', 'api', etc.)
- `subcomponent` (Optional[str]): Specific subcomponent
- `file_paths` (list[str]): Likely affected file paths
- `confidence` (float): Confidence in identification (0.0 to 1.0)

### RootCauseAnalysis

Analysis of potential root causes.

**Fields:**
- `likely_cause` (str): Most likely root cause
- `cause_category` (str): Category of root cause
  - Options: 'logic_error', 'null_pointer', 'race_condition', 'memory_leak', 'configuration', 'integration', 'dependency', 'data_validation', 'security', 'performance', 'ui_ux', 'other'
- `contributing_factors` (list[str]): Other contributing factors
- `similar_issues` (list[str]): Similar issues or patterns
- `confidence` (float): Confidence in analysis (0.0 to 1.0)

### ReproductionSteps

Suggested steps to reproduce the bug.

**Fields:**
- `steps` (list[str]): Step-by-step instructions
- `preconditions` (list[str]): Required setup or prerequisites
- `expected_behavior` (str): What should happen
- `actual_behavior` (str): What actually happens
- `reproducibility` (str): Reliability ('always', 'often', 'sometimes', 'rarely', 'unable')
- `environment_details` (list[str]): Environment info (OS, browser, version, etc.)

## Use Cases

### 1. Production Bug Triage

```python
production_bug = """
CRITICAL: Payment processing fails for credit card transactions

Users report that credit card payments are failing with error:
"Transaction declined - Invalid merchant ID"

Started happening at 2:30 PM EST today.
Affects all credit card transactions (100% failure rate).
PayPal and crypto payments working normally.

Error in logs:
payment-service: ERROR - MerchantIDValidationError: merchant_id 'undefined'
"""

result = await triage_bug(
    bug_report=production_bug,
    context="Deployed payment service v2.1.0 at 2:15 PM EST",
    include_recommendations=True
)

# Severity should be critical, priority urgent
print(f"Severity: {result.severity_classification.severity}")
print(f"Priority: {result.severity_classification.priority}")
print(f"Assignee: {result.recommended_assignee}")

# Send to appropriate team immediately
if result.severity_classification.priority == "urgent":
    notify_on_call_team(result)
```

### 2. Batch Bug Triage

```python
# Triage multiple bugs and prioritize
bugs = [bug1, bug2, bug3, bug4, bug5]
triaged_bugs = []

for bug in bugs:
    severity_check = await quick_severity_check(bug)
    triaged_bugs.append({
        'report': bug,
        'severity': severity_check['severity'],
        'priority': severity_check['priority'],
        'component': severity_check['component']
    })

# Sort by severity and priority
sorted_bugs = sorted(
    triaged_bugs,
    key=lambda x: (
        {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'trivial': 4}[x['severity']],
        {'urgent': 0, 'high': 1, 'medium': 2, 'low': 3, 'backlog': 4}[x['priority']]
    )
)

print("=== Bugs Prioritized ===")
for bug in sorted_bugs:
    print(f"[{bug['severity']}/{bug['priority']}] {bug['component']}")
```

### 3. Component-Specific Routing

```python
bug_report = """
Search results showing incorrect product images.
When searching for "laptop", results show phone images.
"""

component_info = await identify_bug_component(
    bug_report=bug_report,
    codebase_structure="""
    - frontend/search: Search UI components
    - backend/search-service: Search API
    - backend/image-service: Image management
    - backend/product-service: Product data
    """
)

# Route to appropriate team
team_mapping = {
    'frontend': 'frontend-team@company.com',
    'backend': 'backend-team@company.com',
    'database': 'data-team@company.com'
}

team_email = team_mapping.get(component_info['type'])
assign_bug_to_team(bug_report, team_email)
```

### 4. Root Cause Pattern Detection

```python
# Analyze multiple bugs to find patterns
bugs_analyzed = []

for bug in recent_bugs:
    result = await triage_bug(bug, include_recommendations=False)
    bugs_analyzed.append(result)

# Find common root causes
from collections import Counter

root_causes = Counter([
    bug.root_cause.cause_category
    for bug in bugs_analyzed
])

print("=== Common Root Causes ===")
for cause, count in root_causes.most_common():
    print(f"{cause}: {count} occurrences")

# If many null_pointer errors, might need code review
if root_causes['null_pointer'] > 5:
    print("⚠️ High number of null pointer errors - consider code review")
```

### 5. QA Workflow Integration

```python
# Generate test cases from reproduction steps
bug_report = """
Cart total calculation wrong when applying discount codes.
Discount not applied correctly for multi-item carts.
"""

repro = await get_reproduction_steps(bug_report)

# Convert to test case
test_case = {
    'name': 'Test discount calculation for multi-item cart',
    'preconditions': repro['preconditions'],
    'steps': repro['steps'],
    'expected': repro['expected'],
    'actual': repro['actual'],
    'status': 'failing'
}

# Add to test suite
add_regression_test(test_case)
```

## Severity & Priority Guidelines

### Severity Levels

- **Critical**: System crash, data loss, security vulnerability, complete feature failure
- **High**: Major functionality broken, significant user impact, no workaround
- **Medium**: Feature partially broken, moderate impact, workaround exists
- **Low**: Minor issue, cosmetic problem, minimal impact
- **Trivial**: Typos, minor UI issues, negligible impact

### Priority Levels

- **Urgent**: Immediate attention required, production down, security issue
- **High**: Fix in next sprint, significant impact
- **Medium**: Fix soon, moderate impact
- **Low**: Can wait, minor impact
- **Backlog**: Nice to have, minimal impact

### Root Cause Categories

- **logic_error**: Incorrect business logic or algorithm
- **null_pointer**: Null/undefined reference errors
- **race_condition**: Concurrency or timing issues
- **memory_leak**: Memory management problems
- **configuration**: Configuration or settings issues
- **integration**: External system or API problems
- **dependency**: Third-party library issues
- **data_validation**: Input validation or data handling issues
- **security**: Security vulnerabilities
- **performance**: Performance or scalability issues
- **ui_ux**: User interface or experience issues
- **other**: Other categories

## Best Practices

1. **Provide Context**: Include recent deployments, known issues, or system changes in the context parameter
2. **Include Codebase Structure**: Provide architecture information to improve component identification
3. **Use Quick Checks for Screening**: Use `quick_severity_check()` for rapid initial assessment of many bugs
4. **Review Recommendations**: Always review the recommendations list for actionable insights
5. **Track Patterns**: Analyze multiple bugs to identify systemic issues
6. **Verify Confidence Scores**: Check confidence scores for component and root cause identification
7. **Enhance Reproduction Steps**: If reproducibility is low, gather more information
8. **Route Appropriately**: Use component identification to route bugs to the right team
9. **Monitor Critical Bugs**: Set up alerts for critical/urgent bugs
10. **Learn from History**: Reference similar_issues to prevent recurrence

## Integration Examples

### With Bug Tracking Systems

```python
# JIRA integration example
async def create_jira_issue_from_triage(bug_report: str):
    result = await triage_bug(bug_report)

    jira_issue = {
        'summary': result.summary,
        'description': bug_report,
        'priority': result.severity_classification.priority.upper(),
        'severity': result.severity_classification.severity.upper(),
        'component': result.component.component_name,
        'assignee': result.recommended_assignee,
        'labels': result.tags,
        'customFields': {
            'rootCause': result.root_cause.likely_cause,
            'estimatedEffort': result.estimated_effort,
            'reproSteps': '\n'.join(result.reproduction.steps)
        }
    }

    jira.create_issue(jira_issue)
```

### With Incident Management

```python
# PagerDuty integration for critical bugs
async def handle_critical_bug(bug_report: str):
    severity_check = await quick_severity_check(bug_report)

    if severity_check['severity'] == 'critical':
        # Create incident
        pagerduty.create_incident({
            'title': f"Critical Bug: {severity_check['component']}",
            'urgency': 'high',
            'description': severity_check['impact']
        })

        # Alert on-call engineer
        slack.notify_channel('#critical-bugs', f"🚨 Critical bug detected: {severity_check['impact']}")
```

## Limitations

- Analysis quality depends on the detail and clarity of bug reports
- Component identification requires clear error messages or stack traces
- Root cause analysis is probabilistic, not definitive
- May require domain-specific knowledge for specialized systems
- Cannot access actual codebase without additional integration
- Recommendations are general and may need customization

## Environment Variables

Set at least one provider's API key:

```bash
export OPENAI_API_KEY="your-openai-key"
# OR
export ANTHROPIC_API_KEY="your-anthropic-key"
```

## Advanced Configuration

### Custom Model Selection

```python
# Use Claude for analysis
result = await triage_bug(
    bug_report=bug_text,
    llm_provider="anthropic",
    model="claude-3-5-sonnet-20241022"
)
```

### Multi-Model Analysis

```python
# Compare results from different models
openai_result = await triage_bug(bug_report, llm_provider="openai", model="gpt-4o")
claude_result = await triage_bug(bug_report, llm_provider="anthropic", model="claude-3-5-sonnet-20241022")

# Use ensemble approach for critical bugs
if openai_result.severity_classification.severity == claude_result.severity_classification.severity:
    final_severity = openai_result.severity_classification.severity
else:
    # Take more conservative (higher) severity
    severities = [openai_result.severity_classification.severity, claude_result.severity_classification.severity]
    severity_order = ['critical', 'high', 'medium', 'low', 'trivial']
    final_severity = min(severities, key=lambda x: severity_order.index(x))
```

## Integration with Lilypad

This agent supports Lilypad for observability:

```python
from lilypad import configure_lilypad

configure_lilypad(project_name="bug-triage")

# Analysis will be automatically traced
result = await triage_bug(bug_report)
```

## Version History

- **0.1.0** (2024): Initial release with core functionality

## License

MIT License - see LICENSE file for details

## Support

For issues, feature requests, or questions:
- GitHub: https://github.com/greyhaven-ai/sygaldry/issues
- Documentation: https://sygaldry.ai/docs/agents/bug-triage
