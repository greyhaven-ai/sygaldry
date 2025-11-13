"""Financial Statement Analyzer Agent.

Analyzes financial reports, calculates ratios, identifies trends, and provides investment insights.
"""

from __future__ import annotations

from mirascope import llm
from pydantic import BaseModel, Field
from typing import Any, Literal, Optional

# Make lilypad optional
try:
    from lilypad import trace
    LILYPAD_AVAILABLE = True
except ImportError:
    def trace():
        def decorator(func):
            return func
        return decorator
    LILYPAD_AVAILABLE = False


class FinancialRatios(BaseModel):
    """Calculated financial ratios."""

    # Profitability Ratios
    gross_margin: Optional[float] = Field(None, description="Gross profit margin percentage")
    operating_margin: Optional[float] = Field(None, description="Operating profit margin percentage")
    net_margin: Optional[float] = Field(None, description="Net profit margin percentage")
    return_on_assets: Optional[float] = Field(None, description="ROA percentage")
    return_on_equity: Optional[float] = Field(None, description="ROE percentage")

    # Liquidity Ratios
    current_ratio: Optional[float] = Field(None, description="Current assets / current liabilities")
    quick_ratio: Optional[float] = Field(None, description="(Current assets - inventory) / current liabilities")
    cash_ratio: Optional[float] = Field(None, description="Cash / current liabilities")

    # Leverage Ratios
    debt_to_equity: Optional[float] = Field(None, description="Total debt / total equity")
    debt_to_assets: Optional[float] = Field(None, description="Total debt / total assets")
    interest_coverage: Optional[float] = Field(None, description="EBIT / interest expense")

    # Efficiency Ratios
    asset_turnover: Optional[float] = Field(None, description="Revenue / total assets")
    inventory_turnover: Optional[float] = Field(None, description="COGS / average inventory")
    receivables_turnover: Optional[float] = Field(None, description="Revenue / average receivables")


class TrendAnalysis(BaseModel):
    """Trend analysis results."""

    metric: str = Field(..., description="Name of the financial metric")
    trend_direction: Literal["increasing", "decreasing", "stable", "volatile"] = Field(
        ..., description="Direction of the trend"
    )
    change_percentage: float = Field(..., description="Percentage change over period")
    significance: Literal["major", "moderate", "minor"] = Field(..., description="Significance of the trend")
    interpretation: str = Field(..., description="What this trend means for the business")


class RedFlag(BaseModel):
    """Financial red flag or concern."""

    category: str = Field(..., description="Category of concern (e.g., 'liquidity', 'profitability')")
    severity: Literal["low", "medium", "high", "critical"] = Field(..., description="Severity level")
    description: str = Field(..., description="Description of the red flag")
    metric_value: Optional[str] = Field(None, description="The concerning metric value")
    recommendation: str = Field(..., description="Recommended action")


class InvestmentInsight(BaseModel):
    """Investment analysis insight."""

    insight_type: str = Field(..., description="Type of insight (e.g., 'strength', 'weakness', 'opportunity')")
    description: str = Field(..., description="Description of the insight")
    supporting_metrics: list[str] = Field(..., description="Metrics that support this insight")
    impact: Literal["positive", "negative", "neutral"] = Field(..., description="Impact on investment decision")


class FinancialAnalysisResult(BaseModel):
    """Complete financial analysis result."""

    ratios: FinancialRatios = Field(..., description="Calculated financial ratios")
    trends: list[TrendAnalysis] = Field(..., description="Identified trends")
    red_flags: list[RedFlag] = Field(..., description="Financial red flags or concerns")
    insights: list[InvestmentInsight] = Field(..., description="Investment insights")
    summary: str = Field(..., description="Executive summary of financial health")
    overall_rating: Literal["excellent", "good", "fair", "poor", "critical"] = Field(
        ..., description="Overall financial health rating"
    )
    recommendation: Literal["strong_buy", "buy", "hold", "sell", "strong_sell"] = Field(
        ..., description="Investment recommendation"
    )


