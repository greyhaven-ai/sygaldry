"""Test suite for helpdesk_integration tool following best practices."""

import pytest
from pathlib import Path
from tests.utils import BaseToolTest
from unittest.mock import AsyncMock, MagicMock, patch


class TestHelpdeskIntegrationTool(BaseToolTest):
    """Test helpdesk_integration tool component."""

    component_name = "helpdesk_integration"
    component_path = Path("packages/sygaldry_registry/components/tools/helpdesk_integration")

    def get_component_function(self):
        """Import the tool function."""
        from packages.sygaldry_registry.components.tools.helpdesk_integration.tool import search_tickets
        return search_tickets

    def get_test_inputs(self):
        """Provide test inputs for the tool."""
        return [
            {
                "query": "login issue",
                "status": "open",
                "priority": "high",
                "max_results": 5
            },
            {
                "query": "payment error",
                "status": "pending",
                "max_results": 10
            }
        ]

    def validate_tool_output(self, output, input_data):
        """Validate the tool output format."""
        assert isinstance(output, list)
        for ticket in output:
            assert hasattr(ticket, 'id')
            assert hasattr(ticket, 'subject')
            assert hasattr(ticket, 'status')
            assert hasattr(ticket, 'priority')

    @pytest.mark.unit
    def test_tool_has_required_functions(self):
        """Test that all required functions are present."""
        from packages.sygaldry_registry.components.tools.helpdesk_integration import tool

        assert hasattr(tool, 'search_tickets')
        assert hasattr(tool, 'get_ticket')
        assert hasattr(tool, 'create_ticket')
        assert hasattr(tool, 'update_ticket')
        assert hasattr(tool, 'list_ticket_comments')
        assert hasattr(tool, 'add_ticket_comment')
        assert hasattr(tool, 'add_ticket_tags')

    @pytest.mark.unit
    def test_models_structure(self):
        """Test that models have correct structure."""
        from packages.sygaldry_registry.components.tools.helpdesk_integration.tool import (
            Ticket,
            Comment,
            TicketStatus,
            TicketRequester
        )

        # Test Ticket model
        assert hasattr(Ticket, 'model_fields')
        assert 'id' in Ticket.model_fields
        assert 'subject' in Ticket.model_fields
        assert 'status' in Ticket.model_fields
        assert 'priority' in Ticket.model_fields
        assert 'tags' in Ticket.model_fields
        assert 'requester_id' in Ticket.model_fields

        # Test Comment model
        assert hasattr(Comment, 'model_fields')
        assert 'id' in Comment.model_fields
        assert 'body' in Comment.model_fields
        assert 'author_id' in Comment.model_fields
        assert 'public' in Comment.model_fields

        # Test TicketStatus model
        assert hasattr(TicketStatus, 'model_fields')
        assert 'value' in TicketStatus.model_fields
        assert 'label' in TicketStatus.model_fields

        # Test TicketRequester model
        assert hasattr(TicketRequester, 'model_fields')
        assert 'id' in TicketRequester.model_fields
        assert 'name' in TicketRequester.model_fields
        assert 'email' in TicketRequester.model_fields

    @pytest.mark.unit
    def test_search_tickets_structure(self):
        """Test search_tickets function structure."""
        from packages.sygaldry_registry.components.tools.helpdesk_integration.tool import search_tickets
        import inspect

        assert callable(search_tickets)
        sig = inspect.signature(search_tickets)
        params = list(sig.parameters.keys())
        assert 'query' in params
        assert 'status' in params
        assert 'priority' in params
        assert 'max_results' in params

    @pytest.mark.unit
    def test_get_ticket_structure(self):
        """Test get_ticket function structure."""
        from packages.sygaldry_registry.components.tools.helpdesk_integration.tool import get_ticket
        import inspect

        assert callable(get_ticket)
        sig = inspect.signature(get_ticket)
        params = list(sig.parameters.keys())
        assert 'ticket_id' in params

    @pytest.mark.unit
    def test_create_ticket_structure(self):
        """Test create_ticket function structure."""
        from packages.sygaldry_registry.components.tools.helpdesk_integration.tool import create_ticket
        import inspect

        assert callable(create_ticket)
        sig = inspect.signature(create_ticket)
        params = list(sig.parameters.keys())
        assert 'subject' in params
        assert 'description' in params
        assert 'priority' in params

    @pytest.mark.unit
    def test_update_ticket_structure(self):
        """Test update_ticket function structure."""
        from packages.sygaldry_registry.components.tools.helpdesk_integration.tool import update_ticket
        import inspect

        assert callable(update_ticket)
        sig = inspect.signature(update_ticket)
        params = list(sig.parameters.keys())
        assert 'ticket_id' in params
        assert 'status' in params
        assert 'comment' in params

    @pytest.mark.unit
    def test_list_ticket_comments_structure(self):
        """Test list_ticket_comments function structure."""
        from packages.sygaldry_registry.components.tools.helpdesk_integration.tool import list_ticket_comments
        import inspect

        assert callable(list_ticket_comments)
        sig = inspect.signature(list_ticket_comments)
        params = list(sig.parameters.keys())
        assert 'ticket_id' in params
        assert 'max_results' in params

    @pytest.mark.unit
    def test_add_ticket_comment_structure(self):
        """Test add_ticket_comment function structure."""
        from packages.sygaldry_registry.components.tools.helpdesk_integration.tool import add_ticket_comment
        import inspect

        assert callable(add_ticket_comment)
        sig = inspect.signature(add_ticket_comment)
        params = list(sig.parameters.keys())
        assert 'ticket_id' in params
        assert 'body' in params
        assert 'public' in params

    @pytest.mark.unit
    def test_add_ticket_tags_structure(self):
        """Test add_ticket_tags function structure."""
        from packages.sygaldry_registry.components.tools.helpdesk_integration.tool import add_ticket_tags
        import inspect

        assert callable(add_ticket_tags)
        sig = inspect.signature(add_ticket_tags)
        params = list(sig.parameters.keys())
        assert 'ticket_id' in params
        assert 'tags' in params

    @pytest.mark.unit
    def test_ticket_model_validation(self):
        """Test Ticket model validation."""
        from packages.sygaldry_registry.components.tools.helpdesk_integration.tool import Ticket

        # Valid ticket
        ticket = Ticket(
            id=12345,
            subject="Test ticket",
            status="open",
            priority="normal",
            requester_id=67890,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
            url="https://test.zendesk.com/api/v2/tickets/12345.json"
        )
        assert ticket.id == 12345
        assert ticket.subject == "Test ticket"
        assert ticket.status == "open"
        assert ticket.priority == "normal"

    @pytest.mark.unit
    def test_comment_model_validation(self):
        """Test Comment model validation."""
        from packages.sygaldry_registry.components.tools.helpdesk_integration.tool import Comment

        # Valid comment
        comment = Comment(
            id=54321,
            body="This is a test comment",
            author_id=67890,
            created_at="2024-01-01T00:00:00Z",
            public=True
        )
        assert comment.id == 54321
        assert comment.body == "This is a test comment"
        assert comment.public is True

    @pytest.mark.unit
    def test_httpx_import_check(self):
        """Test that HTTPX_AVAILABLE flag works correctly."""
        from packages.sygaldry_registry.components.tools.helpdesk_integration.tool import HTTPX_AVAILABLE

        # Should be True if httpx is installed (which it should be for tests)
        assert isinstance(HTTPX_AVAILABLE, bool)

    @pytest.mark.unit
    def test_zendesk_config_validation(self):
        """Test Zendesk configuration validation."""
        from packages.sygaldry_registry.components.tools.helpdesk_integration.tool import _get_zendesk_config
        import os

        # Save original env vars
        orig_subdomain = os.getenv("ZENDESK_SUBDOMAIN")
        orig_email = os.getenv("ZENDESK_EMAIL")
        orig_token = os.getenv("ZENDESK_API_TOKEN")

        try:
            # Clear env vars
            for var in ["ZENDESK_SUBDOMAIN", "ZENDESK_EMAIL", "ZENDESK_API_TOKEN"]:
                if var in os.environ:
                    del os.environ[var]

            # Should raise ValueError when vars not set
            with pytest.raises(ValueError, match="ZENDESK_SUBDOMAIN"):
                _get_zendesk_config()

            # Set subdomain only
            os.environ["ZENDESK_SUBDOMAIN"] = "test"
            with pytest.raises(ValueError, match="ZENDESK_EMAIL"):
                _get_zendesk_config()

            # Set email only
            os.environ["ZENDESK_EMAIL"] = "test@example.com"
            with pytest.raises(ValueError, match="ZENDESK_API_TOKEN"):
                _get_zendesk_config()

            # Set all vars - should work
            os.environ["ZENDESK_API_TOKEN"] = "test_token"
            base_url, auth_header = _get_zendesk_config()
            assert base_url == "https://test.zendesk.com/api/v2"
            assert "Basic" in auth_header

        finally:
            # Restore original env vars
            if orig_subdomain:
                os.environ["ZENDESK_SUBDOMAIN"] = orig_subdomain
            elif "ZENDESK_SUBDOMAIN" in os.environ:
                del os.environ["ZENDESK_SUBDOMAIN"]

            if orig_email:
                os.environ["ZENDESK_EMAIL"] = orig_email
            elif "ZENDESK_EMAIL" in os.environ:
                del os.environ["ZENDESK_EMAIL"]

            if orig_token:
                os.environ["ZENDESK_API_TOKEN"] = orig_token
            elif "ZENDESK_API_TOKEN" in os.environ:
                del os.environ["ZENDESK_API_TOKEN"]

    @pytest.mark.unit
    def test_status_literal_values(self):
        """Test that status literals are properly defined."""
        from packages.sygaldry_registry.components.tools.helpdesk_integration.tool import Ticket
        import inspect

        # Check status field accepts correct values
        ticket = Ticket(
            id=1,
            subject="Test",
            status="open",
            priority="normal",
            requester_id=1,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
            url="https://test.zendesk.com/api/v2/tickets/1.json"
        )
        assert ticket.status in ["new", "open", "pending", "hold", "solved", "closed"]

    @pytest.mark.unit
    def test_priority_literal_values(self):
        """Test that priority literals are properly defined."""
        from packages.sygaldry_registry.components.tools.helpdesk_integration.tool import Ticket

        # Check priority field accepts correct values
        ticket = Ticket(
            id=1,
            subject="Test",
            status="open",
            priority="high",
            requester_id=1,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
            url="https://test.zendesk.com/api/v2/tickets/1.json"
        )
        assert ticket.priority in ["low", "normal", "high", "urgent"]
