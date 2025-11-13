"""Terminal CLI interface for interacting with the trading agent.

This provides a command-line interface for sending commands and receiving
updates from the agent in real-time.
"""

import asyncio
import sys
from datetime import datetime
from typing import Optional
from .agent_control import AgentController, CommandType


class TerminalInterface:
    """Terminal-based interface for agent communication."""

    def __init__(self, controller: AgentController):
        """Initialize terminal interface.

        Args:
            controller: Agent controller for communication
        """
        self.controller = controller
        self.running = False
        self.command_history: list[str] = []

    def print_banner(self):
        """Print welcome banner."""
        print("\n" + "=" * 70)
        print("🤖 Hyperliquid Trading Agent - Interactive Terminal")
        print("=" * 70)
        print("\nType 'help' for available commands, 'exit' to quit\n")

    def print_help(self):
        """Print help message."""
        print("\n📋 Available Commands:")
        print("  Trading Control:")
        print("    pause              - Pause trading")
        print("    resume             - Resume trading")
        print("    stop               - Stop trading and exit")
        print("")
        print("  Position Management:")
        print("    close all          - Close all positions")
        print("    close <COIN>       - Close specific position")
        print("    positions          - View open positions")
        print("")
        print("  Analysis:")
        print("    analyze <COIN>     - Analyze a market")
        print("    reflect            - Request self-reflection")
        print("    status             - Show agent status")
        print("    performance        - Show performance metrics")
        print("")
        print("  Configuration:")
        print("    risk <PARAM>=<VAL> - Adjust risk parameter")
        print("                         Example: risk max_position_size_pct=0.15")
        print("    strategy <TYPE>    - Change strategy type")
        print("    markets <COINS>    - Update markets (comma-separated)")
        print("")
        print("  Feedback:")
        print("    feedback <MSG>     - Provide feedback to agent")
        print("    approve <ID>       - Approve pending trade")
        print("    reject <ID>        - Reject pending trade")
        print("")
        print("  Utility:")
        print("    history            - View message history")
        print("    clear              - Clear screen")
        print("    help               - Show this help")
        print("    exit               - Exit terminal\n")

    def print_status(self):
        """Print current agent status."""
        status = self.controller.status
        print(f"\n📊 Agent Status:")
        print(f"  Running: {'🟢 Yes' if status.is_running else '🔴 No'}")
        print(f"  Paused: {'⏸️  Yes' if status.is_paused else '▶️  No'}")
        print(f"  Strategy: {status.current_strategy or 'None'}")
        print(f"  Open Positions: {status.open_positions}")
        print(f"  Total P&L: ${status.total_pnl:.2f}")
        print(f"  Daily P&L: ${status.daily_pnl:.2f}")
        if status.pending_approvals > 0:
            print(f"  ⚠️  Pending Approvals: {status.pending_approvals}")
        if status.circuit_breaker_active:
            print(f"  🚨 Circuit Breaker: ACTIVE")
        print()

    async def process_command(self, cmd: str) -> bool:
        """Process a terminal command.

        Args:
            cmd: Command string

        Returns:
            True to continue, False to exit
        """
        cmd = cmd.strip()
        if not cmd:
            return True

        # Add to history
        self.command_history.append(cmd)

        parts = cmd.split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        try:
            # Handle commands
            if command == "exit" or command == "quit":
                print("👋 Exiting terminal...")
                return False

            elif command == "help":
                self.print_help()

            elif command == "status":
                self.print_status()

            elif command == "clear":
                # Clear screen
                print("\033[2J\033[H", end="")
                self.print_banner()

            elif command == "pause":
                print("⏸️  Pausing trading...")
                response = await self.controller.pause_trading()
                if response:
                    print(f"✓ {response.message}")

            elif command == "resume":
                print("▶️  Resuming trading...")
                response = await self.controller.resume_trading()
                if response:
                    print(f"✓ {response.message}")

            elif command == "stop":
                print("⛔ Stopping trading...")
                response = await self.controller.stop_trading()
                if response:
                    print(f"✓ {response.message}")
                return False  # Exit terminal

            elif command == "close":
                if args.lower() == "all":
                    print("🔄 Closing all positions...")
                    response = await self.controller.close_all_positions()
                    if response:
                        print(f"✓ {response.message}")
                elif args:
                    print(f"🔄 Closing {args} position...")
                    # Would need to implement close specific position
                    print("⚠️  Not yet implemented")
                else:
                    print("Usage: close all | close <COIN>")

            elif command == "analyze":
                if not args:
                    print("Usage: analyze <COIN>")
                else:
                    coin = args.upper()
                    print(f"🔍 Analyzing {coin}...")
                    response = await self.controller.request_analysis(coin)
                    if response and response.success:
                        print(f"\n{response.message}\n")

            elif command == "reflect":
                print("🧠 Requesting self-reflection...")
                response = await self.controller.request_self_reflection()
                if response and response.success:
                    print(f"\n{response.message}\n")

            elif command == "feedback":
                if not args:
                    print("Usage: feedback <YOUR MESSAGE>")
                else:
                    print("💬 Sending feedback...")
                    response = await self.controller.provide_feedback(args)
                    if response:
                        print(f"✓ {response.message}")

            elif command == "history":
                history = self.controller.get_message_history(limit=20)
                print("\n📜 Recent Messages:")
                for msg in history[-15:]:
                    ts = msg["timestamp"].split("T")[1][:8] if "T" in msg["timestamp"] else msg["timestamp"][:8]
                    sender = msg["sender"].rjust(8)
                    message = msg["message"][:80]
                    print(f"  [{ts}] {sender}: {message}")
                print()

            elif command == "positions":
                # Would query actual positions
                print("📊 Open Positions:")
                print(f"  Total: {self.controller.status.open_positions}")
                print("  (Detailed position view not yet implemented)")

            elif command == "performance":
                # Would show detailed metrics
                print("📈 Performance Metrics:")
                print("  (Detailed metrics view not yet implemented)")

            elif command == "risk":
                if not args:
                    print("Usage: risk <param>=<value>")
                    print("Example: risk max_position_size_pct=0.15")
                else:
                    try:
                        # Parse param=value
                        param, value = args.split("=")
                        param = param.strip()
                        value = float(value.strip())

                        print(f"⚙️  Adjusting {param} to {value}...")
                        response = await self.controller.adjust_risk(**{param: value})
                        if response:
                            print(f"✓ {response.message}")
                    except ValueError:
                        print("❌ Invalid format. Use: risk param=value")

            elif command == "strategy":
                if not args:
                    print("Usage: strategy <type>")
                    print("Types: trend_following, mean_reversion, funding_arbitrage, etc.")
                else:
                    # Would need market list
                    print(f"🔄 Changing strategy to {args}...")
                    print("⚠️  Need to specify markets. Feature in progress.")

            elif command == "markets":
                if not args:
                    print("Usage: markets <COIN1>,<COIN2>,...")
                else:
                    markets = [m.strip().upper() for m in args.split(",")]
                    print(f"🌐 Updating markets to: {', '.join(markets)}...")
                    print("⚠️  Feature in progress.")

            else:
                print(f"❌ Unknown command: {command}")
                print("Type 'help' for available commands")

        except Exception as e:
            print(f"❌ Error: {e}")

        return True

    async def run(self):
        """Run the terminal interface."""
        self.running = True
        self.print_banner()

        print("💡 Tip: The agent is running in the background. Type commands to interact.\n")

        while self.running:
            try:
                # Prompt
                sys.stdout.write("agent> ")
                sys.stdout.flush()

                # Read command asynchronously
                # Note: In production, use aioconsole.ainput for true async input
                # For now, using asyncio.to_thread to not block
                cmd = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)

                if not cmd:  # EOF
                    break

                should_continue = await self.process_command(cmd.strip())
                if not should_continue:
                    break

            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupt received. Type 'exit' to quit or continue.")
                continue
            except EOFError:
                break

        print("\n👋 Terminal interface closed.\n")


async def run_terminal_interface(controller: AgentController):
    """Run terminal interface for agent interaction.

    Args:
        controller: Agent controller
    """
    terminal = TerminalInterface(controller)
    await terminal.run()
