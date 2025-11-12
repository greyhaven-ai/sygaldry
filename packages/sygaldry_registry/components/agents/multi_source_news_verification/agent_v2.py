from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from datetime import datetime
from enum import Enum
from mirascope import llm
from pydantic import BaseModel, Field
from typing import Optional

# Import search tools for real-time verification
try:
    from duckduckgo_search import DDGS

    DUCKDUCKGO_AVAILABLE = True
except ImportError:
    DUCKDUCKGO_AVAILABLE = False

try:
    import os
    from exa_py import Exa

    EXA_AVAILABLE = bool(os.environ.get("EXA_API_KEY"))
except ImportError:
    EXA_AVAILABLE = False


# ========== ENUMS (unchanged) ==========
class CredibilityLevel(str, Enum):
    """Source credibility levels."""

    VERY_HIGH = "very_high"
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    VERY_LOW = "very_low"
    UNKNOWN = "unknown"


class VerificationStatus(str, Enum):
    """Verification status of claims."""

    VERIFIED = "verified"
    PARTIALLY_VERIFIED = "partially_verified"
    UNVERIFIED = "unverified"
    CONTRADICTED = "contradicted"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    MISLEADING_CONTEXT = "misleading_context"


class BiasDirection(str, Enum):
    """Political/ideological bias direction."""

    FAR_LEFT = "far_left"
    LEFT = "left"
    CENTER_LEFT = "center_left"
    CENTER = "center"
    CENTER_RIGHT = "center_right"
    RIGHT = "right"
    FAR_RIGHT = "far_right"
    UNKNOWN = "unknown"


class MisinformationType(str, Enum):
    """Types of misinformation."""

    FABRICATION = "fabrication"
    MANIPULATION = "manipulation"
    MISREPRESENTATION = "misrepresentation"
    FALSE_CONTEXT = "false_context"
    SATIRE = "satire"
    CLICKBAIT = "clickbait"
    PROPAGANDA = "propaganda"
    CONSPIRACY_THEORY = "conspiracy_theory"


class ClaimType(str, Enum):
    """Types of claims for verification routing."""

    STATISTICAL = "statistical"
    SCIENTIFIC = "scientific"
    MEDICAL = "medical"
    POLITICAL = "political"
    HISTORICAL = "historical"
    QUOTE = "quote"
    IMAGE_VIDEO = "image_video"
    SOCIAL_MEDIA = "social_media"
    FINANCIAL = "financial"
    LEGAL = "legal"
    GENERAL = "general"


# ========== TOOLS (converted to functions) ==========

@llm.tool
def web_search(query: str, max_results: int = 5) -> str:
    """Search the web for real-time information to verify claims.

    Args:
        query: Search query to find relevant information
        max_results: Maximum number of results to return

    Returns:
        Formatted search results or error message
    """
    results = []

    # Try DuckDuckGo first
    if DUCKDUCKGO_AVAILABLE:
        try:
            with DDGS() as ddgs:
                search_results = list(ddgs.text(query, max_results=max_results))
                for result in search_results:
                    results.append(
                        f"Title: {result.get('title', '')}\nURL: {result.get('href', '')}\nSnippet: {result.get('body', '')}"
                    )
            return "\n\n".join(results) if results else "No search results found."
        except Exception as e:
            pass

    # Fallback to Exa if available
    if EXA_AVAILABLE:
        try:
            exa = Exa(os.environ.get("EXA_API_KEY"))
            search_result = exa.search(query=query, num_results=max_results)
            for item in search_result.results:
                results.append(f"Title: {item.title}\nURL: {item.url}\nScore: {item.score}")
            return "\n\n".join(results) if results else "No search results found."
        except Exception as e:
            pass

    return "Web search unavailable. Please install duckduckgo-search or configure EXA_API_KEY."


