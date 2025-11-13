"""Example: Interactive trading with real-time communication and self-reflection.

This example demonstrates:
1. Sending commands to the agent while it's running
2. Agent self-reflection and performance review
3. Human-in-the-loop feedback
4. Real-time strategy adjustments
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def main():
    """Run interactive trading example."""
    from packages.sygaldry_registry.components.agents.hyperliquid_trading_agent import (
        InteractiveHyperliquidAgent,
        RiskParams,
    )

    print("=" * 70)
    print("Hyperliquid Interactive Trading Agent")
    print("Real-time Communication & Self-Reflection")
    print("=" * 70)

    # Check required environment variables
    required_vars = [
        "OPENROUTER_API_KEY",
        "HYPERLIQUID_WALLET_ADDRESS",
        "HYPERLIQUID_API_SECRET",
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"\n❌ Missing required environment variables: {', '.join(missing_vars)}")
        return

    # Configuration
    STARTING_CAPITAL = 1000.0
    MARKETS = ["BTC", "ETH"]
    USE_TESTNET = True

    print(f"\n📊 Configuration:")
    print(f"  Starting Capital: ${STARTING_CAPITAL:.2f}")
    print(f"  Markets: {', '.join(MARKETS)}")
    print(f"  Network: {'TESTNET' if USE_TESTNET else 'MAINNET'}")

    # Initialize interactive agent
    risk_params = RiskParams(
        max_position_size_pct=0.15,
        max_positions=2,
        max_daily_loss_pct=0.05,
        stop_loss_pct=0.02,
        circuit_breaker_enabled=True,
    )

    agent = InteractiveHyperliquidAgent(
        starting_capital=STARTING_CAPITAL,
        risk_params=risk_params,
        testnet=USE_TESTNET,
        reflection_interval_hours=2,  # Reflect every 2 hours
    )

    print(f"\n✅ Agent initialized with interactive capabilities")
    print(f"   - Command queue for real-time communication")
    print(f"   - Self-reflection every 2 hours")
    print(f"   - Human feedback integration")

    # Create a task for the trading loop
    async def run_trading():
        """Run the trading loop."""
        return await agent.run_interactive_trading(
            markets=MARKETS,
            duration_hours=0.5,  # 30 minutes for demo
            check_interval_minutes=2,  # Check every 2 minutes
        )

    # Start trading in background
    trading_task = asyncio.create_task(run_trading())

    # Give it a moment to start
    await asyncio.sleep(5)

    print(f"\n" + "=" * 70)
    print("Interactive Command Examples")
    print("=" * 70)

    # Example 1: Request market analysis
    print(f"\n1️⃣  Requesting market analysis...")
    response = await agent.controller.request_analysis("BTC")
    if response:
        print(f"   Response: {response.message[:100]}...")

    await asyncio.sleep(2)

    # Example 2: Provide human feedback
    print(f"\n2️⃣  Providing human feedback...")
    response = await agent.controller.provide_feedback(
        "Focus more on trend following strategies in the current bullish market. "
        "Avoid mean reversion trades when momentum is strong."
    )
    if response:
        print(f"   Response: {response.message}")

    await asyncio.sleep(2)

    # Example 3: Request self-reflection
    print(f"\n3️⃣  Requesting self-reflection...")
    response = await agent.controller.request_self_reflection()
    if response:
        print(f"   Response:")
        print(f"{response.message[:500]}...")

    await asyncio.sleep(2)

    # Example 4: Adjust risk parameters
    print(f"\n4️⃣  Adjusting risk parameters...")
    response = await agent.controller.adjust_risk(
        max_position_size_pct=0.10,  # Reduce position size to 10%
        stop_loss_pct=0.015,  # Tighten stop loss to 1.5%
    )
    if response:
        print(f"   Response: {response.message}")

    await asyncio.sleep(2)

    # Example 5: Check agent status
    print(f"\n5️⃣  Checking agent status...")
    status = agent.controller.status
    print(f"   Running: {status.is_running}")
    print(f"   Paused: {status.is_paused}")
    print(f"   Strategy: {status.current_strategy}")
    print(f"   Open Positions: {status.open_positions}")
    print(f"   Total P&L: ${status.total_pnl:.2f}")

    await asyncio.sleep(2)

    # Example 6: Pause trading temporarily
    print(f"\n6️⃣  Pausing trading for 10 seconds...")
    response = await agent.controller.pause_trading()
    if response:
        print(f"   Response: {response.message}")

    await asyncio.sleep(10)

    # Example 7: Resume trading
    print(f"\n7️⃣  Resuming trading...")
    response = await agent.controller.resume_trading()
    if response:
        print(f"   Response: {response.message}")

    # Example 8: View message history
    print(f"\n8️⃣  Viewing message history...")
    history = agent.controller.get_message_history(limit=10)
    print(f"   Last {min(len(history), 5)} messages:")
    for msg in history[-5:]:
        sender = msg["sender"].rjust(8)
        timestamp = msg["timestamp"].split("T")[1][:8]
        print(f"   [{timestamp}] {sender}: {msg['message'][:60]}")

    # Let it run a bit more
    print(f"\n⏳ Letting agent trade for a few more minutes...")
    print(f"   (You could continue sending commands...)")

    # Wait for trading to complete
    result = await trading_task

    # Print final results
    print(f"\n" + "=" * 70)
    print("Trading Session Complete!")
    print("=" * 70)

    print(f"\n💰 Financial Summary:")
    print(f"  Starting Capital: ${result['starting_capital']:.2f}")
    print(f"  Ending Capital: ${result['ending_capital']:.2f}")
    print(f"  Total P&L: ${result['total_pnl']:.2f} ({result['total_pnl_pct']:.2f}%)")

    print(f"\n📊 Performance Metrics:")
    metrics = result["metrics"]
    print(f"  Total Trades: {metrics['total_trades']}")
    print(f"  Win Rate: {metrics['win_rate']:.1f}%")

    print(f"\n🧠 Self-Reflection:")
    print(f"  Reflections Performed: {result['reflections_performed']}")
    print(f"  Human Feedback Received: {result['feedback_received']}")

    print(f"\n📈 Session Info:")
    print(f"  Iterations: {result['iterations']}")

    # Show self-reflection history
    if agent.reflection_engine.reflection_history:
        print(f"\n🔍 Last Self-Reflection:")
        last_reflection = agent.reflection_engine.reflection_history[-1]
        print(f"  Confidence: {last_reflection.confidence_level:.0%}")
        print(f"  Lessons Learned: {len(last_reflection.lessons_learned)}")

        if last_reflection.what_worked:
            print(f"\n  ✅ What Worked:")
            for item in last_reflection.what_worked[:3]:
                print(f"     • {item}")

        if last_reflection.recommended_changes:
            print(f"\n  💡 Recommendations:")
            for item in last_reflection.recommended_changes[:3]:
                print(f"     • {item}")

    print(f"\n" + "=" * 70)
    print("Interactive Features Demonstrated:")
    print("=" * 70)
    print("""
    ✓ Real-time market analysis requests
    ✓ Human feedback integration
    ✓ Agent self-reflection and performance review
    ✓ Dynamic risk parameter adjustments
    ✓ Pause/resume trading control
    ✓ Message history tracking
    ✓ Strategy adaptation recommendations

    The agent can:
    - Receive commands while trading
    - Reflect on its own performance
    - Incorporate human feedback
    - Adapt strategy based on results
    - Explain its reasoning
    """)


async def example_concurrent_interaction():
    """Example of interacting with agent while it runs in background."""
    from packages.sygaldry_registry.components.agents.hyperliquid_trading_agent import (
        run_interactive_trading,
        RiskParams,
    )

    print("\n" + "=" * 70)
    print("Concurrent Interaction Example")
    print("=" * 70)

    # Start trading (this runs in background)
    trading_task = asyncio.create_task(
        run_interactive_trading(
            starting_capital=1000.0, markets=["BTC"], risk_params=RiskParams(), duration_hours=1, testnet=True
        )
    )

    # The function returns immediately with the controller
    # You can then interact with the agent via the controller

    # For this example, just wait for completion
    result, controller = await trading_task

    print(f"Trading completed with P&L: ${result['total_pnl']:.2f}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
