#!/usr/bin/env python3
"""
Kelly Criterion Implementation for Dynamic Bet Sizing.

The Kelly Formula: f = (bp - q) / b
Where:
  f = Fraction of bankroll to bet
  b = Odds offered (ratio of win to loss)
  p = Probability of winning
  q = Probability of losing (1 - p)

Practical application:
  - Safe Kelly: f * 0.25 (reduces variance, increases safety)
  - Full Kelly: f * 1.0 (aggressive growth)
  - Half Kelly: f * 0.50 (balanced)
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Tuple


class KellyCriterion:
    """Manages dynamic bet sizing using Kelly Formula."""

    def __init__(self, initial_bankroll: float = 1000.0, kelly_fraction: float = 0.25):
        """
        Initialize Kelly Criterion manager.

        Args:
            initial_bankroll: Starting capital in currency units
            kelly_fraction: Multiplier on Kelly formula (0.25 = 25% Kelly, safer)
        """
        self.initial_bankroll = initial_bankroll
        self.current_bankroll = initial_bankroll
        self.kelly_fraction = kelly_fraction
        self.history: List[Dict] = []
        self.stats_file = os.path.join("logs", "kelly_stats.json")
        self._load_history()

    def _load_history(self) -> None:
        """Load previous session's bankroll history."""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.current_bankroll = data.get("current_bankroll", self.initial_bankroll)
                    self.history = data.get("history", [])
            except Exception as e:
                print(f"⚠️ Could not load Kelly history: {e}")

    def _save_history(self) -> None:
        """Persist bankroll history."""
        os.makedirs("logs", exist_ok=True)
        try:
            with open(self.stats_file, "w", encoding="utf-8") as f:
                json.dump(
                    {"current_bankroll": self.current_bankroll, "history": self.history},
                    f,
                    indent=2,
                )
        except Exception as e:
            print(f"⚠️ Could not save Kelly history: {e}")

    def calculate_bet_size(
        self, win_rate: float, odds: float = 1.9, min_bet: float = 1.0
    ) -> float:
        """
        Calculate optimal bet size using Kelly Criterion.

        Args:
            win_rate: Historical win rate (0.0 to 1.0)
            odds: Decimal odds for the bet (default 1.9 for Blaze 2-outcome)
            min_bet: Minimum bet size to enforce

        Returns:
            Recommended bet size in currency units
        """
        # Validate inputs
        if not (0 <= win_rate <= 1):
            return min_bet

        if odds <= 1:
            return min_bet

        # Kelly Formula: f = (bp - q) / b
        b = odds - 1  # Convert to ratio format
        p = win_rate
        q = 1 - win_rate

        kelly_fraction_raw = (b * p - q) / b

        # Apply safety multiplier
        kelly_fraction_applied = kelly_fraction_raw * self.kelly_fraction

        # Clamp to safe bounds [0.5%, 5%]
        kelly_fraction_applied = max(0.005, min(0.05, kelly_fraction_applied))

        # Calculate bet size
        bet_size = self.current_bankroll * kelly_fraction_applied

        return max(bet_size, min_bet)

    def record_bet(
        self, bet_size: float, win: bool, payout_odds: float = 2.0
    ) -> Dict:
        """
        Record a bet result and update bankroll.

        Args:
            bet_size: Amount bet
            win: Whether the bet won
            payout_odds: Payout multiplier if won (default 2.0 for Blaze doubles)

        Returns:
            Updated bankroll state
        """
        if win:
            profit = bet_size * (payout_odds - 1)
            self.current_bankroll += profit
            result = "WIN"
        else:
            self.current_bankroll -= bet_size
            profit = -bet_size
            result = "LOSS"

        entry = {
            "timestamp": datetime.now().isoformat(),
            "bet_size": bet_size,
            "result": result,
            "profit": profit,
            "bankroll_after": self.current_bankroll,
        }

        self.history.append(entry)
        self._save_history()

        return entry

    def get_stats(self) -> Dict:
        """
        Calculate current session statistics.

        Returns:
            Dict with total profit, win rate, largest win/loss, etc.
        """
        if not self.history:
            return {
                "total_bets": 0,
                "total_wins": 0,
                "total_losses": 0,
                "win_rate": 0.0,
                "total_profit": 0.0,
                "current_bankroll": self.current_bankroll,
                "roi": 0.0,
            }

        wins = sum(1 for h in self.history if h["result"] == "WIN")
        losses = len(self.history) - wins
        total_profit = self.current_bankroll - self.initial_bankroll
        roi = (total_profit / self.initial_bankroll * 100) if self.initial_bankroll > 0 else 0.0

        return {
            "total_bets": len(self.history),
            "total_wins": wins,
            "total_losses": losses,
            "win_rate": wins / len(self.history) if self.history else 0.0,
            "total_profit": total_profit,
            "current_bankroll": self.current_bankroll,
            "roi_percent": roi,
            "largest_bet": max((h["bet_size"] for h in self.history), default=0.0),
            "avg_bet": sum(h["bet_size"] for h in self.history) / len(self.history)
            if self.history
            else 0.0,
        }

    def reset_session(self) -> None:
        """Reset bankroll to initial value (start new session)."""
        self.current_bankroll = self.initial_bankroll
        self.history = []
        self._save_history()
