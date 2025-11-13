"""Example: Autonomous trading with Hyperliquid agent.

This example demonstrates how to fund an agent with capital and let it
develop and execute its own trading strategy autonomously.

IMPORTANT: This example uses testnet by default. Always test thoroughly
on testnet before considering mainnet trading.
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def main():
    """Run autonomous trading example."""
    # Import after environment is loaded
    from packages.sygaldry_registry.components.agents.hyperliquid_trading_agent import (
        trade_autonomous,
        RiskParams,
        HyperliquidTradingAgent,
    )

    print("=" * 60)
    print("Hyperliquid Autonomous Trading Agent Example")
    print("=" * 60)

    # Check required environment variables
    required_vars = [
        "OPENROUTER_API_KEY",
        "HYPERLIQUID_WALLET_ADDRESS",
        "HYPERLIQUID_API_SECRET",
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"\n❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("\nPlease set the following in your .env file:")
        print("- OPENROUTER_API_KEY: Get from https://openrouter.ai/")
        print("- HYPERLIQUID_WALLET_ADDRESS: Your wallet address")
        print("- HYPERLIQUID_API_SECRET: API key from https://app.hyperliquid.xyz/API")
        return

    # Configuration
    STARTING_CAPITAL = 1000.0  # Fund agent with $1000
    MARKETS = ["BTC", "ETH", "SOL"]  # Markets to trade
    DURATION_HOURS = 24  # Run for 24 hours
    USE_TESTNET = True  # ALWAYS USE TESTNET FIRST!

    print(f"\n📊 Configuration:")
    print(f"  Starting Capital: ${STARTING_CAPITAL:.2f}")
    print(f"  Markets: {', '.join(MARKETS)}")
    print(f"  Duration: {DURATION_HOURS} hours")
    print(f"  Network: {'TESTNET' if USE_TESTNET else 'MAINNET'}")
    print(f"  Model: {os.getenv('HYPERLIQUID_MODEL_ID', 'anthropic/claude-3.5-sonnet')}")

    # Define risk parameters
    risk_params = RiskParams(
        # Position limits
        max_position_size_pct=0.2,  # Max 20% per position
        max_positions=3,  # Max 3 concurrent positions
        max_leverage=3.0,  # Max 3x leverage
        # Loss limits
        max_daily_loss_pct=0.05,  # Stop if daily loss exceeds 5%
        max_total_loss_pct=0.20,  # Stop if total loss exceeds 20%
        stop_loss_pct=0.02,  # 2% stop loss per trade
        # Trade limits
        min_trade_size_usd=10.0,  # Min $10 per trade
        max_trade_size_usd=500.0,  # Max $500 per trade
        require_approval_above_usd=100,  # Require approval for trades > $100
        # Circuit breaker
        circuit_breaker_enabled=True,
        circuit_breaker_loss_pct=0.10,  # Trip at 10% daily loss
        circuit_breaker_cooldown_hours=24,
        # Position management
        use_stop_loss=True,
        use_take_profit=True,
        trailing_stop_enabled=True,
    )

    print(f"\n🛡️  Risk Parameters:")
    print(f"  Max Position Size: {risk_params.max_position_size_pct:.0%}")
    print(f"  Max Positions: {risk_params.max_positions}")
    print(f"  Daily Loss Limit: {risk_params.max_daily_loss_pct:.0%}")
    print(f"  Stop Loss: {risk_params.stop_loss_pct:.0%}")
    print(f"  Circuit Breaker: {'Enabled' if risk_params.circuit_breaker_enabled else 'Disabled'}")

    # Example 1: Quick market analysis before trading
    print(f"\n" + "=" * 60)
    print("Step 1: Analyzing Markets")
    print("=" * 60)

    agent = HyperliquidTradingAgent(
        starting_capital=STARTING_CAPITAL,
        risk_params=risk_params,
        testnet=USE_TESTNET,
    )

    for coin in MARKETS[:2]:  # Analyze first 2 markets as example
        print(f"\n🔍 Analyzing {coin}...")
        try:
            analysis = await agent.analyze_market(coin)
            print(f"  Trend: {analysis.trend} ({analysis.trend_strength})")
            print(f"  Sentiment: {analysis.sentiment}")
            print(f"  Recommendation: {analysis.recommendation}")
            print(f"  Confidence: {analysis.confidence:.0%}")
        except Exception as e:
            print(f"  ❌ Error: {e}")

    # Example 2: Have agent develop a strategy
    print(f"\n" + "=" * 60)
    print("Step 2: Developing Autonomous Strategy")
    print("=" * 60)

    try:
        strategy = await agent.develop_strategy(
            markets=MARKETS,
            risk_tolerance="moderate",
            time_horizon="medium",
        )
        print(f"\n✅ Strategy Developed:")
        print(f"  Name: {strategy.name}")
        print(f"  Type: {strategy.type}")
        print(f"  Markets: {', '.join(strategy.markets)}")
        print(f"  Description: {strategy.description}")
        print(f"\n  Entry Rules:")
        for line in strategy.entry_rules.split("\n")[:3]:  # First 3 lines
            print(f"    {line}")
        print(f"\n  Exit Rules:")
        for line in strategy.exit_rules.split("\n")[:3]:  # First 3 lines
            print(f"    {line}")
    except Exception as e:
        print(f"❌ Error developing strategy: {e}")
        return

    # Example 3: Run autonomous trading (shortened for demo)
    print(f"\n" + "=" * 60)
    print("Step 3: Starting Autonomous Trading")
    print("=" * 60)
    print("\n⚠️  In this demo, we'll run for a shorter duration.")
    print("For production, you'd run for the full duration specified.")

    # For demo purposes, run for just a few minutes
    demo_duration = 0.1  # 6 minutes (0.1 hours)

    print(f"\n🤖 Starting autonomous trading...")
    print(f"  Duration: {demo_duration * 60:.0f} minutes (demo)")
    print(f"  Check interval: 2 minutes")
    print(f"  Press Ctrl+C to stop early\n")

    try:
        result = await trade_autonomous(
            starting_capital=STARTING_CAPITAL,
            markets=MARKETS,
            risk_params=risk_params,
            duration_hours=demo_duration,
            testnet=USE_TESTNET,
        )

        # Print results
        print(f"\n" + "=" * 60)
        print("Trading Session Complete!")
        print("=" * 60)

        print(f"\n💰 Financial Summary:")
        print(f"  Starting Capital: ${result['starting_capital']:.2f}")
        print(f"  Ending Capital: ${result['ending_capital']:.2f}")
        print(f"  Total P&L: ${result['total_pnl']:.2f}")
        print(f"  Total P&L %: {result['total_pnl_pct']:.2f}%")

        print(f"\n📊 Performance Metrics:")
        metrics = result['metrics']
        print(f"  Total Trades: {metrics['total_trades']}")
        print(f"  Winning Trades: {metrics['winning_trades']}")
        print(f"  Losing Trades: {metrics['losing_trades']}")
        print(f"  Win Rate: {metrics['win_rate']:.1f}%")

        if metrics['total_trades'] > 0:
            print(f"  Average Win: ${metrics['average_win']:.2f}")
            print(f"  Average Loss: ${metrics['average_loss']:.2f}")
            print(f"  Profit Factor: {metrics['profit_factor']:.2f}")

        print(f"\n📈 Session Info:")
        print(f"  Iterations: {result['iterations']}")

    except KeyboardInterrupt:
        print("\n\n⚠️  Trading stopped by user")

    except Exception as e:
        print(f"\n❌ Error during trading: {e}")
        import traceback

        traceback.print_exc()

    # Example 4: View trade history
    print(f"\n" + "=" * 60)
    print("Trade History")
    print("=" * 60)

    from packages.sygaldry_registry.components.agents.hyperliquid_trading_agent import StateManager

    state_manager = StateManager("hyperliquid_trading_state.db")
    trades = state_manager.get_trade_history(limit=10)

    if trades:
        print(f"\nLast {len(trades)} trades:")
        for i, trade in enumerate(trades, 1):
            print(f"\n{i}. {trade.coin} - {trade.side.upper()}")
            print(f"   Entry: ${trade.entry_price:.2f} @ {trade.entry_time.strftime('%Y-%m-%d %H:%M')}")
            if trade.exit_price:
                print(f"   Exit: ${trade.exit_price:.2f} @ {trade.exit_time.strftime('%Y-%m-%d %H:%M')}")
                print(f"   P&L: ${trade.pnl:.2f} ({trade.pnl_pct:+.2f}%)")
            else:
                print(f"   Status: OPEN")
            print(f"   Reason: {trade.entry_reason[:60]}...")
    else:
        print("\nNo trades recorded yet.")

    print(f"\n" + "=" * 60)
    print("Example Complete!")
    print("=" * 60)
    print("\n💡 Next Steps:")
    print("  1. Review the trade history and agent's decisions")
    print("  2. Adjust risk parameters based on your risk tolerance")
    print("  3. Test different strategies and markets")
    print("  4. Run longer sessions once comfortable with the agent")
    print("  5. Only move to mainnet after extensive testnet testing!")
    print("\n⚠️  Remember: Never trade with funds you can't afford to lose!")


if __name__ == "__main__":
    asyncio.run(main())
