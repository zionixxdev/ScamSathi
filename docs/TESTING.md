# Testing

Two suites, both runnable offline with no API keys.

```bash
cd backend  && pytest                    # 69 tests
cd frontend && npm test                  # 19 tests
cd frontend && npm run build             # tsc -b + vite build
```

## 1. Backend (`backend/tests`)

### `test_engine.py` — detection behaviour

| Test | What it proves |
| --- | --- |
| Legitimate bank debit alert | A genuine transaction SMS stays Low; mitigators fire |
| Genuine UPI receipt / order / interview message | Financial and professional messages are not auto-flagged |
| Fake KYC | ≥50 and categorised `bank_kyc` |
| Fake job with registration fee | ≥50 and `fake_job` |
| UPI collect + PIN trap | ≥50 and `upi_payment` |
| Lottery with processing fee | ≥50 and `lottery_reward` |
| PM Kisan impersonation | ≥50 and `govt_impersonation` |
| Hinglish phishing | ≥50 and `bank_kyc` |
| Devanagari phishing | ≥50 and `bank_kyc` |
| Digital arrest call | ≥70 and `govt_impersonation` |
| Score bounds | Always 0–100, never described as probability |
| Indicator quality | Every indicator has a label, weight and explanation |
| OTP advisory | "Never share this OTP" is not a credential request |
| Explanation languages | English, Hindi and Hinglish all produce language-appropriate text |
| Unknown message | Reported as `unknown`, explanation says "no known scam pattern" |
| Redaction | OTP/card values never reach the stored excerpt |
| Link cross-check | A message with a hostile link gets URL indicators |

### `test_url.py` — URL analysis

Official domain is Low with mitigators; typosquat with bait path is High with `lookalike_of`;
brand-in-subdomain, shorteners, punycode, userinfo trick and private IPs are flagged; HTTPS is reported
but never treated as proof; query strings are stripped; `javascript:`, `ftp:`, `file:`, `data:` are
rejected; **a test patches `httpx.AsyncClient` to raise if any network call is attempted**, proving the
scanner never fetches.

### `test_api.py` — HTTP contract

Health, security headers, CORS allowlist (and rejection of an unknown origin), store/list/read/delete
flow, client isolation, opt-out, stats scoping, URL endpoint, invalid scheme error shape, oversized
input, invalid filters, missing records, invalid client ids, HTML-as-data, and a 429 rate-limit test.

### `test_scoring.py` — maths

Diminishing returns (each extra signal adds less), clamping at 100, mitigators reducing the score, level
thresholds including `Uncertain`, and negation handling.

### Fixtures

`tests/conftest.py` sets `DATABASE_URL` to a temporary SQLite file **before** importing the app, so the
cached settings pick it up and no test touches a real database. The file is deleted at session end.

## 2. Frontend (`frontend/src/**/__tests__`)

| File | Coverage |
| --- | --- |
| `components.test.tsx` | RiskBadge, RiskGauge accessibility label, indicator rendering and evidence, "no match is not proof of safety" copy, mitigator list, donut empty/populated states, EmptyState |
| `format.test.ts` | Risk colour mapping and fallback, percentage formatting, channel labels, relative time, stable client id |
| `api.test.ts` | `X-Client-Id` header, error-envelope → `ApiError` mapping, network failure handling, 204 handling |

Vitest + jsdom + Testing Library, configured in `vite.config.ts` with `src/test/setup.ts`.

## 3. Adding cases

A new scam pattern needs a test with two assertions: a **positive** (the scam is caught with the right
category and a sensible minimum score) and a **negative** (a close legitimate variant stays Low). The
negative case matters more — false positives destroy trust in a safety tool.

```python
@pytest.mark.parametrize("text,minimum,category", [...])
def test_scams_are_detected_with_the_right_category(text, minimum, category):
    result = analyze(text)
    assert result.risk_score >= minimum
    assert result.category.key == category
```

## 4. What is deliberately not claimed

No accuracy, precision, recall or F1 figure is reported. The test suite asserts behaviour on curated
cases; it is not an evaluation on a labelled production corpus, and it should not be presented as one.
