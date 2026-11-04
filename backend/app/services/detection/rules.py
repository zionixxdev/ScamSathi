"""Rule based detection.

Deterministic, explainable and dependency free: every warning sign is a
compiled regular expression with a fixed weight, category and human readable
explanation.  The rule layer is the backbone of the engine - the NLP and AI
layers only add context on top of it.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.core.security import redact
from app.services.detection.lexicons import MITIGATORS, RULES


@dataclass(frozen=True)
class Indicator:
    id: str
    label: str
    category: str
    weight: int
    severity: str
    evidence: str = ""
    explanation: str = ""
    source: str = "rule"

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "label": self.label,
            "category": self.category,
            "weight": self.weight,
            "severity": self.severity,
            "evidence": self.evidence,
            "explanation": self.explanation,
            "source": self.source,
        }


@dataclass(frozen=True)
class _CompiledRule:
    id: str
    label: str
    category: str
    weight: int
    severity: str
    explanation: str
    patterns: tuple[re.Pattern[str], ...]


def _compile(rules: tuple[dict, ...]) -> tuple[_CompiledRule, ...]:
    return tuple(
        _CompiledRule(
            id=rule["id"],
            label=rule["label"],
            category=rule.get("category", "unknown"),
            weight=int(rule["weight"]),
            severity=rule.get("severity", "medium"),
            explanation=rule.get("explanation", ""),
            patterns=tuple(re.compile(p, re.IGNORECASE | re.MULTILINE) for p in rule["patterns"]),
        )
        for rule in rules
    )


COMPILED_RULES = _compile(RULES)
COMPILED_MITIGATORS = _compile(MITIGATORS)

_EVIDENCE_WINDOW = 34

# "Never share this OTP" must not be read as a request to share an OTP.
_NEGATION_RE = re.compile(
    r"(?:\bnever|\bnot|\bdon'?t|\bdo not|\bno|\bavoid|\bwithout|\bmat\b|\bkabhi|\bन)\W*$",
    re.IGNORECASE,
)


def _is_negated(text: str, start: int) -> bool:
    window = text[max(0, start - 22) : start]
    return bool(_NEGATION_RE.search(window))


def _evidence(text: str, start: int, end: int) -> str:
    left = max(0, start - _EVIDENCE_WINDOW)
    right = min(len(text), end + _EVIDENCE_WINDOW)
    snippet = " ".join(text[left:right].split())
    if left > 0:
        snippet = "\u2026" + snippet
    if right < len(text):
        snippet = snippet + "\u2026"
    return redact(snippet)[:220]


def match_indicators(text: str) -> list[Indicator]:
    """Return every warning sign matched in ``text`` (one entry per rule)."""
    found: list[Indicator] = []
    for rule in COMPILED_RULES:
        for pattern in rule.patterns:
            match = pattern.search(text)
            if match and _is_negated(text, match.start()):
                continue
            if match:
                found.append(
                    Indicator(
                        id=rule.id,
                        label=rule.label,
                        category=rule.category,
                        weight=rule.weight,
                        severity=rule.severity,
                        evidence=_evidence(text, match.start(), match.end()),
                        explanation=rule.explanation,
                        source="rule",
                    )
                )
                break
    return found


def match_mitigators(text: str, *, sender_id: str | None = None) -> list[Indicator]:
    """Return legitimate-signal mitigators (they lower the risk score)."""
    found: list[Indicator] = []
    for rule in COMPILED_MITIGATORS:
        if rule.id == "verified_sender_id":
            if not sender_id:
                continue
            haystack = sender_id.strip()
        else:
            if rule.id == "short_message_no_ask" and match_indicators(text):
                continue
            haystack = text
        for pattern in rule.patterns:
            match = pattern.search(haystack)
            if match:
                found.append(
                    Indicator(
                        id=rule.id,
                        label=rule.label,
                        category="mitigator",
                        weight=rule.weight,
                        severity="info",
                        evidence=_evidence(haystack, match.start(), match.end()) if haystack is text else redact(haystack),
                        explanation=rule.explanation,
                        source="rule",
                    )
                )
                break
    return found
