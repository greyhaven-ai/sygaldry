"""Financial Statement Analyzer - Analyzes financial reports and provides investment insights."""

from .agent import (
    FinancialAnalysisResult,
    FinancialRatios,
    TrendAnalysis,
    RedFlag,
    InvestmentInsight,
    analyze_financial_statements,
    calculate_financial_ratios,
    quick_health_check,
    calculate_ratios_only,
)

__all__ = [
    "analyze_financial_statements",
    "FinancialAnalysisResult",
    "FinancialRatios",
    "TrendAnalysis",
    "RedFlag",
    "InvestmentInsight",
    "calculate_financial_ratios",
    "quick_health_check",
    "calculate_ratios_only",
]
