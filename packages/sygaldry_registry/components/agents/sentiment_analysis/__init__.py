"""Sentiment Analysis Agent."""

from .agent import (
    SentimentAnalysisResult,
    EmotionScore,
    AspectSentiment,
    analyze_sentiment,
    quick_sentiment,
    sentiment_with_score,
    aspect_sentiment,
    emotion_analysis,
)

__all__ = [
    "analyze_sentiment",
    "SentimentAnalysisResult",
    "EmotionScore",
    "AspectSentiment",
    "quick_sentiment",
    "sentiment_with_score",
    "aspect_sentiment",
    "emotion_analysis",
]
