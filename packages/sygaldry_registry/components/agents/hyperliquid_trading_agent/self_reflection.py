"""Self-reflection capabilities for the trading agent.

This module enables the agent to review its own performance, learn from mistakes,
and adapt its strategy based on results.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Any, Optional
from mirascope import llm
from pydantic import BaseModel, Field

from .state_manager import StateManager
from .strategies import TradingStrategy


class PerformanceReview(BaseModel):
    """Agent's review of its own performance."""

    review_period: str = Field(..., description="Time period reviewed")
    total_trades: int = Field(..., description="Number of trades in period")
    win_rate: float = Field(..., description="Win rate percentage")
    total_pnl: float = Field(..., description="Total P&L")
    profit_factor: float = Field(..., description="Profit factor")

    # Self-assessment
    what_worked: list[str] = Field(..., description="Strategies and decisions that worked well")
    what_failed: list[str] = Field(..., description="Strategies and decisions that failed")
    mistakes_identified: list[str] = Field(..., description="Specific mistakes made")
    lessons_learned: list[str] = Field(..., description="Lessons learned from experience")

    # Recommendations
    recommended_changes: list[str] = Field(..., description="Recommended strategy adjustments")
    markets_to_avoid: list[str] = Field(default_factory=list, description="Markets showing poor performance")
    markets_to_focus: list[str] = Field(default_factory=list, description="Markets showing strong performance")
    confidence_level: float = Field(..., description="Confidence in current approach (0-1)")

    # Forward looking
    next_steps: list[str] = Field(..., description="Specific next actions to take")
    risk_adjustments: dict[str, Any] = Field(default_factory=dict, description="Suggested risk parameter changes")


class StrategyAdaptation(BaseModel):
    """Adapted strategy based on performance review."""

    should_change_strategy: bool = Field(..., description="Whether to change strategy")
    reason: str = Field(..., description="Reason for change or staying")
    new_strategy_type: Optional[str] = Field(None, description="New strategy type if changing")
    parameter_adjustments: dict[str, Any] = Field(default_factory=dict, description="Strategy parameter adjustments")
    market_adjustments: dict[str, list[str]] = Field(
        default_factory=dict, description="Markets to add/remove"
    )  # {"add": [], "remove": []}


class EnvironmentContext(BaseModel):
    """Agent's understanding of its own environment and state."""

    current_capital: float = Field(..., description="Current capital")
    starting_capital: float = Field(..., description="Starting capital")
    total_pnl_pct: float = Field(..., description="Total P&L percentage")
    days_running: int = Field(..., description="Days agent has been running")

    open_positions: list[dict[str, Any]] = Field(default_factory=list, description="Current open positions")
    recent_trades: list[dict[str, Any]] = Field(default_factory=list, description="Recent trade history")

    risk_state: dict[str, Any] = Field(default_factory=dict, description="Current risk parameters and state")
    circuit_breaker_active: bool = Field(False, description="Circuit breaker status")

    market_conditions: dict[str, str] = Field(
        default_factory=dict, description="Current market conditions per asset"
    )  # {"BTC": "bullish", "ETH": "ranging"}

    recent_feedback: list[str] = Field(default_factory=list, description="Recent human feedback received")


