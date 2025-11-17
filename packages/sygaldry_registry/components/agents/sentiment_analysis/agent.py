"""Sentiment Analysis Agent.

Multi-dimensional sentiment analysis with emotion detection, aspect-based analysis, and trend tracking.
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


class EmotionScore(BaseModel):
    """Emotion detection scores."""

    joy: float = Field(..., ge=0.0, le=1.0, description="Joy/happiness level")
    sadness: float = Field(..., ge=0.0, le=1.0, description="Sadness level")
    anger: float = Field(..., ge=0.0, le=1.0, description="Anger/frustration level")
    fear: float = Field(..., ge=0.0, le=1.0, description="Fear/anxiety level")
    surprise: float = Field(..., ge=0.0, le=1.0, description="Surprise level")
    disgust: float = Field(..., ge=0.0, le=1.0, description="Disgust level")


class AspectSentiment(BaseModel):
    """Sentiment for a specific aspect."""

    aspect: str = Field(..., description="The aspect being discussed (e.g., 'customer service', 'price')")
    sentiment: Literal["positive", "negative", "neutral", "mixed"] = Field(..., description="Sentiment for this aspect")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in this assessment")
    mentions: list[str] = Field(..., description="Specific mentions related to this aspect")


class SentimentAnalysisResult(BaseModel):
    """Complete sentiment analysis result."""

    overall_sentiment: Literal["positive", "negative", "neutral", "mixed"] = Field(
        ..., description="Overall sentiment classification"
    )
    polarity_score: float = Field(..., ge=-1.0, le=1.0, description="Polarity score from -1 (negative) to 1 (positive)")
    subjectivity_score: float = Field(..., ge=0.0, le=1.0, description="Subjectivity score from 0 (objective) to 1 (subjective)")
    # Note: Remove description from nested model fields to avoid OpenAI schema validation error
    # OpenAI rejects $ref with additional keywords like 'description'
    emotions: EmotionScore
    aspects: list[AspectSentiment]
    key_phrases: list[str] = Field(..., description="Key phrases indicating sentiment")
    intensity: Literal["weak", "moderate", "strong", "very_strong"] = Field(
        ..., description="Intensity of the sentiment"
    )
    summary: str = Field(..., description="Summary of the sentiment analysis")


# Rebuild models to resolve forward references
EmotionScore.model_rebuild()
AspectSentiment.model_rebuild()
SentimentAnalysisResult.model_rebuild()


@llm.call(
    provider="openai:completions",
    model_id="gpt-4o-mini",
    format=SentimentAnalysisResult,
)
async def _analyze_sentiment_call(
    text: str,
    analysis_depth: Literal["basic", "detailed", "comprehensive"] = "detailed",
    context: Optional[str] = None
) -> str:
    """
    Analyze sentiment of text with multi-dimensional analysis.

    This agent performs comprehensive sentiment analysis including:
    - Overall sentiment classification (positive/negative/neutral/mixed)
    - Polarity and subjectivity scoring
    - Emotion detection (joy, sadness, anger, fear, surprise, disgust)
    - Aspect-based sentiment analysis
    - Key phrase extraction
    - Intensity assessment

    Args:
        text: The text to analyze
        analysis_depth: Level of analysis detail
        context: Optional context to improve analysis

    Returns:
        SentimentAnalysisResult with complete analysis

    Example:
        ```python
        result = await analyze_sentiment(
            text="The product quality is excellent but the price is too high!",
            analysis_depth="detailed"
        )
        print(f"Overall: {result.overall_sentiment}")
        print(f"Polarity: {result.polarity_score}")
        for aspect in result.aspects:
            print(f"{aspect.aspect}: {aspect.sentiment}")
        ```
    """
    context_info = f"\n\nContext: {context}" if context else ""
    depth_instruction = {
        "basic": "Provide basic sentiment classification and polarity score.",
        "detailed": "Provide detailed analysis including emotions and key aspects.",
        "comprehensive": "Provide comprehensive analysis with all emotions, aspects, and detailed reasoning."
    }[analysis_depth]

    return f"""You are an expert sentiment analysis AI. Analyze the sentiment of the following text.

Text to analyze:
"{text}"
{context_info}

Analysis Depth: {depth_instruction}

