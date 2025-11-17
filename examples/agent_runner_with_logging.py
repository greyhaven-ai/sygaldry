#!/usr/bin/env python3
"""
Agent Runner with Comprehensive Logging and Auditing

This script runs Sygaldry agents in realistic scenarios with full audit trails.
All interactions, results, and errors are logged to files for review.
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import traceback
import os

# Apply Lilypad compatibility patch FIRST, before any other imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from sygaldry.lilypad_compat import patch
if not patch.is_applied():
    patch.apply()

# Add the packages directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "sygaldry_registry"))

# Rich for nice terminal output
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.table import Table
    from rich.logging import RichHandler
    from rich.markdown import Markdown
    from rich.json import JSON
except ImportError:
    print("Please install rich: pip install rich")
    sys.exit(1)

console = Console()

# Create logs directory if it doesn't exist
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Create audit directory for detailed audit trails
AUDIT_DIR = LOGS_DIR / "audit"
AUDIT_DIR.mkdir(exist_ok=True)


class AgentAuditLogger:
    """Comprehensive audit logging for agent interactions."""

    def __init__(self, agent_name: str, session_id: str):
        self.agent_name = agent_name
        self.session_id = session_id
        self.start_time = datetime.now()

        # Create session-specific log file
        timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
        self.log_file = AUDIT_DIR / f"{agent_name}_{session_id}_{timestamp}.jsonl"

        # Also create a readable text log
        self.text_log_file = AUDIT_DIR / f"{agent_name}_{session_id}_{timestamp}.txt"

        # Initialize structured log
        self.log_entries = []

        # Write session header
        self._write_header()

    def _write_header(self):
        """Write session header information."""
        header = {
            "event": "session_start",
            "timestamp": self.start_time.isoformat(),
            "agent_name": self.agent_name,
            "session_id": self.session_id,
            "python_version": sys.version,
            "environment": {
                "openai_key_set": bool(os.getenv("OPENAI_API_KEY")),
                "anthropic_key_set": bool(os.getenv("ANTHROPIC_API_KEY")),
                "google_key_set": bool(os.getenv("GOOGLE_API_KEY")),
            }
        }
        self._write_jsonl(header)
        self._write_text(f"=== SESSION START: {self.agent_name} ===\n")
        self._write_text(f"Session ID: {self.session_id}\n")
        self._write_text(f"Start Time: {self.start_time}\n")
        self._write_text("=" * 60 + "\n\n")

    def log_input(self, function_name: str, params: Dict[str, Any]):
        """Log agent function input."""
        entry = {
            "event": "agent_input",
            "timestamp": datetime.now().isoformat(),
            "function": function_name,
            "parameters": params
        }
        self.log_entries.append(entry)
        self._write_jsonl(entry)

        self._write_text(f"\n[{datetime.now().strftime('%H:%M:%S')}] AGENT INPUT\n")
        self._write_text(f"Function: {function_name}\n")
        self._write_text(f"Parameters: {json.dumps(params, indent=2)}\n")

    def log_output(self, result: Any, duration_seconds: float):
        """Log agent function output."""
        # Convert result to dict if it's a Pydantic model
        if hasattr(result, "model_dump"):
            result_data = result.model_dump()
        elif isinstance(result, dict):
            result_data = result
        else:
            result_data = {"result": str(result)}

        entry = {
            "event": "agent_output",
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": duration_seconds,
            "result": result_data
        }
        self.log_entries.append(entry)
        self._write_jsonl(entry)

        self._write_text(f"\n[{datetime.now().strftime('%H:%M:%S')}] AGENT OUTPUT\n")
        self._write_text(f"Duration: {duration_seconds:.2f}s\n")
        self._write_text(f"Result: {json.dumps(result_data, indent=2)}\n")

    def log_error(self, error: Exception):
        """Log errors."""
        entry = {
            "event": "error",
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc()
        }
        self.log_entries.append(entry)
        self._write_jsonl(entry)

        self._write_text(f"\n[{datetime.now().strftime('%H:%M:%S')}] ERROR\n")
        self._write_text(f"Type: {type(error).__name__}\n")
        self._write_text(f"Message: {str(error)}\n")
        self._write_text(f"Traceback:\n{traceback.format_exc()}\n")

    def log_conversation_turn(self, turn_number: int, user_input: str, agent_response: str):
        """Log conversational turn."""
        entry = {
            "event": "conversation_turn",
            "timestamp": datetime.now().isoformat(),
            "turn_number": turn_number,
            "user_input": user_input,
            "agent_response": agent_response
        }
        self.log_entries.append(entry)
        self._write_jsonl(entry)

        self._write_text(f"\n[{datetime.now().strftime('%H:%M:%S')}] TURN {turn_number}\n")
        self._write_text(f"User: {user_input}\n")
        self._write_text(f"Agent: {agent_response}\n")

    def log_metric(self, metric_name: str, value: Any):
        """Log custom metrics."""
        entry = {
            "event": "metric",
            "timestamp": datetime.now().isoformat(),
            "metric_name": metric_name,
            "value": value
        }
        self.log_entries.append(entry)
        self._write_jsonl(entry)

    def finalize(self):
        """Finalize the audit log."""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        summary = {
            "event": "session_end",
            "timestamp": end_time.isoformat(),
            "duration_seconds": duration,
            "total_entries": len(self.log_entries),
            "summary": self._generate_summary()
        }
        self._write_jsonl(summary)

        self._write_text(f"\n{'=' * 60}\n")
        self._write_text(f"=== SESSION END ===\n")
        self._write_text(f"End Time: {end_time}\n")
        self._write_text(f"Total Duration: {duration:.2f}s\n")
        self._write_text(f"Total Log Entries: {len(self.log_entries)}\n")
        self._write_text(f"{'=' * 60}\n")

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate session summary statistics."""
        event_counts = {}
        total_duration = 0
        error_count = 0

        for entry in self.log_entries:
            event = entry.get("event", "unknown")
            event_counts[event] = event_counts.get(event, 0) + 1

            if event == "agent_output":
                total_duration += entry.get("duration_seconds", 0)
            elif event == "error":
                error_count += 1

        return {
            "event_counts": event_counts,
            "total_agent_duration": total_duration,
            "error_count": error_count,
            "success_rate": (event_counts.get("agent_output", 0) / max(event_counts.get("agent_input", 1), 1)) * 100
        }

    def _write_jsonl(self, data: Dict[str, Any]):
        """Write JSON lines to audit file."""
        with open(self.log_file, "a") as f:
            f.write(json.dumps(data) + "\n")

    def _write_text(self, text: str):
        """Write to human-readable text log."""
        with open(self.text_log_file, "a") as f:
            f.write(text)

    def get_log_files(self) -> Dict[str, Path]:
        """Get paths to log files."""
        return {
            "jsonl": self.log_file,
            "text": self.text_log_file
        }


