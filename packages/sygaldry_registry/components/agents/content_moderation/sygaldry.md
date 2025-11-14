# content_moderation_agent
> Advanced content moderation agent for detecting harmful content, hate speech, misinformation, spam, and policy violations. Features multi-category detection, severity classification, contextual analysis, and action recommendations with support for multiple content types.

**Version**: 0.1.0 | **Type**: agent | **License**: MIT

## Overview

The Content Moderation Agent provides comprehensive content safety analysis and moderation capabilities. It detects multiple categories of harmful content, classifies severity, considers contextual factors, and recommends appropriate moderation actions.

This agent integrates seamlessly with the Mirascope framework and follows AI agent best practices for production deployment.

### Key Features

- **Multi-Category Detection**: Detects hate speech, harassment, violence, sexual content, misinformation, spam, self-harm content, illegal activity, profanity, and personal attacks
- **Severity Classification**: Classifies violations from none to critical
- **Contextual Analysis**: Considers sarcasm, educational value, news reporting, and artistic expression
- **Risk Scoring**: Provides overall risk scores from 0.0 (safe) to 1.0 (critical)
- **Action Recommendations**: Suggests appropriate actions from approval to permanent suspension
- **Configurable Sensitivity**: Supports low, medium, high, and maximum sensitivity levels
- **Multiple Content Types**: Handles text, comments, posts, messages, and reviews
- **Custom Policies**: Supports custom moderation policies

## Quick Start

### Installation

```bash
sygaldry add content_moderation_agent
```

### Dependencies

This agent requires the following dependencies:

**Registry Dependencies:**

- None

**Python Dependencies:**

- `mirascope` >=2.0.0
- `pydantic` >=2.0.0
- `lilypad` >=0.1.0 (optional, for observability)

**Environment Variables:**

- `OPENAI_API_KEY`: OpenAI API key for GPT models (Optional)
- `ANTHROPIC_API_KEY`: Anthropic API key for Claude models (Optional)
- `GOOGLE_API_KEY`: Google API key for Gemini models (Optional)

### Basic Usage

```python
import asyncio
from content_moderation import moderate_content, quick_moderate, check_safety

async def main():
    # Full moderation with detailed analysis
    result = await moderate_content(
        content="Your content here",
        content_type="comment",
        sensitivity_level="high"
    )

    print(f"Overall Verdict: {result.overall_verdict}")
    print(f"Risk Score: {result.risk_score}")
    print(f"Recommended Action: {result.recommended_action.action}")
    print(f"Requires Human Review: {result.recommended_action.requires_human_review}")

    # Display violations
    for violation in result.violations:
        if violation.category != 'none':
            print(f"\nViolation: {violation.category}")
            print(f"  Severity: {violation.severity}")
            print(f"  Confidence: {violation.confidence}")
            print(f"  Explanation: {violation.explanation}")
            print(f"  Evidence: {violation.evidence}")

    # Display contextual factors
    print(f"\nContextual Factors:")
    print(f"  Sarcasm Detected: {result.contextual_factors.sarcasm_detected}")
    print(f"  Educational Context: {result.contextual_factors.educational_context}")
    print(f"  News Reporting: {result.contextual_factors.news_reporting}")

    # Quick safety check
    is_safe = await check_safety("Hello, how are you?")
    print(f"\nQuick Safety Check: {'Safe' if is_safe else 'Unsafe'}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Agent Configuration

### Sensitivity Levels

The agent supports four sensitivity levels:

- **low**: Permissive. Only flags clearly harmful content. Allows controversial discussions.
- **medium**: Balanced judgment. Flags harmful content but allows legitimate discourse. (Default)
- **high**: Strict. Flags potentially harmful content even if borderline.
- **maximum**: Extremely strict. Flags anything that could be remotely harmful or offensive.

```python
# Low sensitivity - permissive
result = await moderate_content(content, sensitivity_level="low")

# High sensitivity - strict
result = await moderate_content(content, sensitivity_level="high")
```

### Content Types

Supported content types:
- `text`: General text content
- `comment`: User comments
- `post`: Social media posts or forum posts
- `message`: Direct messages or chat messages
- `review`: Product or service reviews

```python
result = await moderate_content(
    content="User comment text",
    content_type="comment"
)
```

### Custom Policies

You can provide custom moderation policies:

```python
custom_policies = """
- Allow discussion of controversial topics in educational context
- Zero tolerance for personal information sharing
- Strict enforcement of community guidelines section 3.2
"""

