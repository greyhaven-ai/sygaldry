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

# Import SEC EDGAR tool
try:
    from ...tools.sec_edgar.tool import get_company_info, get_company_filings, get_filing_content
    SEC_EDGAR_AVAILABLE = True
except ImportError:
    get_company_info = None
    get_company_filings = None
    get_filing_content = None
    SEC_EDGAR_AVAILABLE = False


class FinancialRatios(BaseModel):
    """Calculated financial ratios."""

    # Note: All fields must be required for OpenAI schema validation
    # Profitability Ratios
    gross_margin: float | None = Field(..., description="Gross profit margin percentage (null if not calculable)")
    operating_margin: float | None = Field(..., description="Operating profit margin percentage (null if not calculable)")
    net_margin: float | None = Field(..., description="Net profit margin percentage (null if not calculable)")
    return_on_assets: float | None = Field(..., description="ROA percentage (null if not calculable)")
    return_on_equity: float | None = Field(..., description="ROE percentage (null if not calculable)")

    # Liquidity Ratios
    current_ratio: float | None = Field(..., description="Current assets / current liabilities (null if not calculable)")
    quick_ratio: float | None = Field(..., description="(Current assets - inventory) / current liabilities (null if not calculable)")
    cash_ratio: float | None = Field(..., description="Cash / current liabilities (null if not calculable)")

    # Leverage Ratios
    debt_to_equity: float | None = Field(..., description="Total debt / total equity (null if not calculable)")
    debt_to_assets: float | None = Field(..., description="Total debt / total assets (null if not calculable)")
    interest_coverage: float | None = Field(..., description="EBIT / interest expense (null if not calculable)")

    # Efficiency Ratios
    asset_turnover: float | None = Field(..., description="Revenue / total assets (null if not calculable)")
    inventory_turnover: float | None = Field(..., description="COGS / average inventory (null if not calculable)")
    receivables_turnover: float | None = Field(..., description="Revenue / average receivables (null if not calculable)")


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
    # Note: All fields must be required for OpenAI schema validation
    metric_value: str | None = Field(..., description="The concerning metric value (null if not specific)")
    recommendation: str = Field(..., description="Recommended action")


class InvestmentInsight(BaseModel):
    """Investment analysis insight."""

    insight_type: str = Field(..., description="Type of insight (e.g., 'strength', 'weakness', 'opportunity')")
    description: str = Field(..., description="Description of the insight")
    supporting_metrics: list[str] = Field(..., description="Metrics that support this insight")
    impact: Literal["positive", "negative", "neutral"] = Field(..., description="Impact on investment decision")


class FinancialAnalysisResult(BaseModel):
    """Complete financial analysis result."""

    # Note: Field(...) without description for nested models to avoid OpenAI schema error
    # OpenAI rejects $ref with additional keywords like 'description'
    ratios: FinancialRatios = Field(...)
    trends: list[TrendAnalysis] = Field(...)
    red_flags: list[RedFlag] = Field(...)
    insights: list[InvestmentInsight] = Field(...)
    summary: str = Field(..., description="Executive summary of financial health")
    overall_rating: Literal["excellent", "good", "fair", "poor", "critical"] = Field(
        ..., description="Overall financial health rating"
    )
    recommendation: Literal["strong_buy", "buy", "hold", "sell", "strong_sell"] = Field(
        ..., description="Investment recommendation"
    )


# Rebuild models to resolve forward references
FinancialRatios.model_rebuild()
TrendAnalysis.model_rebuild()
RedFlag.model_rebuild()
InvestmentInsight.model_rebuild()
FinancialAnalysisResult.model_rebuild()


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

    # Ensure all fields have values (None if not calculated)
    # Required for OpenAI schema validation
    all_fields = {
        "gross_margin": None,
        "operating_margin": None,
        "net_margin": None,
        "return_on_assets": None,
        "return_on_equity": None,
        "current_ratio": None,
        "quick_ratio": None,
        "cash_ratio": None,
        "debt_to_equity": None,
        "debt_to_assets": None,
        "interest_coverage": None,
        "asset_turnover": None,
        "inventory_turnover": None,
        "receivables_turnover": None,
    }
    all_fields.update(ratios)

    return FinancialRatios(**all_fields)


