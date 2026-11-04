"""OpenAI compatible chat completion provider.

Works with any endpoint that implements ``POST /chat/completions`` (OpenAI,
Groq, Together, Ollama, vLLM, ...).  Only redacted text is sent, the response is
treated as untrusted data, and any failure silently degrades to the local engine.
"""

from __future__ import annotations

import json
import re

import httpx

from app.core.security import redact
from app.services.ai.base import AIInsight

SYSTEM_PROMPT = (
    "You are a fraud analysis assistant for Indian digital scams. "
    "You receive one message that was ALREADY scored by a deterministic rule engine. "
    "Return ONLY a JSON object with keys: "
    '"score_adjustment" (integer between -10 and 10, how much the risk score should change), '
    '"category" (one of: bank_kyc, upi_payment, phishing, fake_job, lottery_reward, '
    "govt_impersonation, otp_account_takeover, investment, delivery_parcel, "
    'fake_customer_support, malicious_url, unknown), and '
    '"rationale" (one short sentence, under 240 characters, citing concrete evidence from the text). '
    "Never invent external facts, never claim a website or phone number was verified, "
    "and never output anything except the JSON object."
)

_CODE_FENCE = re.compile(r"^```(?:json)?|```$", re.MULTILINE)
ALLOWED_CATEGORIES = {
    "bank_kyc", "upi_payment", "phishing", "fake_job", "lottery_reward",
    "govt_impersonation", "otp_account_takeover", "investment", "delivery_parcel",
    "fake_customer_support", "malicious_url", "unknown",
}


class OpenAICompatibleProvider:
    name = "openai_compatible"

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        model: str,
        timeout: float = 8.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout = timeout
        self._transport = transport

    async def analyze(self, *, text: str, category: str, score: int) -> AIInsight:
        payload = {
            "model": self._model,
            "temperature": 0,
            "max_tokens": 220,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Deterministic score: {score}/100. Deterministic category: {category}.\n"
                        f"Message (redacted):\n{redact(text)[:1500]}"
                    ),
                },
            ],
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        try:
            async with httpx.AsyncClient(timeout=self._timeout, transport=self._transport) as client:
                response = await client.post(
                    f"{self._base_url}/chat/completions", json=payload, headers=headers
                )
            if response.status_code != 200:
                return self._failure("The AI provider returned an error.")
            data = response.json()
            content = data["choices"][0]["message"]["content"]
        except Exception:
            return self._failure("The AI provider could not be reached.")

        parsed = self._parse(content)
        if parsed is None:
            return self._failure("The AI provider returned an unusable answer.")

        adjustment = parsed.get("score_adjustment", 0)
        try:
            adjustment = max(-10, min(10, int(adjustment)))
        except (TypeError, ValueError):
            adjustment = 0
        rationale = str(parsed.get("rationale") or "").strip()[:240] or None
        return AIInsight(
            used=True,
            provider=self.name,
            rationale=rationale,
            score_adjustment=adjustment,
            note="Contextual AI layer applied on top of the deterministic engine.",
        )

    @staticmethod
    def _parse(content: str) -> dict | None:
        if not isinstance(content, str):
            return None
        cleaned = _CODE_FENCE.sub("", content).strip()
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start == -1 or end == -1:
            return None
        try:
            parsed = json.loads(cleaned[start : end + 1])
        except json.JSONDecodeError:
            return None
        if not isinstance(parsed, dict):
            return None
        category = parsed.get("category")
        if category is not None and category not in ALLOWED_CATEGORIES:
            parsed.pop("category", None)
        return parsed

    @staticmethod
    def _failure(note: str) -> AIInsight:
        return AIInsight(
            used=False,
            provider="openai_compatible",
            rationale=None,
            score_adjustment=0,
            note=f"{note} The result relies on the local rule and NLP engine only.",
        )
