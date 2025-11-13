"""Hyperliquid trading tools for DEX interactions.

This module provides comprehensive tools for interacting with the Hyperliquid DEX,
including account management, market data retrieval, order execution, and position management.
"""

from __future__ import annotations

import os
from decimal import Decimal
from typing import Any, Literal, Optional
from pydantic import BaseModel, Field
from mirascope import llm

try:
    from hyperliquid.info import Info
    from hyperliquid.exchange import Exchange
    from hyperliquid.utils import constants
    HYPERLIQUID_AVAILABLE = True
except ImportError:
    HYPERLIQUID_AVAILABLE = False
    Info = None
    Exchange = None
    constants = None


# Pydantic models for structured data
class HyperliquidAccount(BaseModel):
    """Account information from Hyperliquid."""

    account_value: float = Field(..., description="Total account value in USD")
    equity: float = Field(..., description="Account equity")
    margin_used: float = Field(..., description="Margin currently used")
    withdrawable: float = Field(..., description="Withdrawable balance")
    account_leverage: float = Field(..., description="Current account leverage")


class HyperliquidPosition(BaseModel):
    """Position information."""

    coin: str = Field(..., description="Trading pair/coin")
    side: Literal["long", "short"] = Field(..., description="Position side")
    size: float = Field(..., description="Position size")
    entry_price: float = Field(..., description="Average entry price")
    mark_price: float = Field(..., description="Current mark price")
    unrealized_pnl: float = Field(..., description="Unrealized profit/loss")
    liquidation_price: Optional[float] = Field(None, description="Liquidation price")
    leverage: float = Field(..., description="Position leverage")
    margin: float = Field(..., description="Position margin")


class HyperliquidOrder(BaseModel):
    """Order information."""

    order_id: str = Field(..., description="Unique order ID")
    coin: str = Field(..., description="Trading pair/coin")
    side: Literal["buy", "sell"] = Field(..., description="Order side")
    order_type: Literal["market", "limit", "stop"] = Field(..., description="Order type")
    size: float = Field(..., description="Order size")
    price: Optional[float] = Field(None, description="Limit price (if applicable)")
    filled: float = Field(0.0, description="Filled amount")
    status: str = Field(..., description="Order status")


class HyperliquidMarketData(BaseModel):
    """Market data for a trading pair."""

    coin: str = Field(..., description="Trading pair/coin")
    mark_price: float = Field(..., description="Current mark price")
    index_price: float = Field(..., description="Index price")
    funding_rate: float = Field(..., description="Current funding rate")
    open_interest: float = Field(..., description="Open interest")
    volume_24h: float = Field(..., description="24h trading volume")
    price_change_24h: float = Field(..., description="24h price change percentage")


class OrderBookLevel(BaseModel):
    """Order book price level."""

    price: float = Field(..., description="Price level")
    size: float = Field(..., description="Total size at this price")


class OrderBook(BaseModel):
    """Order book data."""

    coin: str = Field(..., description="Trading pair/coin")
    bids: list[OrderBookLevel] = Field(..., description="Bid levels")
    asks: list[OrderBookLevel] = Field(..., description="Ask levels")
    timestamp: int = Field(..., description="Timestamp of snapshot")


# Configuration
def get_hyperliquid_config() -> dict[str, Any]:
    """Get Hyperliquid configuration from environment."""
    use_testnet = os.getenv("HYPERLIQUID_USE_TESTNET", "true").lower() == "true"

    return {
        "wallet_address": os.getenv("HYPERLIQUID_WALLET_ADDRESS"),
        "api_secret": os.getenv("HYPERLIQUID_API_SECRET"),
        "use_testnet": use_testnet,
        "api_url": constants.TESTNET_API_URL if use_testnet else constants.MAINNET_API_URL,
    }