@llm.tool
def fact_check_search(claim: str) -> str:
    """Search fact-checking websites for existing verification of claims.

    Args:
        claim: The claim to search for fact-checks

    Returns:
        Formatted fact-check search results
    """
    fact_check_sites = [
        "site:snopes.com",
        "site:factcheck.org",
        "site:politifact.com",
        "site:fullfact.org",
        "site:apnews.com/APFactCheck",
        "site:reuters.com/fact-check",
        "site:washingtonpost.com/news/fact-checker",
        "site:cnn.com/factsfirst",
        "site:nytimes.com/spotlight/fact-checks",
        "site:usatoday.com/news/factcheck",
        "site:factcheck.afp.com",
        "site:poynter.org",
        "site:leadstories.com",
        "site:factcheckni.org",
        "site:chequeado.com",
        "site:africacheck.org",
        "site:teyit.org",
        "site:factly.in",
        "site:boomlive.in",
        "site:altnews.in",
        "site:maldita.es",
        "site:newtral.es",
    ]

    results = []
    if DUCKDUCKGO_AVAILABLE:
        try:
            with DDGS() as ddgs:
                # Search top fact-checking sites
                for site in fact_check_sites[:5]:  # Limit to avoid rate limiting
                    query = f"{site} {claim}"
                    search_results = list(ddgs.text(query, max_results=2))
                    for result in search_results:
                        results.append(
                            f"Source: {site.replace('site:', '')}\nTitle: {result.get('title', '')}\nURL: {result.get('href', '')}\nSnippet: {result.get('body', '')}"
                        )

                # Also do a general fact-check search
                general_query = f'"{claim}" fact check OR debunked OR false OR verified'
                general_results = list(ddgs.text(general_query, max_results=3))
                for result in general_results:
                    results.append(
                        f"General Search:\nTitle: {result.get('title', '')}\nURL: {result.get('href', '')}\nSnippet: {result.get('body', '')}"
                    )

            return "\n\n".join(results) if results else "No fact-checks found for this claim."
        except Exception:
            pass

    return "Fact-check search unavailable. Unable to search fact-checking databases."


@llm.tool
def academic_search(query: str) -> str:
    """Search academic sources and research papers to verify scientific claims.

    Args:
        query: Scientific or academic claim to verify

    Returns:
        Formatted academic search results
    """
    academic_sites = [
        "site:scholar.google.com",
        "site:pubmed.ncbi.nlm.nih.gov",
        "site:arxiv.org",
        "site:jstor.org",
        "site:sciencedirect.com",
        "site:nature.com",
        "site:science.org",
        "site:plos.org",
        "site:academic.oup.com",
        "site:springer.com",
    ]

    results = []
    if DUCKDUCKGO_AVAILABLE:
        try:
            with DDGS() as ddgs:
                # Search academic sources
                for site in academic_sites[:3]:
                    site_query = f"{site} {query}"
                    search_results = list(ddgs.text(site_query, max_results=2))
                    for result in search_results:
                        results.append(
                            f"Academic Source: {site.replace('site:', '')}\nTitle: {result.get('title', '')}\nURL: {result.get('href', '')}\nSnippet: {result.get('body', '')}"
                        )

                # Search for meta-analyses and systematic reviews
                meta_query = f'"{query}" meta-analysis OR systematic review OR peer-reviewed'
                meta_results = list(ddgs.text(meta_query, max_results=2))
                for result in meta_results:
                    results.append(
                        f"Research:\nTitle: {result.get('title', '')}\nURL: {result.get('href', '')}\nSnippet: {result.get('body', '')}"
                    )

            return "\n\n".join(results) if results else "No academic sources found."
        except Exception:
            pass

    return "Academic search unavailable."


