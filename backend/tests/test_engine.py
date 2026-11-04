"""Behavioural tests for the detection engine."""

from __future__ import annotations

import asyncio

import pytest

from app.services.detection.engine import DetectionEngine
from app.services.detection import nlp
from app.core.security import make_excerpt, redact


def analyze(text: str, **kwargs):
    engine = DetectionEngine()
    return asyncio.run(engine.analyze_message(content=text, **kwargs))


LEGIT_BANK_ALERT = (
    "Rs.500.00 debited from A/c XX1234 on 04-11-26 to VPA amazon@ybl. "
    "Avl Bal Rs.12,340.00. Not you? Call 18001234."
)
LEGIT_UPI_RECEIPT = "You received Rs 500 from Rahul via UPI. Ref no 123456789012."
LEGIT_ORDER = "Your Amazon order #123-456 has been delivered. Thank you for shopping with us."
LEGIT_INTERVIEW = (
    "Your interview is scheduled on 12 Nov at 11 AM at our Bengaluru office. "
    "Please carry your ID proof. - Infosys HR"
)

FAKE_KYC = (
    "Dear Customer, your SBI account will be blocked today. Complete your KYC "
    "immediately at http://sbi-kyc-verify.top/update or your account will be suspended."
)
FAKE_JOB = (
    "Work from home part time job. Earn Rs 5000 daily. Pay registration fee Rs 499 to join. "
    "Contact HR on WhatsApp 9876543210."
)
UPI_TRAP = (
    "You have a collect request of Rs 4999 from Rahul. Approve the request and enter UPI PIN "
    "to receive money."
)
LOTTERY = (
    "Congratulations! You have won Rs 25,00,000 in KBC lucky draw. Pay processing fee Rs 5500 "
    "to claim your prize."
)
GOVT = (
    "PM Kisan yojana: your installment is on hold. Update Aadhaar within 24 hours or account "
    "will be blocked. Visit https://pmkisan-update.xyz"
)
HINGLISH = (
    "Aapka bank account block hone wala hai. KYC update nahi kiya toh SIM band ho jayega. "
    "Turant is link par click karein http://bit.ly/3xYz"
)
HINDI = "प्रिय ग्राहक, आपका खाता बंद हो जाएगा। तुरंत केवाईसी अपडेट करें।"
DIGITAL_ARREST = (
    "CBI officer here. A parcel in your name contained narcotics. You are under digital arrest. "
    "Do not tell anyone or we will issue a warrant. Join Skype for verification."
)
UNKNOWN = "Hey, are we still meeting for lunch tomorrow?"


@pytest.mark.parametrize(
    "text,expected_max",
    [
        (LEGIT_BANK_ALERT, 25),
        (LEGIT_UPI_RECEIPT, 25),
        (LEGIT_ORDER, 25),
        (LEGIT_INTERVIEW, 25),
        (UNKNOWN, 20),
    ],
)
def test_legitimate_messages_stay_low(text: str, expected_max: int) -> None:
    result = analyze(text)
    assert result.risk_score <= expected_max, result.indicators
    assert result.risk_level in {"Low", "Uncertain"}


@pytest.mark.parametrize(
    "text,minimum,category",
    [
        (FAKE_KYC, 50, "bank_kyc"),
        (FAKE_JOB, 50, "fake_job"),
        (UPI_TRAP, 50, "upi_payment"),
        (LOTTERY, 50, "lottery_reward"),
        (GOVT, 50, "govt_impersonation"),
        (HINGLISH, 50, "bank_kyc"),
        (HINDI, 50, "bank_kyc"),
        (DIGITAL_ARREST, 70, "govt_impersonation"),
    ],
)
def test_scams_are_detected_with_the_right_category(text: str, minimum: int, category: str) -> None:
    result = analyze(text)
    assert result.risk_score >= minimum, (result.risk_score, [i.id for i in result.indicators])
    assert result.category.key == category


def test_score_is_bounded_and_never_claims_probability() -> None:
    result = analyze(FAKE_KYC)
    assert 0 <= result.risk_score <= 100
    assert "not the probability" in result.disclaimer.lower()
    assert "probability" not in result.explanation.lower()


def test_every_indicator_carries_evidence_and_explanation() -> None:
    result = analyze(FAKE_KYC)
    assert result.indicators
    for indicator in result.indicators:
        assert indicator.label
        assert indicator.explanation
        assert indicator.weight > 0


def test_mitigators_are_reported_for_genuine_alerts() -> None:
    result = analyze(LEGIT_BANK_ALERT)
    assert result.mitigators
    assert {m.id for m in result.mitigators} & {"transaction_template", "helpline_verification_prompt"}


def test_otp_advisory_is_not_read_as_a_credential_request() -> None:
    result = analyze("Your OTP for login is 482913. Never share this OTP with anyone. -ICICI Bank")
    assert result.risk_score < 25
    assert all(i.id != "credential_request" for i in result.indicators)


def test_explanation_languages() -> None:
    english = analyze(FAKE_KYC, language="en")
    hindi = analyze(FAKE_KYC, language="hi")
    hinglish = analyze(FAKE_KYC, language="hinglish")
    assert "warning sign" in english.explanation
    assert any("\u0900" <= ch <= "\u097f" for ch in hindi.explanation)
    assert "score" in hinglish.explanation
    assert hindi.recommended_actions != english.recommended_actions


def test_language_detection() -> None:
    assert nlp.detect_language(HINDI) == "hi"
    assert nlp.detect_language(HINGLISH) == "hinglish"
    assert nlp.detect_language("Your invoice is attached.") == "en"


def test_unknown_message_is_reported_as_unclassified_not_safe() -> None:
    result = analyze(UNKNOWN)
    assert result.category.key == "unknown"
    assert "no known scam pattern" in result.explanation.lower()


def test_secrets_are_redacted_from_the_stored_excerpt() -> None:
    result = analyze("Your OTP is 482913. Share it with our executive to complete verification.")
    assert "482913" not in result.excerpt
    assert "482913" not in make_excerpt("OTP 482913 card 4111111111111111")


def test_redaction_masks_sensitive_numbers() -> None:
    redacted = redact("Call 9876543210, email a@b.com, card 4111111111111111, aadhaar 1234 5678 9012")
    assert "9876543210" not in redacted
    assert "a@b.com" not in redacted
    assert "4111111111111111" not in redacted


def test_message_with_link_is_cross_checked() -> None:
    result = analyze("Please verify your account here: http://sbi-kyc-verify.top/login")
    assert result.url_analysis is not None
    assert result.url_analysis.risk_score >= 25
    assert any(ind.source == "url" for ind in result.indicators)


def test_empty_message_is_rejected_by_the_schema(client) -> None:
    response = client.post("/api/v1/analyze/message", json={"content": "   "})
    assert response.status_code == 422


def test_short_ambiguous_message_reports_uncertainty() -> None:
    result = analyze("Pay now")
    assert result.risk_score < 25
    assert result.confidence <= 0.65
