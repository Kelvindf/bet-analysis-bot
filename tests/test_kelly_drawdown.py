#!/usr/bin/env python3
"""
Unit Tests for Kelly Criterion and Drawdown Manager.

Tests cover:
  - Kelly formula calculations with various win rates
  - Bankroll updates and history tracking
  - Drawdown detection and pause logic
  - State persistence across sessions
"""

import sys
import os
import json
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from strategies.kelly_criterion import KellyCriterion
from scripts.drawdown_manager import DrawdownManager


def test_kelly_criterion_basic():
    """Test basic Kelly calculation."""
    # Clean up state files
    state_file = os.path.join("logs", "kelly_stats.json")
    if os.path.exists(state_file):
        os.remove(state_file)
    
    kelly = KellyCriterion(initial_bankroll=1000.0, kelly_fraction=0.25)

    # Win rate 60%, odds 1.9
    bet_size = kelly.calculate_bet_size(win_rate=0.6, odds=1.9)

    assert bet_size > 0, "Bet size should be positive"
    assert bet_size < 100, "Bet size should be capped (0.5-5% of bankroll)"
    print(f"✅ Test kelly_criterion_basic: bet_size={bet_size:.2f} for 60% WR")


def test_kelly_bet_recording():
    """Test bet recording and bankroll updates."""
    kelly = KellyCriterion(initial_bankroll=1000.0)

    # Record a winning bet
    result_win = kelly.record_bet(bet_size=50.0, win=True, payout_odds=2.0)
    assert result_win["result"] == "WIN"
    assert kelly.current_bankroll > 1000.0, "Bankroll should increase on win"
    print(f"✅ Test kelly_bet_recording (WIN): bankroll={kelly.current_bankroll:.2f}")

    # Record a losing bet
    kelly.record_bet(bet_size=30.0, win=False, payout_odds=2.0)
    assert kelly.current_bankroll < 1000.0 + 50.0, "Bankroll should decrease on loss"
    print(f"✅ Test kelly_bet_recording (LOSS): bankroll={kelly.current_bankroll:.2f}")


def test_kelly_statistics():
    """Test statistics calculation."""
    kelly = KellyCriterion(initial_bankroll=1000.0, kelly_fraction=0.5)

    # Simulate 10 bets: 7 wins, 3 losses
    for i in range(7):
        kelly.record_bet(bet_size=10.0, win=True, payout_odds=2.0)
    for i in range(3):
        kelly.record_bet(bet_size=10.0, win=False, payout_odds=2.0)

    stats = kelly.get_stats()
    assert stats["total_bets"] == 10
    assert stats["total_wins"] == 7
    assert stats["total_losses"] == 3
    assert abs(stats["win_rate"] - 0.7) < 0.01
    print(f"✅ Test kelly_statistics: WR={stats['win_rate']:.2%}, ROI={stats['roi_percent']:.2f}%")


def test_drawdown_detection():
    """Test drawdown threshold detection."""
    drawdown = DrawdownManager(initial_bankroll=1000.0, max_drawdown_percent=5.0)

    # Simulate losses: lose 60 (6% loss - should trigger pause)
    status = drawdown.update_bankroll(940.0)

    assert status["drawdown_percent"] >= 5.0, "Should detect drawdown >= 5%"
    assert drawdown.is_paused is True, "Should pause when drawdown threshold exceeded"
    assert status["action"] == "PAUSED"
    print(f"✅ Test drawdown_detection: {status['drawdown_percent']:.2f}% loss → PAUSED")


def test_drawdown_recovery():
    """Test drawdown recovery tracking."""
    drawdown = DrawdownManager(initial_bankroll=1000.0, max_drawdown_percent=5.0)

    # Trigger pause
    drawdown.update_bankroll(940.0)
    assert drawdown.is_paused is True

    # Manual resume
    resume_status = drawdown.manual_resume()
    assert drawdown.is_paused is False
    print(f"✅ Test drawdown_recovery: Resumed trading. Bankroll={resume_status['bankroll']}")


def test_drawdown_status():
    """Test drawdown status reporting."""
    drawdown = DrawdownManager(initial_bankroll=1000.0, max_drawdown_percent=10.0)

    # Simulate peak and drawdown
    drawdown.update_bankroll(1200.0)  # Reach peak
    drawdown.update_bankroll(1050.0)  # Drawdown: 150 (12.5%)

    status = drawdown.get_status()
    assert status["peak_bankroll"] == 1200.0
    assert status["current_bankroll"] == 1050.0
    assert status["drawdown_amount"] == 150.0
    assert status["is_paused"] is True
    print(f"✅ Test drawdown_status: Peak={status['peak_bankroll']}, Current={status['current_bankroll']}, Drawdown={status['drawdown_percent']:.2f}%")


def run_all_tests():
    """Run all unit tests."""
    print("\n" + "=" * 60)
    print("UNIT TESTS: Kelly Criterion & Drawdown Manager")
    print("=" * 60 + "\n")

    tests = [
        test_kelly_criterion_basic,
        test_kelly_bet_recording,
        test_kelly_statistics,
        test_drawdown_detection,
        test_drawdown_recovery,
        test_drawdown_status,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test_func.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__}: Unexpected error: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60 + "\n")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