@llm.tool
def government_data_search(query: str, country: str = "US") -> str:
    """Search official government sources and databases for statistics and official statements.

    Args:
        query: Claim involving government data, statistics, or official statements
        country: Country code for government sources (US, UK, EU, etc.)

    Returns:
        Formatted government data search results
    """
    gov_sites = {
        "US": [
            "site:data.gov",
            "site:census.gov",
            "site:bls.gov",
            "site:cdc.gov",
            "site:fbi.gov/stats-services",
            "site:whitehouse.gov",
            "site:congress.gov",
            "site:gao.gov",
            "site:cbo.gov",
            "site:federalregister.gov",
        ],
        "UK": ["site:gov.uk", "site:ons.gov.uk", "site:parliament.uk", "site:data.gov.uk"],
        "EU": ["site:europa.eu", "site:ec.europa.eu", "site:eurostat.ec.europa.eu"],
        "GLOBAL": ["site:who.int", "site:un.org", "site:worldbank.org", "site:imf.org", "site:oecd.org"],
    }

    results = []
    sites_to_search = gov_sites.get(country, []) + gov_sites["GLOBAL"]

    if DUCKDUCKGO_AVAILABLE:
        try:
            with DDGS() as ddgs:
                for site in sites_to_search[:4]:
                    site_query = f"{site} {query}"
                    search_results = list(ddgs.text(site_query, max_results=2))
                    for result in search_results:
                        results.append(
                            f"Official Source: {site.replace('site:', '')}\nTitle: {result.get('title', '')}\nURL: {result.get('href', '')}\nSnippet: {result.get('body', '')}"
                        )

            return "\n\n".join(results) if results else "No government data found."
        except Exception:
            pass

    return "Government data search unavailable."


@llm.tool
def reverse_image_search(image_description: str) -> str:
    """Verify images and videos by searching for their original source and context.

    Args:
        image_description: Description of the image or video to verify

    Returns:
        Image verification search results
    """
    if DUCKDUCKGO_AVAILABLE:
        try:
            with DDGS() as ddgs:
                results = []

                # Search for the image description with verification keywords
                queries = [
                    f'"{image_description}" original source',
                    f'"{image_description}" fake OR manipulated OR doctored',
                    f'"{image_description}" fact check image',
                    f'"{image_description}" reverse image search results',
                ]

                for query in queries:
                    search_results = list(ddgs.text(query, max_results=2))
                    for result in search_results:
                        results.append(
                            f"Image Search:\nQuery: {query}\nTitle: {result.get('title', '')}\nURL: {result.get('href', '')}\nSnippet: {result.get('body', '')}"
                        )

                return "\n\n".join(results) if results else "No image verification results found."
        except Exception:
            pass

    return "Image verification search unavailable. Consider using Google Reverse Image Search or TinEye directly."


@llm.tool
def social_media_verification(claim: str, platform: str = "") -> str:
    """Verify claims originating from social media by searching for original posts and context.

    Args:
        claim: Claim or quote from social media
        platform: Social media platform (twitter, facebook, instagram, etc.)

    Returns:
        Social media verification results
    """
    results = []

    if DUCKDUCKGO_AVAILABLE:
        try:
            with DDGS() as ddgs:
                # Platform-specific searches
                if platform:
                    platform_query = f'site:{platform}.com "{claim}"'
                    search_results = list(ddgs.text(platform_query, max_results=3))
                    for result in search_results:
                        results.append(
                            f"Platform Search ({platform}):\nTitle: {result.get('title', '')}\nURL: {result.get('href', '')}\nSnippet: {result.get('body', '')}"
                        )

                # General social media verification
                verification_queries = [
                    f'"{claim}" verified account OR official statement',
                    f'"{claim}" deleted tweet OR deleted post OR screenshot',
                    f'"{claim}" social media hoax OR fake',
                ]

                for query in verification_queries:
                    search_results = list(ddgs.text(query, max_results=2))
                    for result in search_results:
                        results.append(
                            f"Verification Search:\nQuery: {query}\nTitle: {result.get('title', '')}\nURL: {result.get('href', '')}\nSnippet: {result.get('body', '')}"
                        )

            return "\n\n".join(results) if results else "No social media verification results found."
        except Exception:
            pass

    return "Social media verification unavailable."


