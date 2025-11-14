"""Contract Analysis Agent for legal document analysis.

This agent analyzes legal contracts to identify risks, obligations, key terms, and clauses.
It uses LLM capabilities to provide comprehensive contract review and analysis.
"""

from __future__ import annotations

from mirascope import llm
from pydantic import BaseModel, Field
from typing import Literal, Optional

# Make lilypad optional
try:
    from lilypad import trace
    LILYPAD_AVAILABLE = True
except ImportError:
    # Fallback no-op decorator if lilypad not available
    def trace():
        def decorator(func):
            return func
        return decorator
    LILYPAD_AVAILABLE = False


class ContractClause(BaseModel):
    """A clause extracted from a contract."""

    clause_type: str = Field(..., description="Type of clause (e.g., 'termination', 'liability', 'payment')")
    content: str = Field(..., description="The actual text of the clause")
    section: str = Field(..., description="Section number or reference in the contract")
    importance: Literal["low", "medium", "high", "critical"] = Field(..., description="Importance level of the clause")
    explanation: str = Field(..., description="Plain language explanation of what this clause means")


class RiskAssessment(BaseModel):
    """Risk assessment for a contract element."""

    risk_type: str = Field(..., description="Type of risk (e.g., 'financial', 'legal', 'operational')")
    severity: Literal["low", "medium", "high", "critical"] = Field(..., description="Risk severity level")
    description: str = Field(..., description="Description of the risk")
    affected_clause: str = Field(..., description="Which clause or section creates this risk")
    mitigation_suggestion: str = Field(..., description="Suggested way to mitigate this risk")
    likelihood: Literal["unlikely", "possible", "likely", "very_likely"] = Field(
        ..., description="Likelihood of risk occurring"
    )


class ContractObligation(BaseModel):
    """An obligation imposed by the contract."""

    party: str = Field(..., description="Party responsible for the obligation")
    obligation_type: str = Field(..., description="Type of obligation (e.g., 'payment', 'delivery', 'reporting')")
    description: str = Field(..., description="What must be done")
    deadline: Optional[str] = Field(None, description="Deadline or timeline for the obligation")
    consequences: str = Field(..., description="Consequences of failing to meet this obligation")
    recurring: bool = Field(..., description="Whether this is a one-time or recurring obligation")


class KeyTermExtraction(BaseModel):
    """Key terms extracted from contract."""

    terms: list[ContractClause] = Field(..., description="List of key contract clauses")
    contract_type: str = Field(..., description="Type of contract (e.g., 'employment', 'license', 'service')")
    parties: list[str] = Field(..., description="Parties involved in the contract")
    effective_date: Optional[str] = Field(None, description="When the contract becomes effective")
    expiration_date: Optional[str] = Field(None, description="When the contract expires")
    jurisdiction: Optional[str] = Field(None, description="Legal jurisdiction governing the contract")


class RiskAnalysis(BaseModel):
    """Risk analysis results."""

    risks: list[RiskAssessment] = Field(..., description="Identified risks")
    overall_risk_level: Literal["low", "medium", "high", "critical"] = Field(
        ..., description="Overall contract risk level"
    )
    risk_summary: str = Field(..., description="Summary of main risks")
    red_flags: list[str] = Field(..., description="Major red flags or concerning items")


class ObligationExtraction(BaseModel):
    """Extracted obligations from contract."""

    obligations: list[ContractObligation] = Field(..., description="List of contractual obligations")
    obligation_count_by_party: dict[str, int] = Field(..., description="Count of obligations per party")
    critical_obligations: list[str] = Field(..., description="Most critical obligations to track")


class ContractAnalysisResult(BaseModel):
    """Complete contract analysis result."""

    key_terms: list[ContractClause] = Field(..., description="Key terms and clauses identified")
    risks: list[RiskAssessment] = Field(..., description="Risk assessments")
    obligations: list[ContractObligation] = Field(..., description="Contractual obligations")
    summary: str = Field(..., description="Executive summary of the contract")
    recommendations: list[str] = Field(..., description="Recommendations for contract review")
    overall_assessment: Literal["favorable", "neutral", "unfavorable", "requires_legal_review"] = Field(
        ..., description="Overall assessment of the contract"
    )
    contract_type: str = Field(..., description="Type of contract")
    parties: list[str] = Field(..., description="Parties to the contract")