# Step 1: Calculate financial ratios
@trace()
def calculate_financial_ratios(financial_data: dict[str, Any]) -> FinancialRatios:
    """
    Calculate financial ratios from financial statements.

    Args:
        financial_data: Dictionary containing financial statement data

    Returns:
        FinancialRatios object with calculated ratios
    """
    income = financial_data.get("income_statement", {})
    balance = financial_data.get("balance_sheet", {})
    cash_flow = financial_data.get("cash_flow_statement", {})

    ratios = {}

    # Profitability Ratios
    revenue = income.get("revenue") or income.get("total_revenue") or income.get("sales")
    cogs = income.get("cost_of_goods_sold") or income.get("cogs")
    operating_income = income.get("operating_income") or income.get("ebit")
    net_income = income.get("net_income")
    total_assets = balance.get("total_assets")
    total_equity = balance.get("total_equity") or balance.get("shareholders_equity")

    if revenue and cogs:
        ratios["gross_margin"] = ((revenue - cogs) / revenue) * 100

    if revenue and operating_income:
        ratios["operating_margin"] = (operating_income / revenue) * 100

    if revenue and net_income:
        ratios["net_margin"] = (net_income / revenue) * 100

    if total_assets and net_income:
        ratios["return_on_assets"] = (net_income / total_assets) * 100

    if total_equity and net_income and total_equity > 0:
        ratios["return_on_equity"] = (net_income / total_equity) * 100

    # Liquidity Ratios
    current_assets = balance.get("current_assets")
    current_liabilities = balance.get("current_liabilities")
    inventory = balance.get("inventory") or 0
    cash = balance.get("cash") or balance.get("cash_and_equivalents") or 0

    if current_assets and current_liabilities and current_liabilities > 0:
        ratios["current_ratio"] = current_assets / current_liabilities
        ratios["quick_ratio"] = (current_assets - inventory) / current_liabilities
        ratios["cash_ratio"] = cash / current_liabilities

    # Leverage Ratios
    total_liabilities = balance.get("total_liabilities") or balance.get("total_debt")
    interest_expense = income.get("interest_expense")

    if total_liabilities and total_equity and total_equity > 0:
        ratios["debt_to_equity"] = total_liabilities / total_equity

    if total_liabilities and total_assets and total_assets > 0:
        ratios["debt_to_assets"] = total_liabilities / total_assets

    if operating_income and interest_expense and interest_expense > 0:
        ratios["interest_coverage"] = operating_income / interest_expense

    # Efficiency Ratios
    if revenue and total_assets and total_assets > 0:
        ratios["asset_turnover"] = revenue / total_assets

    avg_inventory = balance.get("average_inventory") or inventory
    if cogs and avg_inventory and avg_inventory > 0:
        ratios["inventory_turnover"] = cogs / avg_inventory

    receivables = balance.get("accounts_receivable") or balance.get("receivables")
    if revenue and receivables and receivables > 0:
        ratios["receivables_turnover"] = revenue / receivables

    return FinancialRatios(**ratios)


# Step 2: Analyze ratios and provide insights
@llm.call(
    provider="openai:completions",
    model_id="gpt-4o-mini",
    format=FinancialAnalysisResult,
)
async def analyze_ratios_and_trends(
    ratios: str,
    financial_data: str,
    historical_data: str = "",
    industry_benchmarks: str = ""
) -> str:
    """Analyze financial ratios and identify trends and insights."""
    historical_context = f"\n\nHistorical Data:\n{historical_data}" if historical_data else ""
    benchmark_context = f"\n\nIndustry Benchmarks:\n{industry_benchmarks}" if industry_benchmarks else ""

    return f"""You are an expert financial analyst. Analyze the following financial data and provide comprehensive insights.

Calculated Financial Ratios:
{ratios}

Financial Statements Data:
{financial_data}
{historical_context}
{benchmark_context}

Perform a thorough analysis:

1. **Trend Analysis**:
   - Identify key trends in financial metrics
   - Determine if trends are positive, negative, or stable
   - Assess the significance of each trend
   - Provide business interpretation

2. **Red Flags & Concerns**:
   - Identify any concerning metrics or ratios
   - Flag liquidity issues (current ratio < 1.0)
   - Flag profitability concerns (negative margins, declining ROE)
   - Flag leverage risks (high debt-to-equity > 2.0)
   - Flag efficiency issues
   - Assess severity and provide recommendations

3. **Investment Insights**:
   - Identify financial strengths
   - Identify weaknesses and risks
   - Spot opportunities for improvement
   - Note competitive advantages
   - Assess overall financial health

4. **Summary & Recommendation**:
   - Provide executive summary of financial health
   - Rate overall financial health (excellent/good/fair/poor/critical)
   - Give investment recommendation (strong buy/buy/hold/sell/strong sell)
   - Support with key metrics and reasoning

Consider:
- Profitability: Are margins healthy and improving?
- Liquidity: Can the company meet short-term obligations?
- Leverage: Is debt at sustainable levels?
- Efficiency: Is the company using assets effectively?
- Growth: Are revenues and profits growing?

Be objective and data-driven in your analysis."""


