"""Test suite for github_issues tool following best practices."""

import pytest
from pathlib import Path
from tests.utils import BaseToolTest
from unittest.mock import AsyncMock, MagicMock, patch


class TestGitHubIssuesTool(BaseToolTest):
    """Test github_issues tool component."""

    component_name = "github_issues"
    component_path = Path("packages/sygaldry_registry/components/tools/github_issues")

    def get_component_function(self):
        """Import the tool function."""
        from packages.sygaldry_registry.components.tools.github_issues.tool import search_issues
        return search_issues

    def get_test_inputs(self):
        """Provide test inputs for the tool."""
        return [
            {
                "repo": "facebook/react",
                "query": "is:open label:bug",
                "max_results": 5
            },
            {
                "repo": "microsoft/vscode",
                "query": "is:closed milestone:1.80.0",
                "max_results": 10
            }
        ]

    def validate_tool_output(self, output, input_data):
        """Validate the tool output format."""
        assert isinstance(output, list)
        for issue in output:
            assert 'number' in issue
            assert 'title' in issue
            assert 'state' in issue

    @pytest.mark.unit
    def test_tool_has_required_functions(self):
        """Test that all required functions are present."""
        from packages.sygaldry_registry.components.tools.github_issues import tool

        assert hasattr(tool, 'search_issues')
        assert hasattr(tool, 'get_issue')
        assert hasattr(tool, 'create_issue')
        assert hasattr(tool, 'update_issue')
        assert hasattr(tool, 'list_issue_comments')

    @pytest.mark.unit
    def test_models_structure(self):
        """Test that models have correct structure."""
        from packages.sygaldry_registry.components.tools.github_issues.tool import GitHubIssue

        assert hasattr(GitHubIssue, 'model_fields')
        assert 'number' in GitHubIssue.model_fields
        assert 'title' in GitHubIssue.model_fields
        assert 'state' in GitHubIssue.model_fields
        assert 'labels' in GitHubIssue.model_fields

    @pytest.mark.unit
    def test_search_issues_structure(self):
        """Test search_issues function structure."""
        from packages.sygaldry_registry.components.tools.github_issues.tool import search_issues
        import inspect

        assert callable(search_issues)
        sig = inspect.signature(search_issues)
        params = list(sig.parameters.keys())
        assert 'repo' in params
        assert 'query' in params