class AgentRunner:
    """Run agents with comprehensive logging."""

    def __init__(self):
        self.console = console
        self.current_audit_logger: Optional[AgentAuditLogger] = None

    async def run_single_agent_test(self, agent_name: str, function_name: str, params: Dict[str, Any]):
        """Run a single agent test with logging."""
        session_id = f"single_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        audit_logger = AgentAuditLogger(agent_name, session_id)

        self.console.print(f"\n[cyan]Running {agent_name}.{function_name}[/cyan]")
        self.console.print(f"[dim]Session ID: {session_id}[/dim]\n")

        try:
            # Import the agent module dynamically
            module_path = f"components.agents.{agent_name}"
            module = __import__(module_path, fromlist=[function_name])
            func = getattr(module, function_name)

            # Log input
            audit_logger.log_input(function_name, params)

            # Execute agent
            start_time = datetime.now()

            if asyncio.iscoroutinefunction(func):
                result = await func(**params)
            else:
                result = func(**params)

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # Log output
            audit_logger.log_output(result, duration)

            # Display result
            self.console.print(Panel(
                JSON(json.dumps(result.model_dump() if hasattr(result, "model_dump") else {"result": str(result)}, indent=2)),
                title=f"[green]Success ({duration:.2f}s)[/green]",
                border_style="green"
            ))

            return True

        except Exception as e:
            audit_logger.log_error(e)
            self.console.print(Panel(
                f"[red]{type(e).__name__}:[/red] {str(e)}\n\n{traceback.format_exc()}",
                title="[red]Error[/red]",
                border_style="red"
            ))
            return False

        finally:
            audit_logger.finalize()
            log_files = audit_logger.get_log_files()
            self.console.print(f"\n[dim]Logs saved to:[/dim]")
            self.console.print(f"  [cyan]JSONL:[/cyan] {log_files['jsonl']}")
            self.console.print(f"  [cyan]Text:[/cyan] {log_files['text']}\n")

    async def run_conversational_test(self, agent_name: str, function_name: str, scenario: List[Dict[str, str]]):
        """Run a multi-turn conversational test."""
        session_id = f"conversation_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        audit_logger = AgentAuditLogger(agent_name, session_id)

        self.console.print(f"\n[cyan]Running conversational test: {agent_name}[/cyan]")
        self.console.print(f"[dim]Session ID: {session_id}[/dim]")
        self.console.print(f"[dim]Turns: {len(scenario)}[/dim]\n")

        try:
            # Import the agent
            module_path = f"components.agents.{agent_name}"
            module = __import__(module_path, fromlist=[function_name])
            func = getattr(module, function_name)

            for turn_num, turn in enumerate(scenario, 1):
                user_input = turn.get("user", "")
                expected_params = turn.get("params", {})

                self.console.print(f"\n[yellow]Turn {turn_num}[/yellow]")
                self.console.print(f"[blue]User:[/blue] {user_input}")

                # Log input
                audit_logger.log_input(function_name, expected_params)

                # Execute
                start_time = datetime.now()

                if asyncio.iscoroutinefunction(func):
                    result = await func(**expected_params)
                else:
                    result = func(**expected_params)

                duration = (end_time := datetime.now() - start_time).total_seconds()

                # Log output
                response_text = str(result) if not hasattr(result, "model_dump") else json.dumps(result.model_dump(), indent=2)
                audit_logger.log_output(result, duration)
                audit_logger.log_conversation_turn(turn_num, user_input, response_text)

                self.console.print(f"[green]Agent:[/green] {response_text[:200]}...")
                self.console.print(f"[dim]({duration:.2f}s)[/dim]")

                # Small delay between turns
                await asyncio.sleep(0.5)

            self.console.print("\n[green]✓ Conversational test completed successfully[/green]")
            return True

        except Exception as e:
            audit_logger.log_error(e)
            self.console.print(f"\n[red]✗ Error: {e}[/red]")
            return False

        finally:
            audit_logger.finalize()
            log_files = audit_logger.get_log_files()
            self.console.print(f"\n[dim]Logs saved to:[/dim]")
            self.console.print(f"  [cyan]JSONL:[/cyan] {log_files['jsonl']}")
            self.console.print(f"  [cyan]Text:[/cyan] {log_files['text']}\n")

    def display_logs_summary(self):
        """Display summary of all logs."""
        if not AUDIT_DIR.exists():
            self.console.print("[yellow]No logs found[/yellow]")
            return

        log_files = sorted(AUDIT_DIR.glob("*.jsonl"), key=lambda x: x.stat().st_mtime, reverse=True)

        if not log_files:
            self.console.print("[yellow]No log files found[/yellow]")
            return

        table = Table(title="Audit Logs", show_header=True)
        table.add_column("Time", style="cyan")
        table.add_column("Agent", style="green")
        table.add_column("Session ID", style="yellow")
        table.add_column("Size", style="blue")

        for log_file in log_files[:10]:  # Show last 10
            parts = log_file.stem.split("_")
            if len(parts) >= 3:
                agent_name = parts[0]
                session_id = parts[1]
                timestamp = "_".join(parts[2:])
                size = log_file.stat().st_size

                table.add_row(
                    timestamp,
                    agent_name,
                    session_id,
                    f"{size:,} bytes"
                )

        self.console.print(table)


