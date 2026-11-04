"""Lightweight NLP layer.

No model download, no external service: character statistics, script detection
and URL extraction.  This keeps the engine usable on a free tier host and makes
every signal reproducible.
"""

from __future__ import annotations

import re
import unicodedata

from app.services.detection.rules import Indicator

_DEVANAGARI = re.compile(r"[\u0900-\u097F]")
_CYRILLIC = re.compile(r"[\u0400-\u04FF]")
_URL_RE = re.compile(
    r"(?:https?://|www\.)[^\s<>\"')\]]+|\b[a-z0-9][a-z0-9-]{1,40}\.(?:com|in|net|org|co|top|xyz|click|link|site|online|info|icu|buzz|live|app|shop|store|me|ly|gl|cc|ru|tk|ml|ga|cf|gq)\b(?:/[^\s<>\"')\]]*)?",
    re.IGNORECASE,
)
_PHONE_RE = re.compile(r"(?:\+91[\s-]?)?[6-9]\d{9}\b")
_AMOUNT_RE = re.compile(r"(?:rs\.?|₹|inr)\s?([\d,]{3,12})", re.IGNORECASE)

HINGLISH_MARKERS = (
    "aapka", "aapke", "aapko", "nahi", "nahin", "kya", "hai", "hain", "karein", "kijiye",
    "bhejein", "jayega", "jayegi", "turant", "abhi", "aaj", "paise", "khata", "kijiye",
    "bataye", "milega", "ho", "gaya", "wala", "wahi", "sirf", "jaldi", "bhar", "jeete",
    "karo", "dena", "nahi", "mat", "par", "se", "ka", "ki", "ko",
)


def detect_language(text: str) -> str:
    devanagari = len(_DEVANAGARI.findall(text))
    letters = sum(1 for ch in text if ch.isalpha())
    if letters and devanagari / letters > 0.25:
        return "hi"
    tokens = set(re.findall(r"[a-z]+", text.lower()))
    hits = tokens & set(HINGLISH_MARKERS)
    if len(hits) >= 3 or (len(hits) >= 2 and len(tokens) <= 12):
        return "hinglish"
    return "en"


def extract_urls(text: str) -> list[str]:
    """Extract candidate links without ever visiting them."""
    seen: list[str] = []
    for match in _URL_RE.finditer(text):
        candidate = match.group(0).rstrip(".,;:!?)'\"")
        if candidate.lower() not in {c.lower() for c in seen}:
            seen.append(candidate)
    return seen[:5]


def extract_amounts(text: str) -> list[int]:
    amounts: list[int] = []
    for raw in _AMOUNT_RE.findall(text):
        try:
            amounts.append(int(raw.replace(",", "")))
        except ValueError:
            continue
    return amounts


def phone_numbers(text: str) -> list[str]:
    return _PHONE_RE.findall(text)


def _caps_ratio(text: str) -> float:
    letters = [ch for ch in text if ch.isalpha()]
    if len(letters) < 20:
        return 0.0
    upper = sum(1 for ch in letters if ch.isupper())
    return upper / len(letters)


def _indicator(**kwargs) -> Indicator:
    return Indicator(source="nlp", category=kwargs.pop("category", "phishing"), **kwargs)


def nlp_indicators(text: str) -> list[Indicator]:
    """Style and structure signals that regex rules cannot express."""
    found: list[Indicator] = []

    ratio = _caps_ratio(text)
    if ratio >= 0.55:
        found.append(
            _indicator(
                id="nlp_caps_flood",
                label="Written mostly in capital letters",
                weight=6,
                severity="low",
                evidence=redact(text[:80]),
                explanation="Shouting in capitals is used to grab attention and create alarm.",
            )
        )

    if text.count("!") >= 4 or text.count("?") >= 4:
        found.append(
            _indicator(
                id="nlp_punctuation_flood",
                label="Excessive exclamation or question marks",
                weight=5,
                severity="low",
                evidence=redact(text[:80]),
                explanation="Marketing style punctuation is common in bulk scam broadcasts.",
            )
        )

    links = extract_urls(text)
    if len(links) >= 2:
        found.append(
            _indicator(
                id="nlp_multiple_links",
                label="Contains several links",
                weight=7,
                severity="medium",
                evidence=", ".join(links[:3]),
                explanation="Multiple links in one unsolicited message increase the chance that one is malicious.",
            )
        )

    if _CYRILLIC.search(text) or any(
        unicodedata.category(ch) == "Cf" for ch in text
    ):
        found.append(
            _indicator(
                id="nlp_obfuscated_text",
                label="Contains hidden or lookalike characters",
                weight=12,
                severity="high",
                evidence=redact(text[:80]),
                explanation="Invisible or lookalike characters are used to slip past spam filters.",
            )
        )

    if len(phone_numbers(text)) >= 2:
        found.append(
            _indicator(
                id="nlp_multiple_phone_numbers",
                label="Contains several phone numbers",
                weight=6,
                severity="low",
                evidence=", ".join(phone_numbers(text)[:3]),
                explanation="Multiple contact numbers are typical of callback fraud setups.",
            )
        )

    return found


def text_profile(text: str) -> dict:
    """Structural statistics used for the confidence calculation."""
    words = re.findall(r"\w+", text)
    return {
        "length": len(text),
        "word_count": len(words),
        "link_count": len(extract_urls(text)),
        "amounts": extract_amounts(text),
        "unique_word_ratio": (len(set(w.lower() for w in words)) / len(words)) if words else 0.0,
    }
