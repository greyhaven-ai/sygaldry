"""Example: Trading with MCP-enhanced market research.

This example shows how to use the Hyperliquid trading agent with Exa MCP
integration for enhanced market research and real-time information gathering.

The agent will:
- Use Exa's MCP server for real-time web searches
- Analyze news and market sentiment before trades
- Research token projects and fundamentals
- Make more informed trading decisions

Requirements:
- OPENROUTER_API_KEY
- HYPERLIQUID_WALLET_ADDRESS
- HYPERLIQUID_API_SECRET
- EXA_API_KEY (for MCP integration)
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def main():
    """Run trading agent with MCP-enhanced research capabilities."""
    from packages.sygaldry_registry.components.agents.hyperliquid_trading_agent import (
        InteractiveHyperliquidAgent,
        RiskParams,
    )

    # Check environment
    required_vars = [
        "OPENROUTER_API_KEY",
        "HYPERLIQUID_WALLET_ADDRESS",
        "HYPERLIQUID_API_SECRET",
        "EXA_API_KEY",  # Required for MCP
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("\nRequired environment variables:")
        print("  - OPENROUTER_API_KEY: For LLM calls")
        print("  - HYPERLIQUID_WALLET_ADDRESS: Your Hyperliquid wallet")
        print("  - HYPERLIQUID_API_SECRET: Your Hyperliquid API secret")
        print("  - EXA_API_KEY: For MCP-enhanced web search (get from https://exa.ai)")
        return

    print("=" * 70)
    print("🚀 Hyperliquid Trading Agent with MCP Integration")
    print("=" * 70)
    print("\n📡 MCP Features Enabled:")
    print("  ✓ Real-time web search via Exa")
    print("  ✓ News sentiment analysis")
    print("  ✓ Token project research")
    print("  ✓ Market context gathering")
    print()

    # Initialize agent with MCP enabled
    risk_params = RiskParams(
        max_position_size_pct=0.10,  # Conservative 10% per position
        max_positions=3,
        max_daily_loss_pct=0.05,
        circuit_breaker_enabled=True,
    )

    agent = InteractiveHyperliquidAgent(
        starting_capital=1000.0,
        risk_params=risk_params,
        testnet=True,  # ALWAYS USE TESTNET FIRST!
        reflection_interval_hours=6,
        enable_mcp=True,  # Enable MCP integration
        mcp_api_key=os.getenv("EXA_API_KEY"),
    )

    print(f"✅ Agent initialized with MCP")
    print(f"   Starting Capital: $1000")
    print(f"   Network: TESTNET")
    print(f"   MCP Server: https://mcp.exa.ai/mcp")
    print()

    # Demonstrate MCP capabilities before trading
    print("🔍 Testing MCP Research Capabilities...\n")

    # 1. Get market news context
    print("1. Gathering market news and sentiment...")
    try:
        news_context = await agent.get_market_news_context(["BTC", "ETH"])
        print(f"   ✓ Found news for {len(news_context)} markets")
        for market, news_summary in news_context.items():
            print(f"   📰 {market}: {news_summary[:100]}...")
    except Exception as e:
        print(f"   ⚠️  MCP news search failed: {e}")

    print()

    # 2. Research a specific token
    print("2. Researching Bitcoin fundamentals...")
    try:
        btc_research = await agent.research_token_project("BTC")
        print(f"   ✓ Research complete: {btc_research[:150]}...")
    except Exception as e:
        print(f"   ⚠️  MCP research failed: {e}")

    print()

    # 3. Analyze market with news
    print("3. Performing enhanced market analysis for BTC...")
    try:
        analysis = await agent.analyze_market_with_news("BTC")
        print(f"   ✓ Analysis complete")
        print(f"   📊 Sentiment: {analysis.overall_sentiment}")
        print(f"   💰 Entry: ${analysis.entry_price:.2f}")
        print(f"   🎯 Target: ${analysis.target_price:.2f}")
        print(f"   🛡️  Stop Loss: ${analysis.stop_loss:.2f}")
        if analysis.news_sentiment:
            print(f"   📰 News Impact: {analysis.news_sentiment}")
    except Exception as e:
        print(f"   ⚠️  Enhanced analysis failed: {e}")

    print("\n" + "=" * 70)
    print("🤖 Starting Autonomous Trading with MCP Enhancement")
    print("=" * 70)
    print()

    # Run interactive trading with MCP-enhanced research
    try:
        result = await agent.run_interactive_trading(
            markets=["BTC", "ETH"],
            duration_hours=24,  # Run for 24 hours
            check_interval_minutes=15,  # Check every 15 minutes
        )

        print("\n" + "=" * 70)
        print("📊 Final Trading Results")
        print("=" * 70)

        print(f"\n💰 Financial Summary:")
        print(f"  Starting Capital: ${result['starting_capital']:.2f}")
        print(f"  Ending Capital: ${result['ending_capital']:.2f}")
        print(f"  Total P&L: ${result['total_pnl']:.2f} ({result['total_pnl_pct']:.2f}%)")

        print(f"\n📈 Performance Metrics:")
        metrics = result["metrics"]
        print(f"  Total Trades: {metrics['total_trades']}")
        print(f"  Win Rate: {metrics['win_rate']:.1f}%")

        print(f"\n🧠 AI Enhancement:")
        print(f"  Reflections Performed: {result['reflections_performed']}")
        print(f"  Feedback Items: {result['feedback_received']}")
        print(f"  MCP Searches: {result.get('mcp_searches_performed', 'N/A')}")

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupt received. Shutting down...")
        await agent.controller.stop_trading()
        await asyncio.sleep(1)

    print("\n✅ Session complete!")


async def mcp_research_demo():
    """Quick demo of MCP research capabilities without trading."""
    from packages.sygaldry_registry.components.agents.hyperliquid_trading_agent import ExaMCPClient

    print("=" * 70)
    print("🔬 MCP Research Demo (No Trading)")
    print("=" * 70)
    print()

    exa_key = os.getenv("EXA_API_KEY")
    if not exa_key:
        print("❌ EXA_API_KEY not set. Get one from https://exa.ai")
        return

    # Create MCP client
    async with ExaMCPClient(api_key=exa_key) as client:
        print("✅ Connected to Exa MCP server\n")

        # List available tools
        print("📋 Available MCP tools:")
        tools = await client.list_tools()
        for tool in tools[:5]:  # Show first 5
            print(f"  • {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')[:80]}...")
        print()

        # Example searches
        print("🔍 Example 1: General web search")
        results = await client.web_search("latest Bitcoin price prediction 2024", max_results=3)
        print(f"   Results: {results[:200]}...\n")

        print("🔍 Example 2: News search")
        news = await client.search_news("cryptocurrency market", max_results=3)
        print(f"   News: {news[:200]}...\n")

        print("🔍 Example 3: Company research")
        research = await client.research_company("coinbase.com")
        print(f"   Research: {research[:200]}...\n")

        print("✅ MCP research demo complete!")


async def mcp_with_terminal():
    """Run MCP-enabled agent with terminal interface."""
    from packages.sygaldry_registry.components.agents.hyperliquid_trading_agent import (
        InteractiveHyperliquidAgent,
        RiskParams,
    )
    from packages.sygaldry_registry.components.agents.hyperliquid_trading_agent.terminal_interface import (
        run_terminal_interface,
    )

    # Check environment
    required_vars = ["OPENROUTER_API_KEY", "HYPERLIQUID_WALLET_ADDRESS", "HYPERLIQUID_API_SECRET", "EXA_API_KEY"]

    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return

    print("=" * 70)
    print("🖥️  MCP-Enhanced Trading with Terminal Interface")
    print("=" * 70)
    print()

    # Initialize agent with MCP
    risk_params = RiskParams(
        max_position_size_pct=0.15,
        max_positions=2,
        max_daily_loss_pct=0.05,
        circuit_breaker_enabled=True,
    )

    agent = InteractiveHyperliquidAgent(
        starting_capital=1000.0,
        risk_params=risk_params,
        testnet=True,
        reflection_interval_hours=4,
        enable_mcp=True,  # MCP enabled!
        mcp_api_key=os.getenv("EXA_API_KEY"),
    )

    print(f"✅ Agent initialized with MCP support")
    print(f"   You can now use 'research <TOPIC>' command in terminal!")
    print()

    # Start trading in background
    trading_task = asyncio.create_task(
        agent.run_interactive_trading(
            markets=["BTC", "ETH"],
            duration_hours=24,
            check_interval_minutes=5,
        )
    )

    # Give agent a moment to start
    await asyncio.sleep(2)

    print("🖥️  Starting terminal interface...\n")

    # Run terminal interface
    try:
        terminal_task = asyncio.create_task(run_terminal_interface(agent.controller))

        # Wait for either to complete
        done, pending = await asyncio.wait([trading_task, terminal_task], return_when=asyncio.FIRST_COMPLETED)

        # Cleanup
        if terminal_task in done:
            print("\n⚠️  Terminal closed. Stopping agent...")
            await agent.controller.stop_trading()
            await asyncio.sleep(2)
            trading_task.cancel()

        if trading_task in done and not trading_task.cancelled():
            result = trading_task.result()
            print(f"\n✅ Trading complete! P&L: ${result['total_pnl']:.2f}")

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupt received. Shutting down...")
        await agent.controller.stop_trading()
        await asyncio.sleep(1)

    print("\n✅ Session complete!")


if __name__ == "__main__":
    import sys

    # Check command line arguments
    if "--research-demo" in sys.argv:
        print("Running MCP research demo (no trading)...\n")
        asyncio.run(mcp_research_demo())
    elif "--terminal" in sys.argv:
        print("Running with terminal interface...\n")
        asyncio.run(mcp_with_terminal())
    else:
        print("Running full MCP-enhanced trading...\n")
        print("Other modes:")
        print("  --research-demo : Test MCP research without trading")
        print("  --terminal      : Run with terminal interface\n")
        asyncio.run(main())
