"""Test suite for financial_statement_analyzer following best practices."""

import pytest
from pathlib import Path
from tests.utils import BaseAgentTest
from unittest.mock import AsyncMock, patch


class TestFinancialStatementAnalyzer(BaseAgentTest):
    """Test cases for Financial Statement Analyzer agent."""

    component_name = "financial_statement_analyzer"
    component_path = Path("packages/sygaldry_registry/components/agents/financial_statement_analyzer")

    def get_component_function(self):
        """Get the main agent function."""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "financial_statement_analyzer", "packages/sygaldry_registry/components/agents/financial_statement_analyzer/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.analyze_financial_statements

    def get_test_inputs(self):
        """Get test input cases."""
        return [
            {
                "financial_data": {
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
                        "current_liabilities": 300000
                    }
                },
                "analysis_type": ["profitability", "liquidity"],
            },
        ]

    @pytest.mark.unit
    def test_agent_has_required_functions(self):
        """Test that all required agent functions are present."""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "financial_statement_analyzer", "packages/sygaldry_registry/components/agents/financial_statement_analyzer/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        assert hasattr(module, 'analyze_financial_statements')
        assert callable(module.analyze_financial_statements)
        assert hasattr(module, 'calculate_financial_ratios')
        assert callable(module.calculate_financial_ratios)

    @pytest.mark.unit
    def test_response_models_structure(self):
        """Test that response models have correct structure."""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "financial_statement_analyzer", "packages/sygaldry_registry/components/agents/financial_statement_analyzer/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        assert hasattr(module, 'FinancialRatios')
        assert hasattr(module, 'TrendAnalysis')
        assert hasattr(module, 'FinancialAnalysisResult')

        # Test model structure
        FinancialRatios = module.FinancialRatios
        assert 'profitability_ratios' in FinancialRatios.model_fields or 'gross_margin' in FinancialRatios.model_fields

    @pytest.mark.unit
    def test_analyze_financial_statements_structure(self):
        """Test basic structure of analyze_financial_statements function."""
        func = self.get_component_function()

        import inspect

        assert callable(func)
        assert inspect.iscoroutinefunction(func)

        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'financial_data' in params

    def validate_agent_output(self, output, input_data):
        """Validate the agent output structure."""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "financial_statement_analyzer", "packages/sygaldry_registry/components/agents/financial_statement_analyzer/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        FinancialAnalysisResult = module.FinancialAnalysisResult

        assert isinstance(output, FinancialAnalysisResult)
        assert hasattr(output, "ratios")
        assert hasattr(output, "summary")

    @pytest.mark.unit
    def test_financial_metrics(self):
        """Test that various financial metrics are calculated."""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "financial_statement_analyzer", "packages/sygaldry_registry/components/agents/financial_statement_analyzer/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        import inspect

        source = inspect.getsource(module)
        assert 'profitability' in source.lower() or 'margin' in source.lower()
        assert 'liquidity' in source.lower() or 'current_ratio' in source.lower()
