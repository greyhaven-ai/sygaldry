"""State management and persistence for Hyperliquid trading agent.

This module provides SQLite-based persistence for tracking positions, trades,
and performance metrics over time.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from pydantic import BaseModel, Field


class TradeRecord(BaseModel):
    """Record of a completed trade."""

    id: Optional[int] = Field(None, description="Database ID")
    coin: str = Field(..., description="Trading pair")
    side: str = Field(..., description="Trade side (long/short)")
    entry_time: datetime = Field(..., description="Entry timestamp")
    exit_time: Optional[datetime] = Field(None, description="Exit timestamp")
    entry_price: float = Field(..., description="Entry price")
    exit_price: Optional[float] = Field(None, description="Exit price")
    size: float = Field(..., description="Position size")
    pnl: Optional[float] = Field(None, description="Realized P&L")
    pnl_pct: Optional[float] = Field(None, description="P&L percentage")
    fees: float = Field(0.0, description="Trading fees")
    strategy: str = Field(..., description="Strategy used")
    entry_reason: str = Field(..., description="Reason for entry")
    exit_reason: Optional[str] = Field(None, description="Reason for exit")
    stop_loss: Optional[float] = Field(None, description="Stop loss price")
    take_profit: Optional[float] = Field(None, description="Take profit price")


class PerformanceSnapshot(BaseModel):
    """Performance snapshot at a point in time."""

    timestamp: datetime = Field(..., description="Snapshot timestamp")
    capital: float = Field(..., description="Current capital")
    total_pnl: float = Field(..., description="Total P&L")
    daily_pnl: float = Field(..., description="Daily P&L")
    open_positions: int = Field(..., description="Number of open positions")
    total_trades: int = Field(..., description="Total trades")
    win_rate: float = Field(..., description="Win rate percentage")
    sharpe_ratio: float = Field(..., description="Sharpe ratio")
    max_drawdown: float = Field(..., description="Maximum drawdown")


class StateManager:
    """Manages persistent state for the trading agent using SQLite."""

    def __init__(self, db_path: str = "hyperliquid_trading_state.db"):
        """Initialize state manager.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize database tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Trades table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                coin TEXT NOT NULL,
                side TEXT NOT NULL,
                entry_time TEXT NOT NULL,
                exit_time TEXT,
                entry_price REAL NOT NULL,
                exit_price REAL,
                size REAL NOT NULL,
                pnl REAL,
                pnl_pct REAL,
                fees REAL DEFAULT 0,
                strategy TEXT NOT NULL,
                entry_reason TEXT NOT NULL,
                exit_reason TEXT,
                stop_loss REAL,
                take_profit REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Performance snapshots table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS performance_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                capital REAL NOT NULL,
                total_pnl REAL NOT NULL,
                daily_pnl REAL NOT NULL,
                open_positions INTEGER NOT NULL,
                total_trades INTEGER NOT NULL,
                win_rate REAL NOT NULL,
                sharpe_ratio REAL NOT NULL,
                max_drawdown REAL NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Agent configuration table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS agent_config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Active positions table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS active_positions (
                coin TEXT PRIMARY KEY,
                side TEXT NOT NULL,
                size REAL NOT NULL,
                entry_price REAL NOT NULL,
                entry_time TEXT NOT NULL,
                stop_loss REAL,
                take_profit REAL,
                strategy TEXT NOT NULL,
                entry_reason TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        conn.commit()
        conn.close()

    def record_trade_entry(
        self,
        coin: str,
        side: str,
        entry_price: float,
        size: float,
        strategy: str,
        entry_reason: str,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
    ) -> int:
        """Record a new trade entry.

        Args:
            coin: Trading pair
            side: Trade side
            entry_price: Entry price
            size: Position size
            strategy: Strategy name
            entry_reason: Reason for entry
            stop_loss: Stop loss price
            take_profit: Take profit price

        Returns:
            Trade ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        entry_time = datetime.now().isoformat()

        cursor.execute(
            """
            INSERT INTO trades (coin, side, entry_time, entry_price, size, strategy, entry_reason, stop_loss, take_profit)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (coin, side, entry_time, entry_price, size, strategy, entry_reason, stop_loss, take_profit),
        )

        # Also add to active positions
        cursor.execute(
            """
            INSERT OR REPLACE INTO active_positions
            (coin, side, size, entry_price, entry_time, stop_loss, take_profit, strategy, entry_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (coin, side, size, entry_price, entry_time, stop_loss, take_profit, strategy, entry_reason),
        )

        trade_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return trade_id

    def record_trade_exit(
        self,
        coin: str,
        exit_price: float,
        exit_reason: str,
        fees: float = 0.0,
    ):
        """Record a trade exit.

        Args:
            coin: Trading pair
            exit_price: Exit price
            exit_reason: Reason for exit
            fees: Trading fees
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        exit_time = datetime.now().isoformat()

        # Get the most recent open trade for this coin
        cursor.execute(
            """
            SELECT id, entry_price, size, side FROM trades
            WHERE coin = ? AND exit_time IS NULL
            ORDER BY entry_time DESC LIMIT 1
        """,
            (coin,),
        )

        result = cursor.fetchone()
        if not result:
            conn.close()
            return

        trade_id, entry_price, size, side = result

        # Calculate P&L
        if side == "long":
            pnl = (exit_price - entry_price) * size - fees
        else:  # short
            pnl = (entry_price - exit_price) * size - fees

        pnl_pct = (pnl / (entry_price * size)) * 100 if entry_price * size > 0 else 0

        # Update trade
        cursor.execute(
            """
            UPDATE trades
            SET exit_time = ?, exit_price = ?, pnl = ?, pnl_pct = ?, fees = ?, exit_reason = ?
            WHERE id = ?
        """,
            (exit_time, exit_price, pnl, pnl_pct, fees, exit_reason, trade_id),
        )

        # Remove from active positions
        cursor.execute("DELETE FROM active_positions WHERE coin = ?", (coin,))

        conn.commit()
        conn.close()

    def get_active_positions(self) -> list[dict[str, Any]]:
        """Get all active positions.

        Returns:
            List of active positions
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM active_positions")
        rows = cursor.fetchall()

        positions = [dict(row) for row in rows]
        conn.close()

        return positions

    def get_trade_history(self, limit: int = 100, coin: Optional[str] = None) -> list[TradeRecord]:
        """Get trade history.

        Args:
            limit: Maximum number of trades to return
            coin: Filter by coin (optional)

        Returns:
            List of trade records
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if coin:
            cursor.execute(
                """
                SELECT * FROM trades
                WHERE coin = ?
                ORDER BY entry_time DESC
                LIMIT ?
            """,
                (coin, limit),
            )
        else:
            cursor.execute(
                """
                SELECT * FROM trades
                ORDER BY entry_time DESC
                LIMIT ?
            """,
                (limit,),
            )

        rows = cursor.fetchall()
        conn.close()

        trades = []
        for row in rows:
            trade_dict = dict(row)
            # Convert ISO strings back to datetime
            trade_dict["entry_time"] = datetime.fromisoformat(trade_dict["entry_time"])
            if trade_dict["exit_time"]:
                trade_dict["exit_time"] = datetime.fromisoformat(trade_dict["exit_time"])
            trades.append(TradeRecord(**trade_dict))

        return trades

    def save_performance_snapshot(self, snapshot: PerformanceSnapshot):
        """Save a performance snapshot.

        Args:
            snapshot: Performance snapshot to save
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO performance_snapshots
            (timestamp, capital, total_pnl, daily_pnl, open_positions, total_trades, win_rate, sharpe_ratio, max_drawdown)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                snapshot.timestamp.isoformat(),
                snapshot.capital,
                snapshot.total_pnl,
                snapshot.daily_pnl,
                snapshot.open_positions,
                snapshot.total_trades,
                snapshot.win_rate,
                snapshot.sharpe_ratio,
                snapshot.max_drawdown,
            ),
        )

        conn.commit()
        conn.close()

    def get_performance_history(self, days: int = 30) -> list[PerformanceSnapshot]:
        """Get performance history.

        Args:
            days: Number of days of history to retrieve

        Returns:
            List of performance snapshots
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM performance_snapshots
            WHERE timestamp >= datetime('now', '-' || ? || ' days')
            ORDER BY timestamp DESC
        """,
            (days,),
        )

        rows = cursor.fetchall()
        conn.close()

        snapshots = []
        for row in rows:
            snapshot_dict = dict(row)
            snapshot_dict["timestamp"] = datetime.fromisoformat(snapshot_dict["timestamp"])
            snapshots.append(PerformanceSnapshot(**snapshot_dict))

        return snapshots

    def calculate_performance_metrics(self) -> dict[str, Any]:
        """Calculate current performance metrics from trade history.

        Returns:
            Dictionary of performance metrics
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get closed trades
        cursor.execute(
            """
            SELECT * FROM trades
            WHERE exit_time IS NOT NULL
            ORDER BY exit_time DESC
        """
        )

        trades = cursor.fetchall()
        conn.close()

        if not trades:
            return {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0.0,
                "total_pnl": 0.0,
                "average_win": 0.0,
                "average_loss": 0.0,
                "profit_factor": 0.0,
                "largest_win": 0.0,
                "largest_loss": 0.0,
            }

        total_trades = len(trades)
        winning_trades = [t for t in trades if t["pnl"] and t["pnl"] > 0]
        losing_trades = [t for t in trades if t["pnl"] and t["pnl"] < 0]

        total_pnl = sum(t["pnl"] for t in trades if t["pnl"])
        total_wins = sum(t["pnl"] for t in winning_trades)
        total_losses = abs(sum(t["pnl"] for t in losing_trades))

        metrics = {
            "total_trades": total_trades,
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": (len(winning_trades) / total_trades * 100) if total_trades > 0 else 0,
            "total_pnl": total_pnl,
            "average_win": (total_wins / len(winning_trades)) if winning_trades else 0,
            "average_loss": (total_losses / len(losing_trades)) if losing_trades else 0,
            "profit_factor": (total_wins / total_losses) if total_losses > 0 else 0,
            "largest_win": max((t["pnl"] for t in winning_trades), default=0),
            "largest_loss": min((t["pnl"] for t in losing_trades), default=0),
        }

        return metrics

    def set_config(self, key: str, value: str):
        """Set a configuration value.

        Args:
            key: Configuration key
            value: Configuration value
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO agent_config (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """,
            (key, value),
        )

        conn.commit()
        conn.close()

    def get_config(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT value FROM agent_config WHERE key = ?", (key,))
        result = cursor.fetchone()

        conn.close()

        return result[0] if result else default
