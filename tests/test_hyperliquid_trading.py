"""Unit tests for Hyperliquid trading agent and tools.

These tests cover the core functionality without requiring actual API connections.
"""

import pytest
from datetime import datetime
from packages.sygaldry_registry.components.agents.hyperliquid_trading_agent import (
    RiskManager,
    RiskParams,
    StateManager,
    TradingStrategy,
    StrategyType,
    get_trend_following_strategy,
    get_mean_reversion_strategy,
)


class TestRiskManager:
    """Tests for RiskManager functionality."""

    def test_risk_manager_initialization(self):
        """Test risk manager initializes correctly."""
        risk_params = RiskParams()
        risk_manager = RiskManager(risk_params, starting_capital=1000.0)

        assert risk_manager.starting_capital == 1000.0
        assert risk_manager.risk_params == risk_params
        assert risk_manager.circuit_breaker_triggered_at is None

    def test_calculate_position_size(self):
        """Test position size calculation."""
        risk_params = RiskParams(max_position_size_pct=0.2, stop_loss_pct=0.02)
        risk_manager = RiskManager(risk_params, starting_capital=1000.0)

        # Calculate position size for $50,000 BTC with 2% stop loss
        position_size = risk_manager.calculate_position_size(
            capital=1000.0, entry_price=50000.0, stop_loss_price=49000.0  # $1000 risk per BTC
        )

        # With 2% risk on $1000 capital = $20 risk
        # Price risk = $1000
        # Position size should be $20 / $1000 = 0.02 BTC
        assert 0.015 < position_size < 0.025  # Allow some rounding

    def test_calculate_stop_loss(self):
        """Test stop loss calculation."""
        risk_params = RiskParams(stop_loss_pct=0.02)
        risk_manager = RiskManager(risk_params, starting_capital=1000.0)

        # Long position stop loss
        entry_price = 50000.0
        stop_loss_long = risk_manager.calculate_stop_loss(entry_price, "long")
        assert stop_loss_long == 50000.0 * 0.98  # 2% below entry

        # Short position stop loss
        stop_loss_short = risk_manager.calculate_stop_loss(entry_price, "short")
        assert stop_loss_short == 50000.0 * 1.02  # 2% above entry

    def test_calculate_take_profit(self):
        """Test take profit calculation."""
        risk_params = RiskParams(stop_loss_pct=0.02)
        risk_manager = RiskManager(risk_params, starting_capital=1000.0)

        # Long position with 2:1 risk-reward
        entry_price = 50000.0
        take_profit_long = risk_manager.calculate_take_profit(entry_price, "long", risk_reward_ratio=2.0)
        expected = 50000.0 * 1.04  # 4% above entry (2x the 2% stop)
        assert abs(take_profit_long - expected) < 0.01

    def test_check_new_position_approved(self):
        """Test position check approves valid trades."""
        risk_params = RiskParams(
            max_position_size_pct=0.2, max_positions=3, max_trade_size_usd=500.0, use_stop_loss=True
        )
        risk_manager = RiskManager(risk_params, starting_capital=1000.0)

        result = risk_manager.check_new_position(
            coin="BTC",
            size_usd=100.0,  # 10% of capital
            entry_price=50000.0,
            stop_loss_price=49000.0,
            current_capital=1000.0,
            current_positions=1,
        )

        assert result.approved is True
        assert result.requires_approval is False

    def test_check_new_position_rejected_size(self):
        """Test position check rejects oversized positions."""
        risk_params = RiskParams(max_position_size_pct=0.2, max_positions=3)
        risk_manager = RiskManager(risk_params, starting_capital=1000.0)

        result = risk_manager.check_new_position(
            coin="BTC",
            size_usd=300.0,  # 30% of capital - too large
            entry_price=50000.0,
            stop_loss_price=49000.0,
            current_capital=1000.0,
            current_positions=1,
        )

        assert result.approved is False
        assert "exceeds maximum" in result.reason

    def test_check_new_position_max_positions(self):
        """Test position check respects maximum position limit."""
        risk_params = RiskParams(max_positions=2)
        risk_manager = RiskManager(risk_params, starting_capital=1000.0)

        result = risk_manager.check_new_position(
            coin="BTC",
            size_usd=100.0,
            entry_price=50000.0,
            stop_loss_price=49000.0,
            current_capital=1000.0,
            current_positions=2,  # Already at max
        )

        assert result.approved is False
        assert "Maximum positions limit" in result.reason

    def test_circuit_breaker(self):
        """Test circuit breaker activation."""
        risk_params = RiskParams(circuit_breaker_enabled=True, circuit_breaker_loss_pct=0.10, max_daily_loss_pct=0.05)
        risk_manager = RiskManager(risk_params, starting_capital=1000.0)

        # Simulate large daily loss
        portfolio_risk = risk_manager.check_portfolio_risk(
            current_capital=900.0,  # Lost $100
            positions=[],
            daily_pnl=-120.0,  # -12% daily loss (triggers circuit breaker)
            total_pnl=-100.0,
        )

        assert portfolio_risk.circuit_breaker_active is True
        assert len(portfolio_risk.issues) > 0

        # Verify circuit breaker is active
        assert risk_manager.is_circuit_breaker_active() is True


