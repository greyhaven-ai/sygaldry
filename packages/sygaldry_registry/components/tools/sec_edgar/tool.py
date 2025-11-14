"""SEC EDGAR Tool for accessing SEC filings and financial data.

This tool provides functions to search companies, retrieve filings, and parse
financial data from the SEC EDGAR database using the SEC API.
"""

from __future__ import annotations

import re
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal, Optional

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


class CompanyInfo(BaseModel):
    """SEC company information."""

    cik: str = Field(..., description="Central Index Key (CIK)")
    name: str = Field(..., description="Company name")
    ticker: Optional[str] = Field(None, description="Stock ticker symbol")
    sic: Optional[str] = Field(None, description="Standard Industrial Classification")
    sic_description: Optional[str] = Field(None, description="SIC description")
    state_of_incorporation: Optional[str] = Field(None, description="State of incorporation")
    fiscal_year_end: Optional[str] = Field(None, description="Fiscal year end (MMDD format)")


class SECFiling(BaseModel):
    """SEC filing representation."""

    accession_number: str = Field(..., description="Accession number (unique identifier)")
    filing_type: str = Field(..., description="Filing type (e.g., 10-K, 10-Q, 8-K)")
    filing_date: str = Field(..., description="Filing date (YYYY-MM-DD)")
    report_date: Optional[str] = Field(None, description="Report/period end date")
    company_name: str = Field(..., description="Company name")
    cik: str = Field(..., description="Central Index Key")
    primary_document: Optional[str] = Field(None, description="Primary document filename")
    file_url: str = Field(..., description="URL to filing")
    items: Optional[list[str]] = Field(default_factory=list, description="Items reported (for 8-K)")


class FinancialStatement(BaseModel):
    """Financial statement data from SEC filing."""

    filing_type: str = Field(..., description="Filing type (e.g., 10-K, 10-Q)")
    period_end_date: Optional[str] = Field(None, description="Period end date")
    total_assets: Optional[str] = Field(None, description="Total assets")
    total_liabilities: Optional[str] = Field(None, description="Total liabilities")
    stockholders_equity: Optional[str] = Field(None, description="Stockholders equity")
    revenues: Optional[str] = Field(None, description="Total revenues")
    net_income: Optional[str] = Field(None, description="Net income")
    operating_income: Optional[str] = Field(None, description="Operating income")
    cash_and_equivalents: Optional[str] = Field(None, description="Cash and cash equivalents")
    raw_data: dict = Field(default_factory=dict, description="Raw financial data extracted")


def _get_sec_headers() -> dict[str, str]:
    """Get headers for SEC API requests.

    SEC requires a User-Agent header with contact information.
    """
    return {
        "User-Agent": "Sygaldry SEC Tool (contact@sygaldry.ai)",
        "Accept": "application/json"
    }


def _normalize_cik(cik: str) -> str:
    """Normalize CIK to 10-digit format with leading zeros."""
    return str(cik).strip().zfill(10)


def search_company(ticker_or_name: str) -> list[CompanyInfo]:
    """
    Search for companies by ticker symbol or company name.

    Args:
        ticker_or_name: Stock ticker (e.g., "AAPL") or company name (e.g., "Apple")

    Returns:
        List of matching CompanyInfo objects

    Example:
        ```python
        # Search by ticker
        companies = search_company("AAPL")

        # Search by name
        companies = search_company("Apple Inc")

        for company in companies:
            print(f"{company.name} ({company.ticker}): CIK {company.cik}")
        ```
    """
    if not HTTPX_AVAILABLE:
        raise ImportError("httpx is required for sec_edgar tool. Install with: pip install httpx")

    # Use SEC's company tickers JSON endpoint
    url = "https://www.sec.gov/files/company_tickers.json"
    headers = _get_sec_headers()

    with httpx.Client() as client:
        response = client.get(url, headers=headers, timeout=30.0)
        response.raise_for_status()
        data = response.json()

    # Search through companies
    search_term = ticker_or_name.upper().strip()
    matches = []

    for item in data.values():
        ticker = item.get("ticker", "").upper()
        name = item.get("title", "").upper()

        # Match by ticker or company name
        if search_term in ticker or search_term in name:
            company = CompanyInfo(
                cik=_normalize_cik(str(item["cik_str"])),
                name=item["title"],
                ticker=item.get("ticker")
            )
            matches.append(company)

    return matches