Perform a thorough sentiment analysis:

1. **Overall Sentiment**: Classify as positive, negative, neutral, or mixed
   - Positive: Generally favorable, optimistic, or satisfied
   - Negative: Generally unfavorable, pessimistic, or dissatisfied
   - Neutral: Balanced, factual, or no clear sentiment
   - Mixed: Contains both positive and negative sentiments

2. **Polarity Score**: Assign a score from -1.0 (very negative) to 1.0 (very positive)
   - Very negative: -1.0 to -0.6
   - Negative: -0.6 to -0.2
   - Neutral: -0.2 to 0.2
   - Positive: 0.2 to 0.6
   - Very positive: 0.6 to 1.0

3. **Subjectivity Score**: Assign a score from 0.0 (objective) to 1.0 (subjective)
   - Objective: Facts, data, neutral descriptions
   - Subjective: Opinions, emotions, personal views

4. **Emotion Detection**: Score each emotion from 0.0 to 1.0:
   - Joy: Happiness, delight, satisfaction
   - Sadness: Disappointment, sorrow, melancholy
   - Anger: Frustration, annoyance, rage
   - Fear: Anxiety, worry, concern
   - Surprise: Unexpected, astonishment
   - Disgust: Revulsion, distaste, contempt

5. **Aspect-Based Analysis**: Identify specific aspects mentioned and their sentiment
   - E.g., "customer service", "product quality", "price", "delivery"
   - For each aspect: sentiment, confidence, and specific mentions

6. **Key Phrases**: Extract phrases that strongly indicate sentiment
   - Include both positive and negative key phrases

7. **Intensity**: Assess how strong the sentiment is
   - Weak: Subtle, mild sentiment indicators
   - Moderate: Clear but not extreme sentiment
   - Strong: Clear and emphatic sentiment
   - Very Strong: Extreme, emphatic, or emotionally charged

8. **Summary**: Provide a concise summary explaining the sentiment

Be nuanced and consider:
- Sarcasm or irony (may flip apparent sentiment)
- Mixed sentiments (can be positive about some things, negative about others)
- Context and domain
- Intensity modifiers (very, extremely, slightly, etc.)
- Negations (not good, never satisfied, etc.)"""


# Public API - wrapper that returns parsed result
@trace()
async def analyze_sentiment(
    text: str,
    analysis_depth: Literal["basic", "detailed", "comprehensive"] = "detailed",
    context: Optional[str] = None
) -> SentimentAnalysisResult:
    """
    Analyze sentiment of text with multi-dimensional analysis.

    This is the main public API function. It wraps the Mirascope call and returns
    the parsed result.

    Args:
        text: The text to analyze
        analysis_depth: Level of analysis detail
        context: Optional context to improve analysis

    Returns:
        SentimentAnalysisResult with complete analysis
    """
    response = await _analyze_sentiment_call(text, analysis_depth, context)
    return response.parse()


# Convenience functions
@trace()
async def quick_sentiment(text: str) -> str:
    """
    Quick sentiment classification.

    Returns just the overall sentiment.
    """
    result = await analyze_sentiment(text, analysis_depth="basic")
    return result.overall_sentiment


@trace()
async def sentiment_with_score(text: str) -> dict[str, any]:
    """
    Sentiment with polarity score.

    Returns simplified result with sentiment and score.
    """
    result = await analyze_sentiment(text, analysis_depth="basic")
    return {
        "sentiment": result.overall_sentiment,
        "polarity": result.polarity_score,
        "intensity": result.intensity
    }


@trace()
async def aspect_sentiment(text: str) -> list[dict[str, str]]:
    """
    Extract aspect-based sentiments only.

    Returns list of aspects and their sentiments.
    """
    result = await analyze_sentiment(text, analysis_depth="detailed")
    return [
        {
            "aspect": aspect.aspect,
            "sentiment": aspect.sentiment,
            "confidence": aspect.confidence
        }
        for aspect in result.aspects
    ]


@trace()
async def emotion_analysis(text: str) -> dict[str, float]:
    """
    Extract emotion scores only.

    Returns dictionary of emotion scores.
    """
    result = await analyze_sentiment(text, analysis_depth="detailed")
    return result.emotions.model_dump()
