#!/bin/bash
#
# Quick script to test Sygaldry agents with logging
#

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Sygaldry Agent Testing with Comprehensive Logging"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

# Check for API keys
if [ -z "$OPENAI_API_KEY" ] && [ -z "$ANTHROPIC_API_KEY" ] && [ -z "$GOOGLE_API_KEY" ]; then
    echo "❌ Error: No API keys found"
    echo
    echo "Please set at least one API key:"
    echo "  export OPENAI_API_KEY='your-key'"
    echo "  export ANTHROPIC_API_KEY='your-key'"
    echo "  export GOOGLE_API_KEY='your-key'"
    echo
    exit 1
fi

# Show available API keys
echo "✅ API Keys Configured:"
[ -n "$OPENAI_API_KEY" ] && echo "   - OpenAI"
[ -n "$ANTHROPIC_API_KEY" ] && echo "   - Anthropic"
[ -n "$GOOGLE_API_KEY" ] && echo "   - Google"
echo

# Menu
echo "What would you like to do?"
echo
echo "  1. Run quick agent demos (simple_agent_demo.py)"
echo "  2. Run full interactive tester (interactive_agent_tester.py)"
echo "  3. Run scenario tests with logging (run_scenarios.py)"
echo "  4. Run custom tests with logging (agent_runner_with_logging.py)"
echo "  5. View audit logs (view_logs.py)"
echo "  6. Open Jupyter notebook"
echo
read -p "Enter choice [1-6]: " choice

case $choice in
    1)
        echo
        echo "Running simple agent demos..."
        python3 examples/simple_agent_demo.py
        ;;
    2)
        echo
        echo "Running interactive agent tester..."
        python3 examples/interactive_agent_tester.py
        ;;
    3)
        echo
        echo "Running scenario tests with logging..."
        python3 examples/run_scenarios.py
        echo
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "Tests complete! Logs saved to: logs/audit/"
        echo
        read -p "Would you like to view the logs now? [y/N]: " view_logs
        if [[ "$view_logs" =~ ^[Yy]$ ]]; then
            python3 examples/view_logs.py
        fi
        ;;
    4)
        echo
        echo "Running custom tests with logging..."
        python3 examples/agent_runner_with_logging.py
        ;;
    5)
        echo
        echo "Opening log viewer..."
        python3 examples/view_logs.py
        ;;
    6)
        echo
        echo "Opening Jupyter notebook..."
        cd examples
        jupyter notebook agent_testing_notebook.ipynb
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Done!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
