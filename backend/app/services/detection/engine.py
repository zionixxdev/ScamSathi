"""Hybrid detection engine.

Pipeline: sanitise -> language detection -> rule layer -> NLP layer -> link
analysis -> optional contextual AI -> category -> score -> explanation.

Every stage degrades gracefully: without an AI key or reputation key the engine
still produces a complete, evidence based result.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.config import get_settings
from app.core.security import make_excerpt, sanitize_text
from app.schemas.analysis import (
    AiInsightOut,
    AnalysisResult,
    CategoryOut,
    IndicatorOut,
    MitigatorOut,
    ReputationOut,
    SecondaryCategory,
    UrlAnalysisOut,
    UrlFindingOut,
)
from app.services.ai.base import AIProvider, NullProvider
from app.services.detection import categories, nlp, rules, scoring
from app.services.detection.categories import category_label
from app.services.detection.explain import build_explanation
from app.services.detection.rules import Indicator
from app.services.url.analyzer import UrlReport, analyze_url
from app.services.url.reputation import NoopReputationProvider, ReputationProvider

DISCLAIMER = (
    "The risk score is a heuristic index from 0 to 100, not the probability that a message is "
    "fraudulent. ScamSathi cannot verify senders, phone numbers or websites. Always confirm "
    "through official channels before acting."
)

URL_DISCLAIMER = (
    "This analysis is based on the structure of the link only. ScamSathi never opens the page, "
    "so it cannot see what the site actually does."
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class DetectionEngine:
    def __init__(
        self,
        ai_provider: AIProvider | None = None,
        reputation_provider: ReputationProvider | None = None,
    ) -> None:
        self.ai = ai_provider or NullProvider()
        self.reputation = reputation_provider or NoopReputationProvider()

    # ------------------------------------------------------------------ message
    async def analyze_message(
        self,
        *,
        content: str,
        channel: str = "other",
        language: str = "auto",
        sender_id: str | None = None,
    ) -> AnalysisResult:
        settings = get_settings()
        text = sanitize_text(content, max_chars=settings.max_message_chars)
        detected_language = nlp.detect_language(text)
        explanation_language = detected_language if language in ("auto", None) else language

        indicators = rules.match_indicators(text)
        indicators.extend(nlp.nlp_indicators(text))

        # Link analysis inside the message (lexical only, never fetched).
        url_reports = [analyze_url(u) for u in nlp.extract_urls(text)]
        url_risk = max((report.risk_score for report in url_reports), default=0)
        if url_reports:
            worst = max(url_reports, key=lambda report: report.risk_score)
            for finding in sorted(worst.findings, key=lambda f: f.weight, reverse=True)[:4]:
                indicators.append(
                    Indicator(
                        id=f"url_{finding.id}",
                        label=finding.label,
                        category="malicious_url",
                        weight=min(finding.weight, 24),
                        severity="high" if finding.weight >= 18 else "medium",
                        evidence=f"{worst.host}: {finding.evidence}"[:200],
                        explanation=finding.explanation,
                        source="url",
                    )
                )

        mitigators = rules.match_mitigators(text, sender_id=sender_id)

        # Link findings support the score but must not hijack the category: a
        # fake-KYC SMS with a link is a KYC scam, not a "malicious URL".
        ranking_indicators = [ind for ind in indicators if ind.source != "url"]
        category_key, top_score, secondary = categories.rank_categories(ranking_indicators)
        in_top = sum(1 for ind in ranking_indicators if ind.category == category_key)
        score = scoring.aggregate(
            indicators,
            mitigators,
            top_category_score=top_score,
            indicators_in_top_category=in_top,
            url_risk=url_risk,
        )
        if category_key == "unknown" and url_risk >= 50:
            category_key = "malicious_url"
        if score < 20:
            # A handful of weak signals is not enough to name a category.
            category_key, secondary = "unknown", []
        ambiguous = bool(secondary) and secondary[0][1] >= top_score * 0.8
        conf = scoring.confidence(
            indicators=indicators,
            mitigators=mitigators,
            text_length=len(text),
            ambiguous=ambiguous,
            score=score,
        )

        ai_insight = await self.ai.analyze(text=text, category=category_key, score=score)
        if ai_insight.used and ai_insight.score_adjustment:
            score = max(0, min(100, score + ai_insight.score_adjustment))
        level = scoring.risk_level(score, conf)

        explanation, actions = build_explanation(
            language=explanation_language,
            category_key=category_key,
            score=score,
            level=level,
            indicators=indicators,
            mitigators=mitigators,
            is_url=False,
        )

        return AnalysisResult(
            scan_id=str(uuid.uuid4()),
            scan_type="message",
            channel=channel,
            created_at=_now(),
            risk_score=score,
            risk_level=level,  # type: ignore[arg-type]
            category=CategoryOut(key=category_key, label=category_label(category_key)),
            secondary_categories=[
                SecondaryCategory(key=key, label=category_label(key), score=value)
                for key, value in secondary
            ],
            confidence=conf,
            uncertainty=self._uncertainty(conf, level, explanation_language),
            language=detected_language,
            indicators=[IndicatorOut(**ind.as_dict()) for ind in sorted(indicators, key=lambda i: i.weight, reverse=True)],
            mitigators=[MitigatorOut(id=m.id, label=m.label, explanation=m.explanation) for m in mitigators],
            explanation=explanation,
            recommended_actions=actions,
            excerpt=make_excerpt(text),
            ai=AiInsightOut(
                used=ai_insight.used,
                provider=ai_insight.provider,
                rationale=ai_insight.rationale,
                score_adjustment=ai_insight.score_adjustment,
                note=ai_insight.note,
            ),
            url_analysis=self._url_payload(url_reports[0], ReputationOut(checked=False)) if url_reports else None,
            disclaimer=DISCLAIMER,
        )

    # ---------------------------------------------------------------------- url
    async def analyze_url_scan(self, *, url: str) -> AnalysisResult:
        report = analyze_url(url)
        reputation_result = await self.reputation.lookup(report.normalized)
        reputation = ReputationOut(
            checked=reputation_result.checked,
            provider=reputation_result.provider,
            verdict=reputation_result.verdict,
            note=reputation_result.note,
        )

        score = report.risk_score
        if reputation_result.verdict == "listed":
            score = max(score, 90)
        score = max(0, min(100, score))
        level = scoring.risk_level(score, 0.8 if report.findings else 0.6)
        category_key = "malicious_url" if score >= 25 else "unknown"

        indicators = [
            Indicator(
                id=f.id,
                label=f.label,
                category="malicious_url",
                weight=f.weight,
                severity="high" if f.weight >= 18 else "medium",
                evidence=f.evidence,
                explanation=f.explanation,
                source="url",
            )
            for f in report.findings
        ]
        mitigators = [
            Indicator(
                id=m.id,
                label=m.label,
                category="mitigator",
                weight=m.weight,
                severity="info",
                evidence=m.evidence,
                explanation=m.explanation,
                source="url",
            )
            for m in report.mitigators
        ]

        explanation, actions = build_explanation(
            language="en",
            category_key=category_key,
            score=score,
            level=level,
            indicators=indicators,
            mitigators=mitigators,
            is_url=True,
            url_host=report.host,
            url_findings=[f.label for f in report.findings[:3]],
        )

        return AnalysisResult(
            scan_id=str(uuid.uuid4()),
            scan_type="url",
            channel="url",
            created_at=_now(),
            risk_score=score,
            risk_level=level,  # type: ignore[arg-type]
            category=CategoryOut(key=category_key, label=category_label(category_key)),
            confidence=min(0.9, 0.45 + 0.05 * len(report.findings)),
            uncertainty=(
                None if report.findings else "No structural red flags were found, which is not proof that the site is safe."
            ),
            language="en",
            indicators=[IndicatorOut(**ind.as_dict()) for ind in indicators],
            mitigators=[MitigatorOut(id=m.id, label=m.label, explanation=m.explanation) for m in mitigators],
            explanation=explanation,
            recommended_actions=actions,
            excerpt=report.normalized[:280],
            ai=AiInsightOut(used=False, note="URL scans use the lexical analyser only; no AI provider is called."),
            url_analysis=self._url_payload(report, reputation),
            disclaimer=URL_DISCLAIMER,
        )

    # ------------------------------------------------------------------ helpers
    @staticmethod
    def _url_payload(report: UrlReport, reputation: ReputationOut) -> UrlAnalysisOut:
        return UrlAnalysisOut(
            submitted=report.submitted,
            normalized=report.normalized,
            host=report.host,
            scheme=report.scheme,
            https=report.https,
            is_ip_literal=report.is_ip_literal,
            is_shortener=report.is_shortener,
            is_punycode=report.is_punycode,
            lookalike_of=report.lookalike_of,
            risk_score=report.risk_score,
            risk_level=report.risk_level,
            findings=[UrlFindingOut(**f.as_dict()) for f in report.findings],
            reputation=reputation,
            disclaimer=URL_DISCLAIMER,
        )

    @staticmethod
    def _uncertainty(confidence_value: float, level: str, language: str) -> str | None:
        if level == "Uncertain" or confidence_value < 0.5:
            if language == "hi":
                return "संकेत पर्याप्त स्पष्ट नहीं हैं। कृपया संदेश को आधिकारिक माध्यम से सत्यापित करें।"
            if language == "hinglish":
                return "Sanket poori tarah clear nahi hain. Message ko official channel se verify karein."
            return "The signals are not conclusive either way. Verify the sender through an official channel before acting."
        return None


_engine: DetectionEngine | None = None


def get_engine() -> DetectionEngine:
    """Process wide engine instance (providers are stateless)."""
    global _engine
    if _engine is None:
        from app.services.ai.factory import get_ai_provider
        from app.services.url.reputation import get_reputation_provider

        _engine = DetectionEngine(
            ai_provider=get_ai_provider(), reputation_provider=get_reputation_provider()
        )
    return _engine