def get_info_client(testnet: bool = True) -> Info:
    """Get Hyperliquid Info client for read-only operations."""
    if not HYPERLIQUID_AVAILABLE:
        raise ImportError("hyperliquid-python-sdk is not installed. Install with: pip install hyperliquid-python-sdk")

    api_url = constants.TESTNET_API_URL if testnet else constants.MAINNET_API_URL
    return Info(api_url, skip_ws=True)


def get_exchange_client(testnet: bool = True) -> Exchange:
    """Get Hyperliquid Exchange client for trading operations."""
    if not HYPERLIQUID_AVAILABLE:
        raise ImportError("hyperliquid-python-sdk is not installed. Install with: pip install hyperliquid-python-sdk")

    config = get_hyperliquid_config()

    if not config["api_secret"]:
        raise ValueError("HYPERLIQUID_API_SECRET environment variable is required for trading operations")

    if not config["wallet_address"]:
        raise ValueError("HYPERLIQUID_WALLET_ADDRESS environment variable is required")

    api_url = constants.TESTNET_API_URL if testnet else constants.MAINNET_API_URL

    # Initialize Exchange with wallet and secret
    exchange = Exchange(
        wallet=config["wallet_address"],
        secret=config["api_secret"],
        base_url=api_url,
    )

    return exchange


# Tool functions
@llm.tool
def check_account_balance(testnet: bool = True) -> dict[str, Any]:
    """Check account balance and margin information on Hyperliquid.

    Args:
        testnet: Whether to use testnet (default: True)

    Returns:
        Account balance and margin information
    """
    config = get_hyperliquid_config()
    info = get_info_client(testnet=testnet)

    if not config["wallet_address"]:
        return {"error": "HYPERLIQUID_WALLET_ADDRESS not configured"}

    try:
        user_state = info.user_state(config["wallet_address"])

        # Extract relevant information
        margin_summary = user_state.get("marginSummary", {})

        account_info = HyperliquidAccount(
            account_value=float(margin_summary.get("accountValue", 0)),
            equity=float(margin_summary.get("totalMarginUsed", 0)),
            margin_used=float(margin_summary.get("totalMarginUsed", 0)),
            withdrawable=float(user_state.get("withdrawable", 0)),
            account_leverage=float(margin_summary.get("accountValue", 1)) / max(float(margin_summary.get("totalMarginUsed", 1)), 1),
        )

        return account_info.model_dump()
    except Exception as e:
        return {"error": f"Failed to fetch account balance: {str(e)}"}


@llm.tool
def get_open_positions(testnet: bool = True) -> list[dict[str, Any]]:
    """Get all open positions on Hyperliquid.

    Args:
        testnet: Whether to use testnet (default: True)

    Returns:
        List of open positions
    """
    config = get_hyperliquid_config()
    info = get_info_client(testnet=testnet)

    if not config["wallet_address"]:
        return [{"error": "HYPERLIQUID_WALLET_ADDRESS not configured"}]

    try:
        user_state = info.user_state(config["wallet_address"])
        positions_data = user_state.get("assetPositions", [])

        positions = []
        for pos_data in positions_data:
            position = pos_data.get("position", {})
            if float(position.get("szi", 0)) != 0:  # Only include non-zero positions
                size = float(position.get("szi", 0))
                side = "long" if size > 0 else "short"

                pos = HyperliquidPosition(
                    coin=pos_data.get("coin", ""),
                    side=side,
                    size=abs(size),
                    entry_price=float(position.get("entryPx", 0)),
                    mark_price=float(position.get("positionValue", 0)) / abs(size) if size != 0 else 0,
                    unrealized_pnl=float(position.get("unrealizedPnl", 0)),
                    liquidation_price=float(position.get("liquidationPx")) if position.get("liquidationPx") else None,
                    leverage=float(position.get("leverage", {}).get("value", 1)),
                    margin=float(position.get("marginUsed", 0)),
                )
                positions.append(pos.model_dump())

        return positions
    except Exception as e:
        return [{"error": f"Failed to fetch positions: {str(e)}"}]


