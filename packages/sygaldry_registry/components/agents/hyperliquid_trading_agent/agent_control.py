"""Interactive agent control system for real-time communication and adjustments.

This module provides a command queue and control interface for sending messages
to the running agent and receiving feedback.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from enum import Enum
from queue import Queue, Empty
from typing import Any, Optional
from pydantic import BaseModel, Field


class CommandType(str, Enum):
    """Types of commands that can be sent to the agent."""

    # Strategy commands
    PAUSE_TRADING = "pause_trading"
    RESUME_TRADING = "resume_trading"
    STOP_TRADING = "stop_trading"
    CHANGE_STRATEGY = "change_strategy"
    ADJUST_RISK = "adjust_risk"

    # Position commands
    CLOSE_ALL_POSITIONS = "close_all_positions"
    CLOSE_POSITION = "close_position"
    REDUCE_POSITION = "reduce_position"

    # Analysis commands
    REQUEST_ANALYSIS = "request_analysis"
    REQUEST_PERFORMANCE = "request_performance"
    SELF_REFLECT = "self_reflect"

    # Configuration commands
    UPDATE_MARKETS = "update_markets"
    SET_APPROVAL_REQUIRED = "set_approval_required"

    # Human feedback
    APPROVE_TRADE = "approve_trade"
    REJECT_TRADE = "reject_trade"
    PROVIDE_FEEDBACK = "provide_feedback"


class AgentCommand(BaseModel):
    """A command sent to the agent."""

    command_type: CommandType = Field(..., description="Type of command")
    parameters: dict[str, Any] = Field(default_factory=dict, description="Command parameters")
    timestamp: datetime = Field(default_factory=datetime.now, description="When command was sent")
    message: Optional[str] = Field(None, description="Optional human message to agent")
    requires_response: bool = Field(False, description="Whether command requires a response")


class AgentResponse(BaseModel):
    """Response from the agent to a command."""

    command_type: CommandType = Field(..., description="Command this responds to")
    success: bool = Field(..., description="Whether command was successful")
    message: str = Field(..., description="Response message")
    data: dict[str, Any] = Field(default_factory=dict, description="Response data")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")


class AgentStatus(BaseModel):
    """Current status of the agent."""

    is_running: bool = Field(..., description="Whether agent is running")
    is_paused: bool = Field(False, description="Whether trading is paused")
    current_strategy: Optional[str] = Field(None, description="Current strategy name")
    open_positions: int = Field(0, description="Number of open positions")
    total_pnl: float = Field(0.0, description="Total P&L")
    daily_pnl: float = Field(0.0, description="Today's P&L")
    last_trade_time: Optional[datetime] = Field(None, description="Last trade timestamp")
    pending_approvals: int = Field(0, description="Trades awaiting approval")
    circuit_breaker_active: bool = Field(False, description="Circuit breaker status")


class AgentController:
    """Controller for managing and communicating with a running agent."""

    def __init__(self):
        """Initialize agent controller."""
        self.command_queue: asyncio.Queue = asyncio.Queue()
        self.response_queue: asyncio.Queue = asyncio.Queue()
        self.status = AgentStatus(is_running=False)
        self.message_log: list[tuple[datetime, str, str]] = []  # (time, sender, message)

    async def send_command(self, command: AgentCommand, wait_for_response: bool = True) -> Optional[AgentResponse]:
        """Send a command to the agent.

        Args:
            command: Command to send
            wait_for_response: Whether to wait for response

        Returns:
            Response if waiting, None otherwise
        """
        await self.command_queue.put(command)
        self._log_message("human", f"Command: {command.command_type.value}")

        if command.message:
            self._log_message("human", command.message)

        if wait_for_response and command.requires_response:
            try:
                response = await asyncio.wait_for(self.response_queue.get(), timeout=30.0)
                self._log_message("agent", response.message)
                return response
            except asyncio.TimeoutError:
                self._log_message("system", "Command timed out waiting for response")
                return None

        return None

    async def get_command(self, timeout: float = 0.1) -> Optional[AgentCommand]:
        """Get next command from queue (non-blocking).

        Args:
            timeout: How long to wait for command

        Returns:
            Command if available, None otherwise
        """
        try:
            return await asyncio.wait_for(self.command_queue.get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None

    async def send_response(self, response: AgentResponse):
        """Send a response back to the controller.

        Args:
            response: Response to send
        """
        await self.response_queue.put(response)

    def _log_message(self, sender: str, message: str):
        """Log a message.

        Args:
            sender: Who sent the message (human/agent/system)
            message: Message content
        """
        self.message_log.append((datetime.now(), sender, message))

    def get_message_history(self, limit: int = 50) -> list[dict[str, Any]]:
        """Get recent message history.

        Args:
            limit: Maximum messages to return

        Returns:
            List of messages
        """
        recent = self.message_log[-limit:]
        return [{"timestamp": ts.isoformat(), "sender": sender, "message": msg} for ts, sender, msg in recent]

    # Convenience methods for common commands

    async def pause_trading(self) -> Optional[AgentResponse]:
        """Pause all trading."""
        return await self.send_command(
            AgentCommand(command_type=CommandType.PAUSE_TRADING, message="Pausing trading", requires_response=True)
        )

    async def resume_trading(self) -> Optional[AgentResponse]:
        """Resume trading."""
        return await self.send_command(
            AgentCommand(command_type=CommandType.RESUME_TRADING, message="Resuming trading", requires_response=True)
        )

    async def stop_trading(self) -> Optional[AgentResponse]:
        """Stop trading completely."""
        return await self.send_command(
            AgentCommand(command_type=CommandType.STOP_TRADING, message="Stopping all trading", requires_response=True)
        )

    async def close_all_positions(self) -> Optional[AgentResponse]:
        """Close all open positions."""
        return await self.send_command(
            AgentCommand(
                command_type=CommandType.CLOSE_ALL_POSITIONS, message="Closing all positions", requires_response=True
            )
        )

    async def change_strategy(self, new_strategy_type: str, markets: list[str]) -> Optional[AgentResponse]:
        """Change the trading strategy.

        Args:
            new_strategy_type: New strategy type
            markets: Markets for new strategy

        Returns:
            Response from agent
        """
        return await self.send_command(
            AgentCommand(
                command_type=CommandType.CHANGE_STRATEGY,
                parameters={"strategy_type": new_strategy_type, "markets": markets},
                message=f"Changing strategy to {new_strategy_type} on {markets}",
                requires_response=True,
            )
        )

    async def adjust_risk(self, **risk_params) -> Optional[AgentResponse]:
        """Adjust risk parameters.

        Args:
            **risk_params: Risk parameters to update

        Returns:
            Response from agent
        """
        return await self.send_command(
            AgentCommand(
                command_type=CommandType.ADJUST_RISK,
                parameters=risk_params,
                message=f"Adjusting risk parameters: {risk_params}",
                requires_response=True,
            )
        )

    async def request_analysis(self, coin: str) -> Optional[AgentResponse]:
        """Request market analysis for a coin.

        Args:
            coin: Coin to analyze

        Returns:
            Analysis response
        """
        return await self.send_command(
            AgentCommand(
                command_type=CommandType.REQUEST_ANALYSIS,
                parameters={"coin": coin},
                message=f"Request analysis for {coin}",
                requires_response=True,
            )
        )

    async def request_self_reflection(self) -> Optional[AgentResponse]:
        """Ask agent to reflect on its own performance.

        Returns:
            Self-reflection response
        """
        return await self.send_command(
            AgentCommand(
                command_type=CommandType.SELF_REFLECT, message="Please reflect on your performance", requires_response=True
            )
        )

    async def provide_feedback(self, feedback: str, context: Optional[dict] = None) -> Optional[AgentResponse]:
        """Provide feedback to the agent.

        Args:
            feedback: Feedback message
            context: Optional context data

        Returns:
            Response acknowledging feedback
        """
        return await self.send_command(
            AgentCommand(
                command_type=CommandType.PROVIDE_FEEDBACK,
                parameters=context or {},
                message=f"Feedback: {feedback}",
                requires_response=True,
            )
        )

    async def approve_trade(self, trade_id: str) -> Optional[AgentResponse]:
        """Approve a pending trade.

        Args:
            trade_id: Trade to approve

        Returns:
            Approval confirmation
        """
        return await self.send_command(
            AgentCommand(
                command_type=CommandType.APPROVE_TRADE,
                parameters={"trade_id": trade_id},
                message=f"Approving trade {trade_id}",
                requires_response=True,
            )
        )

    async def reject_trade(self, trade_id: str, reason: str) -> Optional[AgentResponse]:
        """Reject a pending trade.

        Args:
            trade_id: Trade to reject
            reason: Reason for rejection

        Returns:
            Rejection confirmation
        """
        return await self.send_command(
            AgentCommand(
                command_type=CommandType.REJECT_TRADE,
                parameters={"trade_id": trade_id, "reason": reason},
                message=f"Rejecting trade {trade_id}: {reason}",
                requires_response=True,
            )
        )


class InteractiveAgentSession:
    """Interactive session manager for communicating with agent."""

    def __init__(self, controller: AgentController):
        """Initialize interactive session.

        Args:
            controller: Agent controller
        """
        self.controller = controller
        self.running = False

    async def start_interactive_mode(self):
        """Start interactive command-line interface."""
        self.running = True
        print("\n" + "=" * 60)
        print("Interactive Agent Control")
        print("=" * 60)
        print("\nAvailable commands:")
        print("  pause     - Pause trading")
        print("  resume    - Resume trading")
        print("  stop      - Stop trading completely")
        print("  close     - Close all positions")
        print("  status    - Get agent status")
        print("  analyze <COIN> - Analyze a market")
        print("  reflect   - Ask agent to self-reflect")
        print("  feedback <MESSAGE> - Provide feedback to agent")
        print("  history   - View message history")
        print("  help      - Show this help")
        print("  exit      - Exit interactive mode")
        print()

        while self.running:
            try:
                # In real implementation, use aioconsole for async input
                # For now, this is a template
                user_input = input(">>> ").strip().lower()

                if not user_input:
                    continue

                parts = user_input.split(maxsplit=1)
                command = parts[0]
                args = parts[1] if len(parts) > 1 else ""

                if command == "exit":
                    self.running = False
                    print("Exiting interactive mode")
                    break

                elif command == "pause":
                    response = await self.controller.pause_trading()
                    print(f"✓ {response.message if response else 'Command sent'}")

                elif command == "resume":
                    response = await self.controller.resume_trading()
                    print(f"✓ {response.message if response else 'Command sent'}")

                elif command == "stop":
                    response = await self.controller.stop_trading()
                    print(f"✓ {response.message if response else 'Command sent'}")
                    self.running = False

                elif command == "close":
                    response = await self.controller.close_all_positions()
                    print(f"✓ {response.message if response else 'Command sent'}")

                elif command == "status":
                    status = self.controller.status
                    print(f"\nAgent Status:")
                    print(f"  Running: {status.is_running}")
                    print(f"  Paused: {status.is_paused}")
                    print(f"  Strategy: {status.current_strategy}")
                    print(f"  Open Positions: {status.open_positions}")
                    print(f"  Total P&L: ${status.total_pnl:.2f}")
                    print(f"  Daily P&L: ${status.daily_pnl:.2f}")

                elif command == "analyze":
                    if not args:
                        print("Usage: analyze <COIN>")
                    else:
                        response = await self.controller.request_analysis(args.upper())
                        if response and response.success:
                            print(f"\n{response.message}")
                            if "analysis" in response.data:
                                print(f"\nAnalysis: {response.data['analysis']}")

                elif command == "reflect":
                    response = await self.controller.request_self_reflection()
                    if response and response.success:
                        print(f"\n{response.message}")

                elif command == "feedback":
                    if not args:
                        print("Usage: feedback <MESSAGE>")
                    else:
                        response = await self.controller.provide_feedback(args)
                        print(f"✓ {response.message if response else 'Feedback sent'}")

                elif command == "history":
                    history = self.controller.get_message_history(limit=20)
                    print("\nRecent Messages:")
                    for msg in history[-10:]:
                        ts = msg["timestamp"].split("T")[1][:8]
                        sender = msg["sender"].rjust(8)
                        print(f"  [{ts}] {sender}: {msg['message']}")

                elif command == "help":
                    print("\nSee command list above")

                else:
                    print(f"Unknown command: {command}. Type 'help' for commands.")

            except KeyboardInterrupt:
                print("\nExiting interactive mode")
                self.running = False
                break
            except Exception as e:
                print(f"Error: {e}")

        print("Interactive mode ended")
