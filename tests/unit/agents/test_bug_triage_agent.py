"""Test suite for bug_triage_agent following best practices."""

import pytest
from pathlib import Path
from tests.utils import BaseAgentTest
from unittest.mock import AsyncMock, patch


class TestBugTriageAgent(BaseAgentTest):
    """Test cases for Bug Triage agent."""

    component_name = "bug_triage_agent"
    component_path = Path("packages/sygaldry_registry/components/agents/bug_triage")

    def get_component_function(self):
        """Get the main agent function."""
        # Import directly without triggering __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "bug_triage_agent", "packages/sygaldry_registry/components/agents/bug_triage/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.triage_bug

    def get_test_inputs(self):
        """Get test input cases."""
        return [
            {
                "bug_report": """
                Title: Login fails with 500 error when using Google OAuth

                Description:
                Users are reporting they cannot log in using Google OAuth.
                When they click the "Sign in with Google" button, they get redirected
                to Google, authenticate successfully, but then get a 500 Internal Server Error
                when redirected back to our app.

                Error in logs:
                TypeError: Cannot read property 'email' of undefined
                at /api/auth/google/callback:45

                Started happening after yesterday's deployment.
                Affects approximately 30% of login attempts.
                """,
                "context": "Recent deployment included OAuth provider updates",
            },
            {
                "bug_report": """
                Title: Product images not loading on mobile

                Description:
                Product images are not displaying on mobile devices (iOS and Android).
                Desktop version works fine.
                Images show a broken image icon.
                Console shows 404 errors for image URLs.

                Happens on product detail pages and search results.
                Started this morning around 9 AM.
                """,
                "context": "CDN configuration was updated last night",
            },
            {
                "bug_report": """
                Title: Typo in settings page

                Description:
                The word "preferences" is misspelled as "preferances" on the user settings page.
                Located in the Account Settings section under Privacy tab.
                """,
            },
        ]

    @pytest.mark.unit
    def test_agent_has_required_functions(self):
        """Test that all required agent functions are present."""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "bug_triage_agent", "packages/sygaldry_registry/components/agents/bug_triage/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Main functions found in the agent
        assert hasattr(module, 'triage_bug')
        assert callable(module.triage_bug)
        assert hasattr(module, 'classify_severity')
        assert callable(module.classify_severity)
        assert hasattr(module, 'identify_component')
        assert callable(module.identify_component)
        assert hasattr(module, 'analyze_root_cause')
        assert callable(module.analyze_root_cause)
        assert hasattr(module, 'generate_reproduction_steps')
        assert callable(module.generate_reproduction_steps)

    @pytest.mark.unit
    def test_response_models_structure(self):
        """Test that response models have correct structure."""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "bug_triage_agent", "packages/sygaldry_registry/components/agents/bug_triage/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test that the models exist
        assert hasattr(module, 'BugTriageResult')
        assert hasattr(module, 'SeverityClassification')
        assert hasattr(module, 'ComponentIdentification')
        assert hasattr(module, 'RootCauseAnalysis')
        assert hasattr(module, 'ReproductionSteps')

        # Test model structure (check fields exist)
        SeverityClassification = module.SeverityClassification
        assert 'severity' in SeverityClassification.model_fields
        assert 'priority' in SeverityClassification.model_fields
        assert 'severity_reasoning' in SeverityClassification.model_fields
        assert 'user_impact' in SeverityClassification.model_fields
        assert 'business_impact' in SeverityClassification.model_fields

        ComponentIdentification = module.ComponentIdentification
        assert 'component_name' in ComponentIdentification.model_fields
        assert 'component_type' in ComponentIdentification.model_fields
        assert 'confidence' in ComponentIdentification.model_fields

        RootCauseAnalysis = module.RootCauseAnalysis
        assert 'likely_cause' in RootCauseAnalysis.model_fields
        assert 'cause_category' in RootCauseAnalysis.model_fields
        assert 'confidence' in RootCauseAnalysis.model_fields

        ReproductionSteps = module.ReproductionSteps
        assert 'steps' in ReproductionSteps.model_fields
        assert 'expected_behavior' in ReproductionSteps.model_fields
        assert 'actual_behavior' in ReproductionSteps.model_fields
        assert 'reproducibility' in ReproductionSteps.model_fields

    @pytest.mark.unit
    def test_triage_bug_structure(self):
        """Test basic structure of triage_bug function."""
        func = self.get_component_function()

        # Test that function exists and is callable
        import inspect

        assert callable(func)
        assert inspect.iscoroutinefunction(func)

        # Test function signature
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'bug_report' in params
        assert 'context' in params
        assert 'include_recommendations' in params

    def validate_agent_output(self, output, input_data):
        """Validate the agent output structure."""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "bug_triage_agent", "packages/sygaldry_registry/components/agents/bug_triage/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        BugTriageResult = module.BugTriageResult

        # Bug triage should return BugTriageResult
        assert isinstance(output, BugTriageResult)
        assert hasattr(output, "summary")
        assert hasattr(output, "severity_classification")
        assert hasattr(output, "component")
        assert hasattr(output, "root_cause")
        assert hasattr(output, "reproduction")
        assert hasattr(output, "recommended_assignee")
        assert hasattr(output, "estimated_effort")
        assert isinstance(output.recommendations, list)
        assert isinstance(output.tags, list)

    @pytest.mark.unit
    def test_severity_levels(self):
        """Test that severity levels are properly defined."""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "bug_triage_agent", "packages/sygaldry_registry/components/agents/bug_triage/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check for severity level support in source
        import inspect

        source = inspect.getsource(module)
        assert 'critical' in source.lower()
        assert 'high' in source.lower()
        assert 'medium' in source.lower()
        assert 'low' in source.lower()
        assert 'trivial' in source.lower()

    @pytest.mark.unit
    def test_priority_levels(self):
        """Test that priority levels are properly defined."""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "bug_triage_agent", "packages/sygaldry_registry/components/agents/bug_triage/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check for priority level support in source
        import inspect

        source = inspect.getsource(module)
        assert 'urgent' in source.lower()
        assert 'priority' in source.lower()
        assert 'backlog' in source.lower()

    @pytest.mark.unit
    def test_root_cause_categories(self):
        """Test that root cause categories are defined."""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "bug_triage_agent", "packages/sygaldry_registry/components/agents/bug_triage/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check for root cause categories
        import inspect

        source = inspect.getsource(module)
        assert 'logic_error' in source
        assert 'null_pointer' in source
        assert 'race_condition' in source
        assert 'security' in source
        assert 'performance' in source

    @pytest.mark.unit
    def test_convenience_functions(self):
        """Test that convenience functions exist."""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "bug_triage_agent", "packages/sygaldry_registry/components/agents/bug_triage/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test convenience functions
        assert hasattr(module, 'quick_severity_check')
        assert callable(module.quick_severity_check)
        assert hasattr(module, 'get_reproduction_steps')
        assert callable(module.get_reproduction_steps)
        assert hasattr(module, 'identify_bug_component')
        assert callable(module.identify_bug_component)

    @pytest.mark.unit
    def test_lilypad_optional_import(self):
        """Test that lilypad import is optional."""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "bug_triage_agent", "packages/sygaldry_registry/components/agents/bug_triage/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check that LILYPAD_AVAILABLE flag exists
        assert hasattr(module, 'LILYPAD_AVAILABLE')
        assert isinstance(module.LILYPAD_AVAILABLE, bool)

        # Check that trace decorator exists (either from lilypad or fallback)
        assert hasattr(module, 'trace')
        assert callable(module.trace)
