from __future__ import annotations

from lilypad import trace
from mirascope import llm
from pydantic import BaseModel, Field
from typing import Any, Literal, Optional


# Response models for structured outputs
class KeyPoint(BaseModel):
    """A key point extracted from text."""

    point: str = Field(..., description="The key point or insight")
    importance: float = Field(..., ge=0.0, le=1.0, description="Importance score (0-1)")
    evidence: str = Field(..., description="Supporting evidence from the text")


class SummaryAnalysis(BaseModel):
    """Analysis of text for summarization."""

    main_topic: str = Field(..., description="Main topic or theme")
    # Note: Field(...) without description for nested model list to avoid OpenAI schema error
    # OpenAI rejects $ref with additional keywords like 'description'
    key_points: list[KeyPoint] = Field(...)
    target_audience: str = Field(..., description="Identified target audience")
    complexity_level: Literal["simple", "moderate", "complex", "technical"] = Field(..., description="Text complexity")
    recommended_length: int = Field(..., description="Recommended summary length in words")


class Summary(BaseModel):
    """A generated summary."""

    summary: str = Field(..., description="The summary text")
    style: str = Field(..., description="Summary style used")
    word_count: int = Field(..., description="Word count of summary")
    preserved_key_points: list[str] = Field(..., description="Key points preserved in summary")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in summary quality")


class ProgressiveSummary(BaseModel):
    """Progressive summary with multiple levels."""

    one_sentence: str = Field(..., description="One sentence summary")
    paragraph: str = Field(..., description="One paragraph summary")
    detailed: str = Field(..., description="Detailed summary")
    executive: str = Field(..., description="Executive summary")
    key_takeaways: list[str] = Field(..., description="Bullet point takeaways")


class SummaryValidation(BaseModel):
    """Validation results for a summary."""

    is_accurate: bool = Field(..., description="Whether summary accurately represents original")
    missing_points: list[str] = Field(..., description="Important points missing from summary")
    added_information: list[str] = Field(..., description="Information not in original text")
    quality_score: float = Field(..., ge=0.0, le=1.0, description="Overall quality score")
    improvements: list[str] = Field(..., description="Suggested improvements")


# Rebuild models to resolve forward references
KeyPoint.model_rebuild()
SummaryAnalysis.model_rebuild()
Summary.model_rebuild()
ProgressiveSummary.model_rebuild()
SummaryValidation.model_rebuild()


# Step 1: Analyze text for summarization (with CoT)
# Internal LLM call function - returns AsyncResponse
@llm.call(
    provider="openai:completions",
    model_id="gpt-4o-mini",
    format=SummaryAnalysis,
)
async def _analyze_for_summary_call(text: str) -> str:
    """Analyze text using chain-of-thought reasoning."""
    return f"""
    You are an expert text analyst preparing for summarization.

    Let me think through this step-by-step:

    1. First, I'll identify the main topic and theme
    2. Then extract key points with supporting evidence
    3. Determine the target audience based on language and content
    4. Assess the complexity level
    5. Recommend an appropriate summary length

    Text to analyze:
    "{text}"

    Here are examples of good analysis:

    Example 1:
    Text: "Climate change is accelerating. Global temperatures rose 1.1°C since pre-industrial times..."
    Analysis: Main topic: Climate change acceleration, Complexity: moderate, Audience: general public

    Example 2:
    Text: "The transformer architecture revolutionized NLP through self-attention mechanisms..."
    Analysis: Main topic: Transformer architecture in NLP, Complexity: technical, Audience: ML practitioners

    Now analyzing the provided text:
    """


# Public wrapper for analyze_for_summary
async def analyze_for_summary(text: str) -> SummaryAnalysis:
    """Analyze text using chain-of-thought reasoning."""
    response = await _analyze_for_summary_call(text)
    return response.parse()


