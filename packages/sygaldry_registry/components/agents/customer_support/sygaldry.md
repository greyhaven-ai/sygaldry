# Customer Support Agent

## Overview

Intelligent customer support ticket analysis with comprehensive classification, sentiment detection, urgency assessment, and response suggestions. This agent helps support teams quickly triage tickets, understand customer emotions, and provide appropriate responses.

## Features

- **Ticket Classification**: Categorizes tickets into 10+ categories including technical issues, billing, account access, feature requests, and more
- **Urgency Assessment**: Evaluates urgency level (low/medium/high/critical) with priority scoring and estimated response times
- **Sentiment Analysis**: Detects customer sentiment, emotions, satisfaction scores, and churn risk
- **Information Extraction**: Extracts key details like account IDs, order numbers, error codes, and specific issues
- **Response Suggestions**: Generates appropriate responses with recommended tone and next steps
- **Escalation Detection**: Identifies when escalation is needed and recommends which team to escalate to
- **Context-Aware**: Supports optional context about products/services and customer history
- **Multi-Level Analysis**: Choose from basic, detailed, or comprehensive analysis depths

## Installation

```bash
sygaldry add customer_support_agent
```

## Quick Start

### Basic Usage

```python
from customer_support import analyze_support_ticket

# Analyze a customer support ticket
result = await analyze_support_ticket(
    message="I've been trying to log in for 3 hours and keep getting error 403. This is unacceptable!",
    analysis_depth="detailed"
)

# Access the results
print(f"Category: {result.category.primary_category}")
print(f"Urgency: {result.urgency.urgency_level}")
print(f"Sentiment: {result.sentiment.overall_sentiment}")
print(f"Churn Risk: {result.sentiment.churn_risk}")
print(f"\nSuggested Response:\n{result.response_suggestion.suggested_response}")
```

### With Context and History

```python
result = await analyze_support_ticket(
    message="The payment failed again! This is the third time this week.",
    context="SaaS subscription platform with monthly billing",
    customer_history="Premium customer for 2 years, no previous issues",
    analysis_depth="comprehensive"
)
```

### Convenience Functions

```python
from customer_support import (
    classify_ticket,
    assess_urgency,
    detect_sentiment,
    suggest_response,
    extract_ticket_info
)

# Quick classification
category = await classify_ticket(
    "How do I reset my password?"
)
# Returns: {'category': 'account_access', 'subcategory': '...', 'urgency': 'low', ...}

# Urgency assessment only
urgency = await assess_urgency(
    "System is completely down! All users affected!"
)
# Returns: {'urgency_level': 'critical', 'priority': 'critical', ...}

# Sentiment detection only
sentiment = await detect_sentiment(
    "I'm very frustrated with this service."
)
# Returns: {'sentiment': 'negative', 'emotion': 'frustrated', ...}

# Response suggestion
response = await suggest_response(
    message="I need a refund for order #12345",
    context="E-commerce platform with 30-day return policy"
)
# Returns: {'response': '...', 'tone': 'professional', 'next_steps': [...], ...}

# Extract information
info = await extract_ticket_info(
    "My account ID is ACC-12345 and I keep getting error code E403"
)
# Returns: {'account_id': 'ACC-12345', 'error_codes': ['E403'], ...}
```

## Ticket Categories

The agent classifies tickets into the following categories:

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

## Urgency Levels

- **Critical**: Service down, security issue, severe business impact
- **High**: Major functionality broken, multiple users affected
- **Medium**: Important issue but workarounds available
- **Low**: Minor issues, general questions, feature requests

## Response Tones

The agent recommends one of the following tones:

- **empathetic**: For frustrated or upset customers
- **professional**: For standard business inquiries
- **apologetic**: For issues caused by the company
- **reassuring**: For anxious or concerned customers
- **technical**: For technical bug reports or detailed issues

## Analysis Depths

- **basic**: Quick triage with category, urgency, and basic response
- **detailed**: Standard analysis with sentiment, extracted info, and comprehensive suggestions
- **comprehensive**: Deep analysis with multiple insights and detailed reasoning

## Use Cases

- **Support Ticket Triage**: Automatically classify and prioritize incoming tickets
- **Sentiment Monitoring**: Track customer satisfaction and detect churn risks
- **Response Automation**: Generate suggested responses for common issues
- **Escalation Management**: Identify tickets requiring specialized handling
- **Knowledge Base**: Extract common issues and categorize support documentation
- **Team Routing**: Route tickets to appropriate teams based on category
- **Performance Metrics**: Analyze ticket patterns and support team effectiveness

## Example Output Structure

```python
CustomerSupportAnalysis(
    category=TicketCategory(
        primary_category="technical_issue",
        subcategory="login_error",
        confidence=0.95
    ),
    urgency=UrgencyAssessment(
        urgency_level="high",
        priority="high",
        requires_immediate_attention=True,
        estimated_response_time="1 hour",
        reasoning="User is completely blocked from accessing the service"
    ),
    sentiment=CustomerSentiment(
        overall_sentiment="negative",
        emotion="frustrated",
        satisfaction_score=3.0,
        churn_risk="medium"
    ),
    extracted_info=ExtractedInformation(
        error_codes=["403"],
        specific_issue="Unable to log in for 3 hours",
        previous_attempts=["Multiple login attempts"]
    ),
    response_suggestion=ResponseSuggestion(
        suggested_response="I sincerely apologize for the login issues...",
        tone="apologetic",
        next_steps=["Check account status", "Verify credentials", "Clear session"],
        escalation_needed=False
    ),
    summary="Customer experiencing login errors for 3 hours with error 403",
    key_points=["Login blocked", "Error 403", "High frustration"],
    tags=["login", "access", "error_403", "urgent"]
)
```

## Requirements

- Python 3.12+
- Mirascope v2.0+
- Pydantic v2.0+
- OpenAI API key or Anthropic API key

## License

MIT License