# Step 1: Extract key terms and clauses
@llm.call(
    provider="openai:completions",
    model_id="gpt-4o-mini",
    format=KeyTermExtraction,
)
async def extract_key_terms(contract_text: str, focus_areas: list[str] | None = None) -> str:
    """Extract key terms and clauses from contract."""
    focus = f"\n\nSpecific focus areas: {', '.join(focus_areas)}" if focus_areas else ""

    return f"""You are an expert contract lawyer. Analyze this contract and extract all key terms and clauses.

Contract Text:
{contract_text}
{focus}

Identify:
1. Type of contract
2. All parties involved
3. Effective dates and expiration dates
4. Jurisdiction (if specified)
5. Key clauses including:
   - Payment/compensation terms
   - Termination conditions
   - Liability limitations
   - Confidentiality provisions
   - Non-compete clauses
   - Intellectual property rights
   - Warranties and representations
   - Indemnification clauses
   - Dispute resolution mechanisms
   - Renewal/extension terms

For each clause, classify its importance and provide a plain-language explanation."""


# Step 2: Identify risks
@llm.call(
    provider="openai:completions",
    model_id="gpt-4o-mini",
    format=RiskAnalysis,
)
async def identify_risks(contract_text: str, key_terms: str) -> str:
    """Identify risks in the contract."""
    return f"""You are an expert contract lawyer performing risk assessment.

Contract Text:
{contract_text}

Key Terms Already Identified:
{key_terms}

Perform a comprehensive risk analysis:

1. Identify all potential risks including:
   - Financial risks (unlimited liability, payment obligations, penalties)
   - Legal risks (unfavorable jurisdiction, dispute resolution issues)
   - Operational risks (overly restrictive terms, difficult obligations)
   - Reputational risks
   - Compliance risks

2. For each risk:
   - Classify the type and severity
   - Assess likelihood
   - Identify which clause creates the risk
   - Suggest mitigation strategies

3. Identify any red flags:
   - Unusually one-sided terms
   - Automatic renewal clauses
   - Unreasonable penalties
   - Overly broad non-compete or IP assignments
   - Liability caps that are too low
   - Hidden or unclear obligations

4. Provide an overall risk assessment

Be thorough and err on the side of identifying potential issues."""


# Step 3: Extract obligations
@llm.call(
    provider="openai:completions",
    model_id="gpt-4o-mini",
    format=ObligationExtraction,
)
async def extract_obligations(contract_text: str, parties: list[str]) -> str:
    """Extract all contractual obligations."""
    parties_str = ", ".join(parties)

    return f"""You are an expert contract lawyer extracting obligations from a contract.

Contract Text:
{contract_text}

Parties: {parties_str}

Extract ALL obligations for each party:

1. For each obligation identify:
   - Which party is responsible
   - Type of obligation
   - Detailed description of what must be done
   - Any deadlines or timelines
   - Consequences of non-compliance
   - Whether it's one-time or recurring

2. Common obligation types to look for:
   - Payment obligations
   - Delivery/performance obligations
   - Reporting requirements
   - Insurance requirements
   - Confidentiality obligations
   - Notice requirements
   - Compliance obligations
   - Record-keeping requirements
   - Audit rights
   - Cooperation obligations

3. Identify the most critical obligations that require tracking

4. Count obligations by party to assess balance

Be comprehensive and extract every obligation, even minor ones."""


