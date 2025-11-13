"""Example: Trading with terminal-based interaction.

This example shows how to run the agent and interact with it through
a command-line terminal interface.

Run this script and you'll get an interactive prompt where you can:
- Pause/resume trading
- Request analysis
- Provide feedback
- Adjust risk parameters
- And more!
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def main():
    """Run trading agent with terminal interface."""
    from packages.sygaldry_registry.components.agents.hyperliquid_trading_agent import (
        InteractiveHyperliquidAgent,
        RiskParams,
    )
    from packages.sygaldry_registry.components.agents.hyperliquid_trading_agent.terminal_interface import (
        run_terminal_interface,
    )

    # Check environment
    required_vars = [
        "OPENROUTER_API_KEY",
        "HYPERLIQUID_WALLET_ADDRESS",
        "HYPERLIQUID_API_SECRET",
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return

    print("=" * 70)
    print("🚀 Starting Hyperliquid Trading Agent with Terminal Interface")
    print("=" * 70)

    # Initialize agent
    risk_params = RiskParams(
        max_position_size_pct=0.15,
        max_positions=2,
        max_daily_loss_pct=0.05,
        circuit_breaker_enabled=True,
    )

    agent = InteractiveHyperliquidAgent(
        starting_capital=1000.0,
        risk_params=risk_params,
        testnet=True,  # ALWAYS USE TESTNET FIRST!
        reflection_interval_hours=4,
    )

    print(f"\n✅ Agent initialized")
    print(f"   Starting Capital: $1000")
    print(f"   Markets: BTC, ETH")
    print(f"   Network: TESTNET")

    # Start trading in background
    print(f"\n🤖 Starting autonomous trading...")
    trading_task = asyncio.create_task(
        agent.run_interactive_trading(
            markets=["BTC", "ETH"],
            duration_hours=24,  # Run for 24 hours
            check_interval_minutes=5,  # Check every 5 minutes
        )
    )

    # Give agent a moment to start
    await asyncio.sleep(2)

    print(f"✓ Agent is now trading")
    print(f"\n🖥️  Starting terminal interface...")
    print(f"   You can now send commands to the agent!")

    # Run terminal interface
    try:
        terminal_task = asyncio.create_task(run_terminal_interface(agent.controller))

        # Wait for either trading or terminal to complete
        done, pending = await asyncio.wait([trading_task, terminal_task], return_when=asyncio.FIRST_COMPLETED)

        # If terminal exited first, stop trading
        if terminal_task in done:
            print("\n⚠️  Terminal closed. Stopping agent...")
            await agent.controller.stop_trading()
            # Wait a bit for graceful shutdown
            await asyncio.sleep(2)
            trading_task.cancel()

        # If trading completed first, close terminal
        if trading_task in done:
            print("\n⚠️  Trading session completed. Closing terminal...")
            terminal_task.cancel()

        # Get result
        if trading_task.done() and not trading_task.cancelled():
            result = trading_task.result()

            print("\n" + "=" * 70)
            print("📊 Final Results")
            print("=" * 70)

            print(f"\n💰 Financial Summary:")
            print(f"  Starting Capital: ${result['starting_capital']:.2f}")
            print(f"  Ending Capital: ${result['ending_capital']:.2f}")
            print(f"  Total P&L: ${result['total_pnl']:.2f} ({result['total_pnl_pct']:.2f}%)")

            print(f"\n📈 Performance:")
            metrics = result["metrics"]
            print(f"  Total Trades: {metrics['total_trades']}")
            print(f"  Win Rate: {metrics['win_rate']:.1f}%")

            print(f"\n🧠 Learning:")
            print(f"  Reflections: {result['reflections_performed']}")
            print(f"  Feedback Received: {result['feedback_received']}")

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupt received. Shutting down...")
        await agent.controller.stop_trading()
        await asyncio.sleep(1)

    print("\n✅ Session complete!")


async def quick_demo():
    """Quick demo showing terminal interaction without actually trading."""
    from packages.sygaldry_registry.components.agents.hyperliquid_trading_agent import InteractiveHyperliquidAgent
    from packages.sygaldry_registry.components.agents.hyperliquid_trading_agent.terminal_interface import TerminalInterface

    print("=" * 70)
    print("🎮 Terminal Interface Demo (No Trading)")
    print("=" * 70)
    print("\nThis is a demo of the terminal interface.")
    print("Commands you can use:")
    print("  - help      : Show all commands")
    print("  - status    : Show agent status")
    print("  - pause     : Pause trading")
    print("  - analyze BTC : Analyze BTC market")
    print("  - feedback <msg> : Provide feedback")
    print("  - exit      : Exit terminal")
    print()

    # Create a mock agent (not actually trading)
    agent = InteractiveHyperliquidAgent(starting_capital=1000.0, testnet=True)

    # Update status for demo
    agent.controller.status.is_running = True
    agent.controller.status.current_strategy = "Trend Following"
    agent.controller.status.open_positions = 2
    agent.controller.status.total_pnl = 45.50

    # Run terminal
    terminal = TerminalInterface(agent.controller)
    await terminal.run()


if __name__ == "__main__":
    import sys

    # Check if user wants demo mode
    if "--demo" in sys.argv:
        print("Running in DEMO mode (no actual trading)\n")
        asyncio.run(quick_demo())
    else:
        print("Running in LIVE mode (requires API keys)\n")
        print("Tip: Run with --demo flag for a demo without trading\n")
        asyncio.run(main())