@llm.call(
    provider="openrouter",
    model_id=os.getenv("HYPERLIQUID_MODEL_ID", "anthropic/claude-3.5-sonnet"),
    format=PerformanceReview,
)
async def perform_self_reflection(
    environment_context: dict[str, Any],
    trade_history: list[dict[str, Any]],
    current_strategy: dict[str, Any],
) -> str:
    """Agent performs self-reflection on its own performance.

    Args:
        environment_context: Agent's current environment state
        trade_history: Recent trade history
        current_strategy: Current strategy being used

    Returns:
        Self-reflection and performance review
    """
    # Format trade history
    trades_str = "\n".join(
        [
            f"  - {t.get('coin')} {t.get('side')}: Entry ${t.get('entry_price', 0):.2f} → Exit ${t.get('exit_price', 0):.2f} = P&L: ${t.get('pnl', 0):.2f} ({t.get('pnl_pct', 0):.2f}%)"
            for t in trade_history[-20:]
        ]
    )

    # Format positions
    positions_str = "\n".join(
        [
            f"  - {p.get('coin')} {p.get('side')}: Size {p.get('size')} @ ${p.get('entry_price', 0):.2f}, Unrealized P&L: ${p.get('unrealized_pnl', 0):.2f}"
            for p in environment_context.get("open_positions", [])
        ]
    )

    feedback_str = "\n".join([f"  - {fb}" for fb in environment_context.get("recent_feedback", [])])

    return f"""You are a self-aware trading agent analyzing your own performance and learning from your experiences.

## Your Current State

**Capital:**
- Starting: ${environment_context.get('starting_capital', 0):.2f}
- Current: ${environment_context.get('current_capital', 0):.2f}
- Total P&L: {environment_context.get('total_pnl_pct', 0):.2f}%

**Running Time:** {environment_context.get('days_running', 0)} days

**Current Strategy:**
- Type: {current_strategy.get('type')}
- Name: {current_strategy.get('name')}
- Markets: {', '.join(current_strategy.get('markets', []))}
- Entry Rules: {current_strategy.get('entry_rules', 'N/A')}
- Exit Rules: {current_strategy.get('exit_rules', 'N/A')}

**Open Positions ({len(environment_context.get('open_positions', []))}):**
{positions_str if positions_str else '  None'}

**Recent Trades (last 20):**
{trades_str if trades_str else '  No trades yet'}

**Recent Human Feedback:**
{feedback_str if feedback_str else '  No feedback yet'}

**Market Conditions:**
{', '.join([f"{k}: {v}" for k, v in environment_context.get('market_conditions', {}).items()])}

## Self-Reflection Task

Analyze your own performance deeply and honestly:

1. **What Worked Well:**
   - Which trades were your best decisions? Why?
   - What patterns led to success?
   - Which market conditions suited your strategy?

2. **What Failed:**
   - Which trades were mistakes? Why did you take them?
   - What patterns led to losses?
   - When did your strategy fail?

3. **Mistakes Identified:**
   - Did you violate your own entry/exit rules?
   - Did you overtrade or undertrade?
   - Were your position sizes appropriate?
   - Did you let emotions (if you had them) influence decisions?

4. **Lessons Learned:**
   - What have you learned from wins and losses?
   - How should you adapt to current market conditions?
   - What would you do differently?

5. **Recommendations:**
   - Should you change your strategy? If so, to what?
   - Which markets should you focus on or avoid?
   - Should risk parameters be adjusted?
   - What specific changes would improve performance?

6. **Next Steps:**
   - What are your immediate next actions?
   - How will you improve going forward?

7. **Risk Adjustments:**
   - Should position sizes change?
   - Should stop losses be tighter or wider?
   - Any other risk parameter changes?

Be honest, specific, and actionable. Think like a professional trader reviewing their own trading journal.

Provide your confidence level (0-1) in your current approach."""


@llm.call(
    provider="openrouter",
    model_id=os.getenv("HYPERLIQUID_MODEL_ID", "anthropic/claude-3.5-sonnet"),
    format=StrategyAdaptation,
)
async def determine_strategy_adaptation(
    performance_review: dict[str, Any],
    current_strategy: dict[str, Any],
    environment_context: dict[str, Any],
) -> str:
    """Determine if and how to adapt strategy based on performance review.

    Args:
        performance_review: Self-reflection results
        current_strategy: Current strategy configuration
        environment_context: Current environment state

    Returns:
        Strategy adaptation recommendations
    """
    return f"""You are a self-improving trading agent deciding whether to adapt your strategy based on performance.

## Performance Review Summary

**Period:** {performance_review.get('review_period')}
**Trades:** {performance_review.get('total_trades')}
**Win Rate:** {performance_review.get('win_rate', 0):.1f}%
**Total P&L:** ${performance_review.get('total_pnl', 0):.2f}
**Profit Factor:** {performance_review.get('profit_factor', 0):.2f}
**Confidence Level:** {performance_review.get('confidence_level', 0):.0%}

**What Worked:**
{chr(10).join([f"  - {item}" for item in performance_review.get('what_worked', [])])}

**What Failed:**
{chr(10).join([f"  - {item}" for item in performance_review.get('what_failed', [])])}

**Mistakes:**
{chr(10).join([f"  - {item}" for item in performance_review.get('mistakes_identified', [])])}

**Lessons Learned:**
{chr(10).join([f"  - {item}" for item in performance_review.get('lessons_learned', [])])}

**Recommendations:**
{chr(10).join([f"  - {item}" for item in performance_review.get('recommended_changes', [])])}

## Current Strategy

- Type: {current_strategy.get('type')}
- Markets: {', '.join(current_strategy.get('markets', []))}
- Risk Per Trade: {current_strategy.get('risk_per_trade', 0):.1%}

## Current State

- Total P&L: {environment_context.get('total_pnl_pct', 0):.2f}%
- Circuit Breaker: {'ACTIVE' if environment_context.get('circuit_breaker_active') else 'Inactive'}

## Decision Task

Based on the performance review, decide:

1. **Should you change your core strategy?**
   - If performance is poor (low win rate, negative P&L, low confidence)
   - If market conditions have fundamentally changed
   - If strategy shows consistent pattern of losses

2. **What parameter adjustments should you make?**
   - Risk per trade
   - Position sizing
   - Entry/exit rules
   - Stop loss distances
   - Take profit targets

3. **Which markets should you adjust?**
   - Add markets that showed strength
   - Remove markets where you consistently lost
   - Focus on markets that match your strategy

4. **Provide specific reasoning:**
   - Why change or why stay?
   - What evidence supports this decision?
   - What are the expected outcomes?

**Decision Guidelines:**
- Don't change strategy after just a few trades (need enough data)
- Do adapt when clear patterns emerge
- Small adjustments are often better than complete overhauls
- Consider if failures were strategy issues or execution issues
- Balance adaptation with consistency

Make your decision and be specific about what should change."""


