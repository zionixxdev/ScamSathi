"""Unit tests for scoring maths and the rule layer."""

from __future__ import annotations

from app.services.detection import rules, scoring
from app.services.detection.rules import Indicator


def _indicator(weight: int, category: str = "phishing", id_: str = "x") -> Indicator:
    return Indicator(id=id_, label="l", category=category, weight=weight, severity="high")


def test_diminishing_returns() -> None:
    one = scoring.aggregate([_indicator(30)], [], top_category_score=30, indicators_in_top_category=1)
    two = scoring.aggregate(
        [_indicator(30), _indicator(20)], [], top_category_score=50, indicators_in_top_category=2
    )
    three = scoring.aggregate(
        [_indicator(30), _indicator(20), _indicator(10)], [], top_category_score=60, indicators_in_top_category=3
    )
    assert one == 30
    # Each extra signal adds less than the one before it.
    assert 0 < two - one < 30
    assert 0 < three - two < two - one


def test_score_is_clamped() -> None:
    indicators = [_indicator(40) for _ in range(10)]
    score = scoring.aggregate(indicators, [], top_category_score=400, indicators_in_top_category=10)
    assert score == 100


def test_mitigators_reduce_the_score() -> None:
    base = scoring.aggregate([_indicator(20)], [], top_category_score=20, indicators_in_top_category=1)
    reduced = scoring.aggregate(
        [_indicator(20)], [_indicator(10)], top_category_score=20, indicators_in_top_category=1
    )
    assert reduced < base


def test_risk_level_thresholds() -> None:
    assert scoring.risk_level(10, 0.9) == "Low"
    assert scoring.risk_level(30, 0.9) == "Medium"
    assert scoring.risk_level(60, 0.9) == "High"
    assert scoring.risk_level(90, 0.9) == "Critical"
    assert scoring.risk_level(30, 0.3) == "Uncertain"


def test_negated_credential_request_is_ignored() -> None:
    assert not rules.match_indicators("Never share your OTP or PIN with anyone.")
    assert rules.match_indicators("Please share your OTP with our executive.")
