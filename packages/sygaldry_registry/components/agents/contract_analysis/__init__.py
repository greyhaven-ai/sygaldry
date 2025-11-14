"""Contract Analysis Agent - Legal document analysis and risk assessment."""

from .agent import (
    ContractAnalysisResult,
    ContractClause,
    ContractObligation,
    RiskAssessment,
    analyze_contract,
    quick_risk_check,
    extract_obligations_only,
    extract_key_terms,
    identify_risks,
    extract_obligations,
)

__all__ = [
    "analyze_contract",
    "ContractAnalysisResult",
    "ContractClause",
    "ContractObligation",
    "RiskAssessment",
    "quick_risk_check",
    "extract_obligations_only",
    "extract_key_terms",
    "identify_risks",
    "extract_obligations",
]