async def main():
    """Main entry point."""
    runner = AgentRunner()

    console.print(Panel.fit(
        "[bold cyan]Sygaldry Agent Runner with Audit Logging[/bold cyan]\n\n"
        "Test agents in realistic scenarios with comprehensive logging and audit trails.\n"
        "All interactions are logged to files for review and compliance.",
        border_style="cyan"
    ))

    # Check for API keys
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        console.print("[red]Error: No API keys found![/red]")
        console.print("Please set OPENAI_API_KEY or ANTHROPIC_API_KEY")
        return

    while True:
        console.print("\n[bold cyan]Options:[/bold cyan]")
        console.print("  1. Run single agent test")
        console.print("  2. Run conversational test scenario")
        console.print("  3. View logs summary")
        console.print("  4. Run predefined test suite")
        console.print("  q. Quit")

        choice = Prompt.ask("\nSelect option", default="1")

        if choice.lower() == 'q':
            console.print("[cyan]Goodbye![/cyan]")
            break
        elif choice == "1":
            await run_single_test_menu(runner)
        elif choice == "2":
            await run_conversational_test_menu(runner)
        elif choice == "3":
            runner.display_logs_summary()
        elif choice == "4":
            await run_test_suite(runner)


async def run_single_test_menu(runner: AgentRunner):
    """Menu for running single agent tests."""
    console.print("\n[cyan]Single Agent Test[/cyan]")

    # Example: Text Summarization
    agent_name = "text_summarization"
    function_name = "summarize_text"

    text = Prompt.ask(
        "Enter text to summarize",
        default="Artificial intelligence is transforming how we work and live..."
    )

    style = Prompt.ask(
        "Summary style",
        choices=["technical", "executive", "simple", "academic"],
        default="technical"
    )

    max_length = int(Prompt.ask("Max length (words)", default="100"))

    params = {
        "text": text,
        "style": style,
        "max_length": max_length
    }

    await runner.run_single_agent_test(agent_name, function_name, params)