@llm.tool
def expert_source_search(topic: str, claim: str) -> str:
    """Find and verify expert opinions and authoritative sources on specific topics.

    Args:
        topic: Topic requiring expert verification
        claim: Specific claim to verify with experts

    Returns:
        Expert source search results
    """
    expert_sources = [
        "site:harvard.edu",
        "site:stanford.edu",
        "site:mit.edu",
        "site:oxford.ac.uk",
        "site:cambridge.org",
        "site:mayoclinic.org",
        "site:clevelandclinic.org",
        "site:johnshopkins.edu",
        "site:scientificamerican.com",
        "site:theconversation.com",
    ]

    results = []
    if DUCKDUCKGO_AVAILABLE:
        try:
            with DDGS() as ddgs:
                # Search expert sources
                for source in expert_sources[:3]:
                    query = f"{source} {topic} {claim}"
                    search_results = list(ddgs.text(query, max_results=2))
                    for result in search_results:
                        results.append(
                            f"Expert Source: {source.replace('site:', '')}\nTitle: {result.get('title', '')}\nURL: {result.get('href', '')}\nSnippet: {result.get('body', '')}"
                        )

                # Search for expert quotes
                expert_query = f'"{topic}" expert OR professor OR researcher "{claim}"'
                expert_results = list(ddgs.text(expert_query, max_results=3))
                for result in expert_results:
                    results.append(
                        f"Expert Opinion:\nTitle: {result.get('title', '')}\nURL: {result.get('href', '')}\nSnippet: {result.get('body', '')}"
                    )

            return "\n\n".join(results) if results else "No expert sources found."
        except Exception:
            pass

    return "Expert source search unavailable."


# ========== RESPONSE MODELS (unchanged) ==========

class SourceCredibility(BaseModel):
    """Enhanced credibility assessment of a news source."""

    source_name: str = Field(..., description="Name of the news source")
    url: str = Field(..., description="URL of the source")
    credibility_level: CredibilityLevel = Field(..., description="Overall credibility assessment")
    bias_direction: BiasDirection = Field(..., description="Political/ideological bias")
    factual_reporting: str = Field(..., description="Assessment of factual reporting quality")
    transparency: str = Field(..., description="Transparency of ownership and funding")
    editorial_standards: str = Field(..., description="Editorial standards and corrections policy")
    track_record: str = Field(..., description="Historical accuracy track record")
    red_flags: list[str] = Field(..., description="Potential credibility concerns")
    strengths: list[str] = Field(..., description="Credibility strengths")
    fact_checker_ratings: dict[str, str] = Field(default_factory=dict, description="Ratings from fact-checkers")
    media_literacy_notes: list[str] = Field(..., description="Media literacy education points")


class FactCheck(BaseModel):
    """Enhanced fact-checking result for a specific claim."""

    claim: str = Field(..., description="The specific claim being fact-checked")
    verification_status: VerificationStatus = Field(..., description="Verification result")
    supporting_sources: list[str] = Field(..., description="Sources that support the claim")
    contradicting_sources: list[str] = Field(..., description="Sources that contradict the claim")
    primary_sources: list[str] = Field(..., description="Primary source documents")
    evidence_quality: str = Field(..., description="Quality of available evidence")
    confidence_level: float = Field(..., description="Confidence in verification (0-1)")
    context: str = Field(..., description="Important context for the claim")
    missing_context: list[str] = Field(..., description="Context that may be missing")
    fact_checker_consensus: str | None = Field(None, description="Consensus from fact-checkers")
    limitations: list[str] = Field(..., description="Limitations in verification")