def get_company_info(cik: str) -> CompanyInfo:
    """
    Get detailed company information by CIK.

    Args:
        cik: Central Index Key (CIK) - can be padded or unpadded

    Returns:
        CompanyInfo object with detailed company data

    Example:
        ```python
        # Get company info by CIK
        company = get_company_info("0000320193")  # Apple Inc
        print(f"Name: {company.name}")
        print(f"Ticker: {company.ticker}")
        print(f"SIC: {company.sic_description}")
        ```
    """
    if not HTTPX_AVAILABLE:
        raise ImportError("httpx is required for sec_edgar tool. Install with: pip install httpx")

    normalized_cik = _normalize_cik(cik)
    url = f"https://data.sec.gov/submissions/CIK{normalized_cik}.json"
    headers = _get_sec_headers()

    with httpx.Client() as client:
        response = client.get(url, headers=headers, timeout=30.0)
        response.raise_for_status()
        data = response.json()

    # Extract company info
    tickers = data.get("tickers", [])
    ticker = tickers[0] if tickers else None

    return CompanyInfo(
        cik=normalized_cik,
        name=data.get("name", ""),
        ticker=ticker,
        sic=str(data.get("sic")) if data.get("sic") else None,
        sic_description=data.get("sicDescription"),
        state_of_incorporation=data.get("stateOfIncorporation"),
        fiscal_year_end=data.get("fiscalYearEnd")
    )