@llm.tool
def get_market_data(coin: str, testnet: bool = True) -> dict[str, Any]:
    """Get current market data for a trading pair.

    Args:
        coin: Trading pair symbol (e.g., "BTC", "ETH")
        testnet: Whether to use testnet (default: True)

    Returns:
        Current market data including price, funding rate, volume
    """
    info = get_info_client(testnet=testnet)

    try:
        # Get all mids (market data)
        all_mids = info.all_mids()

        # Get metadata
        meta = info.meta()

        # Find the coin in metadata
        coin_meta = None
        for universe_item in meta.get("universe", []):
            if universe_item.get("name") == coin:
                coin_meta = universe_item
                break

        if not coin_meta:
            return {"error": f"Coin {coin} not found"}

        # Get price from all_mids
        mark_price = float(all_mids.get(coin, 0))

        # Get funding rate and other data
        funding_info = info.funding_history(coin, startTime=0, endTime=None)
        current_funding = funding_info[-1] if funding_info else {}

        market_data = HyperliquidMarketData(
            coin=coin,
            mark_price=mark_price,
            index_price=mark_price,  # Simplified; actual index price may differ
            funding_rate=float(current_funding.get("funding", 0)),
            open_interest=float(coin_meta.get("openInterest", 0)),
            volume_24h=float(coin_meta.get("dayNtlVlm", 0)),
            price_change_24h=float(coin_meta.get("prevDayPx", 0)),
        )

        return market_data.model_dump()
    except Exception as e:
        return {"error": f"Failed to fetch market data: {str(e)}"}


@llm.tool
def get_funding_rate(coin: str, testnet: bool = True) -> dict[str, Any]:
    """Get current and historical funding rates for a trading pair.

    Args:
        coin: Trading pair symbol (e.g., "BTC", "ETH")
        testnet: Whether to use testnet (default: True)

    Returns:
        Current funding rate and recent history
    """
    info = get_info_client(testnet=testnet)

    try:
        funding_history = info.funding_history(coin, startTime=0, endTime=None)

        if not funding_history:
            return {"error": f"No funding history found for {coin}"}

        current = funding_history[-1] if funding_history else {}
        recent = funding_history[-10:] if len(funding_history) >= 10 else funding_history

        return {
            "coin": coin,
            "current_funding_rate": float(current.get("funding", 0)),
            "timestamp": current.get("time", 0),
            "recent_rates": [float(f.get("funding", 0)) for f in recent],
            "average_recent": sum(float(f.get("funding", 0)) for f in recent) / len(recent) if recent else 0,
        }
    except Exception as e:
        return {"error": f"Failed to fetch funding rate: {str(e)}"}


@llm.tool
def get_order_book(coin: str, depth: int = 10, testnet: bool = True) -> dict[str, Any]:
    """Get order book for a trading pair.

    Args:
        coin: Trading pair symbol (e.g., "BTC", "ETH")
        depth: Number of price levels to return (default: 10)
        testnet: Whether to use testnet (default: True)

    Returns:
        Order book with bids and asks
    """
    info = get_info_client(testnet=testnet)

    try:
        l2_snapshot = info.l2_snapshot(coin)

        bids = [
            OrderBookLevel(price=float(level["px"]), size=float(level["sz"]))
            for level in l2_snapshot.get("levels", [])[:depth]
            if level.get("n") > 0  # Buy orders
        ]

        asks = [
            OrderBookLevel(price=float(level["px"]), size=float(level["sz"]))
            for level in l2_snapshot.get("levels", [])[:depth]
            if level.get("n") < 0  # Sell orders
        ]

        order_book = OrderBook(
            coin=coin,
            bids=bids,
            asks=asks,
            timestamp=l2_snapshot.get("time", 0),
        )

        return order_book.model_dump()
    except Exception as e:
        return {"error": f"Failed to fetch order book: {str(e)}"}


