#!/usr/bin/env python3
"""
Drawdown Manager - Automatic Trading Pause on Losses.

Protects capital by pausing signal generation when cumulative losses
exceed a specified threshold (e.g., 5-10% of initial bankroll).

Features:
  - Real-time monitoring of drawdown percentage
  - Automatic pause signal when threshold exceeded
  - Resume capability with manual override
  - Detailed logging of pause events
"""

import json
import os
from datetime import datetime
from typing import Dict, Optional


class DrawdownManager:
    """Manages drawdown limits and automatic trading pauses."""

    def __init__(self, initial_bankroll: float = 1000.0, max_drawdown_percent: float = 5.0):
        """
        Initialize Drawdown Manager.

        Args:
            initial_bankroll: Starting capital
            max_drawdown_percent: Maximum acceptable loss percentage before pause (5-10% recommended)
        """
        self.initial_bankroll = initial_bankroll
        self.current_bankroll = initial_bankroll
        self.peak_bankroll = initial_bankroll
        self.max_drawdown_percent = max_drawdown_percent
        self.max_drawdown_amount = (initial_bankroll * max_drawdown_percent) / 100
        self.is_paused = False
        self.pause_history: list = []
        self.state_file = os.path.join("logs", "drawdown_state.json")
        self._load_state()

    def _load_state(self) -> None:
        """Load previous session's drawdown state."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.current_bankroll = data.get("current_bankroll", self.initial_bankroll)
                    self.peak_bankroll = data.get("peak_bankroll", self.initial_bankroll)
                    self.is_paused = data.get("is_paused", False)
                    self.pause_history = data.get("pause_history", [])
            except Exception as e:
                print(f"⚠️ Could not load Drawdown state: {e}")

    def _save_state(self) -> None:
        """Persist drawdown state."""
        os.makedirs("logs", exist_ok=True)
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "current_bankroll": self.current_bankroll,
                        "peak_bankroll": self.peak_bankroll,
                        "is_paused": self.is_paused,
                        "pause_history": self.pause_history,
                    },
                    f,
                    indent=2,
                )
        except Exception as e:
            print(f"⚠️ Could not save Drawdown state: {e}")

    def update_bankroll(self, new_amount: float) -> Dict:
        """
        Update current bankroll and check drawdown limits.

        Args:
            new_amount: Updated bankroll amount

        Returns:
            Dict with current status and any actions taken
        """
        self.current_bankroll = new_amount

        # Track peak (high water mark)
        if new_amount > self.peak_bankroll:
            self.peak_bankroll = new_amount

        # Calculate drawdown
        current_drawdown = self.peak_bankroll - self.current_bankroll
        drawdown_percent = (current_drawdown / self.peak_bankroll * 100) if self.peak_bankroll > 0 else 0

        # Check if threshold exceeded
        should_pause = drawdown_percent >= self.max_drawdown_percent

        status = {
            "current_bankroll": self.current_bankroll,
            "peak_bankroll": self.peak_bankroll,
            "drawdown_amount": current_drawdown,
            "drawdown_percent": round(drawdown_percent, 2),
            "max_threshold": self.max_drawdown_percent,
            "is_paused": self.is_paused,
            "action": "NONE",
        }

        # Pause if necessary
        if should_pause and not self.is_paused:
            self.is_paused = True
            self.pause_history.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "reason": "DRAWDOWN_THRESHOLD_EXCEEDED",
                    "drawdown_percent": drawdown_percent,
                    "bankroll": self.current_bankroll,
                }
            )
            status["action"] = "PAUSED"
            print(f"⚠️ DRAWDOWN LIMIT TRIGGERED: {drawdown_percent:.2f}% loss. Trading PAUSED.")

        # Auto-resume if recovered (optional - conservative: requires explicit resume)
        # Uncomment to enable auto-resume:
        # if drawdown_percent < (self.max_drawdown_percent * 0.8) and self.is_paused:
        #     self.is_paused = False
        #     status["action"] = "RESUMED"

        self._save_state()
        return status

    def manual_resume(self) -> Dict:
        """
        Manually resume trading after drawdown pause.

        Returns:
            Updated status
        """
        if self.is_paused:
            self.is_paused = False
            self.peak_bankroll = self.current_bankroll  # Reset high water mark
            self.pause_history.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "reason": "MANUAL_RESUME",
                    "bankroll": self.current_bankroll,
                }
            )
            self._save_state()
            print(f"✅ Trading RESUMED. New baseline: {self.current_bankroll}")

        return {"is_paused": self.is_paused, "bankroll": self.current_bankroll}

    def reset(self) -> None:
        """Reset drawdown manager for new session."""
        self.current_bankroll = self.initial_bankroll
        self.peak_bankroll = self.initial_bankroll
        self.is_paused = False
        self.pause_history = []
        self._save_state()

    def get_status(self) -> Dict:
        """
        Get current drawdown status.

        Returns:
            Detailed status dict
        """
        current_drawdown = self.peak_bankroll - self.current_bankroll
        drawdown_percent = (current_drawdown / self.peak_bankroll * 100) if self.peak_bankroll > 0 else 0

        return {
            "current_bankroll": self.current_bankroll,
            "peak_bankroll": self.peak_bankroll,
            "drawdown_amount": current_drawdown,
            "drawdown_percent": round(drawdown_percent, 2),
            "max_threshold": self.max_drawdown_percent,
            "is_paused": self.is_paused,
            "pause_count": len(self.pause_history),
            "recovery_needed": round(self.peak_bankroll - self.current_bankroll, 2),
        }
