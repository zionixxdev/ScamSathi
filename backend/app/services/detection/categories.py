"""Scam category classification.

Each indicator votes for its category with its weight.  The winning category is
the highest scoring one; close runners up are reported as secondary so the user
can see the ambiguity instead of a false sense of certainty.
"""

from __future__ import annotations

from collections import defaultdict

from app.services.detection.lexicons import CATEGORIES
from app.services.detection.rules import Indicator

MIN_CATEGORY_SCORE = 12
AMBIGUITY_RATIO = 0.8


def category_label(key: str) -> str:
    return CATEGORIES.get(key, CATEGORIES["unknown"])


def rank_categories(indicators: list[Indicator]) -> tuple[str, int, list[tuple[str, int]]]:
    """Return (top category key, top score, secondary categories)."""
    scores: dict[str, int] = defaultdict(int)
    for indicator in indicators:
        if indicator.category in CATEGORIES and indicator.category != "unknown":
            scores[indicator.category] += indicator.weight

    if not scores:
        return "unknown", 0, []

    ordered = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    top_key, top_score = ordered[0]
    if top_score < MIN_CATEGORY_SCORE:
        return "unknown", top_score, []

    secondary = [
        (key, score)
        for key, score in ordered[1:3]
        if score >= MIN_CATEGORY_SCORE * 0.5 and score >= top_score * AMBIGUITY_RATIO
    ]
    return top_key, top_score, secondary
