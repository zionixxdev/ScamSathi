"""Input hardening, redaction and HTTP security headers.

Rules applied here:
* submitted content is untrusted data and is never executed or rendered
* control characters are stripped, unicode is normalised, sizes are capped
* nothing that looks like an OTP, PIN, card or account number is persisted
"""

from __future__ import annotations

import hashlib
import re
import unicodedata

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

CLIENT_ID_RE = re.compile(r"^[A-Za-z0-9_-]{8,64}$")
_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_ZERO_WIDTH = re.compile(r"[\u200b-\u200f\u202a-\u202e\u2060\ufeff]")

# Patterns that must never leave the process in clear text.
_SENSITIVE_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\b(?:\d[ -]?){13,19}\b"), "[redacted-card]"),
    (re.compile(r"\b(?:otp|OTP)\s*[:\-]?\s*\d{4,8}\b"), "OTP [redacted]"),
    (re.compile(r"\b\d{6}\b(?=\s*(?:is|hai)\s+(?:your|aapka)?\s*(?:otp|OTP))", re.I), "[redacted-otp]"),
    (re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b"), "[redacted-pan]"),
    (re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b"), "[redacted-aadhaar]"),
    (re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]{2,}\b"), "[redacted-email]"),
    (re.compile(r"\b(?:\+91[\s-]?)?[6-9]\d{9}\b"), "[redacted-phone]"),
    (re.compile(r"\b[A-Za-z]{4}0[A-Za-z0-9]{6}\b"), "[redacted-ifsc-account]"),
)


def sanitize_text(raw: str, *, max_chars: int) -> str:
    """Normalise and hard limit untrusted text input."""
    if not isinstance(raw, str):
        raise TypeError("text input must be a string")
    text = unicodedata.normalize("NFKC", raw)
    text = _ZERO_WIDTH.sub("", text)
    text = _CONTROL_CHARS.sub(" ", text)
    text = text.replace("\r\n", "\n").strip()
    if len(text) > max_chars:
        text = text[:max_chars]
    return text


def redact(text: str) -> str:
    """Mask OTPs, card numbers, Aadhaar/PAN, emails and phone numbers."""
    redacted = text
    for pattern, replacement in _SENSITIVE_PATTERNS:
        redacted = pattern.sub(replacement, redacted)
    # Mask any long digit run that survived (account numbers, OTP blobs).
    redacted = re.sub(r"\d{6,}", lambda m: m.group(0)[:2] + "*" * (len(m.group(0)) - 2), redacted)
    return redacted


def make_excerpt(text: str, limit: int = 280) -> str:
    """Redacted, length limited preview safe to store and display."""
    cleaned = " ".join(redact(text).split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1].rstrip() + "\u2026"


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def validate_client_id(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value if CLIENT_ID_RE.match(value) else None


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Defence in depth headers for every response."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        headers = response.headers
        headers.setdefault("X-Content-Type-Options", "nosniff")
        headers.setdefault("X-Frame-Options", "DENY")
        headers.setdefault("Referrer-Policy", "no-referrer")
        headers.setdefault(
            "Permissions-Policy", "geolocation=(), microphone=(), camera=(), payment=()"
        )
        headers.setdefault("Cross-Origin-Resource-Policy", "same-site")
        headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
        # The API returns JSON only, so nothing may be loaded or executed.
        headers.setdefault(
            "Content-Security-Policy",
            "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'",
        )
        if request.url.path.startswith("/api/"):
            headers.setdefault("Cache-Control", "no-store")
        if request.url.scheme == "https":
            headers.setdefault(
                "Strict-Transport-Security", "max-age=31536000; includeSubDomains"
            )
        return response
