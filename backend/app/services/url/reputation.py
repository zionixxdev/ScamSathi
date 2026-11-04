"""Optional URL reputation lookup.

Design rules:
* only the normalised URL, with query string and fragment removed, is sent
* no API key means no lookup - and the response says so instead of pretending
* a failed lookup is reported as unavailable, never as "safe"
"""

from __future__ import annotations

from dataclasses import dataclass

import httpx

from app.config import get_settings


@dataclass(frozen=True)
class ReputationResult:
    checked: bool
    provider: str | None
    verdict: str
    note: str


class ReputationProvider:
    name = "none"

    async def lookup(self, normalized_url: str) -> ReputationResult:  # pragma: no cover
        return ReputationResult(
            checked=False,
            provider=None,
            verdict="not_checked",
            note="No reputation provider is configured, so the URL was not checked against any external database.",
        )


class NoopReputationProvider(ReputationProvider):
    pass


class GoogleSafeBrowsingProvider(ReputationProvider):
    name = "google_safebrowsing"
    ENDPOINT = "https://safebrowsing.googleapis.com/v4/threatMatches:find"

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    async def lookup(self, normalized_url: str) -> ReputationResult:
        payload = {
            "client": {"clientId": "scamsathi", "clientVersion": "1.0.0"},
            "threatInfo": {
                "threatTypes": [
                    "MALWARE",
                    "SOCIAL_ENGINEERING",
                    "UNWANTED_SOFTWARE",
                    "POTENTIALLY_HARMFUL_APPLICATION",
                ],
                "platformTypes": ["ANY_PLATFORM"],
                "threatEntryTypes": ["URL"],
                "threatEntries": [{"url": normalized_url}],
            },
        }
        try:
            async with httpx.AsyncClient(timeout=6.0) as client:
                response = await client.post(
                    self.ENDPOINT, params={"key": self._api_key}, json=payload
                )
            if response.status_code != 200:
                return ReputationResult(
                    checked=False,
                    provider=self.name,
                    verdict="unavailable",
                    note="The reputation service did not answer successfully, so no external verdict is available.",
                )
            data = response.json()
        except Exception:
            return ReputationResult(
                checked=False,
                provider=self.name,
                verdict="unavailable",
                note="The reputation lookup could not be completed, so no external verdict is available.",
            )

        matches = data.get("matches") or []
        if matches:
            types = sorted({match.get("threatType", "UNKNOWN") for match in matches})
            return ReputationResult(
                checked=True,
                provider=self.name,
                verdict="listed",
                note="Google Safe Browsing lists this URL as: " + ", ".join(types) + ".",
            )
        return ReputationResult(
            checked=True,
            provider=self.name,
            verdict="not_listed",
            note="Google Safe Browsing has no listing for this URL. Absence from a blocklist is not proof of safety.",
        )


def get_reputation_provider() -> ReputationProvider:
    settings = get_settings()
    if settings.reputation_provider == "google_safebrowsing" and settings.safebrowsing_api_key:
        return GoogleSafeBrowsingProvider(settings.safebrowsing_api_key)
    return NoopReputationProvider()
