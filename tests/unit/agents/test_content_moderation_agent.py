"""Test suite for content_moderation_agent following best practices."""

import pytest
from pathlib import Path
from tests.utils import BaseAgentTest
from unittest.mock import AsyncMock, patch


class TestContentModerationAgent(BaseAgentTest):
    """Test cases for Content Moderation agent."""

    component_name = "content_moderation_agent"
    component_path = Path("packages/sygaldry_registry/components/agents/content_moderation")

    def get_component_function(self):
        """Get the main agent function."""
        # Import directly without triggering __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "content_moderation_agent",
            "packages/sygaldry_registry/components/agents/content_moderation/agent.py",
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.moderate_content

    def get_test_inputs(self):
        """Get test input cases."""
        return [
            {
                "content": "This is a normal, safe comment about technology.",
                "content_type": "comment",
                "sensitivity_level": "medium",
                "expected_verdict": "safe",
            },
            {
                "content": "I hate those people, they should all be banned!",
                "content_type": "comment",
                "sensitivity_level": "high",
                "expected_verdict": "unsafe",
            },
            {
                "content": "Buy cheap pills now! Click here for amazing deals!!!",
                "content_type": "post",
                "sensitivity_level": "medium",
                "expected_verdict": "unsafe",
            },
            {
                "content": "This product is excellent, highly recommended!",
                "content_type": "review",
                "sensitivity_level": "low",
                "expected_verdict": "safe",
            },
        ]

    @pytest.mark.unit
    def test_agent_has_required_functions(self):
        """Test that all required agent functions are present."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "content_moderation_agent",
            "packages/sygaldry_registry/components/agents/content_moderation/agent.py",
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Main functions found in the agent
        assert hasattr(module, "moderate_content")
        assert callable(module.moderate_content)
        assert hasattr(module, "quick_moderate")
        assert callable(module.quick_moderate)
        assert hasattr(module, "moderate_with_action")
        assert callable(module.moderate_with_action)
        assert hasattr(module, "detect_violations")
        assert callable(module.detect_violations)
        assert hasattr(module, "check_safety")
        assert callable(module.check_safety)
        assert hasattr(module, "get_risk_score")
        assert callable(module.get_risk_score)

    @pytest.mark.unit
    def test_response_models_structure(self):
        """Test that response models have correct structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "content_moderation_agent",
            "packages/sygaldry_registry/components/agents/content_moderation/agent.py",
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test that the models exist
        assert hasattr(module, "ModerationResult")
        assert hasattr(module, "ViolationCategory")
        assert hasattr(module, "ModerationAction")
        assert hasattr(module, "ContextualFactors")

        # Test basic model instantiation
        ViolationCategory = module.ViolationCategory
        violation = ViolationCategory(
            category="spam",
            severity="medium",
            confidence=0.85,
            evidence=["Buy now!", "Click here!"],
            explanation="Contains spam indicators",
        )
        assert violation.category == "spam"
        assert violation.severity == "medium"
        assert violation.confidence == 0.85

        # Test ModerationAction model
        ModerationAction = module.ModerationAction
        action = ModerationAction(
            action="flag_for_review",
            priority="medium",
            reasoning="Borderline content requires human judgment",
            requires_human_review=True,
        )
        assert action.action == "flag_for_review"
        assert action.requires_human_review is True

        # Test ContextualFactors model
        ContextualFactors = module.ContextualFactors
        factors = ContextualFactors(
            sarcasm_detected=False,
            educational_context=True,
            news_reporting=False,
            artistic_expression=False,
            discussion_of_issues=True,
        )
        assert factors.educational_context is True
        assert factors.discussion_of_issues is True

    @pytest.mark.unit
    def test_moderate_content_structure(self):
        """Test basic structure of moderate_content function."""
        # Import the function
        func = self.get_component_function()

        # Test that function exists and is callable
        import inspect

        assert callable(func)
        assert inspect.iscoroutinefunction(func)

        # Test function signature
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert "content" in params
        assert "content_type" in params
        assert "sensitivity_level" in params
        assert "context" in params or "custom_policies" in params

    def validate_agent_output(self, output, input_data):
        """Validate the agent output structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "content_moderation_agent",
            "packages/sygaldry_registry/components/agents/content_moderation/agent.py",
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        ModerationResult = module.ModerationResult

        # Content moderation should return a ModerationResult
        assert isinstance(output, ModerationResult)
        assert hasattr(output, "overall_verdict")
        assert hasattr(output, "violations")
        assert hasattr(output, "recommended_action")
        assert hasattr(output, "contextual_factors")
        assert hasattr(output, "risk_score")
        assert hasattr(output, "summary")
        assert isinstance(output.violations, list)
        assert 0.0 <= output.risk_score <= 1.0

    @pytest.mark.unit
    def test_helper_functions(self):
        """Test helper functions exist and have correct signatures."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        import inspect

        spec = importlib.util.spec_from_file_location(
            "content_moderation_agent",
            "packages/sygaldry_registry/components/agents/content_moderation/agent.py",
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test quick_moderate
        func = module.quick_moderate
        assert callable(func)
        assert inspect.iscoroutinefunction(func)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert "content" in params

        # Test moderate_with_action
        func = module.moderate_with_action
        assert callable(func)
        assert inspect.iscoroutinefunction(func)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert "content" in params

        # Test detect_violations
        func = module.detect_violations
        assert callable(func)
        assert inspect.iscoroutinefunction(func)

        # Test check_safety
        func = module.check_safety
        assert callable(func)
        assert inspect.iscoroutinefunction(func)

        # Test get_risk_score
        func = module.get_risk_score
        assert callable(func)
        assert inspect.iscoroutinefunction(func)

    @pytest.mark.unit
    def test_violation_categories(self):
        """Test that various violation categories are supported."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "content_moderation_agent",
            "packages/sygaldry_registry/components/agents/content_moderation/agent.py",
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check for violation category support
        import inspect

        source = inspect.getsource(module)
        assert "hate_speech" in source.lower()
        assert "harassment" in source.lower()
        assert "violence" in source.lower()
        assert "sexual" in source.lower() or "sexual_content" in source.lower()
        assert "misinformation" in source.lower()
        assert "spam" in source.lower()
        assert "self" in source.lower() and "harm" in source.lower()
        assert "illegal" in source.lower()

    @pytest.mark.unit
    def test_severity_levels(self):
        """Test that severity levels are supported."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "content_moderation_agent",
            "packages/sygaldry_registry/components/agents/content_moderation/agent.py",
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check for severity level support
        import inspect

        source = inspect.getsource(module)
        # Should support none, low, medium, high, critical
        assert "low" in source.lower()
        assert "medium" in source.lower()
        assert "high" in source.lower()
        assert "critical" in source.lower()

    @pytest.mark.unit
    def test_content_types(self):
        """Test that multiple content types are supported."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "content_moderation_agent",
            "packages/sygaldry_registry/components/agents/content_moderation/agent.py",
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check for content type support
        import inspect

        source = inspect.getsource(module)
        assert "text" in source.lower()
        assert "comment" in source.lower()
        assert "post" in source.lower()
        assert "message" in source.lower()

    @pytest.mark.unit
    def test_sensitivity_levels(self):
        """Test that sensitivity levels are supported."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "content_moderation_agent",
            "packages/sygaldry_registry/components/agents/content_moderation/agent.py",
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check for sensitivity level support in moderate_content
        import inspect

        sig = inspect.signature(module.moderate_content)
        params = sig.parameters

        # Should have sensitivity_level parameter
        assert "sensitivity_level" in params

    @pytest.mark.unit
    def test_moderation_actions(self):
        """Test that various moderation actions are supported."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "content_moderation_agent",
            "packages/sygaldry_registry/components/agents/content_moderation/agent.py",
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check for action support
        import inspect

        source = inspect.getsource(module)
        assert "approve" in source.lower()
        assert "flag" in source.lower() or "review" in source.lower()
        assert "remove" in source.lower()
        assert "suspend" in source.lower() or "ban" in source.lower()

    @pytest.mark.unit
    def test_contextual_analysis(self):
        """Test that contextual analysis is supported."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "content_moderation_agent",
            "packages/sygaldry_registry/components/agents/content_moderation/agent.py",
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check for contextual analysis support
        import inspect

        source = inspect.getsource(module)
        assert "context" in source.lower()
        assert "sarcasm" in source.lower() or "irony" in source.lower()
        assert "educational" in source.lower()
        assert "news" in source.lower() or "reporting" in source.lower()

    @pytest.mark.unit
    def test_lilypad_optional(self):
        """Test that lilypad import is optional."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "content_moderation_agent",
            "packages/sygaldry_registry/components/agents/content_moderation/agent.py",
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check for optional lilypad import pattern
        import inspect

        source = inspect.getsource(module)
        assert "try:" in source and "from lilypad import trace" in source
        assert "except ImportError:" in source
        # Should have LILYPAD_AVAILABLE flag or similar pattern
        assert "LILYPAD_AVAILABLE" in source or "def trace()" in source
