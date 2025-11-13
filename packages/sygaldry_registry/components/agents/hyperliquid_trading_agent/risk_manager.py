"""Risk management system for Hyperliquid trading agent.

This module provides comprehensive risk management including position sizing,
stop losses, circuit breakers, and portfolio risk controls.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Optional
from pydantic import BaseModel, Field


class RiskParams(BaseModel):
    """Risk management parameters."""

    # Position limits
    max_position_size_pct: float = Field(0.2, description="Maximum position size as % of capital (e.g., 0.2 = 20%)")
    max_positions: int = Field(3, description="Maximum concurrent positions")
    max_leverage: float = Field(5.0, description="Maximum allowed leverage")

    # Loss limits
    max_daily_loss_pct: float = Field(0.05, description="Maximum daily loss as % of capital (e.g., 0.05 = 5%)")
    max_total_loss_pct: float = Field(0.20, description="Maximum total loss from starting capital (e.g., 0.20 = 20%)")
    stop_loss_pct: float = Field(0.02, description="Default stop loss % (e.g., 0.02 = 2%)")

    # Trade limits
    min_trade_size_usd: float = Field(10.0, description="Minimum trade size in USD")
    max_trade_size_usd: float = Field(10000.0, description="Maximum trade size in USD")
    require_approval_above_usd: Optional[float] = Field(None, description="Require human approval for trades above this value")

    # Circuit breaker
    circuit_breaker_enabled: bool = Field(True, description="Enable circuit breaker on large losses")
    circuit_breaker_loss_pct: float = Field(0.10, description="Circuit breaker triggers at this loss % (e.g., 0.10 = 10%)")
    circuit_breaker_cooldown_hours: int = Field(24, description="Hours to wait after circuit breaker trips")

    # Position management
    use_stop_loss: bool = Field(True, description="Use stop losses on all positions")
    use_take_profit: bool = Field(True, description="Use take profit orders")
    trailing_stop_enabled: bool = Field(False, description="Enable trailing stop losses")
    partial_close_enabled: bool = Field(False, description="Enable partial position closes at targets")

    # Portfolio limits
    max_correlated_exposure: float = Field(0.5, description="Max exposure to correlated assets (e.g., 0.5 = 50%)")
    diversification_required: bool = Field(True, description="Require diversification across markets")


class RiskCheckResult(BaseModel):
    """Result of a risk check."""

    approved: bool = Field(..., description="Whether the action is approved")
    reason: str = Field(..., description="Reason for approval/rejection")
    warnings: list[str] = Field(default_factory=list, description="Warning messages")
    suggested_adjustments: dict[str, Any] = Field(default_factory=dict, description="Suggested parameter adjustments")
    requires_approval: bool = Field(False, description="Requires human approval")


class PositionRisk(BaseModel):
    """Risk assessment for a position."""

    coin: str = Field(..., description="Trading pair")
    position_size_usd: float = Field(..., description="Position size in USD")
    position_size_pct: float = Field(..., description="Position size as % of capital")
    leverage: float = Field(..., description="Position leverage")
    risk_amount_usd: float = Field(..., description="Amount at risk (to stop loss)")
    risk_pct: float = Field(..., description="Risk as % of capital")
    stop_loss_price: Optional[float] = Field(None, description="Stop loss price")
    liquidation_distance_pct: Optional[float] = Field(None, description="Distance to liquidation as %")
    within_limits: bool = Field(..., description="Whether position is within risk limits")
    issues: list[str] = Field(default_factory=list, description="Risk issues identified")


class PortfolioRisk(BaseModel):
    """Overall portfolio risk assessment."""

    total_positions: int = Field(..., description="Number of open positions")
    total_exposure_usd: float = Field(..., description="Total exposure in USD")
    total_exposure_pct: float = Field(..., description="Total exposure as % of capital")
    average_leverage: float = Field(..., description="Average portfolio leverage")
    daily_pnl: float = Field(..., description="Today's P&L")
    daily_pnl_pct: float = Field(..., description="Today's P&L as %")
    total_pnl: float = Field(..., description="Total P&L from start")
    total_pnl_pct: float = Field(..., description="Total P&L as %")
    circuit_breaker_active: bool = Field(False, description="Whether circuit breaker is active")
    circuit_breaker_until: Optional[datetime] = Field(None, description="Circuit breaker active until")
    within_limits: bool = Field(..., description="Whether portfolio is within risk limits")
    issues: list[str] = Field(default_factory=list, description="Portfolio risk issues")


class RiskManager:
    """Risk management system for trading operations."""

    def __init__(self, risk_params: RiskParams, starting_capital: float):
        """Initialize risk manager.

        Args:
            risk_params: Risk management parameters
            starting_capital: Starting capital in USD
        """
        self.risk_params = risk_params
        self.starting_capital = starting_capital
        self.circuit_breaker_triggered_at: Optional[datetime] = None

    def check_new_position(
        self,
        coin: str,
        size_usd: float,
        entry_price: float,
        stop_loss_price: Optional[float],
        current_capital: float,
        current_positions: int,
        leverage: float = 1.0,
    ) -> RiskCheckResult:
        """Check if a new position meets risk requirements.

        Args:
            coin: Trading pair
            size_usd: Position size in USD
            entry_price: Entry price
            stop_loss_price: Stop loss price (optional)
            current_capital: Current account capital
            current_positions: Number of current open positions
            leverage: Position leverage

        Returns:
            RiskCheckResult with approval status and details
        """
        warnings = []
        issues = []
        adjustments = {}

        # Check circuit breaker
        if self.is_circuit_breaker_active():
            return RiskCheckResult(
                approved=False,
                reason="Circuit breaker is active due to excessive losses",
                warnings=[f"Circuit breaker active until {self.circuit_breaker_triggered_at + timedelta(hours=self.risk_params.circuit_breaker_cooldown_hours)}"],
            )

        # Check position count
        if current_positions >= self.risk_params.max_positions:
            return RiskCheckResult(
                approved=False,
                reason=f"Maximum positions limit reached ({self.risk_params.max_positions})",
                warnings=[f"Close some positions before opening new ones"],
            )

        # Check position size
        position_size_pct = size_usd / current_capital
        if position_size_pct > self.risk_params.max_position_size_pct:
            issues.append(f"Position size {position_size_pct:.1%} exceeds maximum {self.risk_params.max_position_size_pct:.1%}")
            suggested_size = current_capital * self.risk_params.max_position_size_pct
            adjustments["suggested_size_usd"] = suggested_size
            warnings.append(f"Consider reducing position size to ${suggested_size:.2f}")

        # Check trade size limits
        if size_usd < self.risk_params.min_trade_size_usd:
            return RiskCheckResult(
                approved=False,
                reason=f"Trade size ${size_usd:.2f} below minimum ${self.risk_params.min_trade_size_usd:.2f}",
            )

        if size_usd > self.risk_params.max_trade_size_usd:
            return RiskCheckResult(
                approved=False,
                reason=f"Trade size ${size_usd:.2f} exceeds maximum ${self.risk_params.max_trade_size_usd:.2f}",
            )

        # Check leverage
        if leverage > self.risk_params.max_leverage:
            issues.append(f"Leverage {leverage}x exceeds maximum {self.risk_params.max_leverage}x")
            adjustments["suggested_leverage"] = self.risk_params.max_leverage

        # Check stop loss
        requires_approval = False
        if self.risk_params.use_stop_loss and not stop_loss_price:
            warnings.append("No stop loss specified - this is risky")
            adjustments["suggested_stop_loss"] = entry_price * (1 - self.risk_params.stop_loss_pct)

        # Calculate risk amount
        risk_amount = 0
        if stop_loss_price:
            risk_pct = abs(entry_price - stop_loss_price) / entry_price
            risk_amount = size_usd * risk_pct
            risk_amount_pct = risk_amount / current_capital

            if risk_amount_pct > self.risk_params.stop_loss_pct * 2:  # More than 2x normal risk
                warnings.append(f"Risk amount {risk_amount_pct:.1%} is high")

        # Check if approval required
        if self.risk_params.require_approval_above_usd and size_usd > self.risk_params.require_approval_above_usd:
            requires_approval = True
            warnings.append(f"Trade size ${size_usd:.2f} requires human approval")

        # Determine if approved
        approved = len(issues) == 0
        if not approved:
            reason = "; ".join(issues)
        elif requires_approval:
            reason = "Trade meets risk limits but requires approval due to size"
        else:
            reason = "Trade meets all risk requirements"

        return RiskCheckResult(
            approved=approved,
            reason=reason,
            warnings=warnings,
            suggested_adjustments=adjustments,
            requires_approval=requires_approval,
        )

    def check_portfolio_risk(
        self,
        current_capital: float,
        positions: list[dict[str, Any]],
        daily_pnl: float,
        total_pnl: float,
    ) -> PortfolioRisk:
        """Check overall portfolio risk.

        Args:
            current_capital: Current account capital
            positions: List of open positions
            daily_pnl: Today's profit/loss
            total_pnl: Total profit/loss from start

        Returns:
            PortfolioRisk assessment
        """
        issues = []

        # Calculate exposure
        total_exposure = sum(pos.get("size", 0) * pos.get("mark_price", 0) for pos in positions)
        total_exposure_pct = total_exposure / current_capital if current_capital > 0 else 0

        # Calculate average leverage
        avg_leverage = total_exposure / current_capital if current_capital > 0 else 0

        # Calculate P&L percentages
        daily_pnl_pct = daily_pnl / current_capital if current_capital > 0 else 0
        total_pnl_pct = total_pnl / self.starting_capital if self.starting_capital > 0 else 0

        # Check daily loss limit
        if self.risk_params.max_daily_loss_pct > 0 and daily_pnl_pct < -self.risk_params.max_daily_loss_pct:
            issues.append(f"Daily loss {daily_pnl_pct:.1%} exceeds limit {-self.risk_params.max_daily_loss_pct:.1%}")

        # Check total loss limit
        if self.risk_params.max_total_loss_pct > 0 and total_pnl_pct < -self.risk_params.max_total_loss_pct:
            issues.append(f"Total loss {total_pnl_pct:.1%} exceeds limit {-self.risk_params.max_total_loss_pct:.1%}")

        # Check circuit breaker
        circuit_breaker_active = False
        circuit_breaker_until = None
        if self.risk_params.circuit_breaker_enabled and daily_pnl_pct < -self.risk_params.circuit_breaker_loss_pct:
            if not self.circuit_breaker_triggered_at:
                self.circuit_breaker_triggered_at = datetime.now()
            circuit_breaker_active = True
            circuit_breaker_until = self.circuit_breaker_triggered_at + timedelta(hours=self.risk_params.circuit_breaker_cooldown_hours)
            issues.append(f"Circuit breaker triggered! Daily loss {daily_pnl_pct:.1%} exceeds {-self.risk_params.circuit_breaker_loss_pct:.1%}")

        # Check leverage
        if avg_leverage > self.risk_params.max_leverage:
            issues.append(f"Average leverage {avg_leverage:.1f}x exceeds maximum {self.risk_params.max_leverage}x")

        within_limits = len(issues) == 0

        return PortfolioRisk(
            total_positions=len(positions),
            total_exposure_usd=total_exposure,
            total_exposure_pct=total_exposure_pct,
            average_leverage=avg_leverage,
            daily_pnl=daily_pnl,
            daily_pnl_pct=daily_pnl_pct,
            total_pnl=total_pnl,
            total_pnl_pct=total_pnl_pct,
            circuit_breaker_active=circuit_breaker_active,
            circuit_breaker_until=circuit_breaker_until,
            within_limits=within_limits,
            issues=issues,
        )

    def calculate_position_size(
        self,
        capital: float,
        entry_price: float,
        stop_loss_price: float,
        risk_pct: Optional[float] = None,
    ) -> float:
        """Calculate position size based on risk parameters.

        Uses the formula: Position Size = (Capital * Risk%) / (Entry Price - Stop Loss)

        Args:
            capital: Available capital
            entry_price: Entry price
            stop_loss_price: Stop loss price
            risk_pct: Risk percentage (uses default if not specified)

        Returns:
            Recommended position size in base currency
        """
        if risk_pct is None:
            risk_pct = self.risk_params.stop_loss_pct

        risk_amount = capital * risk_pct
        price_risk = abs(entry_price - stop_loss_price)

        if price_risk == 0:
            return 0

        position_size = risk_amount / price_risk

        # Apply maximum position size limit
        max_size = capital * self.risk_params.max_position_size_pct / entry_price
        position_size = min(position_size, max_size)

        return position_size

    def calculate_stop_loss(
        self,
        entry_price: float,
        side: str,
        stop_loss_pct: Optional[float] = None,
    ) -> float:
        """Calculate stop loss price.

        Args:
            entry_price: Entry price
            side: Position side ("long" or "short")
            stop_loss_pct: Stop loss percentage (uses default if not specified)

        Returns:
            Stop loss price
        """
        if stop_loss_pct is None:
            stop_loss_pct = self.risk_params.stop_loss_pct

        if side == "long":
            return entry_price * (1 - stop_loss_pct)
        else:  # short
            return entry_price * (1 + stop_loss_pct)

    def calculate_take_profit(
        self,
        entry_price: float,
        side: str,
        risk_reward_ratio: float = 2.0,
        stop_loss_pct: Optional[float] = None,
    ) -> float:
        """Calculate take profit price based on risk-reward ratio.

        Args:
            entry_price: Entry price
            side: Position side ("long" or "short")
            risk_reward_ratio: Risk-reward ratio (e.g., 2.0 = 2:1)
            stop_loss_pct: Stop loss percentage (uses default if not specified)

        Returns:
            Take profit price
        """
        if stop_loss_pct is None:
            stop_loss_pct = self.risk_params.stop_loss_pct

        reward_pct = stop_loss_pct * risk_reward_ratio

        if side == "long":
            return entry_price * (1 + reward_pct)
        else:  # short
            return entry_price * (1 - reward_pct)

    def is_circuit_breaker_active(self) -> bool:
        """Check if circuit breaker is currently active.

        Returns:
            True if circuit breaker is active
        """
        if not self.circuit_breaker_triggered_at:
            return False

        cooldown_end = self.circuit_breaker_triggered_at + timedelta(hours=self.risk_params.circuit_breaker_cooldown_hours)
        if datetime.now() > cooldown_end:
            self.circuit_breaker_triggered_at = None
            return False

        return True

    def reset_circuit_breaker(self):
        """Manually reset the circuit breaker."""
        self.circuit_breaker_triggered_at = None