# Step 2: Generate summary with style (few-shot)
# Internal LLM call function - returns AsyncResponse
@llm.call(
    provider="openai:completions",
    model_id="gpt-4o-mini",
    format=Summary,
)
async def _generate_summary_call(
    text: str,
    main_topic: str,
    key_points: str,
    target_audience: str,
    complexity_level: str,
    target_length: int,
    style: str,
    few_shot_examples: str,
    style_guidelines: str,
) -> str:
    """Generate summary with few-shot examples."""
    return f"""
    You are an expert summarizer. Generate a {style} summary based on this analysis.

    Original text: "{text}"

    Analysis:
    - Main topic: {main_topic}
    - Key points: {key_points}
    - Target audience: {target_audience}
    - Complexity: {complexity_level}
    - Target length: {target_length} words

    Examples of {style} summaries:

    {few_shot_examples}

    Guidelines for {style} summary:
    {style_guidelines}

    Generate a summary that:
    1. Captures all key points
    2. Matches the target audience
    3. Uses appropriate language for the style
    4. Stays within the target length
    5. Maintains accuracy to the original
    """


# Public wrapper for generate_summary
async def generate_summary(
    text: str,
    main_topic: str,
    key_points: str,
    target_audience: str,
    complexity_level: str,
    target_length: int,
    style: str,
    few_shot_examples: str,
    style_guidelines: str,
) -> Summary:
    """Generate summary with few-shot examples."""
    response = await _generate_summary_call(
        text=text,
        main_topic=main_topic,
        key_points=key_points,
        target_audience=target_audience,
        complexity_level=complexity_level,
        target_length=target_length,
        style=style,
        few_shot_examples=few_shot_examples,
        style_guidelines=style_guidelines,
    )
    return response.parse()


# Step 3: Progressive summarization chain
# Internal LLM call function - returns AsyncResponse
@llm.call(
    provider="openai:completions",
    model_id="gpt-4o-mini",
    format=ProgressiveSummary,
)
async def _generate_progressive_summary_call(text: str, key_points: str) -> str:
    """Generate summaries at multiple levels of detail."""
    return f"""
    Create progressive summaries of increasing detail.

    Text: "{text}"
    Key points: {key_points}

    Generate:
    1. One sentence summary (capture the absolute essence)
    2. One paragraph summary (main points with context)
    3. Detailed summary (comprehensive with nuance)
    4. Executive summary (decision-focused)
    5. Key takeaways (bullet points)

    Ensure each level builds upon the previous while adding appropriate detail.
    """


# Public wrapper for generate_progressive_summary
async def generate_progressive_summary(text: str, key_points: str) -> ProgressiveSummary:
    """Generate summaries at multiple levels of detail."""
    response = await _generate_progressive_summary_call(text=text, key_points=key_points)
    return response.parse()


# Step 4: Validate and refine summary
# Internal LLM call function - returns AsyncResponse
@llm.call(
    provider="openai:completions",
    model_id="gpt-4o-mini",
    format=SummaryValidation,
)
async def _validate_summary_call(original_text: str, summary: str, key_points: str) -> str:
    """Validate summary accuracy and quality."""
    return f"""
    Validate this summary against the original text.

    Original text: "{original_text}"
    Generated summary: "{summary}"
    Key points to preserve: {key_points}

    Check for:
    1. Accuracy - Does the summary faithfully represent the original?
    2. Completeness - Are all key points included?
    3. Additions - Is there any information not in the original?
    4. Clarity - Is the summary clear and well-structured?
    5. Conciseness - Is it appropriately concise?

    Provide specific feedback and improvement suggestions.
    """


# Public wrapper for validate_summary
async def validate_summary(original_text: str, summary: str, key_points: str) -> SummaryValidation:
    """Validate summary accuracy and quality."""
    response = await _validate_summary_call(original_text=original_text, summary=summary, key_points=key_points)
    return response.parse()


