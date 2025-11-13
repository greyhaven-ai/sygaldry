"""Test suite for contract_analysis_agent following best practices."""

import pytest
from pathlib import Path
from tests.utils import BaseAgentTest
from unittest.mock import AsyncMock, patch


class TestContractAnalysisAgent(BaseAgentTest):
    """Test cases for Contract Analysis agent."""

    component_name = "contract_analysis_agent"
    component_path = Path("packages/sygaldry_registry/components/agents/contract_analysis")

    def get_component_function(self):
        """Get the main agent function."""
        # Import directly without triggering __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "contract_analysis_agent", "packages/sygaldry_registry/components/agents/contract_analysis/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.analyze_contract

    def get_test_inputs(self):
        """Get test input cases."""
        return [
            {
                "contract_text": """
                EMPLOYMENT AGREEMENT

                This Agreement is made on January 1, 2024 between Acme Corp and John Doe.

                1. Term: Employment shall commence on January 15, 2024 and continue for 2 years.
                2. Compensation: Employee shall receive $120,000 annually.
                3. Termination: Either party may terminate with 30 days notice.
                4. Non-Compete: Employee agrees not to work for competitors for 1 year after termination.
                5. Confidentiality: Employee shall not disclose confidential information.
                """,
                "analysis_focus": ["risks", "obligations", "key_terms"],
            },
            {
                "contract_text": """
                SOFTWARE LICENSE AGREEMENT

                Licensor grants a non-exclusive license to use the Software.
                License fee: $50,000 per year.
                Liability limited to license fees paid.
                Automatic renewal unless cancelled 60 days before term ends.
                """,
                "analysis_focus": ["liabilities", "renewal_terms", "fees"],
            },
        ]

    @pytest.mark.unit
    def test_agent_has_required_functions(self):
        """Test that all required agent functions are present."""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "contract_analysis_agent", "packages/sygaldry_registry/components/agents/contract_analysis/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Main functions found in the agent
        assert hasattr(module, 'analyze_contract')
        assert callable(module.analyze_contract)
        assert hasattr(module, 'extract_key_terms')
        assert callable(module.extract_key_terms)
        assert hasattr(module, 'identify_risks')
        assert callable(module.identify_risks)
        assert hasattr(module, 'extract_obligations')
        assert callable(module.extract_obligations)

    @pytest.mark.unit
    def test_response_models_structure(self):
        """Test that response models have correct structure."""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "contract_analysis_agent", "packages/sygaldry_registry/components/agents/contract_analysis/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test that the models exist
        assert hasattr(module, 'ContractClause')
        assert hasattr(module, 'RiskAssessment')
        assert hasattr(module, 'ContractObligation')
        assert hasattr(module, 'ContractAnalysisResult')

        # Test model structure (check fields exist)
        ContractClause = module.ContractClause
        assert 'clause_type' in ContractClause.model_fields
        assert 'content' in ContractClause.model_fields
        assert 'section' in ContractClause.model_fields
        assert 'importance' in ContractClause.model_fields
        assert 'explanation' in ContractClause.model_fields

        RiskAssessment = module.RiskAssessment
        assert 'risk_type' in RiskAssessment.model_fields
        assert 'severity' in RiskAssessment.model_fields
        assert 'description' in RiskAssessment.model_fields

    @pytest.mark.unit
    def test_analyze_contract_structure(self):
        """Test basic structure of analyze_contract function."""
        func = self.get_component_function()

        # Test that function exists and is callable
        import inspect

        assert callable(func)
        assert inspect.iscoroutinefunction(func)

        # Test function signature
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'contract_text' in params
        assert 'analysis_focus' in params or 'focus_areas' in params

    def validate_agent_output(self, output, input_data):
        """Validate the agent output structure."""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "contract_analysis_agent", "packages/sygaldry_registry/components/agents/contract_analysis/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        ContractAnalysisResult = module.ContractAnalysisResult

        # Contract analysis should return ContractAnalysisResult
        assert isinstance(output, ContractAnalysisResult)
        assert hasattr(output, "key_terms")
        assert hasattr(output, "risks")
        assert hasattr(output, "obligations")
        assert hasattr(output, "summary")
        assert isinstance(output.key_terms, list)
        assert isinstance(output.risks, list)
        assert isinstance(output.obligations, list)

    @pytest.mark.unit
    def test_contract_clause_types(self):
        """Test that various contract clause types are recognized."""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "contract_analysis_agent", "packages/sygaldry_registry/components/agents/contract_analysis/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check for clause type support
        import inspect

        source = inspect.getsource(module)
        assert 'termination' in source.lower()
        assert 'liability' in source.lower() or 'liabilities' in source.lower()
        assert 'payment' in source.lower() or 'compensation' in source.lower()
        assert 'confidentiality' in source.lower() or 'nda' in source.lower()
