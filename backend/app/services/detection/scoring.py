"""Risk scoring.

The score is a heuristic urgency/risk index on a 0-100 scale.  It is **not** a
calibrated probability that a message is fraudulent, and the API never presents
it as one.

Aggregation uses diminishing returns: the first warning sign matters most, and
each additional sign adds less, so a message cannot reach 100 by piling up weak
signals alone.
"""

from __future__ import annotations

from app.services.detection.rules import Indicator

_DECAY = (1.0, 0.85, 0.72, 0.6, 0.5)
_DECAY_TAIL = 0.4
COHERENCE_BONUS = {2: 4, 3: 8}

# Combinations that are far stronger together than apart (a lure plus a fee, a
# threat plus a credential request, ...).  Scam kits reuse these templates.
COMBOS: tuple[tuple[frozenset[str], int], ...] = (
    (frozenset({"lottery_lure", "advance_fee"}), 14),
    (frozenset({"job_lure", "advance_fee"}), 10),
    (frozenset({"credential_request", "urgency_pressure"}), 10),
    (frozenset({"threat_of_block", "kyc_update"}), 8),
    (frozenset({"lottery_lure", "credential_request"}), 8),
    (frozenset({"digital_arrest", "secrecy_pressure"}), 12),
    (frozenset({"account_takeover_setup", "fake_support"}), 12),
    (frozenset({"upi_collect_or_pin", "credential_request"}), 10),
    (frozenset({"investment_returns", "vip_group_lure"}), 12),
    (frozenset({"investment_returns", "channel_redirect"}), 8),
)
MAX_COMBO_BONUS = 28


def aggregate(
    indicators: list[Indicator],
    mitigators: list[Indicator],
    *,
    top_category_score: int,
    indicators_in_top_category: int,
    url_risk: int = 0,
) -> int:
    weights = sorted((ind.weight for ind in indicators), reverse=True)
    raw = 0.0
    for index, weight in enumerate(weights):
        factor = _DECAY[index] if index < len(_DECAY) else _DECAY_TAIL
        raw += weight * factor

    raw += COHERENCE_BONUS.get(min(indicators_in_top_category, 3), 0) if indicators_in_top_category >= 2 else 0

    matched_ids = {ind.id for ind in indicators}
    combo_bonus = sum(bonus for ids, bonus in COMBOS if ids <= matched_ids)
    raw += min(MAX_COMBO_BONUS, combo_bonus)

    # A malicious link is a strong, independent signal.
    if url_risk >= 50:
        raw += 14
    elif url_risk >= 25:
        raw += 7

    raw -= sum(mit.weight for mit in mitigators)
    return int(round(max(0.0, min(100.0, raw))))


def confidence(
    *,
    indicators: list[Indicator],
    mitigators: list[Indicator],
    text_length: int,
    ambiguous: bool,
    score: int,
) -> float:
    """How sure the engine is about its own reading of the message.

    This is separate from the risk score: a clean, ordinary message can be read
    with high confidence, and a very short ambiguous one with low confidence.
    """
    if not indicators:
        value = 0.62 - (0.15 if text_length < 25 else 0.0)
        return round(max(0.05, min(0.95, value)), 2)

    value = 0.40 + min(0.30, 0.055 * len(indicators))
    if text_length >= 60:
        value += 0.10
    elif text_length < 25:
        value -= 0.12
    if mitigators:
        value += 0.06
    if ambiguous:
        value -= 0.12
    return round(max(0.05, min(0.95, value)), 2)


def risk_level(score: int, confidence_value: float) -> str:
    if confidence_value < 0.45 and 12 <= score < 50:
        return "Uncertain"
    if score >= 75:
        return "Critical"
    if score >= 50:
        return "High"
    if score >= 25:
        return "Medium"
    return "Low"