class TestStateManager:
    """Tests for StateManager functionality."""

    @pytest.fixture
    def state_manager(self, tmp_path):
        """Create a temporary state manager."""
        db_path = tmp_path / "test_state.db"
        return StateManager(str(db_path))

    def test_state_manager_initialization(self, state_manager):
        """Test state manager initializes with database."""
        # Should create database without errors
        assert state_manager.db_path.endswith("test_state.db")

    def test_record_trade_entry_and_exit(self, state_manager):
        """Test recording trade entry and exit."""
        # Record entry
        trade_id = state_manager.record_trade_entry(
            coin="BTC",
            side="long",
            entry_price=50000.0,
            size=0.1,
            strategy="Trend Following",
            entry_reason="MA crossover",
            stop_loss=49000.0,
            take_profit=52000.0,
        )

        assert trade_id > 0

        # Check active positions
        active = state_manager.get_active_positions()
        assert len(active) == 1
        assert active[0]["coin"] == "BTC"

        # Record exit
        state_manager.record_trade_exit(coin="BTC", exit_price=51000.0, exit_reason="Take profit hit", fees=5.0)

        # Check active positions again
        active = state_manager.get_active_positions()
        assert len(active) == 0

        # Check trade history
        trades = state_manager.get_trade_history(limit=1)
        assert len(trades) == 1
        assert trades[0].coin == "BTC"
        assert trades[0].exit_price == 51000.0
        assert trades[0].pnl is not None

    def test_calculate_performance_metrics(self, state_manager):
        """Test performance metrics calculation."""
        # Record some trades
        trades = [
            ("BTC", "long", 50000.0, 51000.0, 0.1),  # Win
            ("ETH", "long", 3000.0, 2900.0, 1.0),  # Loss
            ("SOL", "long", 100.0, 105.0, 5.0),  # Win
        ]

        for coin, side, entry, exit, size in trades:
            state_manager.record_trade_entry(
                coin=coin,
                side=side,
                entry_price=entry,
                size=size,
                strategy="Test",
                entry_reason="Test entry",
            )
            state_manager.record_trade_exit(coin=coin, exit_price=exit, exit_reason="Test exit")

        metrics = state_manager.calculate_performance_metrics()

        assert metrics["total_trades"] == 3
        assert metrics["winning_trades"] == 2
        assert metrics["losing_trades"] == 1
        assert 60 < metrics["win_rate"] < 70  # ~66.7%
        assert metrics["total_pnl"] > 0  # Net positive


class TestTradingStrategies:
    """Tests for trading strategy configurations."""

    def test_get_trend_following_strategy(self):
        """Test trend following strategy creation."""
        strategy = get_trend_following_strategy(markets=["BTC", "ETH"], risk_per_trade=0.02)

        assert strategy.type == StrategyType.TREND_FOLLOWING
        assert strategy.markets == ["BTC", "ETH"]
        assert strategy.risk_per_trade == 0.02
        assert strategy.use_stop_loss is True
        assert strategy.use_trailing_stop is True

    def test_get_mean_reversion_strategy(self):
        """Test mean reversion strategy creation."""
        strategy = get_mean_reversion_strategy(markets=["ETH"], risk_per_trade=0.015)

        assert strategy.type == StrategyType.MEAN_REVERSION
        assert strategy.markets == ["ETH"]
        assert strategy.risk_per_trade == 0.015
        assert "rsi_period" in strategy.parameters

    def test_custom_strategy_creation(self):
        """Test custom strategy creation."""
        strategy = TradingStrategy(
            type=StrategyType.CUSTOM,
            name="My Custom Strategy",
            description="Test strategy",
            markets=["BTC"],
            entry_rules="Buy on dips",
            exit_rules="Sell on spikes",
            risk_per_trade=0.01,
            max_positions=2,
        )

        assert strategy.type == StrategyType.CUSTOM
        assert strategy.name == "My Custom Strategy"
        assert strategy.markets == ["BTC"]
        assert strategy.max_positions == 2


# Integration test (requires environment setup)
@pytest.mark.integration
class TestHyperliquidIntegration:
    """Integration tests requiring actual environment setup."""

    @pytest.mark.skip(reason="Requires API credentials and testnet access")
    async def test_market_analysis(self):
        """Test market analysis with real API."""
        from packages.sygaldry_registry.components.agents.hyperliquid_trading_agent import HyperliquidTradingAgent

        agent = HyperliquidTradingAgent(starting_capital=1000.0, testnet=True)

        analysis = await agent.analyze_market("BTC")

        assert analysis.coin == "BTC"
        assert analysis.trend in ["bullish", "bearish", "neutral"]
        assert 0 <= analysis.confidence <= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