@llm.tool
def place_market_order(
    coin: str,
    side: Literal["buy", "sell"],
    size: float,
    reduce_only: bool = False,
    testnet: bool = True,
) -> dict[str, Any]:
    """Place a market order on Hyperliquid.

    Args:
        coin: Trading pair symbol (e.g., "BTC", "ETH")
        side: Order side - "buy" or "sell"
        size: Order size in base currency
        reduce_only: If True, only reduce existing position
        testnet: Whether to use testnet (default: True)

    Returns:
        Order execution result
    """
    try:
        exchange = get_exchange_client(testnet=testnet)

        # Place market order
        is_buy = side == "buy"
        result = exchange.market_order(
            coin=coin,
            is_buy=is_buy,
            sz=size,
            reduce_only=reduce_only,
        )

        return {
            "success": True,
            "order_result": result,
            "coin": coin,
            "side": side,
            "size": size,
            "type": "market",
        }
    except Exception as e:
        return {"success": False, "error": f"Failed to place market order: {str(e)}"}


@llm.tool
def place_limit_order(
    coin: str,
    side: Literal["buy", "sell"],
    size: float,
    price: float,
    reduce_only: bool = False,
    post_only: bool = False,
    testnet: bool = True,
) -> dict[str, Any]:
    """Place a limit order on Hyperliquid.

    Args:
        coin: Trading pair symbol (e.g., "BTC", "ETH")
        side: Order side - "buy" or "sell"
        size: Order size in base currency
        price: Limit price
        reduce_only: If True, only reduce existing position
        post_only: If True, order will only be a maker order
        testnet: Whether to use testnet (default: True)

    Returns:
        Order placement result
    """
    try:
        exchange = get_exchange_client(testnet=testnet)

        # Place limit order
        is_buy = side == "buy"
        result = exchange.limit_order(
            coin=coin,
            is_buy=is_buy,
            sz=size,
            limit_px=price,
            reduce_only=reduce_only,
            post_only=post_only,
        )

        return {
            "success": True,
            "order_result": result,
            "coin": coin,
            "side": side,
            "size": size,
            "price": price,
            "type": "limit",
        }
    except Exception as e:
        return {"success": False, "error": f"Failed to place limit order: {str(e)}"}


@llm.tool
def cancel_order(coin: str, order_id: int, testnet: bool = True) -> dict[str, Any]:
    """Cancel an open order on Hyperliquid.

    Args:
        coin: Trading pair symbol (e.g., "BTC", "ETH")
        order_id: Order ID to cancel
        testnet: Whether to use testnet (default: True)

    Returns:
        Cancellation result
    """
    try:
        exchange = get_exchange_client(testnet=testnet)

        result = exchange.cancel(coin=coin, oid=order_id)

        return {
            "success": True,
            "cancel_result": result,
            "coin": coin,
            "order_id": order_id,
        }
    except Exception as e:
        return {"success": False, "error": f"Failed to cancel order: {str(e)}"}


@llm.tool
def close_position(
    coin: str,
    testnet: bool = True,
) -> dict[str, Any]:
    """Close an entire position on Hyperliquid using a market order.

    Args:
        coin: Trading pair symbol (e.g., "BTC", "ETH")
        testnet: Whether to use testnet (default: True)

    Returns:
        Position close result
    """
    try:
        # First get the current position
        positions = get_open_positions(testnet=testnet)

        target_position = None
        for pos in positions:
            if pos.get("coin") == coin:
                target_position = pos
                break

        if not target_position:
            return {"success": False, "error": f"No open position found for {coin}"}

        # Determine close side (opposite of position)
        position_side = target_position["side"]
        close_side = "sell" if position_side == "long" else "buy"
        size = target_position["size"]

        # Place market order to close
        result = place_market_order(
            coin=coin,
            side=close_side,
            size=size,
            reduce_only=True,
            testnet=testnet,
        )

        return {
            "success": result.get("success", False),
            "close_result": result,
            "position_closed": {
                "coin": coin,
                "side": position_side,
                "size": size,
            },
        }
    except Exception as e:
        return {"success": False, "error": f"Failed to close position: {str(e)}"}