class SelfReflectionEngine:
    """Engine for agent self-reflection and adaptation."""

    def __init__(self, state_manager: StateManager, starting_capital: float):
        """Initialize self-reflection engine.

        Args:
            state_manager: State manager for accessing history
            starting_capital: Starting capital amount
        """
        self.state_manager = state_manager
        self.starting_capital = starting_capital
        self.last_reflection_time: Optional[datetime] = None
        self.reflection_history: list[PerformanceReview] = []

    def _build_environment_context(
        self,
        current_capital: float,
        open_positions: list[dict],
        risk_state: dict,
        circuit_breaker_active: bool,
        recent_feedback: list[str],
    ) -> EnvironmentContext:
        """Build environment context for self-reflection.

        Args:
            current_capital: Current capital
            open_positions: Open positions
            risk_state: Risk parameters
            circuit_breaker_active: Circuit breaker status
            recent_feedback: Recent human feedback

        Returns:
            Environment context
        """
        # Get trade history
        trades = self.state_manager.get_trade_history(limit=100)
        recent_trades = [
            {
                "coin": t.coin,
                "side": t.side,
                "entry_price": t.entry_price,
                "exit_price": t.exit_price,
                "pnl": t.pnl,
                "pnl_pct": t.pnl_pct,
                "entry_reason": t.entry_reason,
                "exit_reason": t.exit_reason,
            }
            for t in trades[:20]
        ]

        # Calculate days running
        if trades:
            first_trade_time = trades[-1].entry_time
            days_running = (datetime.now() - first_trade_time).days
        else:
            days_running = 0

        return EnvironmentContext(
            current_capital=current_capital,
            starting_capital=self.starting_capital,
            total_pnl_pct=((current_capital - self.starting_capital) / self.starting_capital * 100),
            days_running=max(days_running, 1),
            open_positions=open_positions,
            recent_trades=recent_trades,
            risk_state=risk_state,
            circuit_breaker_active=circuit_breaker_active,
            recent_feedback=recent_feedback[-10:],  # Last 10 feedback items
        )

    async def perform_reflection(
        self,
        current_capital: float,
        open_positions: list[dict],
        current_strategy: TradingStrategy,
        risk_state: dict,
        circuit_breaker_active: bool = False,
        recent_feedback: list[str] = None,
    ) -> PerformanceReview:
        """Perform self-reflection on performance.

        Args:
            current_capital: Current capital
            open_positions: Current open positions
            current_strategy: Current trading strategy
            risk_state: Current risk parameters
            circuit_breaker_active: Whether circuit breaker is active
            recent_feedback: Recent human feedback

        Returns:
            Performance review
        """
        # Build environment context
        env_context = self._build_environment_context(
            current_capital=current_capital,
            open_positions=open_positions,
            risk_state=risk_state,
            circuit_breaker_active=circuit_breaker_active,
            recent_feedback=recent_feedback or [],
        )

        # Get trade history
        trades = self.state_manager.get_trade_history(limit=100)
        trade_dicts = [
            {
                "coin": t.coin,
                "side": t.side,
                "entry_price": t.entry_price,
                "exit_price": t.exit_price,
                "pnl": t.pnl,
                "pnl_pct": t.pnl_pct,
                "entry_reason": t.entry_reason,
                "exit_reason": t.exit_reason,
            }
            for t in trades
        ]

        # Perform reflection
        review = await perform_self_reflection(
            environment_context=env_context.model_dump(),
            trade_history=trade_dicts,
            current_strategy=current_strategy.model_dump(),
        )

        # Store reflection
        self.reflection_history.append(review)
        self.last_reflection_time = datetime.now()

        return review

    async def determine_adaptation(
        self, performance_review: PerformanceReview, current_strategy: TradingStrategy, env_context: EnvironmentContext
    ) -> StrategyAdaptation:
        """Determine strategy adaptation based on performance review.

        Args:
            performance_review: Performance review
            current_strategy: Current strategy
            env_context: Environment context

        Returns:
            Strategy adaptation plan
        """
        adaptation = await determine_strategy_adaptation(
            performance_review=performance_review.model_dump(),
            current_strategy=current_strategy.model_dump(),
            environment_context=env_context.model_dump(),
        )

        return adaptation
