#!/usr/bin/env python3
"""
Quick Scenario Runner with Logging

Run predefined test scenarios with comprehensive logging.
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# Import the agent runner
sys.path.insert(0, str(Path(__file__).parent))
from agent_runner_with_logging import AgentRunner, AgentAuditLogger, console

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "sygaldry_registry"))


async def load_scenarios():
    """Load test scenarios from JSON file."""
    scenarios_file = Path(__file__).parent / "test_scenarios.json"
    if not scenarios_file.exists():
        console.print("[red]test_scenarios.json not found![/red]")
        return None

    with open(scenarios_file, "r") as f:
        return json.load(f)


async def run_scenario(runner: AgentRunner, scenario: dict, category: str):
    """Run a single scenario."""
    console.print(f"\n[bold cyan]Running: {scenario['name']}[/bold cyan]")
    console.print(f"[dim]Category: {category}[/dim]")

    try:
        success = await runner.run_single_agent_test(
            scenario["agent"],
            scenario["function"],
            scenario["params"]
        )
        return success
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return False


async def run_conversational_scenario(runner: AgentRunner, scenario: dict):
    """Run a conversational scenario."""
    console.print(f"\n[bold cyan]Running: {scenario['name']}[/bold cyan]")
    console.print(f"[dim]Type: Conversational (Multi-turn)[/dim]")

    try:
        success = await runner.run_conversational_test(
            scenario["agent"],
            scenario["function"],
            scenario.get("turns", [])
        )
        return success
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return False


async def main():
    """Main entry point."""
    console.print("[bold cyan]Sygaldry Scenario Runner[/bold cyan]\n")

    # Load scenarios
    scenarios = await load_scenarios()
    if not scenarios:
        return

    runner = AgentRunner()

    # Display available categories
    categories = list(scenarios.keys())
    console.print("[yellow]Available scenario categories:[/yellow]")
    for i, category in enumerate(categories, 1):
        count = len(scenarios[category])
        console.print(f"  {i}. {category.replace('_', ' ').title()} ({count} scenarios)")

    console.print("\n[cyan]Options:[/cyan]")
    console.print("  Enter category number to run all scenarios in that category")
    console.print("  Enter 'all' to run ALL scenarios")
    console.print("  Enter 'q' to quit")

    choice = input("\nYour choice: ").strip()

    if choice.lower() == 'q':
        return
    elif choice.lower() == 'all':
        # Run all scenarios
        results = {}
        for category, category_scenarios in scenarios.items():
            console.print(f"\n{'='*60}")
            console.print(f"[bold yellow]{category.replace('_', ' ').title()}[/bold yellow]")
            console.print('='*60)

            category_results = []

            if category == "conversational_scenarios":
                for scenario in category_scenarios:
                    success = await run_conversational_scenario(runner, scenario)
                    category_results.append((scenario["name"], success))
                    await asyncio.sleep(1)
            else:
                for scenario in category_scenarios:
                    success = await run_scenario(runner, scenario, category)
                    category_results.append((scenario["name"], success))
                    await asyncio.sleep(1)

            results[category] = category_results

        # Print summary
        print_summary(results)

    elif choice.isdigit() and 1 <= int(choice) <= len(categories):
        # Run scenarios in selected category
        category = categories[int(choice) - 1]
        category_scenarios = scenarios[category]

        console.print(f"\n[yellow]Running {category.replace('_', ' ').title()}[/yellow]")
        console.print(f"[dim]{len(category_scenarios)} scenarios[/dim]\n")

        results = []

        if category == "conversational_scenarios":
            for scenario in category_scenarios:
                success = await run_conversational_scenario(runner, scenario)
                results.append((scenario["name"], success))
                await asyncio.sleep(1)
        else:
            for scenario in category_scenarios:
                success = await run_scenario(runner, scenario, category)
                results.append((scenario["name"], success))
                await asyncio.sleep(1)

        # Print category summary
        print_category_summary(category, results)

    else:
        console.print("[red]Invalid choice![/red]")


def print_category_summary(category: str, results: list):
    """Print summary for a category."""
    console.print(f"\n{'='*60}")
    console.print(f"[bold cyan]{category.replace('_', ' ').title()} - Summary[/bold cyan]")
    console.print('='*60)

    for name, success in results:
        status = "[green]✓ PASS[/green]" if success else "[red]✗ FAIL[/red]"
        console.print(f"{status} - {name}")

    passed = sum(1 for _, s in results if s)
    console.print(f"\n[cyan]Passed: {passed}/{len(results)}[/cyan]")


def print_summary(results: dict):
    """Print overall summary."""
    console.print(f"\n{'='*60}")
    console.print("[bold cyan]Overall Summary[/bold cyan]")
    console.print('='*60)

    total_passed = 0
    total_tests = 0

    for category, category_results in results.items():
        passed = sum(1 for _, s in category_results if s)
        total = len(category_results)
        total_passed += passed
        total_tests += total

        rate = (passed / total * 100) if total > 0 else 0
        console.print(f"\n[yellow]{category.replace('_', ' ').title()}[/yellow]")
        console.print(f"  Passed: {passed}/{total} ({rate:.0f}%)")

        for name, success in category_results:
            status = "[green]✓[/green]" if success else "[red]✗[/red]"
            console.print(f"    {status} {name}")

    overall_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    console.print(f"\n{'='*60}")
    console.print(f"[bold cyan]Total: {total_passed}/{total_tests} ({overall_rate:.0f}%)[/bold cyan]")
    console.print('='*60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[cyan]Interrupted by user[/cyan]")