def get_company_filings(
    cik: str,
    filing_type: Optional[str] = None,
    max_results: int = 10,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> list[SECFiling]:
    """
    Get recent filings for a company.

    Args:
        cik: Central Index Key (CIK)
        filing_type: Filter by filing type (e.g., "10-K", "10-Q", "8-K")
        max_results: Maximum number of filings to return
        start_date: Filter filings after this date (YYYY-MM-DD)
        end_date: Filter filings before this date (YYYY-MM-DD)

    Returns:
        List of SECFiling objects

    Example:
        ```python
        # Get recent 10-K filings
        filings = get_company_filings(
            cik="0000320193",
            filing_type="10-K",
            max_results=5
        )

        for filing in filings:
            print(f"{filing.filing_type} filed {filing.filing_date}")
            print(f"URL: {filing.file_url}")
        ```
    """
    if not HTTPX_AVAILABLE:
        raise ImportError("httpx is required for sec_edgar tool. Install with: pip install httpx")

    normalized_cik = _normalize_cik(cik)
    url = f"https://data.sec.gov/submissions/CIK{normalized_cik}.json"
    headers = _get_sec_headers()

    with httpx.Client() as client:
        response = client.get(url, headers=headers, timeout=30.0)
        response.raise_for_status()
        data = response.json()

    company_name = data.get("name", "")
    recent_filings = data.get("filings", {}).get("recent", {})

    if not recent_filings:
        return []

    # Extract filing data
    filings = []
    accession_numbers = recent_filings.get("accessionNumber", [])
    filing_dates = recent_filings.get("filingDate", [])
    forms = recent_filings.get("form", [])
    primary_docs = recent_filings.get("primaryDocument", [])
    report_dates = recent_filings.get("reportDate", [])

    for i in range(len(accession_numbers)):
        form = forms[i] if i < len(forms) else ""
        filing_date = filing_dates[i] if i < len(filing_dates) else ""

        # Apply filters
        if filing_type and form != filing_type:
            continue

        if start_date and filing_date < start_date:
            continue

        if end_date and filing_date > end_date:
            continue

        accession = accession_numbers[i].replace("-", "")
        primary_doc = primary_docs[i] if i < len(primary_docs) else ""
        report_date = report_dates[i] if i < len(report_dates) else None

        # Construct filing URL
        file_url = f"https://www.sec.gov/Archives/edgar/data/{normalized_cik.lstrip('0')}/{accession}/{primary_doc}"

        filing = SECFiling(
            accession_number=accession_numbers[i],
            filing_type=form,
            filing_date=filing_date,
            report_date=report_date,
            company_name=company_name,
            cik=normalized_cik,
            primary_document=primary_doc,
            file_url=file_url
        )
        filings.append(filing)

        if len(filings) >= max_results:
            break

    return filings


def get_filing_content(cik: str, accession_number: str, document: str) -> str:
    """
    Get the raw content of a specific filing document.

    Args:
        cik: Central Index Key (CIK)
        accession_number: Accession number of the filing
        document: Document filename to retrieve

    Returns:
        Raw filing content as string

    Example:
        ```python
        # Get filing content
        content = get_filing_content(
            cik="0000320193",
            accession_number="0000320193-23-000106",
            document="aapl-20230930.htm"
        )

        # Parse or analyze content
        if "Total assets" in content:
            print("Found financial data")
        ```
    """
    if not HTTPX_AVAILABLE:
        raise ImportError("httpx is required for sec_edgar tool. Install with: pip install httpx")

    normalized_cik = _normalize_cik(cik)
    accession_clean = accession_number.replace("-", "")

    url = f"https://www.sec.gov/Archives/edgar/data/{normalized_cik.lstrip('0')}/{accession_clean}/{document}"
    headers = _get_sec_headers()

    with httpx.Client() as client:
        response = client.get(url, headers=headers, timeout=30.0)
        response.raise_for_status()
        return response.text


def parse_financial_data(filing_content: str, filing_type: str = "10-K") -> FinancialStatement:
    """
    Parse financial data from filing content.

    This is a basic parser that extracts common financial metrics using regex patterns.
    For production use, consider using specialized XBRL parsers.

    Args:
        filing_content: Raw filing content (HTML/XML)
        filing_type: Type of filing (e.g., "10-K", "10-Q")

    Returns:
        FinancialStatement object with extracted data

    Example:
        ```python
        # Get and parse filing
        filings = get_company_filings("0000320193", filing_type="10-K", max_results=1)
        content = get_filing_content(
            filings[0].cik,
            filings[0].accession_number,
            filings[0].primary_document
        )

        financial_data = parse_financial_data(content, "10-K")
        print(f"Total Assets: {financial_data.total_assets}")
        print(f"Net Income: {financial_data.net_income}")
        ```
    """
    # Extract period end date
    period_pattern = r'Period[- ]End[- ]Date[:\s]*(\d{4}-\d{2}-\d{2})'
    period_match = re.search(period_pattern, filing_content, re.IGNORECASE)
    period_end_date = period_match.group(1) if period_match else None

    # Common financial metrics patterns (simplified)
    patterns = {
        "total_assets": r'Total\s+[Aa]ssets[:\s]*\$?\s*([\d,]+)',
        "total_liabilities": r'Total\s+[Ll]iabilities[:\s]*\$?\s*([\d,]+)',
        "stockholders_equity": r'[Ss]tockholders[\'\s]+[Ee]quity[:\s]*\$?\s*([\d,]+)',
        "revenues": r'Total\s+[Rr]even(?:ues?|ue)[:\s]*\$?\s*([\d,]+)',
        "net_income": r'Net\s+[Ii]ncome[:\s]*\$?\s*([\d,]+)',
        "operating_income": r'Operating\s+[Ii]ncome[:\s]*\$?\s*([\d,]+)',
        "cash_and_equivalents": r'Cash\s+and\s+[Cc]ash\s+[Ee]quivalents[:\s]*\$?\s*([\d,]+)'
    }

    extracted_data = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, filing_content)
        if match:
            extracted_data[key] = match.group(1)

    return FinancialStatement(
        filing_type=filing_type,
        period_end_date=period_end_date,
        total_assets=extracted_data.get("total_assets"),
        total_liabilities=extracted_data.get("total_liabilities"),
        stockholders_equity=extracted_data.get("stockholders_equity"),
        revenues=extracted_data.get("revenues"),
        net_income=extracted_data.get("net_income"),
        operating_income=extracted_data.get("operating_income"),
        cash_and_equivalents=extracted_data.get("cash_and_equivalents"),
        raw_data=extracted_data
    )


def get_recent_8k_items(cik: str, max_results: int = 10) -> list[SECFiling]:
    """
    Get recent 8-K filings with parsed items.

    8-K filings report major corporate events. This function retrieves recent
    8-K filings for a company.

    Args:
        cik: Central Index Key (CIK)
        max_results: Maximum number of 8-K filings to return

    Returns:
        List of SECFiling objects for 8-K filings

    Example:
        ```python
        # Get recent 8-K events
        filings = get_recent_8k_items("0000320193", max_results=5)

        for filing in filings:
            print(f"8-K filed {filing.filing_date}")
            if filing.items:
                print(f"Items: {', '.join(filing.items)}")
        ```
    """
    return get_company_filings(cik=cik, filing_type="8-K", max_results=max_results)