result = await moderate_content(
    content=content,
    custom_policies=custom_policies
)
```

## Agent Architecture

This agent implements the following key patterns:

- **Structured Outputs**: Uses Pydantic models for reliable, typed responses
- **Multi-Category Analysis**: Comprehensive detection across 10+ violation categories
- **Contextual Awareness**: Considers context, intent, and cultural factors
- **Risk-Based Scoring**: Quantitative risk assessment for automated decision-making
- **Error Handling**: Robust error handling with graceful fallbacks
- **Async Support**: Full async/await support for optimal performance
- Instrumented with Lilypad for observability and tracing (when available)
- Supports automatic versioning and A/B testing

### Violation Categories

1. **Hate Speech**: Attacks based on protected characteristics
2. **Harassment**: Targeted abuse, bullying, or threats
3. **Violence**: Glorification or incitement of violence
4. **Sexual Content**: Inappropriate sexual content or exploitation
5. **Misinformation**: False or misleading information
6. **Spam**: Manipulation, scams, or unwanted content
7. **Self-Harm**: Content promoting self-harm or suicide
8. **Illegal Activity**: Promotion of illegal activities
9. **Profanity**: Excessive or inappropriate profane language
10. **Personal Attacks**: Ad hominem attacks in discussions

### Template Variables

- `provider`: `openai`
- `model`: `gpt-4o-mini`
- `sensitivity_level`: `medium`

### Advanced Configuration

Configure template variables using CLI options or environment variables.

### LLM Provider Configuration

This agent supports multiple LLM providers through Mirascope:

- **OpenAI**: Set `OPENAI_API_KEY` for GPT models (Recommended: gpt-4o-mini or gpt-4o)
- **Anthropic**: Set `ANTHROPIC_API_KEY` for Claude models (Recommended: claude-3-5-sonnet)
- **Google**: Set `GOOGLE_API_KEY` for Gemini models
- **Groq**: Set `GROQ_API_KEY` for Groq models

Configure the provider and model using template variables or function parameters.

## API Reference

### Main Functions

#### `moderate_content()`

```python
async def moderate_content(
    content: str,
    content_type: Literal["text", "comment", "post", "message", "review"] = "text",
    context: Optional[str] = None,
    sensitivity_level: Literal["low", "medium", "high", "maximum"] = "medium",
    custom_policies: Optional[str] = None
) -> ModerationResult
```

Performs comprehensive content moderation with full analysis.

#### `quick_moderate()`

```python
async def quick_moderate(content: str) -> str
```

Quick moderation returning only the overall verdict.

#### `moderate_with_action()`

```python
async def moderate_with_action(
    content: str,
    sensitivity_level: str = "medium"
) -> dict[str, any]
```

Returns verdict, action, risk score, and review requirement.

#### `detect_violations()`

```python
async def detect_violations(content: str) -> list[dict[str, any]]
```

Returns only detected violations without full moderation.

#### `check_safety()`

```python
async def check_safety(content: str) -> bool
```

Simple boolean safety check.

#### `get_risk_score()`

```python
async def get_risk_score(content: str) -> float
```

Returns only the risk score (0.0 to 1.0).

### Response Models

#### `ModerationResult`

```python
class ModerationResult(BaseModel):
    overall_verdict: Literal["safe", "questionable", "unsafe", "harmful"]
    violations: list[ViolationCategory]
    recommended_action: ModerationAction
    contextual_factors: ContextualFactors
    risk_score: float  # 0.0 to 1.0
    content_type_detected: str
    target_groups: list[str]
    summary: str
```

#### `ViolationCategory`

```python
class ViolationCategory(BaseModel):
    category: str  # hate_speech, harassment, violence, etc.
    severity: Literal["none", "low", "medium", "high", "critical"]
    confidence: float  # 0.0 to 1.0
    evidence: list[str]
    explanation: str
```

#### `ModerationAction`

```python
class ModerationAction(BaseModel):
    action: str  # approve, flag_for_review, remove_content, etc.
    priority: Literal["low", "medium", "high", "urgent"]
    reasoning: str
    requires_human_review: bool
```

## Advanced Examples

### Example 1: Batch Content Moderation

```python
import asyncio
from content_moderation import moderate_content

async def moderate_batch(contents: list[str]):
    """Moderate multiple pieces of content."""
    tasks = [moderate_content(content) for content in contents]
    results = await asyncio.gather(*tasks)

    # Filter for unsafe content
    unsafe_content = [
        (content, result)
        for content, result in zip(contents, results)
        if result.overall_verdict in ["unsafe", "harmful"]
    ]

    return unsafe_content

# Usage
contents = ["Comment 1", "Comment 2", "Comment 3"]
unsafe = await moderate_batch(contents)
for content, result in unsafe:
    print(f"Unsafe: {content[:50]}... - {result.recommended_action.action}")
```

### Example 2: Custom Moderation Workflow

```python
from content_moderation import moderate_content

async def moderate_with_escalation(content: str, content_type: str):
    """Moderate content with automatic escalation."""
    result = await moderate_content(
        content=content,
        content_type=content_type,
        sensitivity_level="high"
    )

    if result.risk_score >= 0.8:
        # Critical risk - immediate action
        return {
            "action": "immediate_removal",
            "escalate": True,
            "notify": "admin_team",
            "result": result
        }
    elif result.risk_score >= 0.6:
        # High risk - flag for review
        return {
            "action": "flag_for_review",
            "escalate": True,
            "notify": "moderator_team",
            "result": result
        }
    elif result.overall_verdict == "questionable":
        # Questionable - automated decision with logging
        return {
            "action": result.recommended_action.action,
            "escalate": False,
            "notify": None,
            "result": result
        }
    else:
        # Safe - approve
        return {
            "action": "approve",
            "escalate": False,
            "notify": None,
            "result": result
        }

