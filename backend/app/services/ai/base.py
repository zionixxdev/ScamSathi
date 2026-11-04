"""Provider abstraction for the optional contextual AI layer.

The interface is deliberately tiny: an AI provider may add a bounded score
adjustment and a short rationale, nothing else.  It can never replace the
deterministic rule result, and the application works fully without any provider.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class AIInsight:
    used: bool = False
    provider: str | None = None
    rationale: str | None = None
    score_adjustment: int = 0
    note: str | None = None


class AIProvider(Protocol):
    name: str

    async def analyze(self, *, text: str, category: str, score: int) -> AIInsight: ...


class NullProvider:
    """Used when no AI provider is configured or the key is missing."""

    name = "none"

    async def analyze(self, *, text: str, category: str, score: int) -> AIInsight:
        return AIInsight(
            used=False,
            provider=None,
            rationale=None,
            score_adjustment=0,
            note="No contextual AI provider is configured. This result comes from the local rule and NLP engine alone.",
        )
