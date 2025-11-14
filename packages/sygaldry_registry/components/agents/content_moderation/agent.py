"""Content Moderation Agent.

Advanced content moderation with multi-category detection, severity classification, and action recommendations.
"""

from __future__ import annotations

from mirascope import llm
from pydantic import BaseModel, Field
from typing import Literal, Optional

try:
    from lilypad import trace
    LILYPAD_AVAILABLE = True
except ImportError:
    def trace():
        def decorator(func):
            return func
        return decorator
    LILYPAD_AVAILABLE = False


class ViolationCategory(BaseModel):
    """A specific content violation category."""

    category: Literal[
        "hate_speech",
        "harassment",
        "violence",
        "sexual_content",
        "misinformation",
        "spam",
        "self_harm",
        "illegal_activity",
        "profanity",
        "personal_attacks",
        "none"
    ] = Field(..., description="Type of violation detected")
    severity: Literal["none", "low", "medium", "high", "critical"] = Field(
        ..., description="Severity level of the violation"
    )
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in this detection")
    evidence: list[str] = Field(..., description="Specific text excerpts that violate policies")
    explanation: str = Field(..., description="Explanation of why this is a violation")


class ModerationAction(BaseModel):
    """Recommended moderation action."""

    action: Literal[
        "approve",
        "flag_for_review",
        "hide_content",
        "remove_content",
        "suspend_user_temporary",
        "suspend_user_permanent",
        "escalate_to_human"
    ] = Field(..., description="Recommended action to take")
    priority: Literal["low", "medium", "high", "urgent"] = Field(..., description="Priority of action")
    reasoning: str = Field(..., description="Reasoning behind this recommendation")
    requires_human_review: bool = Field(..., description="Whether human review is required")


class ContextualFactors(BaseModel):
    """Contextual factors affecting moderation."""

    sarcasm_detected: bool = Field(..., description="Whether sarcasm or irony is detected")
    educational_context: bool = Field(..., description="Whether content has educational value")
    news_reporting: bool = Field(..., description="Whether content is news reporting")
    artistic_expression: bool = Field(..., description="Whether content is artistic expression")
    discussion_of_issues: bool = Field(..., description="Whether discussing issues vs promoting them")


class ModerationResult(BaseModel):
    """Complete content moderation result."""

    overall_verdict: Literal["safe", "questionable", "unsafe", "harmful"] = Field(
        ..., description="Overall content safety verdict"
    )
    violations: list[ViolationCategory] = Field(..., description="Detected violations")
    recommended_action: ModerationAction = Field(..., description="Recommended moderation action")
    contextual_factors: ContextualFactors = Field(..., description="Context affecting moderation decision")
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Overall risk score from 0 (safe) to 1 (critical)")
    content_type_detected: Literal["text", "comment", "post", "message", "review", "other"] = Field(
        ..., description="Type of content detected"
    )
    target_groups: list[str] = Field(..., description="Groups targeted by harmful content (if any)")
    summary: str = Field(..., description="Summary of moderation findings")