async def run_conversational_test_menu(runner: AgentRunner):
    """Menu for running conversational tests."""
    console.print("\n[cyan]Conversational Test[/cyan]")
    console.print("[yellow]Using customer support agent as example[/yellow]\n")

    # Example multi-turn scenario for customer support
    scenario = [
        {
            "user": "My account isn't working",
            "params": {
                "message": "My account isn't working",
                "context": {}
            }
        },
        {
            "user": "I can't log in",
            "params": {
                "message": "I can't log in",
                "context": {"previous_issue": "account_problem"}
            }
        },
        {
            "user": "I've tried resetting my password but didn't receive the email",
            "params": {
                "message": "I've tried resetting my password but didn't receive the email",
                "context": {"issue_type": "login", "attempted_solution": "password_reset"}
            }
        }
    ]

    await runner.run_conversational_test(
        "customer_support",
        "handle_support_message",
        scenario
    )


async def run_test_suite(runner: AgentRunner):
    """Run a predefined test suite."""
    console.print("\n[cyan]Running Test Suite[/cyan]\n")

    tests = [
        {
            "name": "Text Summarization - Technical",
            "agent": "text_summarization",
            "function": "summarize_text",
            "params": {
                "text": "Machine learning models have become increasingly sophisticated...",
                "style": "technical",
                "max_length": 50
            }
        },
        {
            "name": "Sentiment Analysis - Positive",
            "agent": "sentiment_analysis",
            "function": "analyze_sentiment",
            "params": {
                "text": "This product exceeded all my expectations! Absolutely amazing quality."
            }
        },
        {
            "name": "PII Scrubbing - Email Detection",
            "agent": "pii_scrubbing",
            "function": "scrub_pii",
            "params": {
                "text": "Contact me at john.doe@example.com or call 555-123-4567",
                "scrubbing_method": "mask"
            }
        }
    ]

    results = []
    for test in tests:
        console.print(f"\n[yellow]Test: {test['name']}[/yellow]")
        success = await runner.run_single_agent_test(
            test["agent"],
            test["function"],
            test["params"]
        )
        results.append((test["name"], success))
        await asyncio.sleep(1)

    # Summary
    console.print("\n" + "=" * 60)
    console.print("[bold cyan]Test Suite Results[/bold cyan]")
    console.print("=" * 60)

    for name, success in results:
        status = "[green]✓ PASS[/green]" if success else "[red]✗ FAIL[/red]"
        console.print(f"{status} - {name}")

    passed = sum(1 for _, s in results if s)
    console.print(f"\n[cyan]Passed: {passed}/{len(results)}[/cyan]")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[cyan]Interrupted by user[/cyan]")
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/red]")
        console.print(traceback.format_exc())