# Usage
workflow_result = await moderate_with_escalation(
    "User comment text",
    "comment"
)
```

### Example 3: Multi-Provider Usage

```python
# Using different LLM providers for different sensitivity levels
from content_moderation import moderate_content

# Use GPT-4 for high-stakes moderation
result_gpt4 = await moderate_content(
    content="High-stakes content",
    sensitivity_level="maximum"
)

# Use Claude for nuanced context analysis
result_claude = await moderate_content(
    content="Nuanced content requiring context",
    sensitivity_level="medium",
    context="Academic discussion of historical events"
)
```

### Example 4: Violation Tracking

```python
from content_moderation import detect_violations
from collections import Counter

async def analyze_violation_patterns(contents: list[str]):
    """Analyze patterns in content violations."""
    all_violations = []

    for content in contents:
        violations = await detect_violations(content)
        all_violations.extend(violations)

    # Count violation types
    violation_types = Counter(v['category'] for v in all_violations)

    # Count severity levels
    severity_levels = Counter(v['severity'] for v in all_violations)

    return {
        "total_violations": len(all_violations),
        "violation_types": dict(violation_types),
        "severity_distribution": dict(severity_levels),
        "most_common": violation_types.most_common(3)
    }

# Usage
stats = await analyze_violation_patterns(user_comments)
print(f"Total violations: {stats['total_violations']}")
print(f"Most common: {stats['most_common']}")
```

## Integration with Mirascope

This agent follows Mirascope v2 best practices:

- Uses `@llm.call` decorator with `format=` parameter for structured outputs
- Implements Pydantic response models for type safety
- Supports async/await patterns for optimal performance
- Compatible with multiple LLM providers
- Includes comprehensive error handling
- Instrumented with Lilypad for observability and tracing (when available)
- Supports automatic versioning and A/B testing

## Use Cases

### Platform Moderation

- Social media platforms
- Forum and community moderation
- Comment section management
- User-generated content platforms

### Enterprise Applications

- Internal communication monitoring
- Employee conduct compliance
- Customer service quality assurance
- Brand protection

### Educational Platforms

- Student content monitoring
- Cyberbullying prevention
- Educational content appropriateness
- Academic integrity

### E-commerce

- Product review moderation
- Seller communication monitoring
- Customer feedback analysis
- Marketplace safety

## Best Practices

1. **Sensitivity Calibration**: Start with "medium" sensitivity and adjust based on your needs
2. **Human Review**: Always have humans review high-risk decisions
3. **Context Matters**: Provide context when available to improve accuracy
4. **Appeal Process**: Implement an appeal process for moderation decisions
5. **Transparency**: Be transparent with users about moderation policies
6. **Regular Updates**: Update custom policies as community standards evolve
7. **Batch Processing**: Use batch processing for efficiency with large volumes
8. **Audit Logs**: Maintain audit logs of moderation decisions
9. **Cultural Sensitivity**: Consider cultural context in global applications
10. **Continuous Improvement**: Analyze false positives/negatives to improve

## Troubleshooting

### Common Issues

- **API Key Issues**: Ensure your LLM provider API key is set correctly
- **Dependency Conflicts**: Run `sygaldry add content_moderation_agent` to reinstall dependencies
- **Timeout Errors**: Increase timeout values for complex content
- **False Positives**: Adjust sensitivity_level or provide additional context
- **Rate Limiting**: Implement rate limiting and batch processing for high volumes

### Performance Optimization

For high-volume moderation:

```python
import asyncio
from content_moderation import moderate_content

async def moderate_in_batches(contents: list[str], batch_size: int = 10):
    """Moderate content in batches to avoid rate limits."""
    results = []
    for i in range(0, len(contents), batch_size):
        batch = contents[i:i+batch_size]
        batch_results = await asyncio.gather(
            *[moderate_content(c) for c in batch]
        )
        results.extend(batch_results)
        # Optional: Add delay between batches
        await asyncio.sleep(1)
    return results
```

## Migration Notes

This agent uses Mirascope v2 API with:
- `@llm.call` decorator instead of `@prompt_template`
- `format=` parameter instead of `response_model=`
- Functional prompts returning f-strings
- Optional Lilypad integration with graceful fallback

---

**Key Benefits:**

- **Comprehensive Detection**: 10+ violation categories
- **Context-Aware**: Considers sarcasm, education, news, art
- **Actionable Results**: Clear recommendations for moderation actions
- **Configurable**: Adjustable sensitivity and custom policies
- **Production-Ready**: Async, scalable, and observable

**Related Components:**

- sentiment_analysis_agent: For sentiment analysis
- pii_scrubbing_agent: For privacy protection

**References:**

- [Mirascope Documentation](https://mirascope.com)
- [Sygaldry Registry](https://github.com/greyhaven-ai/sygaldry)
- [Content Moderation Best Practices](https://www.trust-and-safety.org)
