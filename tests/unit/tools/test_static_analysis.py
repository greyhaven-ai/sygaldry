"""Test suite for static_analysis tool following best practices."""

import pytest
from pathlib import Path
from tests.utils import BaseToolTest
from unittest.mock import MagicMock, patch, Mock
import json
import subprocess


class TestStaticAnalysisTool(BaseToolTest):
    """Test static_analysis tool component."""

    component_name = "static_analysis"
    component_path = Path("packages/sygaldry_registry/components/tools/static_analysis")

    def get_component_function(self):
        """Import the tool function."""
        from packages.sygaldry_registry.components.tools.static_analysis.tool import analyze_code
        return analyze_code

    def get_test_inputs(self):
        """Provide test inputs for the tool."""
        return [
            {
                "file_path": "test_file.py",
                "tools": ["pylint"],
                "include_security": False
            },
            {
                "file_path": "test_directory/",
                "tools": ["all"],
                "include_security": True
            }
        ]

    def validate_tool_output(self, output, input_data):
        """Validate the tool output format."""
        assert hasattr(output, 'target')
        assert hasattr(output, 'tools_run')
        assert hasattr(output, 'code_issues')
        assert hasattr(output, 'security_issues')
        assert hasattr(output, 'total_issues')
        assert isinstance(output.tools_run, list)
        assert isinstance(output.code_issues, list)

    @pytest.mark.unit
    def test_tool_has_required_functions(self):
        """Test that all required functions are present."""
        from packages.sygaldry_registry.components.tools.static_analysis import tool

        assert hasattr(tool, 'run_pylint')
        assert hasattr(tool, 'run_flake8')
        assert hasattr(tool, 'run_mypy')
        assert hasattr(tool, 'run_bandit')
        assert hasattr(tool, 'run_semgrep')
        assert hasattr(tool, 'analyze_code')

    @pytest.mark.unit
    def test_models_structure(self):
        """Test that models have correct structure."""
        from packages.sygaldry_registry.components.tools.static_analysis.tool import (
            CodeIssue,
            SecurityIssue,
            AnalysisResult
        )

        # Test CodeIssue model
        assert hasattr(CodeIssue, 'model_fields')
        assert 'file_path' in CodeIssue.model_fields
        assert 'line' in CodeIssue.model_fields
        assert 'severity' in CodeIssue.model_fields
        assert 'category' in CodeIssue.model_fields
        assert 'message' in CodeIssue.model_fields
        assert 'tool' in CodeIssue.model_fields

        # Test SecurityIssue model
        assert hasattr(SecurityIssue, 'model_fields')
        assert 'file_path' in SecurityIssue.model_fields
        assert 'severity' in SecurityIssue.model_fields
        assert 'confidence' in SecurityIssue.model_fields
        assert 'issue_id' in SecurityIssue.model_fields
        assert 'message' in SecurityIssue.model_fields

        # Test AnalysisResult model
        assert hasattr(AnalysisResult, 'model_fields')
        assert 'target' in AnalysisResult.model_fields
        assert 'tools_run' in AnalysisResult.model_fields
        assert 'code_issues' in AnalysisResult.model_fields
        assert 'security_issues' in AnalysisResult.model_fields
        assert 'total_issues' in AnalysisResult.model_fields
        assert 'summary' in AnalysisResult.model_fields

    @pytest.mark.unit
    def test_run_pylint_structure(self):
        """Test run_pylint function structure."""
        from packages.sygaldry_registry.components.tools.static_analysis.tool import run_pylint
        import inspect

        assert callable(run_pylint)
        sig = inspect.signature(run_pylint)
        params = list(sig.parameters.keys())
        assert 'file_path' in params

    @pytest.mark.unit
    def test_run_flake8_structure(self):
        """Test run_flake8 function structure."""
        from packages.sygaldry_registry.components.tools.static_analysis.tool import run_flake8
        import inspect

        assert callable(run_flake8)
        sig = inspect.signature(run_flake8)
        params = list(sig.parameters.keys())
        assert 'file_path' in params

    @pytest.mark.unit
    def test_run_mypy_structure(self):
        """Test run_mypy function structure."""
        from packages.sygaldry_registry.components.tools.static_analysis.tool import run_mypy
        import inspect

        assert callable(run_mypy)
        sig = inspect.signature(run_mypy)
        params = list(sig.parameters.keys())
        assert 'file_path' in params

    @pytest.mark.unit
    def test_run_bandit_structure(self):
        """Test run_bandit function structure."""
        from packages.sygaldry_registry.components.tools.static_analysis.tool import run_bandit
        import inspect

        assert callable(run_bandit)
        sig = inspect.signature(run_bandit)
        params = list(sig.parameters.keys())
        assert 'file_path' in params

    @pytest.mark.unit
    def test_analyze_code_structure(self):
        """Test analyze_code function structure."""
        from packages.sygaldry_registry.components.tools.static_analysis.tool import analyze_code
        import inspect

        assert callable(analyze_code)
        sig = inspect.signature(analyze_code)
        params = list(sig.parameters.keys())
        assert 'file_path' in params
        assert 'tools' in params
        assert 'include_security' in params

    @pytest.mark.unit
    @patch('subprocess.run')
    def test_check_tool_available(self, mock_run):
        """Test tool availability checking."""
        from packages.sygaldry_registry.components.tools.static_analysis.tool import _check_tool_available

        # Mock successful tool check
        mock_run.return_value = Mock(returncode=0)
        assert _check_tool_available("pylint") is True

        # Mock failed tool check
        mock_run.return_value = Mock(returncode=1)
        assert _check_tool_available("nonexistent") is False

        # Mock FileNotFoundError
        mock_run.side_effect = FileNotFoundError()
        assert _check_tool_available("missing_tool") is False

    @pytest.mark.unit
    @patch('subprocess.run')
    @patch('packages.sygaldry_registry.components.tools.static_analysis.tool._check_tool_available')
    def test_run_pylint_with_mock(self, mock_check, mock_run):
        """Test run_pylint with mocked subprocess."""
        from packages.sygaldry_registry.components.tools.static_analysis.tool import run_pylint

        mock_check.return_value = True

        # Mock pylint output
        mock_output = [
            {
                "path": "test.py",
                "line": 10,
                "column": 5,
                "type": "error",
                "message-id": "E0001",
                "message": "Syntax error"
            },
            {
                "path": "test.py",
                "line": 20,
                "column": 10,
                "type": "warning",
                "message-id": "W0612",
                "message": "Unused variable"
            }
        ]

        mock_run.return_value = Mock(
            returncode=1,
            stdout=json.dumps(mock_output),
            stderr=""
        )

        issues = run_pylint("test.py")

        assert len(issues) == 2
        assert issues[0].file_path == "test.py"
        assert issues[0].line == 10
        assert issues[0].severity == "error"
        assert issues[0].tool == "pylint"
        assert issues[1].severity == "warning"

    @pytest.mark.unit
    @patch('subprocess.run')
    @patch('packages.sygaldry_registry.components.tools.static_analysis.tool._check_tool_available')
    def test_run_flake8_with_mock(self, mock_check, mock_run):
        """Test run_flake8 with mocked subprocess."""
        from packages.sygaldry_registry.components.tools.static_analysis.tool import run_flake8

        mock_check.return_value = True

        # Mock flake8 JSON output
        mock_output = {
            "test.py": [
                {
                    "code": "E501",
                    "line_number": 15,
                    "column_number": 80,
                    "text": "line too long"
                }
            ]
        }

        mock_run.return_value = Mock(
            returncode=1,
            stdout=json.dumps(mock_output),
            stderr=""
        )

        issues = run_flake8("test.py")

        assert len(issues) == 1
        assert issues[0].file_path == "test.py"
        assert issues[0].line == 15
        assert issues[0].category == "E501"
        assert issues[0].tool == "flake8"

    @pytest.mark.unit
    @patch('subprocess.run')
    @patch('packages.sygaldry_registry.components.tools.static_analysis.tool._check_tool_available')
    def test_run_mypy_with_mock(self, mock_check, mock_run):
        """Test run_mypy with mocked subprocess."""
        from packages.sygaldry_registry.components.tools.static_analysis.tool import run_mypy

        mock_check.return_value = True

        # Mock mypy output
        mock_output = "test.py:25:10: error: Incompatible types\ntest.py:30:5: warning: Unused import"

        mock_run.return_value = Mock(
            returncode=1,
            stdout=mock_output,
            stderr=""
        )

        issues = run_mypy("test.py")

        assert len(issues) == 2
        assert issues[0].file_path == "test.py"
        assert issues[0].line == 25
        assert issues[0].column == 10
        assert issues[0].severity == "error"
        assert issues[0].tool == "mypy"

    @pytest.mark.unit
    @patch('subprocess.run')
    @patch('packages.sygaldry_registry.components.tools.static_analysis.tool._check_tool_available')
    def test_run_bandit_with_mock(self, mock_check, mock_run):
        """Test run_bandit with mocked subprocess."""
        from packages.sygaldry_registry.components.tools.static_analysis.tool import run_bandit

        mock_check.return_value = True

        # Mock bandit output
        mock_output = {
            "results": [
                {
                    "filename": "test.py",
                    "line_number": 42,
                    "issue_severity": "HIGH",
                    "issue_confidence": "HIGH",
                    "test_id": "B301",
                    "issue_text": "Use of pickle module",
                    "code": "import pickle"
                }
            ]
        }

        mock_run.return_value = Mock(
            returncode=1,
            stdout=json.dumps(mock_output),
            stderr=""
        )

        issues = run_bandit("test.py")

        assert len(issues) == 1
        assert issues[0].file_path == "test.py"
        assert issues[0].line == 42
        assert issues[0].severity == "high"
        assert issues[0].confidence == "high"
        assert issues[0].issue_id == "B301"

    @pytest.mark.unit
    @patch('packages.sygaldry_registry.components.tools.static_analysis.tool.run_pylint')
    @patch('packages.sygaldry_registry.components.tools.static_analysis.tool.run_flake8')
    @patch('packages.sygaldry_registry.components.tools.static_analysis.tool.run_mypy')
    def test_analyze_code_integration(self, mock_mypy, mock_flake8, mock_pylint):
        """Test analyze_code integration with all tools."""
        from packages.sygaldry_registry.components.tools.static_analysis.tool import (
            analyze_code,
            CodeIssue
        )

        # Mock return values
        mock_pylint.return_value = [
            CodeIssue(
                file_path="test.py",
                line=10,
                column=5,
                severity="error",
                category="E0001",
                message="Test error",
                tool="pylint"
            )
        ]
        mock_flake8.return_value = []
        mock_mypy.return_value = []

        result = analyze_code("test.py", tools=["all"], include_security=False)

        assert result.target == "test.py"
        assert "pylint" in result.tools_run
        assert len(result.code_issues) == 1
        assert result.total_issues == 1
        assert result.summary["total"] == 1

    @pytest.mark.unit
    def test_code_issue_model_validation(self):
        """Test CodeIssue model validation."""
        from packages.sygaldry_registry.components.tools.static_analysis.tool import CodeIssue

        # Valid issue
        issue = CodeIssue(
            file_path="test.py",
            line=10,
            column=5,
            severity="error",
            category="E001",
            message="Test error",
            tool="pylint"
        )

        assert issue.file_path == "test.py"
        assert issue.line == 10
        assert issue.severity == "error"

        # Test with None values
        issue2 = CodeIssue(
            file_path="test.py",
            line=None,
            column=None,
            severity="warning",
            category="W001",
            message="Test warning",
            tool="flake8"
        )

        assert issue2.line is None
        assert issue2.column is None

    @pytest.mark.unit
    def test_security_issue_model_validation(self):
        """Test SecurityIssue model validation."""
        from packages.sygaldry_registry.components.tools.static_analysis.tool import SecurityIssue

        # Valid issue
        issue = SecurityIssue(
            file_path="test.py",
            line=42,
            severity="high",
            confidence="medium",
            cwe_id="CWE-89",
            issue_id="B608",
            message="SQL injection risk",
            code_snippet="cursor.execute(query)"
        )

        assert issue.file_path == "test.py"
        assert issue.severity == "high"
        assert issue.confidence == "medium"

    @pytest.mark.unit
    def test_analysis_result_model_validation(self):
        """Test AnalysisResult model validation."""
        from packages.sygaldry_registry.components.tools.static_analysis.tool import AnalysisResult

        result = AnalysisResult(
            target="test.py",
            tools_run=["pylint", "flake8"],
            tools_failed=["mypy"],
            code_issues=[],
            security_issues=[],
            total_issues=0,
            summary={"total": 0}
        )

        assert result.target == "test.py"
        assert len(result.tools_run) == 2
        assert "pylint" in result.tools_run

    @pytest.mark.unit
    @patch('subprocess.run')
    @patch('packages.sygaldry_registry.components.tools.static_analysis.tool._check_tool_available')
    def test_tool_timeout_handling(self, mock_check, mock_run):
        """Test timeout handling."""
        from packages.sygaldry_registry.components.tools.static_analysis.tool import run_pylint

        mock_check.return_value = True
        mock_run.side_effect = subprocess.TimeoutExpired("pylint", 60.0)

        with pytest.raises(RuntimeError, match="timed out"):
            run_pylint("test.py")

    @pytest.mark.unit
    @patch('subprocess.run')
    @patch('packages.sygaldry_registry.components.tools.static_analysis.tool._check_tool_available')
    def test_tool_not_available(self, mock_check, mock_run):
        """Test handling of unavailable tools."""
        from packages.sygaldry_registry.components.tools.static_analysis.tool import run_pylint

        mock_check.return_value = False

        with pytest.raises(RuntimeError, match="not available"):
            run_pylint("test.py")

    @pytest.mark.unit
    @patch('packages.sygaldry_registry.components.tools.static_analysis.tool.run_pylint')
    def test_analyze_code_error_handling(self, mock_pylint):
        """Test analyze_code handles tool errors gracefully."""
        from packages.sygaldry_registry.components.tools.static_analysis.tool import analyze_code

        # Mock pylint to raise an error
        mock_pylint.side_effect = RuntimeError("Tool failed")

        result = analyze_code("test.py", tools=["pylint"], include_security=False)

        assert len(result.tools_failed) > 0
        assert any("pylint" in failure for failure in result.tools_failed)

    @pytest.mark.unit
    @patch('subprocess.run')
    @patch('packages.sygaldry_registry.components.tools.static_analysis.tool._check_tool_available')
    def test_flake8_plain_output_fallback(self, mock_check, mock_run):
        """Test flake8 plain text parsing fallback."""
        from packages.sygaldry_registry.components.tools.static_analysis.tool import _parse_flake8_plain_output

        plain_output = "test.py:10:5: E501 line too long\ntest.py:20:10: W503 line break before operator"

        issues = _parse_flake8_plain_output(plain_output, "test.py")

        assert len(issues) == 2
        assert issues[0].line == 10
        assert issues[0].category == "E501"
        assert issues[1].line == 20
        assert issues[1].category == "W503"