# Main contract analysis function
@trace()
async def analyze_contract(
    contract_text: str,
    analysis_focus: list[str] | None = None,
    include_recommendations: bool = True,
    llm_provider: str = "openai",
    model: str = "gpt-4o-mini",
) -> ContractAnalysisResult:
    """
    Analyze a legal contract to identify risks, obligations, and key terms.

    This agent performs comprehensive contract analysis including:
    - Key term extraction and clause categorization
    - Risk assessment with severity and likelihood ratings
    - Obligation extraction with party assignments
    - Executive summary and recommendations

    Args:
        contract_text: The full text of the contract to analyze
        analysis_focus: Optional list of specific areas to focus on (e.g., ['risks', 'payments', 'termination'])
        include_recommendations: Whether to include actionable recommendations
        llm_provider: LLM provider to use
        model: Specific model to use

    Returns:
        ContractAnalysisResult with complete analysis

    Example:
        ```python
        result = await analyze_contract(
            contract_text=my_contract,
            analysis_focus=['risks', 'liabilities'],
            include_recommendations=True
        )

        print(f"Contract Type: {result.contract_type}")
        print(f"Overall Assessment: {result.overall_assessment}")
        print(f"\\nRisks Found: {len(result.risks)}")
        for risk in result.risks:
            print(f"  - {risk.risk_type}: {risk.description}")
        ```
    """
    # Step 1: Extract key terms
    key_terms_result = await extract_key_terms(contract_text, analysis_focus)

    # Prepare key terms summary for risk analysis
    key_terms_summary = "\n".join([
        f"- {term.clause_type}: {term.content} (importance: {term.importance})"
        for term in key_terms_result.terms
    ])

    # Step 2: Identify risks
    risk_analysis = await identify_risks(contract_text, key_terms_summary)

    # Step 3: Extract obligations
    obligations_result = await extract_obligations(contract_text, key_terms_result.parties)

    # Step 4: Generate summary and recommendations
    @llm.call(
        provider="openai:completions",
        model_id="gpt-4o-mini",
    )
    async def generate_summary_and_recommendations(
        contract_type: str,
        parties: list[str],
        risk_count: int,
        obligation_count: int,
        overall_risk: str,
    ) -> str:
        """Generate executive summary and recommendations."""
        parties_str = " and ".join(parties)

        return f"""You are an expert contract lawyer providing an executive summary.

Contract Type: {contract_type}
Parties: {parties_str}
Risks Identified: {risk_count}
Obligations: {obligation_count}
Overall Risk Level: {overall_risk}

Provide:
1. A concise executive summary (2-3 paragraphs) suitable for business stakeholders
2. Key highlights they need to know
3. Overall recommendation (favorable, neutral, unfavorable, or requires legal review)

Keep the summary clear, actionable, and business-focused."""

    summary_text = await generate_summary_and_recommendations(
        contract_type=key_terms_result.contract_type,
        parties=key_terms_result.parties,
        risk_count=len(risk_analysis.risks),
        obligation_count=len(obligations_result.obligations),
        overall_risk=risk_analysis.overall_risk_level,
    )

    # Generate recommendations
    recommendations = []

    if include_recommendations:
        if risk_analysis.overall_risk_level in ["high", "critical"]:
            recommendations.append("Recommend legal review before signing")

        if len(risk_analysis.red_flags) > 0:
            recommendations.append(f"Address {len(risk_analysis.red_flags)} red flags identified in risk analysis")

        # Add specific mitigation recommendations
        for risk in risk_analysis.risks[:3]:  # Top 3 risks
            if risk.severity in ["high", "critical"]:
                recommendations.append(risk.mitigation_suggestion)

        # Check for imbalanced obligations
        if len(obligations_result.obligation_count_by_party) == 2:
            counts = list(obligations_result.obligation_count_by_party.values())
            if max(counts) > min(counts) * 2:
                recommendations.append("Review obligation balance - contract appears one-sided")

    # Determine overall assessment
    assessment = "favorable"
    if risk_analysis.overall_risk_level == "critical" or len(risk_analysis.red_flags) > 3:
        assessment = "requires_legal_review"
    elif risk_analysis.overall_risk_level == "high" or len(risk_analysis.red_flags) > 1:
        assessment = "unfavorable"
    elif risk_analysis.overall_risk_level == "medium":
        assessment = "neutral"

    return ContractAnalysisResult(
        key_terms=key_terms_result.terms,
        risks=risk_analysis.risks,
        obligations=obligations_result.obligations,
        summary=summary_text,
        recommendations=recommendations if include_recommendations else [],
        overall_assessment=assessment,
        contract_type=key_terms_result.contract_type,
        parties=key_terms_result.parties,
    )


# Convenience functions
async def quick_risk_check(contract_text: str) -> dict[str, any]:
    """
    Quick risk assessment of a contract.

    Returns simplified risk information.
    """
    result = await analyze_contract(contract_text, analysis_focus=["risks"], include_recommendations=False)

    return {
        "overall_risk": result.overall_assessment,
        "risk_count": len(result.risks),
        "critical_risks": [r.description for r in result.risks if r.severity == "critical"],
        "high_risks": [r.description for r in result.risks if r.severity == "high"],
    }


async def extract_obligations_only(contract_text: str) -> list[dict[str, str]]:
    """
    Extract only obligations without full analysis.

    Returns simplified obligation list.
    """
    result = await analyze_contract(contract_text, analysis_focus=["obligations"], include_recommendations=False)

    return [
        {
            "party": ob.party,
            "type": ob.obligation_type,
            "description": ob.description,
            "deadline": ob.deadline or "No deadline specified",
        }
        for ob in result.obligations
    ]
