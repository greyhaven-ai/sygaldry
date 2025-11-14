# Financial Statement Analyzer Agent

## Overview

The Financial Statement Analyzer is a comprehensive financial analysis tool that calculates ratios, identifies trends, detects red flags, and provides investment insights from financial statements.

## Features

- **Ratio Calculation**: Automated calculation of 15+ financial ratios
- **Profitability Analysis**: Gross, operating, and net margins, ROA, ROE
- **Liquidity Assessment**: Current, quick, and cash ratios
- **Leverage Analysis**: Debt-to-equity, debt-to-assets, interest coverage
- **Efficiency Metrics**: Asset, inventory, and receivables turnover
- **Trend Identification**: Analyzes changes over time
- **Red Flag Detection**: Identifies concerning metrics and risks
- **Investment Insights**: Provides actionable investment recommendations
- **Benchmarking**: Compare against industry standards

## Installation

```bash
sygaldry add financial_statement_analyzer
```

## Quick Start

```python
import asyncio
from financial_statement_analyzer import analyze_financial_statements

async def main():
    financial_data = {
        "income_statement": {
            "revenue": 1000000,
            "cost_of_goods_sold": 600000,
            "operating_income": 200000,
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

asyncio.run(main())
```

## Response Models

### FinancialAnalysisResult

Complete financial analysis with ratios, trends, and recommendations.

### FinancialRatios

All calculated financial ratios including profitability, liquidity, leverage, and efficiency metrics.

## Best Practices

1. Provide complete financial statements for accurate analysis
2. Include historical data for trend analysis
3. Add industry benchmarks for context
4. Review red flags carefully
5. Consider all metrics together, not in isolation

## License

MIT License
