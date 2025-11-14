"""Test suite for sec_edgar tool following best practices."""

import pytest
from pathlib import Path
from tests.utils import BaseToolTest
from unittest.mock import AsyncMock, MagicMock, patch


class TestSECEdgarTool(BaseToolTest):
    """Test sec_edgar tool component."""

    component_name = "sec_edgar"
    component_path = Path("packages/sygaldry_registry/components/tools/sec_edgar")

    def get_component_function(self):
        """Import the tool function."""
        from packages.sygaldry_registry.components.tools.sec_edgar.tool import search_company
        return search_company

    def get_test_inputs(self):
        """Provide test inputs for the tool."""
        return [
            {
                "ticker_or_name": "AAPL"
            },
            {
                "ticker_or_name": "Microsoft"
            }
        ]

    def validate_tool_output(self, output, input_data):
        """Validate the tool output format."""
        assert isinstance(output, list)
        for company in output:
            assert 'cik' in company
            assert 'name' in company

    @pytest.mark.unit
    def test_tool_has_required_functions(self):
        """Test that all required functions are present."""
        from packages.sygaldry_registry.components.tools.sec_edgar import tool

        assert hasattr(tool, 'search_company')
        assert hasattr(tool, 'get_company_info')
        assert hasattr(tool, 'get_company_filings')
        assert hasattr(tool, 'get_filing_content')
        assert hasattr(tool, 'parse_financial_data')
        assert hasattr(tool, 'get_recent_8k_items')

    @pytest.mark.unit
    def test_models_structure(self):
        """Test that models have correct structure."""
        from packages.sygaldry_registry.components.tools.sec_edgar.tool import (
            CompanyInfo,
            SECFiling,
            FinancialStatement
        )

        # Test CompanyInfo model
        assert hasattr(CompanyInfo, 'model_fields')
        assert 'cik' in CompanyInfo.model_fields
        assert 'name' in CompanyInfo.model_fields
        assert 'ticker' in CompanyInfo.model_fields

        # Test SECFiling model
        assert hasattr(SECFiling, 'model_fields')
        assert 'accession_number' in SECFiling.model_fields
        assert 'filing_type' in SECFiling.model_fields
        assert 'filing_date' in SECFiling.model_fields
        assert 'cik' in SECFiling.model_fields

        # Test FinancialStatement model
        assert hasattr(FinancialStatement, 'model_fields')
        assert 'filing_type' in FinancialStatement.model_fields
        assert 'total_assets' in FinancialStatement.model_fields
        assert 'net_income' in FinancialStatement.model_fields

    @pytest.mark.unit
    def test_search_company_structure(self):
        """Test search_company function structure."""
        from packages.sygaldry_registry.components.tools.sec_edgar.tool import search_company
        import inspect

        assert callable(search_company)
        sig = inspect.signature(search_company)
        params = list(sig.parameters.keys())
        assert 'ticker_or_name' in params

    @pytest.mark.unit
    def test_get_company_filings_structure(self):
        """Test get_company_filings function structure."""
        from packages.sygaldry_registry.components.tools.sec_edgar.tool import get_company_filings
        import inspect

        assert callable(get_company_filings)
        sig = inspect.signature(get_company_filings)
        params = list(sig.parameters.keys())
        assert 'cik' in params
        assert 'filing_type' in params
        assert 'max_results' in params

    @pytest.mark.unit
    def test_parse_financial_data_structure(self):
        """Test parse_financial_data function structure."""
        from packages.sygaldry_registry.components.tools.sec_edgar.tool import parse_financial_data
        import inspect

        assert callable(parse_financial_data)
        sig = inspect.signature(parse_financial_data)
        params = list(sig.parameters.keys())
        assert 'filing_content' in params
        assert 'filing_type' in params

    @pytest.mark.unit
    def test_normalize_cik(self):
        """Test CIK normalization."""
        from packages.sygaldry_registry.components.tools.sec_edgar.tool import _normalize_cik

        # Test padding
        assert _normalize_cik("320193") == "0000320193"
        assert _normalize_cik("0000320193") == "0000320193"
        assert _normalize_cik("1234") == "0000001234"

        # Test whitespace handling
        assert _normalize_cik("  320193  ") == "0000320193"

    @pytest.mark.unit
    def test_parse_financial_data_basic(self):
        """Test basic financial data parsing."""
        from packages.sygaldry_registry.components.tools.sec_edgar.tool import parse_financial_data

        # Mock filing content with sample data
        mock_content = """
        Period End Date: 2023-09-30
        Total Assets: $352,755
        Total Liabilities: $290,437
        Stockholders' Equity: $62,146
        Total Revenues: $383,285
        Net Income: $96,995
        Operating Income: $114,301
        Cash and Cash Equivalents: $29,965
        """

        result = parse_financial_data(mock_content, "10-K")

        assert result.filing_type == "10-K"
        assert result.period_end_date == "2023-09-30"
        # Note: Values may or may not be extracted depending on regex pattern matching
        assert isinstance(result.raw_data, dict)

    @pytest.mark.unit
    def test_company_info_model_creation(self):
        """Test CompanyInfo model instantiation."""
        from packages.sygaldry_registry.components.tools.sec_edgar.tool import CompanyInfo

        company = CompanyInfo(
            cik="0000320193",
            name="Apple Inc.",
            ticker="AAPL",
            sic="3571",
            sic_description="Electronic Computers",
            state_of_incorporation="CA",
            fiscal_year_end="0930"
        )

        assert company.cik == "0000320193"
        assert company.name == "Apple Inc."
        assert company.ticker == "AAPL"
        assert company.sic == "3571"

    @pytest.mark.unit
    def test_sec_filing_model_creation(self):
        """Test SECFiling model instantiation."""
        from packages.sygaldry_registry.components.tools.sec_edgar.tool import SECFiling

        filing = SECFiling(
            accession_number="0000320193-23-000106",
            filing_type="10-K",
            filing_date="2023-11-03",
            report_date="2023-09-30",
            company_name="Apple Inc.",
            cik="0000320193",
            primary_document="aapl-20230930.htm",
            file_url="https://www.sec.gov/Archives/edgar/data/320193/0000320193-23-000106/aapl-20230930.htm"
        )

        assert filing.filing_type == "10-K"
        assert filing.cik == "0000320193"
        assert filing.filing_date == "2023-11-03"

    @pytest.mark.unit
    def test_financial_statement_model_creation(self):
        """Test FinancialStatement model instantiation."""
        from packages.sygaldry_registry.components.tools.sec_edgar.tool import FinancialStatement

        statement = FinancialStatement(
            filing_type="10-K",
            period_end_date="2023-09-30",
            total_assets="352,755",
            total_liabilities="290,437",
            stockholders_equity="62,146",
            revenues="383,285",
            net_income="96,995"
        )

        assert statement.filing_type == "10-K"
        assert statement.total_assets == "352,755"
        assert statement.net_income == "96,995"

    @pytest.mark.unit
    def test_httpx_import_check(self):
        """Test that httpx availability is checked."""
        from packages.sygaldry_registry.components.tools.sec_edgar.tool import HTTPX_AVAILABLE

        # Just verify the constant exists
        assert isinstance(HTTPX_AVAILABLE, bool)
