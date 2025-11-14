"""Test suite for sentiment_analysis_agent."""

import pytest
from pathlib import Path
from tests.utils import BaseAgentTest


class TestSentimentAnalysisAgent(BaseAgentTest):
    """Test cases for Sentiment Analysis agent."""

    component_name = "sentiment_analysis_agent"
    component_path = Path("packages/sygaldry_registry/components/agents/sentiment_analysis")

    def get_component_function(self):
        """Get the main agent function."""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "sentiment_analysis_agent", "packages/sygaldry_registry/components/agents/sentiment_analysis/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.analyze_sentiment

    def get_test_inputs(self):
        """Get test input cases."""
        return [
            {"text": "This product is absolutely amazing! Best purchase ever!", "analysis_depth": "detailed"},
            {"text": "Terrible service, very disappointed.", "analysis_depth": "basic"},
        ]

    @pytest.mark.unit
    def test_agent_has_required_functions(self):
        """Test that all required agent functions are present."""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "sentiment_analysis_agent", "packages/sygaldry_registry/components/agents/sentiment_analysis/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        assert hasattr(module, 'analyze_sentiment')
        assert callable(module.analyze_sentiment)

    @pytest.mark.unit
    def test_response_models_structure(self):
        """Test that response models have correct structure."""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "sentiment_analysis_agent", "packages/sygaldry_registry/components/agents/sentiment_analysis/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        assert hasattr(module, 'SentimentAnalysisResult')
        SentimentAnalysisResult = module.SentimentAnalysisResult
        assert 'overall_sentiment' in SentimentAnalysisResult.model_fields

    def validate_agent_output(self, output, input_data):
        """Validate the agent output structure."""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "sentiment_analysis_agent", "packages/sygaldry_registry/components/agents/sentiment_analysis/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        SentimentAnalysisResult = module.SentimentAnalysisResult

        assert isinstance(output, SentimentAnalysisResult)
        assert hasattr(output, "overall_sentiment")
