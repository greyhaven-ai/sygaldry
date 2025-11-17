from __future__ import annotations

from datetime import datetime
from mirascope import llm
from pydantic import BaseModel, Field
from typing import Literal, Optional

# Import Exa websets tools
try:
    from exa_websets_tools import (
        WebsetCriteria,
        WebsetEnrichment,
        WebsetSearchConfig,
        create_webset,
        get_webset_status,
        list_webset_items,
    )
except ImportError:
    # Fallback if tools aren't available yet
    create_webset = None
    get_webset_status = None
    list_webset_items = None
    WebsetSearchConfig = None
    WebsetEnrichment = None
    WebsetCriteria = None


class SalesTarget(BaseModel):
    """Sales target profile specification."""

    # Note: All fields must be required for OpenAI schema validation
    role_title: str | None = Field(..., description="Target job title (null if not specified)")
    company_size: str | None = Field(..., description="Company size range (null if not specified)")
    location: str | None = Field(..., description="Geographic location (null if not specified)")
    industry: str | None = Field(..., description="Target industry or vertical (null if not specified)")
    company_stage: str | None = Field(..., description="Company stage (null if not specified)")
    additional_criteria: list[str] = Field(..., description="Additional filtering criteria (empty list if none)")


class SalesIntelligenceResponse(BaseModel):
    """Response from sales intelligence search."""

    webset_id: str = Field(..., description="ID of the created webset")
    search_query: str = Field(..., description="Search query used")
    entity_type: str = Field(..., description="Type of entity searched for")
    # Note: All fields must be required for OpenAI schema validation
    criteria: list[str] = Field(..., description="Verification criteria applied (empty list if none)")
    enrichments: list[str] = Field(..., description="Data enrichments requested (empty list if none)")
    estimated_results: int | None = Field(..., description="Estimated number of results (null if unknown)")
    status: str = Field(..., description="Current status of the webset")


# Rebuild models to resolve forward references
SalesTarget.model_rebuild()
SalesIntelligenceResponse.model_rebuild()


# Internal LLM call function - returns AsyncResponse
@llm.call(
    provider="openai:completions",
    model_id="gpt-4o-mini",
    format=SalesIntelligenceResponse,
    tools=[create_webset, get_webset_status, list_webset_items] if create_webset else [],
)
async def _sales_intelligence_agent_call(
    role_or_company: str,
    company_size: str | None = None,
    location: str | None = None,
    industry: str | None = None,
    company_stage: str | None = None,
    additional_requirements: list[str] | None = None,
    llm_provider: str = "openai",
    model: str = "gpt-4o-mini",
) -> str:
    """
    Find targeted sales prospects using Exa websets.

    Args:
        role_or_company: Target role title or company type
        company_size: Company size requirements
        location: Geographic location
        industry: Target industry or vertical
        company_stage: Company stage or type
        additional_requirements: Additional filtering criteria
        llm_provider: LLM provider to use
        model: Model to use

    Returns:
        Sales intelligence response with webset details
    """
    current_date = datetime.now().strftime("%Y-%m-%d")
    additional_reqs = "\n".join(additional_requirements) if additional_requirements else "None"

    return f"""SYSTEM:
You are a sales intelligence agent specializing in finding targeted business contacts and companies using Exa's webset API.
Current date: {current_date}

Your capabilities:
- Create websets to find specific types of contacts and companies
- Define precise search criteria for qualification
- Request enrichments for contact information, company data, and social profiles
- Monitor search progress and retrieve results

Search Strategy:
1. Translate the sales target into a precise search query
2. Determine the appropriate entity type (person, company, etc.)
3. Define verification criteria based on the requirements
4. Add enrichments for relevant data extraction
5. Create the webset and monitor its progress

Entity Types:
- Use "person" for individual contacts (heads of sales, managers, etc.)
- Use "company" for organizational searches (agencies, startups, etc.)
- Use "research_lab" for academic/research institutions

Enrichment Options:
- LinkedIn profiles
- Company information (size, funding, industry)
- Contact details
- Recent activities/updates
- Team composition

USER REQUEST:
Role/Company Type: {role_or_company}
Company Size: {company_size}
Location: {location}
Industry: {industry}
Stage/Type: {company_stage}
Additional Requirements: {additional_reqs}

Create a webset to find these sales targets with appropriate criteria and enrichments."""


# Public wrapper - returns parsed SalesIntelligenceResponse
async def sales_intelligence_agent(
    role_or_company: str,
    company_size: str | None = None,
    location: str | None = None,
    industry: str | None = None,
    company_stage: str | None = None,
    additional_requirements: list[str] | None = None,
    llm_provider: str = "openai",
    model: str = "gpt-4o-mini",
) -> SalesIntelligenceResponse:
    """Find targeted sales prospects using Exa websets.

    Args:
        role_or_company: Target role title or company type
        company_size: Company size requirements
        location: Geographic location
        industry: Target industry or vertical
        company_stage: Company stage or type
        additional_requirements: Additional filtering criteria
        llm_provider: LLM provider to use
        model: Model to use

    Returns:
        SalesIntelligenceResponse with webset details
    """
    response = await _sales_intelligence_agent_call(
        role_or_company=role_or_company,
        company_size=company_size,
        location=location,
        industry=industry,
        company_stage=company_stage,
        additional_requirements=additional_requirements,
        llm_provider=llm_provider,
        model=model
    )
    return response.parse()


# Convenience functions for common sales searches
async def find_sales_leaders(company_size: str, location: str, **kwargs) -> SalesIntelligenceResponse:
    """Find heads of sales at companies matching criteria."""
    return await sales_intelligence_agent(role_or_company="Head of Sales", company_size=company_size, location=location, **kwargs)


async def find_marketing_agencies(location: str, max_employees: int = 50, **kwargs) -> SalesIntelligenceResponse:
    """Find marketing agencies in a specific location."""
    return await sales_intelligence_agent(
        role_or_company="Marketing agency", company_size=f"less than {max_employees} employees", location=location, **kwargs
    )


async def find_startup_executives(role: str, funding_stage: str, year: int = 2024, **kwargs) -> SalesIntelligenceResponse:
    """Find executives at startups that raised funding."""
    return await sales_intelligence_agent(
        role_or_company=role,
        company_stage=f"{funding_stage} in {year}",
        additional_requirements=[f"Must have a {role} position filled"],
        **kwargs,
    )
