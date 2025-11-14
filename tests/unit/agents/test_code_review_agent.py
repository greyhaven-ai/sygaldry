"""Test suite for code_review_agent."""

import pytest
from pathlib import Path
from tests.utils import BaseAgentTest


class TestCodeReviewAgent(BaseAgentTest):
    """Test cases for Code Review agent."""

    component_name = "code_review_agent"
    component_path = Path("packages/sygaldry_registry/components/agents/code_review")

    def get_component_function(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "code_review_agent", "packages/sygaldry_registry/components/agents/code_review/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.review_code

    def get_test_inputs(self):
        return [{"code": "def add(a, b): return a + b", "language": "python"}]

    @pytest.mark.unit
    def test_agent_has_required_functions(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "code_review_agent", "packages/sygaldry_registry/components/agents/code_review/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        assert hasattr(module, 'review_code')
        assert callable(module.review_code)

    @pytest.mark.unit
    def test_response_models_structure(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "code_review_agent", "packages/sygaldry_registry/components/agents/code_review/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        assert hasattr(module, 'CodeReviewResult')

    def validate_agent_output(self, output, input_data):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "code_review_agent", "packages/sygaldry_registry/components/agents/code_review/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        CodeReviewResult = module.CodeReviewResult
        assert isinstance(output, CodeReviewResult)
        assert hasattr(output, "issues")
