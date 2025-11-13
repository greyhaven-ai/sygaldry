"""Tests for Exa MCP integration with Hyperliquid trading agent.

These tests follow TDD - written before implementation to define the expected behavior.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime


class TestExaMCPClient:
    """Tests for Exa MCP client wrapper."""

    def test_mcp_client_initialization(self):
        """Test that MCP client can be initialized with API key."""
        from packages.sygaldry_registry.components.agents.hyperliquid_trading_agent.mcp_client import ExaMCPClient

        client = ExaMCPClient(api_key="test_key")

        assert client.api_key == "test_key"
        assert client.server_url == "https://mcp.exa.ai/mcp"
        assert client.enabled_tools is not None

    def test_mcp_client_custom_server(self):
        """Test initialization with custom server URL."""
        from packages.sygaldry_registry.components.agents.hyperliquid_trading_agent.mcp_client import ExaMCPClient

        client = ExaMCPClient(api_key="test_key", server_url="http://localhost:3000")

        assert client.server_url == "http://localhost:3000"

    @pytest.mark.asyncio
    async def test_list_available_tools(self):
        """Test listing available MCP tools."""
        from packages.sygaldry_registry.components.agents.hyperliquid_trading_agent.mcp_client import ExaMCPClient

        client = ExaMCPClient(api_key="test_key")

        # Mock the MCP server response
        with patch.object(client, "_call_mcp") as mock_call:
            mock_call.return_value = {
                "tools": [
                    {"name": "web_search_exa", "description": "Web search"},
                    {"name": "get_code_context_exa", "description": "Code search"},
                ]
            }

            tools = await client.list_tools()

            assert len(tools) >= 2
            assert any(t["name"] == "web_search_exa" for t in tools)
            assert any(t["name"] == "get_code_context_exa" for t in tools)

    @pytest.mark.asyncio
    async def test_web_search_exa(self):
        """Test web search via MCP."""
        from packages.sygaldry_registry.components.agents.hyperliquid_trading_agent.mcp_client import ExaMCPClient

        client = ExaMCPClient(api_key="test_key")

        # Mock response
        with patch.object(client, "_call_mcp") as mock_call:
            mock_call.return_value = {
                "content": [
                    {
                        "type": "text",
                        "text": "Found 3 results for Bitcoin news:\n1. BTC hits new high\n2. Institutional adoption\n3. Network upgrade",
                    }
                ]
            }

            result = await client.web_search("Latest Bitcoin news")

            assert result is not None
            assert "Bitcoin" in result or "BTC" in result
            mock_call.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_code_context(self):
        """Test code context retrieval via MCP."""
        from packages.sygaldry_registry.components.agents.hyperliquid_trading_agent.mcp_client import ExaMCPClient

        client = ExaMCPClient(api_key="test_key")

        with patch.object(client, "_call_mcp") as mock_call:
            mock_call.return_value = {
                "content": [{"type": "text", "text": "Example: async def trade():\n    await execute_order()"}]
            }

            result = await client.get_code_context("python async trading examples")

            assert result is not None
            assert "async" in result or "await" in result


class TestAgentMCPIntegration:
    """Tests for Hyperliquid agent using MCP for market research."""

    @pytest.mark.asyncio
    async def test_agent_with_mcp_enabled(self):
        """Test agent initialization with MCP enabled."""
        from packages.sygaldry_registry.components.agents.hyperliquid_trading_agent import InteractiveHyperliquidAgent

        agent = InteractiveHyperliquidAgent(
            starting_capital=1000.0, testnet=True, enable_mcp=True, mcp_api_key="test_key"
        )

        assert agent.mcp_enabled is True
        assert agent.mcp_client is not None

    @pytest.mark.asyncio
    async def test_agent_without_mcp(self):
        """Test agent works without MCP."""
        from packages.sygaldry_registry.components.agents.hyperliquid_trading_agent import InteractiveHyperliquidAgent

        agent = InteractiveHyperliquidAgent(starting_capital=1000.0, testnet=True, enable_mcp=False)

        assert agent.mcp_enabled is False
        assert agent.mcp_client is None

    @pytest.mark.asyncio
    async def test_market_analysis_with_news_research(self):
        """Test market analysis enhanced with MCP news research."""
        from packages.sygaldry_registry.components.agents.hyperliquid_trading_agent import InteractiveHyperliquidAgent

        agent = InteractiveHyperliquidAgent(
            starting_capital=1000.0, testnet=True, enable_mcp=True, mcp_api_key="test_key"
        )

        # Mock MCP news search
        mock_news = "Bitcoin surges on ETF approval news. Institutional demand increasing."

        with patch.object(agent.mcp_client, "web_search", return_value=mock_news):
            # This should include news research in analysis
            analysis = await agent.analyze_market_with_news("BTC")

            assert analysis is not None
            # Analysis should reference the news
            assert "news" in analysis.reasoning.lower() or "etf" in analysis.reasoning.lower()

    @pytest.mark.asyncio
    async def test_company_research_for_token(self):
        """Test company research for token projects."""
        from packages.sygaldry_registry.components.agents.hyperliquid_trading_agent import InteractiveHyperliquidAgent

        agent = InteractiveHyperliquidAgent(
            starting_capital=1000.0, testnet=True, enable_mcp=True, mcp_api_key="test_key"
        )

        with patch.object(agent.mcp_client, "company_research") as mock_research:
            mock_research.return_value = "Solana: High-performance blockchain with 65k TPS..."

            research = await agent.research_token_project("SOL")

            assert research is not None
            mock_research.assert_called_once()

    @pytest.mark.asyncio
    async def test_self_reflection_includes_news_context(self):
        """Test that self-reflection can include recent news context."""
        from packages.sygaldry_registry.components.agents.hyperliquid_trading_agent import InteractiveHyperliquidAgent

        agent = InteractiveHyperliquidAgent(
            starting_capital=1000.0, testnet=True, enable_mcp=True, mcp_api_key="test_key"
        )

        # Mock news about market conditions
        with patch.object(agent.mcp_client, "web_search") as mock_search:
            mock_search.return_value = "Crypto market in consolidation phase. Low volatility expected."

            # Reflection should be able to access market news
            # Implementation will determine exact API
            news_context = await agent.get_market_news_context(["BTC", "ETH"])

            assert news_context is not None
            mock_search.assert_called()


class TestMCPToolSelection:
    """Tests for intelligent MCP tool selection."""

    @pytest.mark.asyncio
    async def test_use_web_search_for_news(self):
        """Test that web_search_exa is used for news queries."""
        from packages.sygaldry_registry.components.agents.hyperliquid_trading_agent.mcp_client import ExaMCPClient

        client = ExaMCPClient(api_key="test_key")

        with patch.object(client, "_call_tool") as mock_call:
            mock_call.return_value = "News results..."

            await client.search_news("Bitcoin")

            # Should call web_search_exa tool
            call_args = mock_call.call_args
            assert call_args[0][0] == "web_search_exa"

    @pytest.mark.asyncio
    async def test_use_company_research_for_projects(self):
        """Test that company_research is used for project research."""
        from packages.sygaldry_registry.components.agents.hyperliquid_trading_agent.mcp_client import ExaMCPClient

        client = ExaMCPClient(api_key="test_key")

        with patch.object(client, "_call_tool") as mock_call:
            mock_call.return_value = "Company info..."

            await client.research_company("ethereum.org")

            call_args = mock_call.call_args
            assert call_args[0][0] == "company_research"


class TestMCPErrorHandling:
    """Tests for MCP error handling and fallbacks."""

    @pytest.mark.asyncio
    async def test_graceful_fallback_when_mcp_unavailable(self):
        """Test agent works when MCP is unavailable."""
        from packages.sygaldry_registry.components.agents.hyperliquid_trading_agent import InteractiveHyperliquidAgent

        agent = InteractiveHyperliquidAgent(
            starting_capital=1000.0, testnet=True, enable_mcp=True, mcp_api_key="test_key"
        )

        # Simulate MCP server down
        with patch.object(agent.mcp_client, "web_search", side_effect=Exception("MCP unavailable")):
            # Should still work, just without news
            analysis = await agent.analyze_market("BTC")

            assert analysis is not None
            # Should have base analysis even without news

    @pytest.mark.asyncio
    async def test_retry_on_mcp_timeout(self):
        """Test retry logic for MCP timeouts."""
        from packages.sygaldry_registry.components.agents.hyperliquid_trading_agent.mcp_client import ExaMCPClient

        client = ExaMCPClient(api_key="test_key", retry_attempts=3)

        with patch.object(client, "_call_mcp") as mock_call:
            # Fail twice, succeed on third
            mock_call.side_effect = [
                TimeoutError("Timeout"),
                TimeoutError("Timeout"),
                {"content": [{"type": "text", "text": "Success"}]},
            ]

            result = await client.web_search("test query")

            assert result == "Success"
            assert mock_call.call_count == 3


class TestMCPConfiguration:
    """Tests for MCP configuration options."""

    def test_configure_enabled_tools(self):
        """Test configuring which MCP tools are enabled."""
        from packages.sygaldry_registry.components.agents.hyperliquid_trading_agent.mcp_client import ExaMCPClient

        client = ExaMCPClient(api_key="test_key", enabled_tools=["web_search_exa", "company_research"])

        assert "web_search_exa" in client.enabled_tools
        assert "company_research" in client.enabled_tools
        assert "linkedin_search" not in client.enabled_tools

    def test_mcp_from_environment(self):
        """Test loading MCP config from environment."""
        import os

        from packages.sygaldry_registry.components.agents.hyperliquid_trading_agent.mcp_client import ExaMCPClient

        with patch.dict(os.environ, {"EXA_API_KEY": "env_test_key", "EXA_MCP_SERVER": "http://custom:3000"}):
            client = ExaMCPClient.from_env()

            assert client.api_key == "env_test_key"
            assert client.server_url == "http://custom:3000"


@pytest.mark.integration
class TestMCPLiveIntegration:
    """Integration tests requiring actual MCP server (skipped by default)."""

    @pytest.mark.skip(reason="Requires Exa API key and live MCP server")
    @pytest.mark.asyncio
    async def test_live_mcp_web_search(self):
        """Test actual MCP web search."""
        import os

        from packages.sygaldry_registry.components.agents.hyperliquid_trading_agent.mcp_client import ExaMCPClient

        api_key = os.getenv("EXA_API_KEY")
        if not api_key:
            pytest.skip("EXA_API_KEY not set")

        client = ExaMCPClient(api_key=api_key)
        result = await client.web_search("Latest Bitcoin price")

        assert result is not None
        assert len(result) > 0

    @pytest.mark.skip(reason="Requires Exa API key and live trading environment")
    @pytest.mark.asyncio
    async def test_live_agent_with_mcp(self):
        """Test agent with live MCP integration."""
        import os

        from packages.sygaldry_registry.components.agents.hyperliquid_trading_agent import InteractiveHyperliquidAgent

        api_key = os.getenv("EXA_API_KEY")
        if not api_key:
            pytest.skip("EXA_API_KEY not set")

        agent = InteractiveHyperliquidAgent(
            starting_capital=1000.0, testnet=True, enable_mcp=True, mcp_api_key=api_key
        )

        analysis = await agent.analyze_market_with_news("BTC")

        assert analysis is not None
        assert analysis.coin == "BTC"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
