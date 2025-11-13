"""Customer Support Agent.

Intelligent customer support ticket analysis with classification, sentiment detection, urgency assessment, and response suggestions.
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


class TicketCategory(BaseModel):
    """Ticket category classification."""

    primary_category: Literal[
        "technical_issue",
        "billing",
        "account_access",
        "feature_request",
        "product_inquiry",
        "complaint",
        "refund_request",
        "general_inquiry",
        "bug_report",
        "other"
    ] = Field(..., description="Primary category of the ticket")
    subcategory: str = Field(..., description="More specific subcategory")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in classification")


class UrgencyAssessment(BaseModel):
    """Urgency and priority assessment."""

    urgency_level: Literal["low", "medium", "high", "critical"] = Field(
        ..., description="Urgency level of the ticket"
    )
    priority: Literal["low", "medium", "high", "critical"] = Field(
        ..., description="Priority level for handling"
    )
    requires_immediate_attention: bool = Field(
        ..., description="Whether ticket requires immediate attention"
    )
    estimated_response_time: str = Field(
        ..., description="Recommended response time (e.g., '1 hour', '24 hours')"
    )
    reasoning: str = Field(..., description="Reasoning for urgency assessment")


class CustomerSentiment(BaseModel):
    """Customer sentiment analysis."""

    overall_sentiment: Literal["positive", "neutral", "negative", "very_negative"] = Field(
        ..., description="Overall customer sentiment"
    )
    emotion: Literal["satisfied", "frustrated", "angry", "confused", "anxious", "neutral"] = Field(
        ..., description="Detected primary emotion"
    )
    satisfaction_score: float = Field(
        ..., ge=0.0, le=10.0, description="Customer satisfaction score 0-10"
    )
    churn_risk: Literal["low", "medium", "high"] = Field(
        ..., description="Risk of customer churn based on sentiment"
    )


class ExtractedInformation(BaseModel):
    """Key information extracted from the message."""

    customer_name: Optional[str] = Field(None, description="Customer name if mentioned")
    account_id: Optional[str] = Field(None, description="Account ID if mentioned")
    order_number: Optional[str] = Field(None, description="Order number if mentioned")
    product_name: Optional[str] = Field(None, description="Product/service mentioned")
    error_codes: list[str] = Field(default_factory=list, description="Any error codes mentioned")
    specific_issue: str = Field(..., description="Specific issue or request")
    previous_attempts: list[str] = Field(
        default_factory=list, description="Previous troubleshooting attempts mentioned"
    )
    contact_preference: Optional[str] = Field(
        None, description="Preferred contact method if mentioned"
    )


class ResponseSuggestion(BaseModel):
    """Suggested response and actions."""

    suggested_response: str = Field(..., description="Suggested response to customer")
    tone: Literal["empathetic", "professional", "apologetic", "reassuring", "technical"] = Field(
        ..., description="Recommended tone for response"
    )
    next_steps: list[str] = Field(..., description="Recommended next steps")
    escalation_needed: bool = Field(..., description="Whether escalation is needed")
    escalation_reason: Optional[str] = Field(
        None, description="Reason for escalation if needed"
    )
    escalate_to: Optional[str] = Field(
        None, description="Department/team to escalate to"
    )
    canned_response_tags: list[str] = Field(
        default_factory=list, description="Tags for relevant canned responses"
    )


class CustomerSupportAnalysis(BaseModel):
    """Complete customer support ticket analysis."""

    category: TicketCategory = Field(..., description="Ticket classification")
    urgency: UrgencyAssessment = Field(..., description="Urgency and priority assessment")
    sentiment: CustomerSentiment = Field(..., description="Customer sentiment analysis")
    extracted_info: ExtractedInformation = Field(..., description="Extracted key information")
    response_suggestion: ResponseSuggestion = Field(..., description="Response suggestions")
    summary: str = Field(..., description="Brief summary of the ticket")
    key_points: list[str] = Field(..., description="Key points from the message")
    tags: list[str] = Field(..., description="Relevant tags for ticket organization")


@llm.call(
    provider="openai:completions",
    model_id="gpt-4o-mini",
    format=CustomerSupportAnalysis,
)
async def analyze_support_ticket(
    message: str,
    context: Optional[str] = None,
    customer_history: Optional[str] = None,
    analysis_depth: Literal["basic", "detailed", "comprehensive"] = "detailed"
) -> str:
    """
    Analyze customer support ticket with comprehensive classification and recommendations.

    This agent performs intelligent customer support analysis including:
    - Ticket classification and categorization
    - Urgency and priority assessment
    - Sentiment and emotion detection
    - Key information extraction
    - Response suggestions with appropriate tone
    - Escalation recommendations
    - Next steps and action items

    Args:
        message: The customer support message/ticket
        context: Optional context about the product/service
        customer_history: Optional customer history or previous tickets
        analysis_depth: Level of analysis detail

    Returns:
        CustomerSupportAnalysis with complete ticket analysis

    Example:
        ```python
        result = await analyze_support_ticket(
            message="I've been trying to log in for 3 hours and keep getting error 403. This is unacceptable!",
            analysis_depth="detailed"
        )
        print(f"Category: {result.category.primary_category}")
        print(f"Urgency: {result.urgency.urgency_level}")
        print(f"Sentiment: {result.sentiment.overall_sentiment}")
        print(f"Response: {result.response_suggestion.suggested_response}")
        ```
    """
    context_info = f"\n\nProduct/Service Context: {context}" if context else ""
    history_info = f"\n\nCustomer History: {customer_history}" if customer_history else ""

    depth_instruction = {
        "basic": "Provide basic classification, urgency, and suggested response.",
        "detailed": "Provide detailed analysis including sentiment, extracted information, and comprehensive response suggestions.",
        "comprehensive": "Provide comprehensive analysis with deep insights, multiple response options, and detailed reasoning."
    }[analysis_depth]

    return f"""You are an expert customer support AI assistant. Analyze the following customer support message/ticket.

