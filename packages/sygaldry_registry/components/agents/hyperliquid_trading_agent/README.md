# Hyperliquid Trading Agent

An autonomous trading agent for Hyperliquid DEX with AI-powered strategy development, comprehensive risk management, and performance tracking.

## Overview

This agent allows you to:
- **Fund an agent** with a specific amount of capital
- **Autonomous trading**: Let the AI analyze markets and develop its own trading strategy
- **Guided trading**: Provide your own strategy and let the AI execute it with proper risk management
- **Hybrid approach**: AI optimizes and executes your base strategy

## Key Features

### 🤖 Autonomous Strategy Development
- AI analyzes multiple markets in real-time
- Develops trading strategies based on current conditions
- Adapts to market trends, volatility, and opportunities

### 📊 Comprehensive Market Analysis
- Real-time price and volume analysis
- Order book depth and liquidity assessment
- Funding rate analysis for arbitrage opportunities
- Multi-timeframe trend analysis

### 🛡️ Advanced Risk Management
- **Position Limits**: Maximum position size per trade
- **Loss Limits**: Daily and total loss thresholds
- **Circuit Breaker**: Auto-stop on excessive losses
- **Stop Losses**: Automatic stop loss on all positions
- **Position Sizing**: Risk-based position sizing
- **Leverage Control**: Maximum leverage limits

### 📈 Performance Tracking
- SQLite database for persistent state
- Trade history with entry/exit prices
- P&L tracking per trade and overall
- Performance metrics (win rate, profit factor, Sharpe ratio)
- Performance snapshots over time

### 🎯 Multiple Strategy Types
- **Trend Following**: Follow strong directional moves
- **Mean Reversion**: Trade oversold/overbought conditions
- **Funding Arbitrage**: Capture funding rate payments
- **Breakout**: Trade breakouts from consolidation
- **Momentum**: Quick momentum-based trades
- **Grid Trading**: Profit from ranging markets
- **Custom**: Define your own strategy

## Installation

```bash
# Install via Sygaldry CLI
sygaldry add hyperliquid-trading-agent

# Or install dependencies manually
pip install mirascope>=2.0.0a1 pydantic hyperliquid-python-sdk sqlalchemy
```

## Environment Setup

Create a `.env` file with:

```bash
# OpenRouter API (for AI analysis)
OPENROUTER_API_KEY=your_openrouter_key_here

# Optional: Specify model (default: anthropic/claude-3.5-sonnet)
HYPERLIQUID_MODEL_ID=anthropic/claude-3.5-sonnet

# Hyperliquid Configuration
HYPERLIQUID_WALLET_ADDRESS=0x...your_wallet_address
HYPERLIQUID_API_SECRET=your_api_secret_here

# Safety: Always start with testnet
HYPERLIQUID_USE_TESTNET=true
```

### Getting API Keys