# Step 2: Analyze ratios and provide insights
# Internal LLM call function - returns AsyncResponse
@llm.call(
    provider="openai:completions",
    model_id="gpt-4o-mini",
    format=FinancialAnalysisResult,
)
async def _analyze_ratios_and_trends_call(
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


# Public wrapper - returns parsed FinancialAnalysisResult
async def analyze_ratios_and_trends(
    ratios: str,
    financial_data: str,
    historical_data: str = "",
    industry_benchmarks: str = ""
) -> FinancialAnalysisResult:
    """Analyze financial ratios and identify trends and insights.

    Args:
        ratios: Formatted string of calculated ratios
        financial_data: Financial statements data as string
        historical_data: Optional historical data
        industry_benchmarks: Optional industry benchmarks

    Returns:
        FinancialAnalysisResult with comprehensive analysis
    """
    response = await _analyze_ratios_and_trends_call(
        ratios=ratios,
        financial_data=financial_data,
        historical_data=historical_data,
        industry_benchmarks=industry_benchmarks
    )
    return response.parse()


# Fetch financial data from SEC EDGAR
@trace()
async def fetch_sec_edgar_data(
    ticker_or_cik: str,
    filing_type: str = "10-K",
    max_filings: int = 1
) -> Optional[dict[str, Any]]:
    """
    Fetch financial data from SEC EDGAR.

    Args:
        ticker_or_cik: Company ticker symbol or CIK number
        filing_type: Type of filing to fetch (10-K, 10-Q, 8-K)
        max_filings: Maximum number of filings to fetch

    Returns:
        Dictionary with financial data or None if unavailable

    Example:
        ```python
        data = await fetch_sec_edgar_data("AAPL", filing_type="10-K")
        if data:
            result = await analyze_financial_statements(data)
        ```
    """
    if not SEC_EDGAR_AVAILABLE:
        return None

    try:
        # Get company info
        company_info = await get_company_info(ticker_or_cik)

        # Get recent filings
        filings = await get_company_filings(
            ticker_or_cik,
            filing_type=filing_type,
            max_results=max_filings
        )

        if not filings:
            return None

        # Get the most recent filing content
        filing_content = await get_filing_content(
            ticker_or_cik,
            filings[0].accession_number
        )

        # Parse basic financial data from filing
        # Note: This is a simplified parser - real implementation would need
        # more sophisticated XBRL/HTML parsing
        financial_data = {
            "company_name": company_info.name,
            "ticker": company_info.ticker,
            "filing_type": filing_type,
            "filing_date": filings[0].filing_date,
            "income_statement": {},
            "balance_sheet": {},
            "cash_flow_statement": {}
        }

        return financial_data

    except Exception:
        return None


# Main function
@trace()
async def analyze_financial_statements(
    financial_data: Optional[dict[str, Any]] = None,
    ticker: Optional[str] = None,
    historical_data: Optional[list[dict[str, Any]]] = None,
    industry_benchmarks: Optional[dict[str, float]] = None,
    analysis_type: Optional[list[str]] = None,
    fetch_from_sec: bool = True,
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
    - Optional SEC EDGAR data fetching

    Args:
        financial_data: Dictionary with income_statement, balance_sheet, cash_flow_statement
        ticker: Company ticker symbol (e.g., "AAPL") - fetches data from SEC EDGAR if provided
        historical_data: Optional list of historical period data for trend analysis
        industry_benchmarks: Optional industry average ratios for comparison
        analysis_type: Optional focus areas (e.g., ['profitability', 'liquidity'])
        fetch_from_sec: Whether to fetch data from SEC EDGAR when ticker is provided
        llm_provider: LLM provider to use
        model: Specific model to use

    Returns:
        FinancialAnalysisResult with complete analysis

    Example:
        ```python
        # Option 1: Provide financial data directly
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

        # Option 2: Fetch from SEC EDGAR by ticker
        result = await analyze_financial_statements(ticker="AAPL")

        print(f"Overall Rating: {result.overall_rating}")
        print(f"Recommendation: {result.recommendation}")
        ```
    """
    # Fetch from SEC EDGAR if ticker provided and no financial_data
    if not financial_data and ticker and fetch_from_sec:
        financial_data = await fetch_sec_edgar_data(ticker)
        if not financial_data:
            raise ValueError(f"Could not fetch financial data for ticker: {ticker}")

    if not financial_data:
        raise ValueError("Either financial_data or ticker must be provided")

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
