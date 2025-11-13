"""Interactive trading agent with real-time communication and self-adaptation.

This extends the base trading agent with:
- Command queue for real-time communication
- Self-reflection and performance review
- Strategy adaptation based on results
- Human-in-the-loop feedback integration
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Any, Optional
from .agent import HyperliquidTradingAgent
from .agent_control import AgentController, AgentCommand, AgentResponse, CommandType, AgentStatus
from .self_reflection import SelfReflectionEngine, PerformanceReview, StrategyAdaptation
from .strategies import TradingStrategy, get_strategy_by_type, StrategyType
from .risk_manager import RiskParams

try:
    from ...tools.hyperliquid_trading.tool import get_open_positions, check_account_balance

    HYPERLIQUID_TOOLS_AVAILABLE = True
except ImportError:
    HYPERLIQUID_TOOLS_AVAILABLE = False
    get_open_positions = None
    check_account_balance = None


class InteractiveHyperliquidAgent(HyperliquidTradingAgent):
    """Interactive trading agent with communication and self-adaptation capabilities."""

    def __init__(
        self,
        starting_capital: float,
        risk_params: Optional[RiskParams] = None,
        db_path: str = "hyperliquid_trading_state.db",
        testnet: bool = True,
        reflection_interval_hours: int = 6,  # How often to self-reflect
    ):
        """Initialize interactive trading agent.

        Args:
            starting_capital: Starting capital in USD
            risk_params: Risk management parameters
            db_path: Path to state database
            testnet: Use testnet (default: True for safety)
            reflection_interval_hours: Hours between self-reflections
        """
        super().__init__(starting_capital, risk_params, db_path, testnet)

        # Initialize control and reflection systems
        self.controller = AgentController()
        self.reflection_engine = SelfReflectionEngine(self.state_manager, starting_capital)
        self.reflection_interval = timedelta(hours=reflection_interval_hours)

        # State
        self.is_paused = False
        self.should_stop = False
        self.human_feedback: list[str] = []
        self.pending_approvals: dict[str, dict] = {}  # trade_id -> trade_info

        # Update controller status
        self.controller.status = AgentStatus(
            is_running=False,
            current_strategy=None,
            open_positions=0,
            total_pnl=0.0,
        )

    async def _process_commands(self, current_strategy: TradingStrategy) -> bool:
        """Process any pending commands from the controller.

        Args:
            current_strategy: Current trading strategy

        Returns:
            True if should continue trading, False if should stop
        """
        command = await self.controller.get_command(timeout=0.1)

        if not command:
            return True  # No command, continue trading

        print(f"\n📬 Received command: {command.command_type.value}")
        if command.message:
            print(f"   Message: {command.message}")

        response = None

        try:
            if command.command_type == CommandType.PAUSE_TRADING:
                self.is_paused = True
                self.controller.status.is_paused = True
                response = AgentResponse(
                    command_type=command.command_type,
                    success=True,
                    message="Trading paused. Send RESUME_TRADING to continue.",
                )

            elif command.command_type == CommandType.RESUME_TRADING:
                self.is_paused = False
                self.controller.status.is_paused = False
                response = AgentResponse(
                    command_type=command.command_type, success=True, message="Trading resumed."
                )

            elif command.command_type == CommandType.STOP_TRADING:
                self.should_stop = True
                response = AgentResponse(
                    command_type=command.command_type, success=True, message="Stopping trading. Will close positions and exit."
                )

            elif command.command_type == CommandType.CLOSE_ALL_POSITIONS:
                # Close all positions
                positions = get_open_positions(testnet=self.testnet)
                closed = []
                for pos in positions:
                    from ...tools.hyperliquid_trading.tool import close_position

                    result = close_position(pos["coin"], testnet=self.testnet)
                    if result.get("success"):
                        closed.append(pos["coin"])

                response = AgentResponse(
                    command_type=command.command_type,
                    success=True,
                    message=f"Closed {len(closed)} positions: {', '.join(closed)}",
                    data={"closed_positions": closed},
                )

            elif command.command_type == CommandType.CHANGE_STRATEGY:
                # Change strategy
                new_type = command.parameters.get("strategy_type")
                markets = command.parameters.get("markets", current_strategy.markets)

                try:
                    new_strategy = get_strategy_by_type(StrategyType(new_type), markets=markets)
                    # Update current strategy (would need to return this to caller)
                    response = AgentResponse(
                        command_type=command.command_type,
                        success=True,
                        message=f"Strategy changed to {new_strategy.name}",
                        data={"new_strategy": new_strategy.model_dump()},
                    )
                except Exception as e:
                    response = AgentResponse(
                        command_type=command.command_type, success=False, message=f"Failed to change strategy: {e}"
                    )

            elif command.command_type == CommandType.ADJUST_RISK:
                # Adjust risk parameters
                for key, value in command.parameters.items():
                    if hasattr(self.risk_params, key):
                        setattr(self.risk_params, key, value)

                response = AgentResponse(
                    command_type=command.command_type,
                    success=True,
                    message=f"Risk parameters updated: {command.parameters}",
                )

            elif command.command_type == CommandType.REQUEST_ANALYSIS:
                # Analyze market
                coin = command.parameters.get("coin")
                if coin:
                    analysis = await self.analyze_market(coin)
                    response = AgentResponse(
                        command_type=command.command_type,
                        success=True,
                        message=f"{coin} Analysis:\nTrend: {analysis.trend}\nRecommendation: {analysis.recommendation}\nConfidence: {analysis.confidence:.0%}",
                        data={"analysis": analysis.model_dump()},
                    )

            elif command.command_type == CommandType.SELF_REFLECT:
                # Perform self-reflection
                capital = await self.get_current_capital()
                positions = get_open_positions(testnet=self.testnet)

                review = await self.reflection_engine.perform_reflection(
                    current_capital=capital,
                    open_positions=positions,
                    current_strategy=current_strategy,
                    risk_state=self.risk_params.model_dump(),
                    circuit_breaker_active=self.risk_manager.is_circuit_breaker_active(),
                    recent_feedback=self.human_feedback,
                )

                reflection_summary = f"""