# Main function
@trace()
async def analyze_financial_statements(
    financial_data: dict[str, Any],
    historical_data: Optional[list[dict[str, Any]]] = None,
    industry_benchmarks: Optional[dict[str, float]] = None,
    analysis_type: Optional[list[str]] = None,
    llm_provider: str = "openai",
    model: str = "gpt-4o-mini",
) -> FinancialAnalysisResult:
    """
    Analyze financial statements and provide comprehensive insights.

    This agent performs:
    - Financial ratio calculation (profitability, liquidity, leverage, efficiency)
    - Trend analysis and identification
    - Red flag detection
    - Investment insights and recommendations

    Args:
        financial_data: Dictionary with income_statement, balance_sheet, cash_flow_statement
        historical_data: Optional list of historical period data for trend analysis
        industry_benchmarks: Optional industry average ratios for comparison
        analysis_type: Optional focus areas (e.g., ['profitability', 'liquidity'])
        llm_provider: LLM provider to use
        model: Specific model to use

    Returns:
        FinancialAnalysisResult with complete analysis

    Example:
        ```python
        financial_data = {
            "income_statement": {
                "revenue": 1000000,
                "cost_of_goods_sold": 600000,
                "operating_expenses": 250000,
                "net_income": 150000
            },
            "balance_sheet": {
                "total_assets": 2000000,
                "current_assets": 500000,
                "total_liabilities": 800000,
                "current_liabilities": 300000,
                "total_equity": 1200000
            }
        }

        result = await analyze_financial_statements(financial_data)
        print(f"Overall Rating: {result.overall_rating}")
        print(f"Recommendation: {result.recommendation}")
        ```
    """
    # Step 1: Calculate ratios
    ratios = calculate_financial_ratios(financial_data)

    # Format ratios for LLM
    ratios_str = "\n".join([
        f"- {key.replace('_', ' ').title()}: {value:.2f}{'%' if 'margin' in key or 'return' in key else ''}"
        for key, value in ratios.model_dump().items()
        if value is not None
    ])

    # Format financial data
    import json
    financial_data_str = json.dumps(financial_data, indent=2)

    # Format historical data if provided
    historical_str = ""
    if historical_data:
        historical_str = json.dumps(historical_data, indent=2)

    # Format industry benchmarks if provided
    benchmark_str = ""
    if industry_benchmarks:
        benchmark_str = "\n".join([
            f"- {key.replace('_', ' ').title()}: {value}"
            for key, value in industry_benchmarks.items()
        ])

    # Step 2: Analyze with LLM
    result = await analyze_ratios_and_trends(
        ratios=ratios_str,
        financial_data=financial_data_str,
        historical_data=historical_str,
        industry_benchmarks=benchmark_str
    )

    return result


# Convenience functions
async def quick_health_check(financial_data: dict[str, Any]) -> dict[str, Any]:
    """
    Quick financial health assessment.

    Returns simplified health information.
    """
    ratios = calculate_financial_ratios(financial_data)

    health = {
        "profitability": "unknown",
        "liquidity": "unknown",
        "leverage": "unknown",
        "key_metrics": {}
    }

    if ratios.net_margin is not None:
        health["key_metrics"]["net_margin"] = f"{ratios.net_margin:.2f}%"
        health["profitability"] = "healthy" if ratios.net_margin > 10 else "concerning" if ratios.net_margin > 0 else "poor"

    if ratios.current_ratio is not None:
        health["key_metrics"]["current_ratio"] = f"{ratios.current_ratio:.2f}"
        health["liquidity"] = "healthy" if ratios.current_ratio > 1.5 else "adequate" if ratios.current_ratio > 1.0 else "concerning"

    if ratios.debt_to_equity is not None:
        health["key_metrics"]["debt_to_equity"] = f"{ratios.debt_to_equity:.2f}"
        health["leverage"] = "healthy" if ratios.debt_to_equity < 1.0 else "moderate" if ratios.debt_to_equity < 2.0 else "high"

    return health


async def calculate_ratios_only(financial_data: dict[str, Any]) -> dict[str, float]:
    """
    Calculate only financial ratios without full analysis.

    Returns dictionary of ratios.
    """
    ratios = calculate_financial_ratios(financial_data)
    return {k: v for k, v in ratios.model_dump().items() if v is not None}
