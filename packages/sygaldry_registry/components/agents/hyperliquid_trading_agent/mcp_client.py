"""Exa MCP (Model Context Protocol) client for enhanced market research.

This client connects to Exa's MCP server to provide real-time web search,
code context, and research capabilities to the trading agent.
"""

from __future__ import annotations

import os
import asyncio
import httpx
from typing import Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class MCPTool(BaseModel):
    """An MCP tool definition."""

    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    input_schema: dict[str, Any] = Field(default_factory=dict, description="Input schema")


class MCPResponse(BaseModel):
    """Response from MCP server."""

    content: list[dict[str, Any]] = Field(..., description="Response content")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Response metadata")


class ExaMCPClient:
    """Client for interacting with Exa's MCP server.

    Provides access to Exa's specialized search tools via the Model Context Protocol.
    """

    def __init__(
        self,
        api_key: str,
        server_url: str = "https://mcp.exa.ai/mcp",
        enabled_tools: Optional[list[str]] = None,
        retry_attempts: int = 3,
        timeout: int = 30,
    ):
        """Initialize MCP client.

        Args:
            api_key: Exa API key
            server_url: MCP server URL (default: Exa's hosted server)
            enabled_tools: List of tools to enable (None = all available)
            retry_attempts: Number of retry attempts on failure
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.server_url = server_url
        self.enabled_tools = enabled_tools or [
            "web_search_exa",
            "get_code_context_exa",
            "company_research",
            "crawling",
        ]
        self.retry_attempts = retry_attempts
        self.timeout = timeout
        self._client = httpx.AsyncClient(timeout=timeout)

    @classmethod
    def from_env(cls) -> ExaMCPClient:
        """Create client from environment variables.

        Expects:
        - EXA_API_KEY: API key
        - EXA_MCP_SERVER (optional): Custom server URL

        Returns:
            Configured MCP client
        """
        api_key = os.getenv("EXA_API_KEY")
        if not api_key:
            raise ValueError("EXA_API_KEY environment variable not set")

        server_url = os.getenv("EXA_MCP_SERVER", "https://mcp.exa.ai/mcp")

        return cls(api_key=api_key, server_url=server_url)

    async def _call_mcp(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        """Call MCP server with retry logic.

        Args:
            method: MCP method to call
            params: Method parameters

        Returns:
            MCP response

        Raises:
            Exception: If all retry attempts fail
        """
        last_error = None

        for attempt in range(self.retry_attempts):
            try:
                response = await self._client.post(
                    self.server_url,
                    json={"jsonrpc": "2.0", "id": str(datetime.now().timestamp()), "method": method, "params": params},
                    headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                )

                response.raise_for_status()
                data = response.json()

                if "error" in data:
                    raise Exception(f"MCP error: {data['error']}")

                return data.get("result", {})

            except (httpx.TimeoutException, httpx.ConnectError) as e:
                last_error = e
                if attempt < self.retry_attempts - 1:
                    # Exponential backoff
                    await asyncio.sleep(2**attempt)
                continue

            except Exception as e:
                # Don't retry on other errors
                raise e

        raise last_error or Exception("MCP call failed after all retries")

    async def _call_tool(self, tool_name: str, arguments: dict[str, Any]) -> str:
        """Call an MCP tool.

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            Tool response as string
        """
        if tool_name not in self.enabled_tools:
            raise ValueError(f"Tool {tool_name} not enabled. Enabled tools: {self.enabled_tools}")

        result = await self._call_mcp("tools/call", {"name": tool_name, "arguments": arguments})

        # Extract text from content
        content = result.get("content", [])
        if content and isinstance(content, list):
            texts = [item.get("text", "") for item in content if item.get("type") == "text"]
            return "\n".join(texts)

        return str(result)

    async def list_tools(self) -> list[dict[str, Any]]:
        """List available MCP tools.

        Returns:
            List of available tools
        """
        result = await self._call_mcp("tools/list", {})
        return result.get("tools", [])

    async def web_search(self, query: str, max_results: int = 5) -> str:
        """Perform web search using MCP.

        Args:
            query: Search query
            max_results: Maximum results to return

        Returns:
            Search results as text
        """
        return await self._call_tool(
            "web_search_exa", {"query": query, "numResults": max_results, "type": "auto", "useAutoprompt": True}
        )

    async def search_news(self, topic: str, max_results: int = 5) -> str:
        """Search for news on a topic.

        Args:
            topic: News topic to search
            max_results: Maximum results

        Returns:
            News results as text
        """
        # Use category filter for news
        return await self._call_tool(
            "web_search_exa",
            {
                "query": f"{topic} news latest",
                "numResults": max_results,
                "type": "neural",
                "category": "news",
                "useAutoprompt": True,
            },
        )

    async def get_code_context(self, query: str, max_results: int = 5) -> str:
        """Get code examples and documentation.

        Args:
            query: What code/documentation to find
            max_results: Maximum results

        Returns:
            Code examples and docs as text
        """
        return await self._call_tool("get_code_context_exa", {"query": query, "numResults": max_results})

    async def research_company(self, domain_or_query: str) -> str:
        """Research a company or project.

        Args:
            domain_or_query: Company domain or search query

        Returns:
            Company research results
        """
        return await self._call_tool("company_research", {"query": domain_or_query})

    async def crawl_url(self, url: str) -> str:
        """Extract content from a specific URL.

        Args:
            url: URL to crawl

        Returns:
            Extracted content
        """
        return await self._call_tool("crawling", {"url": url})

    async def deep_research_start(self, topic: str, num_sources: int = 10) -> dict[str, Any]:
        """Start a deep research task.

        Args:
            topic: Research topic
            num_sources: Number of sources to analyze

        Returns:
            Research task info
        """
        result = await self._call_mcp(
            "tools/call", {"name": "deep_researcher_start", "arguments": {"topic": topic, "numSources": num_sources}}
        )

        return result

    async def deep_research_check(self, task_id: str) -> dict[str, Any]:
        """Check status of deep research task.

        Args:
            task_id: Research task ID

        Returns:
            Research results or status
        """
        result = await self._call_mcp("tools/call", {"name": "deep_researcher_check", "arguments": {"taskId": task_id}})

        return result

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


# Helper function for quick MCP access
async def quick_exa_search(query: str, api_key: Optional[str] = None) -> str:
    """Quick Exa web search via MCP.

    Args:
        query: Search query
        api_key: Exa API key (or from EXA_API_KEY env var)

    Returns:
        Search results
    """
    api_key = api_key or os.getenv("EXA_API_KEY")
    if not api_key:
        raise ValueError("EXA_API_KEY not provided and not in environment")

    async with ExaMCPClient(api_key=api_key) as client:
        return await client.web_search(query)
