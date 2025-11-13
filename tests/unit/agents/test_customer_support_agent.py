"""Test suite for customer_support_agent."""

import pytest
from pathlib import Path
from tests.utils import BaseAgentTest


class TestCustomerSupportAgent(BaseAgentTest):
    """Test cases for Customer Support agent."""

    component_name = "customer_support_agent"
    component_path = Path("packages/sygaldry_registry/components/agents/customer_support")

    def get_component_function(self):
        """Get the main agent function."""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "customer_support_agent", "packages/sygaldry_registry/components/agents/customer_support/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.analyze_support_ticket

    def get_test_inputs(self):
        """Get test input cases."""
        return [
            {
                "message": "I've been trying to log in for 3 hours and keep getting error 403. This is unacceptable!",
                "analysis_depth": "detailed"
            },
            {
                "message": "How do I reset my password?",
                "analysis_depth": "basic"
            },
            {
                "message": "I need a refund for order #12345. The product doesn't work as advertised.",
                "analysis_depth": "detailed"
            },
            {
                "message": "The system is completely down! All users are affected! This is costing us money!",
                "analysis_depth": "comprehensive"
            },
        ]

    @pytest.mark.unit
    def test_agent_has_required_functions(self):
        """Test that all required agent functions are present."""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "customer_support_agent", "packages/sygaldry_registry/components/agents/customer_support/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Main function
        assert hasattr(module, 'analyze_support_ticket')
        assert callable(module.analyze_support_ticket)

        # Convenience functions
        assert hasattr(module, 'classify_ticket')
        assert callable(module.classify_ticket)
        assert hasattr(module, 'assess_urgency')
        assert callable(module.assess_urgency)
        assert hasattr(module, 'detect_sentiment')
        assert callable(module.detect_sentiment)
        assert hasattr(module, 'suggest_response')
        assert callable(module.suggest_response)
        assert hasattr(module, 'extract_ticket_info')
        assert callable(module.extract_ticket_info)

    @pytest.mark.unit
    def test_response_models_structure(self):
        """Test that response models have correct structure."""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "customer_support_agent", "packages/sygaldry_registry/components/agents/customer_support/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check main response model
        assert hasattr(module, 'CustomerSupportAnalysis')
        CustomerSupportAnalysis = module.CustomerSupportAnalysis
        assert 'category' in CustomerSupportAnalysis.model_fields
        assert 'urgency' in CustomerSupportAnalysis.model_fields
        assert 'sentiment' in CustomerSupportAnalysis.model_fields
        assert 'extracted_info' in CustomerSupportAnalysis.model_fields
        assert 'response_suggestion' in CustomerSupportAnalysis.model_fields
        assert 'summary' in CustomerSupportAnalysis.model_fields

        # Check component models
        assert hasattr(module, 'TicketCategory')
        TicketCategory = module.TicketCategory
        assert 'primary_category' in TicketCategory.model_fields
        assert 'subcategory' in TicketCategory.model_fields
        assert 'confidence' in TicketCategory.model_fields

        assert hasattr(module, 'UrgencyAssessment')
        UrgencyAssessment = module.UrgencyAssessment
        assert 'urgency_level' in UrgencyAssessment.model_fields
        assert 'priority' in UrgencyAssessment.model_fields
        assert 'requires_immediate_attention' in UrgencyAssessment.model_fields

        assert hasattr(module, 'CustomerSentiment')
        CustomerSentiment = module.CustomerSentiment
        assert 'overall_sentiment' in CustomerSentiment.model_fields
        assert 'emotion' in CustomerSentiment.model_fields
        assert 'satisfaction_score' in CustomerSentiment.model_fields
        assert 'churn_risk' in CustomerSentiment.model_fields

        assert hasattr(module, 'ExtractedInformation')
        ExtractedInformation = module.ExtractedInformation
        assert 'specific_issue' in ExtractedInformation.model_fields
        assert 'error_codes' in ExtractedInformation.model_fields

        assert hasattr(module, 'ResponseSuggestion')
        ResponseSuggestion = module.ResponseSuggestion
        assert 'suggested_response' in ResponseSuggestion.model_fields
        assert 'tone' in ResponseSuggestion.model_fields
        assert 'next_steps' in ResponseSuggestion.model_fields
        assert 'escalation_needed' in ResponseSuggestion.model_fields

    @pytest.mark.unit
    def test_lilypad_optional_import(self):
        """Test that lilypad import is optional and doesn't break the module."""
        import importlib.util
        import sys

        # Temporarily block lilypad import
        original_lilypad = sys.modules.get('lilypad')
        if 'lilypad' in sys.modules:
            del sys.modules['lilypad']

        # Mock lilypad as unavailable
        import builtins
        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == 'lilypad':
                raise ImportError("Mocked lilypad unavailable")
            return original_import(name, *args, **kwargs)

        builtins.__import__ = mock_import

        try:
            # Import the module
            spec = importlib.util.spec_from_file_location(
                "customer_support_agent", "packages/sygaldry_registry/components/agents/customer_support/agent.py"
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Check that LILYPAD_AVAILABLE is False
            assert hasattr(module, 'LILYPAD_AVAILABLE')
            assert module.LILYPAD_AVAILABLE is False

            # Check that functions still exist and are callable
            assert hasattr(module, 'analyze_support_ticket')
            assert callable(module.analyze_support_ticket)
            assert hasattr(module, 'classify_ticket')
            assert callable(module.classify_ticket)

        finally:
            # Restore original import
            builtins.__import__ = original_import
            if original_lilypad is not None:
                sys.modules['lilypad'] = original_lilypad

    @pytest.mark.unit
    def test_ticket_categories_enum(self):
        """Test that ticket category literals are properly defined."""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "customer_support_agent", "packages/sygaldry_registry/components/agents/customer_support/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        TicketCategory = module.TicketCategory
        field = TicketCategory.model_fields['primary_category']

        # Check that the field has the expected literal values
        # The metadata should contain the allowed values
        assert field.annotation is not None

    @pytest.mark.unit
    def test_urgency_levels_enum(self):
        """Test that urgency level literals are properly defined."""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "customer_support_agent", "packages/sygaldry_registry/components/agents/customer_support/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        UrgencyAssessment = module.UrgencyAssessment
        urgency_field = UrgencyAssessment.model_fields['urgency_level']
        priority_field = UrgencyAssessment.model_fields['priority']

        # Check that the fields are defined
        assert urgency_field.annotation is not None
        assert priority_field.annotation is not None

    def validate_agent_output(self, output, input_data):
        """Validate the agent output structure."""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "customer_support_agent", "packages/sygaldry_registry/components/agents/customer_support/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        CustomerSupportAnalysis = module.CustomerSupportAnalysis

        assert isinstance(output, CustomerSupportAnalysis)
        assert hasattr(output, "category")
        assert hasattr(output, "urgency")
        assert hasattr(output, "sentiment")
        assert hasattr(output, "extracted_info")
        assert hasattr(output, "response_suggestion")
        assert hasattr(output, "summary")
        assert hasattr(output, "key_points")
        assert hasattr(output, "tags")

        # Validate nested structures
        assert hasattr(output.category, "primary_category")
        assert hasattr(output.urgency, "urgency_level")
        assert hasattr(output.sentiment, "overall_sentiment")
        assert hasattr(output.extracted_info, "specific_issue")
        assert hasattr(output.response_suggestion, "suggested_response")

        # Validate types
        assert isinstance(output.summary, str)
        assert isinstance(output.key_points, list)
        assert isinstance(output.tags, list)
        assert isinstance(output.response_suggestion.next_steps, list)