Customer Message:
"{message}"
{context_info}{history_info}

Analysis Depth: {depth_instruction}

Perform a thorough customer support analysis:

## 1. Ticket Classification
Classify the ticket into the most appropriate category:
- **technical_issue**: Technical problems, bugs, errors, system issues
- **billing**: Billing inquiries, payment issues, invoicing questions
- **account_access**: Login issues, password resets, account lockouts
- **feature_request**: Requests for new features or enhancements
- **product_inquiry**: Questions about products, services, or features
- **complaint**: General complaints or dissatisfaction
- **refund_request**: Refund or cancellation requests
- **general_inquiry**: General questions or information requests
- **bug_report**: Specific bug reports with reproduction steps
- **other**: Other issues not fitting above categories

Provide a specific subcategory and confidence score.

## 2. Urgency Assessment
Assess the urgency and priority:
- **Critical**: Service down, security issue, severe business impact
- **High**: Major functionality broken, multiple users affected
- **Medium**: Important issue but workarounds available
- **Low**: Minor issues, general questions, feature requests

Consider:
- Time sensitivity mentioned
- Business impact
- Customer frustration level
- Whether service is completely blocked
- Number of users potentially affected

Provide estimated response time and reasoning.

## 3. Sentiment Analysis
Analyze customer sentiment:
- Overall sentiment: positive, neutral, negative, very_negative
- Primary emotion: satisfied, frustrated, angry, confused, anxious, neutral
- Satisfaction score (0-10)
- Churn risk: low, medium, high

Consider:
- Language tone and word choice
- Exclamation marks, caps, or emotional indicators
- Frustration or satisfaction expressed
- Loyalty indicators or churn signals

## 4. Extract Key Information
Extract all relevant information:
- Customer name (if mentioned)
- Account ID, order number, product name
- Error codes or error messages
- Specific issue description
- Previous troubleshooting attempts
- Contact preferences

## 5. Response Suggestion
Suggest an appropriate response:
- Draft a suggested response addressing the issue
- Recommend appropriate tone (empathetic, professional, apologetic, reassuring, technical)
- Provide clear next steps
- Determine if escalation is needed
- If escalation needed: specify reason and which team
- Suggest relevant canned response tags

Response should:
- Acknowledge the customer's issue
- Show empathy and understanding
- Provide clear action items
- Set appropriate expectations
- Be professional yet personable

## 6. Summary and Organization
Provide:
- Brief summary of the ticket
- Key points (3-5 bullet points)
- Relevant tags for organization and search

Be thorough, empathetic, and action-oriented in your analysis."""


# Convenience functions
@trace()
async def classify_ticket(message: str) -> dict[str, str]:
    """
    Quick ticket classification.

    Returns just the category and urgency.
    """
    result = await analyze_support_ticket(message, analysis_depth="basic")
    return {
        "category": result.category.primary_category,
        "subcategory": result.category.subcategory,
        "urgency": result.urgency.urgency_level,
        "priority": result.urgency.priority
    }


@trace()
async def assess_urgency(message: str) -> dict[str, any]:
    """
    Quick urgency assessment.

    Returns urgency information only.
    """
    result = await analyze_support_ticket(message, analysis_depth="basic")
    return {
        "urgency_level": result.urgency.urgency_level,
        "priority": result.urgency.priority,
        "requires_immediate_attention": result.urgency.requires_immediate_attention,
        "estimated_response_time": result.urgency.estimated_response_time
    }


@trace()
async def detect_sentiment(message: str) -> dict[str, any]:
    """
    Quick sentiment detection.

    Returns sentiment information only.
    """
    result = await analyze_support_ticket(message, analysis_depth="basic")
    return {
        "sentiment": result.sentiment.overall_sentiment,
        "emotion": result.sentiment.emotion,
        "satisfaction_score": result.sentiment.satisfaction_score,
        "churn_risk": result.sentiment.churn_risk
    }


@trace()
async def suggest_response(message: str, context: Optional[str] = None) -> dict[str, any]:
    """
    Generate response suggestion.

    Returns suggested response and action items.
    """
    result = await analyze_support_ticket(message, context=context, analysis_depth="detailed")
    return {
        "response": result.response_suggestion.suggested_response,
        "tone": result.response_suggestion.tone,
        "next_steps": result.response_suggestion.next_steps,
        "escalation_needed": result.response_suggestion.escalation_needed,
        "escalate_to": result.response_suggestion.escalate_to
    }


@trace()
async def extract_ticket_info(message: str) -> dict[str, any]:
    """
    Extract key information from ticket.

    Returns extracted information only.
    """
    result = await analyze_support_ticket(message, analysis_depth="detailed")
    return result.extracted_info.model_dump()
