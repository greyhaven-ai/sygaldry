"""Hyperliquid autonomous trading agent with comprehensive strategy execution and risk management."""

from .agent import (
    HyperliquidTradingAgent,
    MarketAnalysis,
    AutonomousStrategyPlan,
    TradeDecision,
    trade_autonomous,
    trade_with_strategy,
)
from .strategies import (
    StrategyType,
    TradingStrategy,
    TradingSignal,
    SignalStrength,
    TimeFrame,
    StrategyPerformance,
    get_strategy_by_type,
    get_trend_following_strategy,
    get_mean_reversion_strategy,
    get_funding_arbitrage_strategy,
    get_breakout_strategy,
    get_momentum_strategy,
    get_grid_trading_strategy,
)
from .risk_manager import (
    RiskManager,
    RiskParams,
    RiskCheckResult,
    PortfolioRisk,
    PositionRisk,
)
from .state_manager import (
    StateManager,
    TradeRecord,
    PerformanceSnapshot,
)
from .interactive_agent import (
    InteractiveHyperliquidAgent,
    run_interactive_trading,
)
from .agent_control import (
    AgentController,
    AgentCommand,
    AgentResponse,
    CommandType,
    AgentStatus,
    InteractiveAgentSession,
)
from .self_reflection import (
    SelfReflectionEngine,
    PerformanceReview,
    StrategyAdaptation,
    EnvironmentContext,
)
from .terminal_interface import (
    TerminalInterface,
    run_terminal_interface,
)
from .mcp_client import (
    ExaMCPClient,
    MCPTool,
    MCPResponse,
    quick_exa_search,
)

__all__ = [
    # Agent
    "HyperliquidTradingAgent",
    "MarketAnalysis",
    "AutonomousStrategyPlan",
    "TradeDecision",
    "trade_autonomous",
    "trade_with_strategy",
    # Interactive Agent
    "InteractiveHyperliquidAgent",
    "run_interactive_trading",
    # Agent Control
    "AgentController",
    "AgentCommand",
    "AgentResponse",
    "CommandType",
    "AgentStatus",
    "InteractiveAgentSession",
    # Self-Reflection
    "SelfReflectionEngine",
    "PerformanceReview",
    "StrategyAdaptation",
    "EnvironmentContext",
    # Terminal Interface
    "TerminalInterface",
    "run_terminal_interface",
    # MCP Client
    "ExaMCPClient",
    "MCPTool",
    "MCPResponse",
    "quick_exa_search",
    # Strategies
    "StrategyType",
    "TradingStrategy",
    "TradingSignal",
    "SignalStrength",
    "TimeFrame",
    "StrategyPerformance",
    "get_strategy_by_type",
    "get_trend_following_strategy",
    "get_mean_reversion_strategy",
    "get_funding_arbitrage_strategy",
    "get_breakout_strategy",
    "get_momentum_strategy",
    "get_grid_trading_strategy",
    # Risk Management
    "RiskManager",
    "RiskParams",
    "RiskCheckResult",
    "PortfolioRisk",
    "PositionRisk",
    # State Management
    "StateManager",
    "TradeRecord",
    "PerformanceSnapshot",
]