# Main summarization function with advanced chaining
@trace()
async def summarize_text(
    text: str,
    style: Literal["technical", "executive", "simple", "academic", "journalistic"] = "executive",
    target_length: int | None = None,
    progressive: bool = False,
    validate: bool = True,
    max_iterations: int = 3,
    llm_provider: str = "openai",
    model: str = "gpt-4o-mini",
) -> Summary | ProgressiveSummary:
    """
    Summarize text using advanced prompt engineering techniques.

    This agent uses chain-of-thought reasoning, few-shot learning,
    and iterative refinement to generate high-quality summaries.

    Args:
        text: Text to summarize
        style: Summary style
        target_length: Target length in words (None for auto)
        progressive: Generate multi-level progressive summary
        validate: Validate and refine the summary
        max_iterations: Maximum refinement iterations
        llm_provider: LLM provider to use
        model: Specific model to use

    Returns:
        Summary or ProgressiveSummary based on options
    """
    # Step 1: Analyze the text
    analysis = await analyze_for_summary(text)

    # Convert key points to string for prompts
    key_points_str = "\n".join([f"- {kp.point} (importance: {kp.importance})" for kp in analysis.key_points])

    # If progressive summary requested
    if progressive:
        return await generate_progressive_summary(text=text, key_points=key_points_str)

    # Determine target length
    if target_length is None:
        target_length = analysis.recommended_length

    # Get style-specific examples and guidelines
    few_shot_examples, style_guidelines = get_style_config(style)

    # Step 2: Generate initial summary
    summary = await generate_summary(
        text=text,
        main_topic=analysis.main_topic,
        key_points=key_points_str,
        target_audience=analysis.target_audience,
        complexity_level=analysis.complexity_level,
        target_length=target_length,
        style=style,
        few_shot_examples=few_shot_examples,
        style_guidelines=style_guidelines,
    )

    # Step 3: Validate and refine if requested
    if validate:
        for _ in range(max_iterations):
            validation = await validate_summary(original_text=text, summary=summary.summary, key_points=key_points_str)

            if validation.quality_score >= 0.8 and validation.is_accurate:
                break

            # Refine based on feedback
            refinement_prompt = f"""
            Improve this summary based on feedback:
            Summary: {summary.summary}
            Missing points: {validation.missing_points}
            Improvements needed: {validation.improvements}
            """

            # Generate refined summary
            summary = await generate_summary(
                text=text,
                main_topic=analysis.main_topic,
                key_points=key_points_str + f"\nMissing: {validation.missing_points}",
                target_audience=analysis.target_audience,
                complexity_level=analysis.complexity_level,
                target_length=target_length,
                style=style,
                few_shot_examples=few_shot_examples,
                style_guidelines=style_guidelines,
            )

    return summary


def get_style_config(style: str) -> tuple[str, str]:
    """Get few-shot examples and guidelines for each style."""
    configs = {
        "technical": (
            """Example: 'The system uses microservices architecture with Docker containers...'
            → 'Microservices architecture implemented via Docker enables scalable deployment.'""",
            "Use technical terminology, focus on specifications and implementation details",
        ),
        "executive": (
            """Example: 'Q3 revenue increased 23% driven by cloud services...'
            → 'Strong Q3 performance with 23% revenue growth from cloud expansion.'""",
            "Focus on outcomes, metrics, and strategic implications",
        ),
        "simple": (
            """Example: 'Photosynthesis converts light energy into chemical energy...'
            → 'Plants use sunlight to make their own food.'""",
            "Use simple language, avoid jargon, explain complex concepts simply",
        ),
        "academic": (
            """Example: 'The study examines correlation between variables X and Y...'
            → 'Research demonstrates significant correlation (p<0.05) between X and Y variables.'""",
            "Maintain scholarly tone, include methodology and findings",
        ),
        "journalistic": (
            """Example: 'The new policy affects millions of citizens...'
            → 'New policy to impact millions as government shifts approach.'""",
            "Lead with most important information, answer who/what/when/where/why",
        ),
    }
    return configs.get(style, ("", "Generate a clear, concise summary"))


# Convenience functions
async def quick_summary(text: str) -> str:
    """Generate a quick summary with defaults."""
    result = await summarize_text(text, validate=False)
    return result.summary


async def executive_brief(text: str) -> dict[str, Any]:
    """Generate an executive brief with key metrics."""
    summary = await summarize_text(text=text, style="executive", validate=True)
    progressive = await summarize_text(text=text, progressive=True)

    return {
        "one_line": progressive.one_sentence,
        "summary": summary.summary,
        "key_takeaways": progressive.key_takeaways,
        "word_count": summary.word_count,
        "confidence": summary.confidence_score,
    }


async def multi_style_summary(text: str, styles: list[str] | None = None) -> dict[str, str]:
    """Generate summaries in multiple styles."""
    if styles is None:
        styles = ["technical", "executive", "simple"]
    summaries = {}
    for style in styles:
        result = await summarize_text(text=text, style=style, validate=False)
        summaries[style] = result.summary
    return summaries