1. **OpenRouter**: Sign up at [openrouter.ai](https://openrouter.ai/) and create an API key
2. **Hyperliquid API Wallet**: Visit [app.hyperliquid.xyz/API](https://app.hyperliquid.xyz/API) to generate a dedicated API wallet
   - This is more secure than using your main wallet's private key
   - The API wallet can trade on behalf of your main wallet

## Usage Examples

### Example 1: Autonomous Trading

Let the AI develop and execute its own strategy:

```python
import asyncio
from sygaldry_registry.agents.hyperliquid_trading_agent import (
    trade_autonomous,
    RiskParams,
)

async def main():
    # Define risk parameters
    risk_params = RiskParams(
        max_position_size_pct=0.2,      # Max 20% of capital per position
        max_daily_loss_pct=0.05,        # Stop if daily loss exceeds 5%
        stop_loss_pct=0.02,             # 2% stop loss per trade
        max_positions=3,                # Max 3 concurrent positions
        require_approval_above_usd=100, # Require approval for trades > $100
        circuit_breaker_enabled=True,   # Enable circuit breaker
    )

    # Run autonomous trading
    result = await trade_autonomous(
        starting_capital=1000.0,        # Fund agent with $1000
        markets=["BTC", "ETH", "SOL"],  # Trade these markets
        risk_params=risk_params,
        duration_hours=24,              # Run for 24 hours
        testnet=True,                   # USE TESTNET FIRST!
    )

    # Print results
    print(f"Starting Capital: ${result['starting_capital']:.2f}")
    print(f"Ending Capital: ${result['ending_capital']:.2f}")
    print(f"Total P&L: ${result['total_pnl']:.2f} ({result['total_pnl_pct']:.2f}%)")
    print(f"Total Trades: {result['metrics']['total_trades']}")
    print(f"Win Rate: {result['metrics']['win_rate']:.1f}%")

asyncio.run(main())
```

### Example 2: Guided Trading with Pre-defined Strategy

Provide your own strategy:

```python
import asyncio
from sygaldry_registry.agents.hyperliquid_trading_agent import (
    trade_with_strategy,
    get_trend_following_strategy,
    RiskParams,
)

async def main():
    # Get a pre-defined strategy
    strategy = get_trend_following_strategy(
        markets=["BTC"],
        risk_per_trade=0.02,  # Risk 2% per trade
    )

    # Or create custom strategy
    from sygaldry_registry.agents.hyperliquid_trading_agent import TradingStrategy, StrategyType

    custom_strategy = TradingStrategy(
        type=StrategyType.CUSTOM,
        name="My Scalping Strategy",
        description="Quick scalps on ETH",
        markets=["ETH"],
        entry_rules="Enter long when price dips 2% from 1h high with volume",
        exit_rules="Exit at 1% profit or 0.5% loss",
        risk_per_trade=0.01,
        max_positions=2,
        use_stop_loss=True,
        use_take_profit=True,
    )

    # Execute the strategy
    result = await trade_with_strategy(
        starting_capital=1000.0,
        strategy=custom_strategy,
        risk_params=RiskParams(max_daily_loss_pct=0.03),
        testnet=True,
    )

    print(f"Actions Taken: {len(result['actions'])}")
    for action in result['actions']:
        print(f"  {action}")

asyncio.run(main())
```

### Example 3: Market Analysis Only

Just analyze markets without trading:

```python
import asyncio
from sygaldry_registry.agents.hyperliquid_trading_agent import HyperliquidTradingAgent

async def main():
    agent = HyperliquidTradingAgent(
        starting_capital=1000.0,
        testnet=True,
    )

    # Analyze BTC market
    analysis = await agent.analyze_market("BTC")

    print(f"Coin: {analysis.coin}")
    print(f"Trend: {analysis.trend} ({analysis.trend_strength})")
    print(f"Sentiment: {analysis.sentiment}")
    print(f"Recommendation: {analysis.recommendation}")
    print(f"Confidence: {analysis.confidence:.2%}")
    print(f"\nReasoning:\n{analysis.reasoning}")
    print(f"\nKey Levels:")
    for level_name, price in analysis.key_levels.items():
        print(f"  {level_name}: ${price:.2f}")

asyncio.run(main())
```

### Example 4: Develop Strategy Without Executing

Have the AI design a strategy for you to review:

```python
import asyncio
from sygaldry_registry.agents.hyperliquid_trading_agent import HyperliquidTradingAgent

async def main():
    agent = HyperliquidTradingAgent(
        starting_capital=1000.0,
        testnet=True,
    )

    # Have AI develop a strategy
    strategy = await agent.develop_strategy(
        markets=["BTC", "ETH", "SOL"],
        risk_tolerance="moderate",
        time_horizon="medium",
    )

    print(f"Strategy Name: {strategy.name}")
    print(f"Type: {strategy.type}")
    print(f"Description: {strategy.description}")
    print(f"\nMarkets: {', '.join(strategy.markets)}")
    print(f"\nEntry Rules:\n{strategy.entry_rules}")
    print(f"\nExit Rules:\n{strategy.exit_rules}")
    print(f"\nRisk Per Trade: {strategy.risk_per_trade:.1%}")
    print(f"Max Positions: {strategy.max_positions}")

asyncio.run(main())
```

## Risk Parameters

Configure comprehensive risk controls:

```python
from sygaldry_registry.agents.hyperliquid_trading_agent import RiskParams

risk_params = RiskParams(
    # Position Limits
    max_position_size_pct=0.2,      # 20% max per position
    max_positions=3,                 # Max 3 concurrent positions
    max_leverage=5.0,                # Max 5x leverage

    # Loss Limits
    max_daily_loss_pct=0.05,        # 5% daily loss limit
    max_total_loss_pct=0.20,        # 20% total loss limit
    stop_loss_pct=0.02,             # 2% stop loss per trade

    # Trade Size Limits
    min_trade_size_usd=10.0,        # Min $10 per trade
    max_trade_size_usd=10000.0,     # Max $10,000 per trade
    require_approval_above_usd=100, # Require approval for trades > $100

    # Circuit Breaker
    circuit_breaker_enabled=True,
    circuit_breaker_loss_pct=0.10,  # Trip at 10% daily loss
    circuit_breaker_cooldown_hours=24,

    # Position Management
    use_stop_loss=True,
    use_take_profit=True,
    trailing_stop_enabled=False,
    partial_close_enabled=False,
)
```

## Strategy Types

### 1. Trend Following
Best for: Strong directional markets
```python
from sygaldry_registry.agents.hyperliquid_trading_agent import get_trend_following_strategy

strategy = get_trend_following_strategy(
    markets=["BTC", "ETH"],
    risk_per_trade=0.02,
)
```

### 2. Mean Reversion
Best for: Ranging/oscillating markets
```python
from sygaldry_registry.agents.hyperliquid_trading_agent import get_mean_reversion_strategy

strategy = get_mean_reversion_strategy(
    markets=["ETH"],
    risk_per_trade=0.015,
)
```

### 3. Funding Arbitrage
Best for: High funding rate environments
```python
from sygaldry_registry.agents.hyperliquid_trading_agent import get_funding_arbitrage_strategy

strategy = get_funding_arbitrage_strategy(
    markets=["BTC", "ETH", "SOL"],
)
```

### 4. Other Strategies
- `get_breakout_strategy()` - Trade breakouts from consolidation
- `get_momentum_strategy()` - Follow strong momentum
- `get_grid_trading_strategy()` - Profit from ranging markets

## Performance Tracking

The agent automatically saves all trades and performance metrics to a SQLite database:

```python
from sygaldry_registry.agents.hyperliquid_trading_agent import StateManager

# Access trade history
state_manager = StateManager("hyperliquid_trading_state.db")

# Get recent trades
trades = state_manager.get_trade_history(limit=50)
for trade in trades:
    print(f"{trade.coin}: {trade.side} @ ${trade.entry_price:.2f}")
    if trade.pnl:
        print(f"  P&L: ${trade.pnl:.2f} ({trade.pnl_pct:.2f}%)")

# Get performance metrics
metrics = state_manager.calculate_performance_metrics()
print(f"Total Trades: {metrics['total_trades']}")
print(f"Win Rate: {metrics['win_rate']:.1f}%")
print(f"Total P&L: ${metrics['total_pnl']:.2f}")
print(f"Profit Factor: {metrics['profit_factor']:.2f}")
```

## Safety Guidelines

### ⚠️ IMPORTANT: Start with Testnet

Always test thoroughly on testnet before using real funds:

```python
# GOOD: Testing on testnet
result = await trade_autonomous(
    starting_capital=1000.0,
    markets=["BTC"],
    testnet=True,  # ✅ Safe
)

# RISKY: Going straight to mainnet
result = await trade_autonomous(
    starting_capital=1000.0,
    markets=["BTC"],
    testnet=False,  # ⚠️ Only after extensive testnet testing!
)
```

### Best Practices

1. **Always start with testnet** - Test for days/weeks before mainnet
2. **Start small** - Use small amounts when moving to mainnet
3. **Monitor actively** - Check the agent's performance regularly
4. **Set strict limits** - Use conservative risk parameters initially
5. **Enable circuit breaker** - Protect against unexpected losses
6. **Review trades** - Understand why the agent makes each decision
7. **Gradual scaling** - Slowly increase capital as you gain confidence

### Risk Warnings

- ⚠️ Cryptocurrency trading is highly risky
- ⚠️ You can lose all your capital
- ⚠️ Past performance doesn't guarantee future results
- ⚠️ The agent's AI analysis can be wrong
- ⚠️ Smart contracts and DEXes have risks
- ⚠️ Always trade with funds you can afford to lose

## Architecture

```
hyperliquid_trading_agent/
├── agent.py              # Main agent with AI reasoning
├── strategies.py         # Strategy definitions and templates
├── risk_manager.py       # Risk management system
├── state_manager.py      # SQLite-based state persistence
└── component.json        # Component metadata

Dependencies:
├── hyperliquid_trading/  # Hyperliquid SDK integration tool
└── OpenRouter           # LLM provider for AI analysis
```

## Troubleshooting

### "Circuit breaker is active"
The agent detected excessive losses and stopped trading for safety. Wait for the cooldown period or manually reset:
```python
agent.risk_manager.reset_circuit_breaker()
```

### "Maximum positions limit reached"
The agent has reached the maximum number of concurrent positions. Close some positions or increase the limit in RiskParams.

### "Position size exceeds maximum"
Reduce the position size or increase `max_position_size_pct` in RiskParams.

## Contributing

Found a bug or have a feature request? Open an issue at:
https://github.com/greyhaven-ai/sygaldry/issues

## License

MIT License - See LICENSE file for details

## Disclaimer

This software is provided "as is" without warranty of any kind. Use at your own risk. The authors are not responsible for any losses incurred from using this agent. Always trade responsibly and within your risk tolerance.

## 🔥 New: Interactive Mode with Real-Time Communication

The agent now supports **interactive mode** with real-time communication and self-reflection capabilities!

### Interactive Features

#### 1. **Real-Time Commands**

Send commands to the agent while it's running:

```python
import asyncio
from sygaldry_registry.agents.hyperliquid_trading_agent import (
    InteractiveHyperliquidAgent,
    RiskParams,
)

async def main():
    # Initialize interactive agent
    agent = InteractiveHyperliquidAgent(
        starting_capital=1000.0,
        risk_params=RiskParams(),
        testnet=True,
        reflection_interval_hours=6,  # Self-reflect every 6 hours
    )

    # Start trading in background
    trading_task = asyncio.create_task(
        agent.run_interactive_trading(
            markets=["BTC", "ETH"],
            duration_hours=24,
        )
    )

    # Wait a bit for agent to start
    await asyncio.sleep(10)

    # Now you can send commands!
    
    # Pause trading
    await agent.controller.pause_trading()
    
    # Request market analysis
    response = await agent.controller.request_analysis("BTC")
    print(response.message)
    
    # Provide human feedback
    await agent.controller.provide_feedback(
        "I noticed you're taking too many losses on ETH. "
        "Consider reducing position size or avoiding that market."
    )
    
    # Request self-reflection
    response = await agent.controller.request_self_reflection()
    print(response.data["review"])
    
    # Adjust risk parameters on the fly
    await agent.controller.adjust_risk(
        max_position_size_pct=0.10,  # Reduce to 10%
        stop_loss_pct=0.015,  # Tighten stops
    )
    
    # Resume trading
    await agent.controller.resume_trading()
    
    # Close all positions
    await agent.controller.close_all_positions()
    
    # Change strategy
    await agent.controller.change_strategy("mean_reversion", ["BTC"])
    
    # Wait for completion
    result = await trading_task

asyncio.run(main())
```

#### 2. **Self-Reflection & Learning**

The agent periodically reviews its own performance:

```python
# Agent automatically reflects every N hours (configurable)
agent = InteractiveHyperliquidAgent(
    starting_capital=1000.0,
    reflection_interval_hours=4,  # Reflect every 4 hours
)

# You can also request reflection manually
response = await agent.controller.request_self_reflection()

# The agent will analyze:
# - What strategies worked well
# - What strategies failed
# - Mistakes it made
# - Lessons learned
# - Recommended changes
```

Example self-reflection output:

```
Self-Reflection Summary:
- Win Rate: 65.0%
- Total P&L: $125.50
- Confidence: 75%

What Worked:
  • Trend following entries during high volume periods
  • Quick exits when momentum reversed
  • Proper position sizing based on volatility

What Failed:
  • Mean reversion trades in strong trending markets
  • Holding losers too long hoping for reversal
  • Ignoring funding rate signals

Lessons Learned:
  • Market regime matters - don't fight the trend
  • Cut losses faster when thesis invalidated
  • Combine multiple signals for higher probability

Recommendations:
  • Focus on trend following in current market
  • Reduce mean reversion position sizes
  • Add funding rate filter to entry criteria
```

#### 3. **Human-in-the-Loop Feedback**

Provide continuous feedback to guide the agent:

```python
# Provide feedback about specific trades
await agent.controller.provide_feedback(
    "Great job on that BTC long! You caught the breakout perfectly. "
    "The entry timing was excellent."
)

# Strategic guidance
await agent.controller.provide_feedback(
    "The market is becoming more choppy. Consider reducing position "
    "sizes and being more selective with entries."
)

# Feedback on mistakes
await agent.controller.provide_feedback(
    "That ETH trade violated your entry rules. You entered without "
    "proper volume confirmation. Stay disciplined!"
)

# The agent incorporates this feedback into future decisions
# and self-reflection
```

#### 4. **Environment Awareness**

The agent has access to and understands its own state:

- Current capital and P&L
- Open positions and their performance
- Recent trade history
- Risk parameters and limits
- Circuit breaker status
- Recent human feedback
- Market conditions per asset

```python
# Agent can explain its current state
status = agent.controller.status

print(f"Agent is running: {status.is_running}")
print(f"Current strategy: {status.current_strategy}")
print(f"Open positions: {status.open_positions}")
print(f"Total P&L: ${status.total_pnl:.2f}")
print(f"Circuit breaker: {status.circuit_breaker_active}")
```

#### 5. **Adaptive Strategy**

The agent can adapt its strategy based on performance:

```python
# After self-reflection, agent may recommend changes
# You can approve or modify these recommendations

# Example: Agent realizes mean reversion isn't working
# and recommends switching to trend following

response = await agent.controller.request_self_reflection()
review = response.data["review"]

if review["confidence_level"] < 0.5:
    # Low confidence - consider changes
    print(f"Agent recommends: {review['recommended_changes']}")
    
    # You can accept the recommendation
    await agent.controller.change_strategy(
        "trend_following",
        markets=review["markets_to_focus"]
    )
```

### Available Commands

All commands that can be sent to the agent:

```python
from sygaldry_registry.agents.hyperliquid_trading_agent import CommandType

# Trading control
await controller.pause_trading()
await controller.resume_trading()
await controller.stop_trading()

# Position management
await controller.close_all_positions()
await controller.close_position("BTC")

# Analysis & reflection
await controller.request_analysis("BTC")
await controller.request_self_reflection()
await controller.request_performance()

# Configuration
await controller.change_strategy("trend_following", ["BTC", "ETH"])
await controller.adjust_risk(max_position_size_pct=0.15)
await controller.update_markets(["BTC", "SOL"])

# Human feedback
await controller.provide_feedback("Your feedback here")
await controller.approve_trade(trade_id="123")
await controller.reject_trade(trade_id="123", reason="Too risky")
```

### Message History

View all communication with the agent:

```python
# Get message history
history = agent.controller.get_message_history(limit=50)

for msg in history:
    print(f"[{msg['timestamp']}] {msg['sender']}: {msg['message']}")
```

Example output:
```
[14:23:15] human: Pausing trading
[14:23:15] agent: Trading paused. Send RESUME_TRADING to continue.
[14:25:30] human: Request analysis for BTC
[14:25:32] agent: BTC Analysis: Trend: bullish, Confidence: 85%
[14:30:00] human: Feedback: Good trade on that BTC long!
[14:30:01] agent: Thank you for the feedback. I'll incorporate this...
```

### Combining Interactive and Autonomous Modes

```python
async def supervised_autonomous_trading():
    """Autonomous trading with human supervision."""
    
    agent = InteractiveHyperliquidAgent(
        starting_capital=1000.0,
        risk_params=RiskParams(
            require_approval_above_usd=100,  # Require approval for large trades
        ),
        reflection_interval_hours=3,
    )
    
    # Start autonomous trading
    trading_task = asyncio.create_task(
        agent.run_interactive_trading(markets=["BTC", "ETH"])
    )
    
    # Monitor and provide guidance
    while not trading_task.done():
        await asyncio.sleep(300)  # Check every 5 minutes
        
        # Get current status
        status = agent.controller.status
        
        # If losing too much, intervene
        if status.daily_pnl < -50:
            await agent.controller.pause_trading()
            await agent.controller.provide_feedback(
                "Daily loss limit approaching. Reassess strategy."
            )
            
            # Request reflection
            await agent.controller.request_self_reflection()
            
            # Resume with reduced risk
            await agent.controller.adjust_risk(
                max_position_size_pct=0.10
            )
            await agent.controller.resume_trading()
    
    return await trading_task
```

### Benefits of Interactive Mode

1. **Real-time control**: Pause, resume, or stop trading instantly
2. **Continuous learning**: Agent learns from its mistakes and your feedback
3. **Adaptive strategy**: Changes approach based on performance
4. **Transparency**: See agent's reasoning and reflection
5. **Human oversight**: Provide guidance without micromanaging
6. **Risk management**: Intervene quickly if needed
7. **Performance insights**: Understand what works and what doesn't

This makes the agent much more powerful - it's not just autonomous, it's **collaborative**!


## 🖥️ Terminal Interface

For the easiest interaction, use the **terminal interface**:

```bash
python examples/hyperliquid_terminal_trading.py
```

This gives you an interactive command-line interface:

```
==================================================================
🤖 Hyperliquid Trading Agent - Interactive Terminal
==================================================================

Type 'help' for available commands, 'exit' to quit

agent> help

📋 Available Commands:
  Trading Control:
    pause              - Pause trading
    resume             - Resume trading
    stop               - Stop trading and exit

  Position Management:
    close all          - Close all positions
    close <COIN>       - Close specific position
    positions          - View open positions

  Analysis:
    analyze <COIN>     - Analyze a market
    reflect            - Request self-reflection
    status             - Show agent status
    performance        - Show performance metrics

  Configuration:
    risk <PARAM>=<VAL> - Adjust risk parameter
    strategy <TYPE>    - Change strategy type
    markets <COINS>    - Update markets

  Feedback:
    feedback <MSG>     - Provide feedback to agent
    approve <ID>       - Approve pending trade
    reject <ID>        - Reject pending trade

  Utility:
    history            - View message history
    clear              - Clear screen
    help               - Show this help
    exit               - Exit terminal

agent> status

📊 Agent Status:
  Running: 🟢 Yes
  Paused: ▶️  No
  Strategy: Trend Following
  Open Positions: 2
  Total P&L: $125.50
  Daily P&L: $45.20

agent> analyze BTC

🔍 Analyzing BTC...

BTC Analysis:
Trend: bullish (strong)
Recommendation: buy
Confidence: 85%

The market is showing strong bullish momentum with increasing volume...

agent> feedback Great job on that last trade! Keep it up.

💬 Sending feedback...
✓ Thank you for the feedback. I'll incorporate this into my decision making.

agent> pause

⏸️  Pausing trading...
✓ Trading paused. Send RESUME_TRADING to continue.

agent> exit

👋 Exiting terminal...
```

### Terminal vs Programmatic

**Terminal Mode** (Easiest):
```bash
# Just run the script and type commands
python examples/hyperliquid_terminal_trading.py
```

**Programmatic Mode** (More Control):
```python
# Write Python code to interact
agent = InteractiveHyperliquidAgent(...)
await agent.controller.pause_trading()
```

Both use the same underlying system, so choose what works best for you!

### Demo Mode

Try the terminal without actual trading:

```bash
python examples/hyperliquid_terminal_trading.py --demo
```

This lets you explore the terminal interface without needing API keys.

