# SEC EDGAR Tool

## Overview

SEC EDGAR tool for accessing SEC filings and financial data via the SEC API. Search companies by ticker or name, retrieve 10-K, 10-Q, and 8-K filings, and parse financial statements.

## Features

- Search companies by ticker symbol or name
- Get detailed company information by CIK
- Retrieve recent filings (10-K, 10-Q, 8-K, etc.)
- Filter filings by type and date range
- Get raw filing content
- Parse financial data from filings
- No API key required (free public API)

## Installation

```bash
sygaldry add sec_edgar
pip install httpx
```

## Quick Start

```python
from sec_edgar import search_company, get_company_filings, get_filing_content

# Search for a company
companies = search_company("AAPL")
company = companies[0]
print(f"{company.name}: CIK {company.cik}")

# Get recent 10-K annual reports
filings = get_company_filings(
    cik=company.cik,
    filing_type="10-K",
    max_results=3
)

for filing in filings:
    print(f"{filing.filing_type} filed on {filing.filing_date}")
    print(f"URL: {filing.file_url}")
```

## Functions

### search_company()
Search for companies by ticker symbol or name.

**Parameters:**
- `ticker_or_name` (str): Stock ticker (e.g., "AAPL") or company name

**Returns:** List of `CompanyInfo` objects

**Example:**
```python
companies = search_company("Microsoft")
for company in companies:
    print(f"{company.name} - {company.ticker}")
```

### get_company_info()
Get detailed company information by CIK.

**Parameters:**
- `cik` (str): Central Index Key (CIK)

**Returns:** `CompanyInfo` object

**Example:**
```python
company = get_company_info("0000789019")  # Microsoft
print(f"SIC: {company.sic_description}")
print(f"Fiscal Year End: {company.fiscal_year_end}")
```

### get_company_filings()
Get recent filings for a company.

**Parameters:**
- `cik` (str): Central Index Key
- `filing_type` (str, optional): Filter by type (e.g., "10-K", "10-Q", "8-K")
- `max_results` (int): Maximum number of results (default: 10)
- `start_date` (str, optional): Filter after date (YYYY-MM-DD)
- `end_date` (str, optional): Filter before date (YYYY-MM-DD)

**Returns:** List of `SECFiling` objects

**Example:**
```python
# Get 10-Q quarterly reports from 2023
filings = get_company_filings(
    cik="0000320193",
    filing_type="10-Q",
    start_date="2023-01-01",
    end_date="2023-12-31",
    max_results=10
)
```

### get_filing_content()
Get the raw content of a specific filing document.

**Parameters:**
- `cik` (str): Central Index Key
- `accession_number` (str): Accession number
- `document` (str): Document filename

**Returns:** Raw filing content as string

**Example:**
```python
filings = get_company_filings("0000320193", filing_type="10-K", max_results=1)
content = get_filing_content(
    cik=filings[0].cik,
    accession_number=filings[0].accession_number,
    document=filings[0].primary_document
)
```

### parse_financial_data()
Parse financial data from filing content using regex patterns.

**Parameters:**
- `filing_content` (str): Raw filing content
- `filing_type` (str): Type of filing (default: "10-K")

**Returns:** `FinancialStatement` object

**Example:**
```python
financial_data = parse_financial_data(content, "10-K")
print(f"Total Assets: {financial_data.total_assets}")
print(f"Net Income: {financial_data.net_income}")
print(f"Revenues: {financial_data.revenues}")
```

### get_recent_8k_items()
Get recent 8-K filings (material corporate events).

**Parameters:**
- `cik` (str): Central Index Key
- `max_results` (int): Maximum number of results (default: 10)

**Returns:** List of `SECFiling` objects

**Example:**
```python
filings = get_recent_8k_items("0000320193", max_results=5)
for filing in filings:
    print(f"Event on {filing.filing_date}")
```

## Data Models

### CompanyInfo
- `cik`: Central Index Key
- `name`: Company name
- `ticker`: Stock ticker symbol
- `sic`: Standard Industrial Classification code
- `sic_description`: Industry description
- `state_of_incorporation`: State of incorporation
- `fiscal_year_end`: Fiscal year end (MMDD format)

### SECFiling
- `accession_number`: Unique identifier
- `filing_type`: Filing type (10-K, 10-Q, 8-K, etc.)
- `filing_date`: Date filed with SEC
- `report_date`: Period end date
- `company_name`: Company name
- `cik`: Central Index Key
- `primary_document`: Main document filename
- `file_url`: URL to filing
- `items`: Items reported (for 8-K filings)

### FinancialStatement
- `filing_type`: Filing type
- `period_end_date`: Period end date
- `total_assets`: Total assets
- `total_liabilities`: Total liabilities
- `stockholders_equity`: Stockholders equity
- `revenues`: Total revenues
- `net_income`: Net income
- `operating_income`: Operating income
- `cash_and_equivalents`: Cash and cash equivalents
- `raw_data`: Raw extracted data dictionary

## Use Cases

### Financial Analysis
Retrieve and analyze financial statements for investment research:

```python
# Get latest 10-K
companies = search_company("Tesla")
filings = get_company_filings(companies[0].cik, filing_type="10-K", max_results=1)

# Get and parse financial data
content = get_filing_content(
    filings[0].cik,
    filings[0].accession_number,
    filings[0].primary_document
)
financials = parse_financial_data(content)
print(f"Net Income: {financials.net_income}")
```

### Corporate Event Monitoring
Track material corporate events via 8-K filings:

```python
# Monitor recent events
filings = get_recent_8k_items("0000789019", max_results=10)
for filing in filings:
    print(f"{filing.filing_date}: {filing.filing_type}")
```

### Multi-Company Comparison
Compare financial metrics across companies:

```python
companies = ["AAPL", "MSFT", "GOOGL"]
for ticker in companies:
    results = search_company(ticker)
    if results:
        filings = get_company_filings(results[0].cik, filing_type="10-K", max_results=1)
        print(f"{ticker}: {len(filings)} filings found")
```

## Rate Limits

The SEC API is free and public, but please be respectful:
- Limit requests to 10 per second
- Use appropriate User-Agent headers (automatically handled)
- Cache responses when possible

## Notes

- CIKs can be provided with or without leading zeros (automatically normalized)
- Financial data parsing uses regex patterns and may not capture all metrics
- For production XBRL parsing, consider specialized libraries
- SEC updates the EDGAR database regularly

## Related Components

- `financial_statement_analyzer` - Agent for analyzing financial reports
- `contract_analysis_agent` - Agent for analyzing SEC filings as contracts
- `market_intelligence_agent` - Agent for market research using SEC data

## License

MIT