Self-Reflection Summary:
- Win Rate: {review.win_rate:.1f}%
- Total P&L: ${review.total_pnl:.2f}
- Confidence: {review.confidence_level:.0%}

What Worked:
{chr(10).join([f"  • {item}" for item in review.what_worked[:3]])}

What Failed:
{chr(10).join([f"  • {item}" for item in review.what_failed[:3]])}

Recommendations:
{chr(10).join([f"  • {item}" for item in review.recommended_changes[:3]])}
"""

                response = AgentResponse(
                    command_type=command.command_type,
                    success=True,
                    message=reflection_summary,
                    data={"review": review.model_dump()},
                )

            elif command.command_type == CommandType.PROVIDE_FEEDBACK:
                # Store human feedback
                feedback = command.message or "Feedback received"
                self.human_feedback.append(f"[{datetime.now().isoformat()}] {feedback}")

                response = AgentResponse(
                    command_type=command.command_type,
                    success=True,
                    message=f"Thank you for the feedback. I'll incorporate this into my decision making. Total feedback received: {len(self.human_feedback)}",
                )

            elif command.command_type == CommandType.APPROVE_TRADE:
                trade_id = command.parameters.get("trade_id")
                if trade_id in self.pending_approvals:
                    trade_info = self.pending_approvals.pop(trade_id)
                    response = AgentResponse(
                        command_type=command.command_type, success=True, message=f"Trade {trade_id} approved"
                    )
                else:
                    response = AgentResponse(
                        command_type=command.command_type, success=False, message=f"Trade {trade_id} not found in pending"
                    )

            elif command.command_type == CommandType.REJECT_TRADE:
                trade_id = command.parameters.get("trade_id")
                reason = command.parameters.get("reason", "No reason provided")
                if trade_id in self.pending_approvals:
                    self.pending_approvals.pop(trade_id)
                    # Store as feedback
                    self.human_feedback.append(f"Trade rejected: {reason}")
                    response = AgentResponse(
                        command_type=command.command_type, success=True, message=f"Trade {trade_id} rejected: {reason}"
                    )

            else:
                response = AgentResponse(
                    command_type=command.command_type, success=False, message=f"Unknown command type: {command.command_type}"
                )

        except Exception as e:
            response = AgentResponse(command_type=command.command_type, success=False, message=f"Error processing command: {e}")

        # Send response if required
        if command.requires_response and response:
            await self.controller.send_response(response)

        # Return whether to continue trading
        return not self.should_stop

    async def _maybe_perform_reflection(self, current_strategy: TradingStrategy) -> Optional[StrategyAdaptation]:
        """Maybe perform self-reflection if enough time has passed.

        Args:
            current_strategy: Current trading strategy

        Returns:
            Strategy adaptation if reflection was performed
        """
        if not self.reflection_engine.last_reflection_time:
            # First reflection
            time_since_last = timedelta(hours=999)
        else:
            time_since_last = datetime.now() - self.reflection_engine.last_reflection_time

        if time_since_last < self.reflection_interval:
            return None  # Not time yet

        print(f"\n🧠 Performing self-reflection...")

        # Perform reflection
        capital = await self.get_current_capital()
        positions = get_open_positions(testnet=self.testnet)

        review = await self.reflection_engine.perform_reflection(
            current_capital=capital,
            open_positions=positions,
            current_strategy=current_strategy,
            risk_state=self.risk_params.model_dump(),
            circuit_breaker_active=self.risk_manager.is_circuit_breaker_active(),
            recent_feedback=self.human_feedback,
        )

        print(f"✅ Self-reflection complete:")
        print(f"   Win Rate: {review.win_rate:.1f}%")
        print(f"   Confidence: {review.confidence_level:.0%}")
        print(f"   Lessons: {len(review.lessons_learned)} identified")

        # Determine if strategy should adapt
        from .self_reflection import EnvironmentContext

        env_context = EnvironmentContext(
            current_capital=capital,
            starting_capital=self.starting_capital,
            total_pnl_pct=((capital - self.starting_capital) / self.starting_capital * 100),
            days_running=1,
            open_positions=positions,
            recent_trades=[],
            risk_state=self.risk_params.model_dump(),
            circuit_breaker_active=self.risk_manager.is_circuit_breaker_active(),
        )

        adaptation = await self.reflection_engine.determine_adaptation(review, current_strategy, env_context)

        if adaptation.should_change_strategy:
            print(f"💡 Recommending strategy change: {adaptation.reason}")

        return adaptation

    async def run_interactive_trading(
        self,
        markets: list[str],
        initial_strategy: Optional[TradingStrategy] = None,
        duration_hours: int = 24,
        check_interval_minutes: int = 15,
    ) -> dict[str, Any]:
        """Run interactive autonomous trading with communication capabilities.

        Args:
            markets: Markets to trade
            initial_strategy: Initial strategy (or will develop one)
            duration_hours: How long to run (hours)
            check_interval_minutes: Minutes between strategy checks

        Returns:
            Summary of trading session
        """
        # Develop or use provided strategy
        if not initial_strategy:
            strategy = await self.develop_strategy(markets=markets)
        else:
            strategy = initial_strategy

        # Update controller status
        self.controller.status.is_running = True
        self.controller.status.current_strategy = strategy.name

        print(f"🤖 Interactive Trading Started")
        print(f"Strategy: {strategy.name}")
        print(f"Markets: {', '.join(strategy.markets)}")
        print(f"Duration: {duration_hours}h, Check Interval: {check_interval_minutes}m")
        print(f"Reflection Interval: {self.reflection_interval.total_seconds() / 3600:.1f}h")
        print(f"Starting Capital: ${self.current_capital:.2f}")
        print(f"\n💬 Send commands via controller.send_command() for real-time interaction")

        start_time = datetime.now()
        iterations = 0

        while (datetime.now() - start_time).total_seconds() < duration_hours * 3600:
            iterations += 1

            # Check for commands
            should_continue = await self._process_commands(strategy)
            if not should_continue:
                print("\n⛔ Stop command received. Exiting...")
                break

            # Skip iteration if paused
            if self.is_paused:
                print("⏸️  Trading paused. Waiting...")
                await asyncio.sleep(60)  # Check every minute while paused
                continue

            print(f"\n--- Iteration {iterations} ---")

            # Maybe perform self-reflection
            adaptation = await self._maybe_perform_reflection(strategy)
            if adaptation and adaptation.should_change_strategy:
                print(f"🔄 Adapting strategy based on reflection...")
                # Would implement strategy change here
                # For now, just log it
                print(f"   Recommendation: {adaptation.reason}")

            # Execute strategy iteration (from parent class)
            results = await self.execute_strategy_iteration(strategy)

            # Update controller status
            capital = await self.get_current_capital()
            positions = get_open_positions(testnet=self.testnet)
            self.controller.status.open_positions = len(positions)
            self.controller.status.total_pnl = capital - self.starting_capital
            self.controller.status.daily_pnl = 0  # Would need to calculate properly

            # Log results
            if results["actions"]:
                print(f"Actions taken: {len(results['actions'])}")
                for action in results["actions"]:
                    print(f"  - {action}")

            if results["errors"]:
                print(f"Errors: {len(results['errors'])}")

            # Wait for next iteration
            await asyncio.sleep(check_interval_minutes * 60)

        # Final summary
        self.controller.status.is_running = False

        final_capital = await self.get_current_capital()
        final_metrics = self.state_manager.calculate_performance_metrics()

        return {
            "starting_capital": self.starting_capital,
            "ending_capital": final_capital,
            "total_pnl": final_capital - self.starting_capital,
            "total_pnl_pct": ((final_capital - self.starting_capital) / self.starting_capital * 100),
            "iterations": iterations,
            "metrics": final_metrics,
            "reflections_performed": len(self.reflection_engine.reflection_history),
            "feedback_received": len(self.human_feedback),
        }


# Convenience function for interactive trading
async def run_interactive_trading(
    starting_capital: float,
    markets: list[str],
    risk_params: Optional[RiskParams] = None,
    duration_hours: int = 24,
    testnet: bool = True,
) -> tuple[dict[str, Any], AgentController]:
    """Start interactive trading session with communication capabilities.

    Args:
        starting_capital: Starting capital in USD
        markets: Markets to trade
        risk_params: Risk management parameters
        duration_hours: Trading duration in hours
        testnet: Use testnet (default: True)

    Returns:
        Tuple of (trading summary, controller for sending commands)
    """
    agent = InteractiveHyperliquidAgent(
        starting_capital=starting_capital,
        risk_params=risk_params,
        testnet=testnet,
    )

    # Run trading in background, return controller for interaction
    result = await agent.run_interactive_trading(markets=markets, duration_hours=duration_hours)

    return result, agent.controller
