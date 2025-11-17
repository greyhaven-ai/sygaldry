#!/usr/bin/env python3
"""
Log Viewer and Analyzer

View and analyze audit logs from agent testing sessions.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.prompt import Prompt
    from rich import print as rprint
except ImportError:
    print("Please install rich: pip install rich")
    sys.exit(1)

console = Console()

# Logs directory
LOGS_DIR = Path(__file__).parent.parent / "logs" / "audit"


def list_log_files():
    """List all available log files."""
    if not LOGS_DIR.exists():
        console.print("[yellow]No logs directory found[/yellow]")
        return []

    log_files = sorted(LOGS_DIR.glob("*.jsonl"), key=lambda x: x.stat().st_mtime, reverse=True)
    return log_files


def display_log_list():
    """Display list of log files."""
    log_files = list_log_files()

    if not log_files:
        console.print("[yellow]No log files found[/yellow]")
        return None

    table = Table(title="Available Audit Logs", show_header=True)
    table.add_column("#", style="cyan", width=4)
    table.add_column("Timestamp", style="yellow")
    table.add_column("Agent", style="green")
    table.add_column("Session ID", style="blue")
    table.add_column("Size", style="magenta")
    table.add_column("Path", style="dim")

    for i, log_file in enumerate(log_files[:20], 1):  # Show last 20
        parts = log_file.stem.split("_")
        if len(parts) >= 3:
            agent_name = parts[0]
            session_id = parts[1]
            timestamp_str = "_".join(parts[2:])
            size = log_file.stat().st_size

            # Parse timestamp
            try:
                timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                time_display = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            except:
                time_display = timestamp_str

            table.add_row(
                str(i),
                time_display,
                agent_name,
                session_id,
                f"{size:,}B",
                str(log_file.relative_to(LOGS_DIR.parent))
            )

    console.print(table)
    return log_files[:20]


def load_log_file(log_file: Path):
    """Load and parse a JSONL log file."""
    entries = []
    with open(log_file, "r") as f:
        for line in f:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries


def analyze_log(entries: list):
    """Analyze log entries and generate statistics."""
    stats = {
        "total_entries": len(entries),
        "events": defaultdict(int),
        "errors": [],
        "metrics": {},
        "timeline": []
    }

    start_time = None
    end_time = None
    total_agent_duration = 0
    agent_calls = 0

    for entry in entries:
        event = entry.get("event", "unknown")
        stats["events"][event] += 1

        timestamp = entry.get("timestamp")
        if timestamp:
            dt = datetime.fromisoformat(timestamp)
            if start_time is None:
                start_time = dt
            end_time = dt

        if event == "error":
            stats["errors"].append({
                "timestamp": timestamp,
                "type": entry.get("error_type"),
                "message": entry.get("error_message")
            })
        elif event == "agent_output":
            duration = entry.get("duration_seconds", 0)
            total_agent_duration += duration
            agent_calls += 1
        elif event == "metric":
            metric_name = entry.get("metric_name")
            stats["metrics"][metric_name] = entry.get("value")

        stats["timeline"].append({
            "timestamp": timestamp,
            "event": event
        })

    # Calculate session duration
    if start_time and end_time:
        stats["session_duration"] = (end_time - start_time).total_seconds()
        stats["start_time"] = start_time.isoformat()
        stats["end_time"] = end_time.isoformat()

    # Calculate averages
    if agent_calls > 0:
        stats["avg_agent_duration"] = total_agent_duration / agent_calls

    stats["total_agent_duration"] = total_agent_duration
    stats["agent_calls"] = agent_calls
    stats["success_rate"] = (agent_calls / max(stats["events"].get("agent_input", 1), 1)) * 100

    return stats


def display_log_analysis(stats: dict):
    """Display log analysis."""
    # Session summary
    console.print("\n[bold cyan]Session Summary[/bold cyan]")
    summary_table = Table(show_header=False, box=None)
    summary_table.add_column("Metric", style="yellow")
    summary_table.add_column("Value", style="green")

    if "start_time" in stats:
        summary_table.add_row("Start Time", stats["start_time"])
        summary_table.add_row("End Time", stats["end_time"])
        summary_table.add_row("Duration", f"{stats.get('session_duration', 0):.2f}s")

    summary_table.add_row("Total Entries", str(stats["total_entries"]))
    summary_table.add_row("Agent Calls", str(stats.get("agent_calls", 0)))
    summary_table.add_row("Success Rate", f"{stats.get('success_rate', 0):.1f}%")

    if "avg_agent_duration" in stats:
        summary_table.add_row("Avg Call Duration", f"{stats['avg_agent_duration']:.2f}s")

    console.print(summary_table)

    # Event breakdown
    console.print("\n[bold cyan]Event Breakdown[/bold cyan]")
    events_table = Table(show_header=True)
    events_table.add_column("Event Type", style="yellow")
    events_table.add_column("Count", style="green", justify="right")

    for event, count in sorted(stats["events"].items(), key=lambda x: x[1], reverse=True):
        events_table.add_row(event, str(count))

    console.print(events_table)

    # Errors
    if stats["errors"]:
        console.print("\n[bold red]Errors[/bold red]")
        for error in stats["errors"]:
            console.print(Panel(
                f"[red]{error['type']}:[/red] {error['message']}",
                title=error['timestamp'],
                border_style="red"
            ))

    # Metrics
    if stats["metrics"]:
        console.print("\n[bold cyan]Custom Metrics[/bold cyan]")
        metrics_table = Table(show_header=False, box=None)
        metrics_table.add_column("Metric", style="yellow")
        metrics_table.add_column("Value", style="green")

        for metric, value in stats["metrics"].items():
            metrics_table.add_row(metric, str(value))

        console.print(metrics_table)


def display_log_entries(entries: list, event_filter: str = None):
    """Display log entries."""
    filtered = entries if not event_filter else [e for e in entries if e.get("event") == event_filter]

    for i, entry in enumerate(filtered, 1):
        event = entry.get("event", "unknown")
        timestamp = entry.get("timestamp", "")

        if event == "agent_input":
            console.print(f"\n[yellow]{i}. AGENT INPUT[/yellow] [{timestamp}]")
            console.print(f"Function: {entry.get('function')}")
            console.print(Syntax(json.dumps(entry.get('parameters', {}), indent=2), "json"))

        elif event == "agent_output":
            console.print(f"\n[green]{i}. AGENT OUTPUT[/green] [{timestamp}]")
            console.print(f"Duration: {entry.get('duration_seconds', 0):.2f}s")
            console.print(Syntax(json.dumps(entry.get('result', {}), indent=2), "json"))

        elif event == "error":
            console.print(f"\n[red]{i}. ERROR[/red] [{timestamp}]")
            console.print(f"Type: {entry.get('error_type')}")
            console.print(f"Message: {entry.get('error_message')}")

        elif event == "conversation_turn":
            console.print(f"\n[cyan]{i}. CONVERSATION TURN {entry.get('turn_number')}[/cyan] [{timestamp}]")
            console.print(f"[blue]User:[/blue] {entry.get('user_input')}")
            console.print(f"[green]Agent:[/green] {entry.get('agent_response')[:200]}...")

        elif event == "session_start":
            console.print(f"\n[bold cyan]{i}. SESSION START[/bold cyan] [{timestamp}]")
            console.print(f"Agent: {entry.get('agent_name')}")
            console.print(f"Session ID: {entry.get('session_id')}")

        elif event == "session_end":
            console.print(f"\n[bold cyan]{i}. SESSION END[/bold cyan] [{timestamp}]")
            console.print(f"Duration: {entry.get('duration_seconds', 0):.2f}s")
            console.print(f"Total Entries: {entry.get('total_entries', 0)}")


def main():
    """Main entry point."""
    console.print(Panel.fit(
        "[bold cyan]Sygaldry Log Viewer & Analyzer[/bold cyan]\n\n"
        "View and analyze audit logs from agent testing sessions",
        border_style="cyan"
    ))

    while True:
        log_files = display_log_list()

        if not log_files:
            break

        console.print("\n[cyan]Options:[/cyan]")
        console.print("  Enter log number to view details")
        console.print("  Enter 'q' to quit")

        choice = Prompt.ask("\nYour choice").strip()

        if choice.lower() == 'q':
            break

        if choice.isdigit() and 1 <= int(choice) <= len(log_files):
            log_file = log_files[int(choice) - 1]
            console.print(f"\n[cyan]Loading: {log_file.name}[/cyan]\n")

            entries = load_log_file(log_file)
            stats = analyze_log(entries)

            # Display analysis
            display_log_analysis(stats)

            # Ask what to do next
            console.print("\n[cyan]View options:[/cyan]")
            console.print("  1. View all entries")
            console.print("  2. View inputs only")
            console.print("  3. View outputs only")
            console.print("  4. View errors only")
            console.print("  5. View conversation turns")
            console.print("  6. Back to log list")

            view_choice = Prompt.ask("\nView option", default="6")

            if view_choice == "1":
                display_log_entries(entries)
            elif view_choice == "2":
                display_log_entries(entries, "agent_input")
            elif view_choice == "3":
                display_log_entries(entries, "agent_output")
            elif view_choice == "4":
                display_log_entries(entries, "error")
            elif view_choice == "5":
                display_log_entries(entries, "conversation_turn")

            input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[cyan]Interrupted by user[/cyan]")