@llm.call(
    provider="openai:completions",
    model_id="gpt-4o-mini",
    format=ModerationResult,
)
async def moderate_content(
    content: str,
    content_type: Literal["text", "comment", "post", "message", "review"] = "text",
    context: Optional[str] = None,
    sensitivity_level: Literal["low", "medium", "high", "maximum"] = "medium",
    custom_policies: Optional[str] = None
) -> str:
    """
    Moderate content for harmful material, policy violations, and safety issues.

    This agent performs comprehensive content moderation including:
    - Hate speech and harassment detection
    - Violence and graphic content detection
    - Sexual content and exploitation detection
    - Misinformation and disinformation detection
    - Spam and manipulation detection
    - Self-harm content detection
    - Illegal activity detection
    - Context-aware analysis (sarcasm, education, news, art)
    - Severity classification
    - Action recommendations

    Args:
        content: The content to moderate
        content_type: Type of content being moderated
        context: Optional context to improve moderation accuracy
        sensitivity_level: How strict the moderation should be
        custom_policies: Optional custom moderation policies

    Returns:
        ModerationResult with comprehensive analysis and recommendations

    Example:
        ```python
        result = await moderate_content(
            content="Your text here",
            content_type="comment",
            sensitivity_level="high"
        )
        print(f"Verdict: {result.overall_verdict}")
        print(f"Risk Score: {result.risk_score}")
        print(f"Action: {result.recommended_action.action}")
        for violation in result.violations:
            print(f"{violation.category}: {violation.severity}")
        ```
    """
    context_info = f"\n\nAdditional Context: {context}" if context else ""
    custom_policy_info = f"\n\nCustom Policies: {custom_policies}" if custom_policies else ""

    sensitivity_instructions = {
        "low": "Be permissive. Only flag clearly harmful content. Allow controversial discussions.",
        "medium": "Use balanced judgment. Flag harmful content but allow legitimate discourse.",
        "high": "Be strict. Flag potentially harmful content even if borderline.",
        "maximum": "Be extremely strict. Flag anything that could be remotely harmful or offensive."
    }[sensitivity_level]

    return f"""You are an expert content moderation AI with expertise in online safety, policy enforcement, and context analysis.

Content Type: {content_type}

Content to Moderate:
"{content}"
{context_info}
{custom_policy_info}

Sensitivity Level: {sensitivity_instructions}

Perform comprehensive content moderation:

1. **VIOLATION DETECTION**
   Analyze for these violation categories:

   a) HATE SPEECH: Attacks based on race, ethnicity, religion, gender, sexual orientation, disability, etc.
      - Direct slurs, epithets, or derogatory language
      - Dehumanizing comparisons or metaphors
      - Calls for exclusion, segregation, or violence
      - Denial of existence or rights

   b) HARASSMENT: Targeted abuse, bullying, threats, or intimidation
      - Personal attacks or insults
      - Doxxing or privacy violations
      - Sustained campaigns against individuals
      - Threats of harm

   c) VIOLENCE: Glorification, incitement, or graphic depiction of violence
      - Threats of physical harm
      - Glorification of violent acts
      - Graphic descriptions
      - Incitement to violence

   d) SEXUAL CONTENT: Inappropriate sexual content or exploitation
      - Explicit sexual content
      - Sexual harassment
      - Sexualization of minors
      - Non-consensual sexual content

   e) MISINFORMATION: False or misleading information, especially harmful
      - Medical misinformation
      - Election misinformation
      - Crisis misinformation
      - Manipulated media

   f) SPAM: Manipulation, scams, or repetitive unwanted content
      - Commercial spam
      - Scams and phishing
      - Manipulation tactics
      - Automated/bot-like content

   g) SELF-HARM: Content promoting self-harm or suicide
      - Encouragement of self-harm
      - Suicide promotion
      - Eating disorder promotion
      - Dangerous challenges

   h) ILLEGAL ACTIVITY: Promotion or coordination of illegal activities
      - Drug trafficking
      - Weapon sales
      - Human trafficking
      - Fraud and scams

   i) PROFANITY: Excessive or inappropriate use of profane language

   j) PERSONAL ATTACKS: Ad hominem attacks in discussions

2. **CONTEXTUAL ANALYSIS**
   Consider these factors:
   - Sarcasm/Irony: Is the content satirical or ironic?
   - Educational Value: Is it educational discussion of harmful topics?
   - News Reporting: Is it legitimate journalism?
   - Artistic Expression: Is it art, literature, or creative work?
   - Discussion vs Promotion: Discussing an issue vs promoting harmful behavior

3. **SEVERITY ASSESSMENT**
   For each violation, classify severity:
   - None: No violation
   - Low: Minor violation, may not require action
   - Medium: Clear violation, requires attention
   - High: Serious violation, requires immediate action
   - Critical: Extreme violation, requires urgent action

4. **EVIDENCE COLLECTION**
   For each violation:
   - Extract specific text that violates policies
   - Explain why it's a violation
   - Consider context and intent

5. **RISK SCORING**
   Calculate overall risk score (0.0 to 1.0):
   - 0.0-0.2: Safe, no concerns
   - 0.2-0.4: Minor concerns, low risk
   - 0.4-0.6: Moderate risk, requires monitoring
   - 0.6-0.8: High risk, action recommended
   - 0.8-1.0: Critical risk, immediate action required

6. **ACTION RECOMMENDATION**
   Based on violations and severity, recommend:
   - approve: Content is safe, allow it
   - flag_for_review: Questionable, have human review
   - hide_content: Hide but don't delete (user can appeal)
   - remove_content: Delete the content
   - suspend_user_temporary: Temporary user suspension
   - suspend_user_permanent: Permanent user ban
   - escalate_to_human: Complex case requiring human judgment

7. **TARGET GROUPS**
   Identify any groups targeted by harmful content

8. **OVERALL VERDICT**
   - safe: No policy violations, content is appropriate
   - questionable: Borderline, may need review
   - unsafe: Violates policies, action needed
   - harmful: Seriously harmful, urgent action needed

IMPORTANT CONSIDERATIONS:
- Context matters: News reporting violence is different from promoting violence
- Intent matters: Discussing hate speech to condemn it vs using it
- Nuance matters: Consider sarcasm, satire, and educational contexts
- Be fair: Don't over-moderate legitimate discourse
- Be safe: When in doubt, flag for human review
- Cultural sensitivity: Consider cultural contexts
- False positives: Better to flag than miss harmful content
- Severity calibration: Match severity to actual harm potential

Provide a comprehensive moderation report."""


# Convenience functions
@trace()
async def quick_moderate(content: str) -> str:
    """
    Quick content moderation.

    Returns just the overall verdict.
    """
    result = await moderate_content(content)
    return result.overall_verdict


@trace()
async def moderate_with_action(content: str, sensitivity_level: str = "medium") -> dict[str, any]:
    """
    Moderate content and return verdict with recommended action.

    Returns simplified result with verdict, action, and risk score.
    """
    result = await moderate_content(content, sensitivity_level=sensitivity_level)
    return {
        "verdict": result.overall_verdict,
        "action": result.recommended_action.action,
        "risk_score": result.risk_score,
        "requires_review": result.recommended_action.requires_human_review
    }


@trace()
async def detect_violations(content: str) -> list[dict[str, any]]:
    """
    Detect violations only without full moderation.

    Returns list of detected violations.
    """
    result = await moderate_content(content)
    return [
        {
            "category": violation.category,
            "severity": violation.severity,
            "confidence": violation.confidence,
            "explanation": violation.explanation
        }
        for violation in result.violations
        if violation.category != "none"
    ]


@trace()
async def check_safety(content: str) -> bool:
    """
    Simple safety check.

    Returns True if content is safe, False otherwise.
    """
    result = await moderate_content(content)
    return result.overall_verdict == "safe"


@trace()
async def get_risk_score(content: str) -> float:
    """
    Get risk score only.

    Returns risk score from 0.0 (safe) to 1.0 (critical).
    """
    result = await moderate_content(content)
    return result.risk_score