class BiasAnalysis(BaseModel):
    """Analysis of bias in news content."""

    bias_type: str = Field(..., description="Type of bias detected")
    bias_indicators: list[str] = Field(..., description="Specific indicators of bias")
    loaded_language: list[str] = Field(..., description="Examples of loaded language")
    framing_analysis: str = Field(..., description="How the story is framed")
    missing_perspectives: list[str] = Field(..., description="Perspectives not included")
    source_selection_bias: str = Field(..., description="Bias in source selection")
    visual_bias: str | None = Field(None, description="Bias in visual elements")
    headline_bias: str = Field(..., description="Bias in headline vs content")


class NewsAnalysis(BaseModel):
    """Enhanced analysis of news content and claims."""

    headline: str = Field(..., description="News headline")
    main_claims: list[str] = Field(..., description="Key claims made in the article")
    claim_types: dict[str, ClaimType] = Field(..., description="Type categorization for each claim")
    claim_sources: dict[str, list[str]] = Field(..., description="Sources for each claim")
    emotional_language: list[str] = Field(..., description="Emotionally charged language used")
    missing_context: list[str] = Field(..., description="Important context that may be missing")
    potential_biases: list[str] = Field(..., description="Potential biases in presentation")
    bias_analysis: BiasAnalysis = Field(..., description="Detailed bias analysis")
    factual_vs_opinion: dict[str, str] = Field(..., description="Distinction between facts and opinions")
    sensationalism_score: float = Field(..., description="Level of sensationalism (0-1)")
    completeness_score: float = Field(..., description="Completeness of reporting (0-1)")
    transparency_score: float = Field(..., description="Transparency about sources (0-1)")
    misinformation_indicators: list[MisinformationType] = Field(..., description="Potential misinformation types")
    verification_priority: list[str] = Field(..., description="Claims prioritized for verification")


class MediaLiteracyReport(BaseModel):
    """Media literacy education component."""

    key_questions: list[str] = Field(..., description="Questions readers should ask")
    red_flags_found: list[str] = Field(..., description="Red flags in this content")
    verification_tips: list[str] = Field(..., description="Tips for verifying similar content")
    critical_thinking_prompts: list[str] = Field(..., description="Prompts for critical analysis")
    fact_checking_resources: list[str] = Field(..., description="Resources for fact-checking")
    media_literacy_lessons: list[str] = Field(..., description="Key media literacy lessons")


class NewsVerification(BaseModel):
    """Enhanced comprehensive news verification result."""

    original_article: str = Field(..., description="Original article or claim")
    source_credibility: list[SourceCredibility] = Field(..., description="Credibility of sources")
    news_analysis: NewsAnalysis = Field(..., description="Analysis of the news content")
    fact_checks: list[FactCheck] = Field(..., description="Fact-checking results")
    cross_reference_analysis: str = Field(..., description="Cross-reference analysis across sources")
    consensus_level: str = Field(..., description="Level of consensus across sources")
    reliability_indicators: list[str] = Field(..., description="Indicators of reliability")
    warning_signs: list[str] = Field(..., description="Warning signs of misinformation")
    media_literacy_report: MediaLiteracyReport = Field(..., description="Media literacy education")
    recommendations: list[str] = Field(..., description="Recommendations for readers")
    alternative_sources: list[str] = Field(..., description="Alternative sources to consult")


class VerificationResult(BaseModel):
    """Enhanced final verification result with summary."""

    verification: NewsVerification
    overall_credibility: CredibilityLevel = Field(..., description="Overall credibility assessment")
    misinformation_risk: str = Field(..., description="Risk level of misinformation")
    key_findings: list[str] = Field(..., description="Key findings from verification")
    confidence_score: float = Field(..., description="Overall confidence in assessment (0-1)")
    action_recommendations: list[str] = Field(..., description="Recommended actions for readers")
    follow_up_suggestions: list[str] = Field(..., description="Suggestions for further verification")
    share_recommendations: str = Field(..., description="Recommendations about sharing this content")
    educational_value: str = Field(..., description="Educational insights from this verification")


# ========== AGENT FUNCTIONS (to be converted) ==========
# TO BE CONTINUED...
