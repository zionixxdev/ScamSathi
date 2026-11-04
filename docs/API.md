# API reference

Base URL: `http://localhost:8000` · Prefix: `/api/v1` · Content type: `application/json`
Interactive docs: `/docs` (Swagger UI) · Schema: `/openapi.json`

## Conventions

### Client identity

Send `X-Client-Id` on every request: an anonymous, browser-generated string matching
`^[A-Za-z0-9_-]{8,64}$`.

- Without it, analysis still works but **nothing is stored** (`stored: false`).
- History and stats are scoped to this id at the SQL level. An invalid id is ignored, never rejected.

### Error envelope

```json
{ "error": { "code": "validation_error", "message": "The submitted request is not valid.",
             "details": [{ "field": "body.content", "message": "String should have at least 1 character" }] } }
```

| Status | Code | Meaning |
| --- | --- | --- |
| 400 | `invalid_url` / `invalid_scheme` | URL unparseable or not http/https |
| 404 | `not_found` / `invalid_filter` | Record or filter target missing |
| 413 | `input_too_large` | Input above the configured cap |
| 422 | `validation_error` | Pydantic rejected the body |
| 429 | `rate_limited` | Rate limit hit; `details.retry_after_seconds` is set |
| 500 | `internal_error` | Never includes a stack trace or internal path |

### Rate limits

Per IP, sliding window: `RATE_LIMIT_ANALYZE` (default 30/60 s) for `/analyze/*`,
`RATE_LIMIT_DEFAULT` (default 120/60 s) elsewhere. Exceeding it returns `429`.

---

## POST /analyze/message

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `content` | string | yes | 1–5000 chars |
| `channel` | enum | no | `sms`, `whatsapp`, `email`, `job_offer`, `payment_request`, `other` |
| `language` | enum | no | `auto` (default), `en`, `hi`, `hinglish` — controls explanation language |
| `sender_id` | string | no | SMS DLT header, e.g. `VM-SBIINB`; can add a mitigator |
| `store` | bool | no | Default `true`; requires a valid client id |

```bash
curl -X POST localhost:8000/api/v1/analyze/message \
  -H 'Content-Type: application/json' -H 'X-Client-Id: demo-client-0001' \
  -d '{"content":"Aapka account block hone wala hai. KYC update nahi kiya toh SIM band ho jayega. Turant click karein http://bit.ly/3xYz","channel":"whatsapp"}'
```

```json
{
  "scan_id": "8d1f…",
  "scan_type": "message",
  "channel": "whatsapp",
  "created_at": "2026-11-04T16:20:11Z",
  "risk_score": 96,
  "risk_level": "Critical",
  "category": { "key": "bank_kyc", "label": "Bank / KYC fraud" },
  "secondary_categories": [],
  "confidence": 0.68,
  "uncertainty": null,
  "language": "hinglish",
  "indicators": [
    {
      "id": "kyc_update",
      "label": "Demands an urgent KYC or account update",
      "category": "bank_kyc",
      "weight": 20,
      "severity": "high",
      "evidence": "…KYC update nahi kiya toh SIM band ho jayega…",
      "explanation": "Banks complete KYC at a branch or inside their own app…",
      "source": "rule"
    }
  ],
  "mitigators": [],
  "explanation": "Is message ka score 96/100 (Bahut zyada risk) hai aur ye Bank / KYC fraud jaisa lagta hai. …",
  "recommended_actions": ["Message ka jawab na dein…"],
  "excerpt": "Aapka account block hone wala hai. …",
  "ai": { "used": false, "provider": null, "rationale": null, "score_adjustment": 0,
          "note": "No contextual AI provider is configured…" },
  "url_analysis": { "host": "bit.ly", "is_shortener": true, "risk_score": 26, "…": "…" },
  "stored": true,
  "disclaimer": "The risk score is a heuristic index from 0 to 100, not the probability…"
}
```

## POST /analyze/url

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `url` | string | yes | ≤2048 chars, `http`/`https` only |
| `store` | bool | no | Default `true` |

Returns the same `AnalysisResult` shape with `scan_type: "url"` and a populated `url_analysis`
(`host`, `https`, `is_shortener`, `is_punycode`, `is_ip_literal`, `lookalike_of`, `findings`,
`reputation`).

Non-http schemes (`javascript:`, `ftp:`, `file:`, `data:`) return `400 invalid_scheme`. The URL is never
opened, resolved or screenshotted.

## GET /history

| Query | Type | Default | Notes |
| --- | --- | --- | --- |
| `limit` | int | 20 | 1–100 |
| `offset` | int | 0 | ≥0 |
| `risk_level` | string | – | `Low`, `Medium`, `High`, `Critical`, `Uncertain` |

```json
{ "items": [ { "scan_id": "…", "scan_type": "message", "channel": "sms", "risk_score": 73,
               "risk_level": "High", "category": {"key":"govt_impersonation","label":"Government impersonation"},
               "confidence": 0.8, "excerpt": "…", "created_at": "2026-11-04T16:20:11Z" } ],
  "total": 1, "limit": 20, "offset": 0 }
```

Without a client id: `{ "items": [], "total": 0, … }` — never an error, never someone else's data.

## GET /history/{scan_id}

Returns the full stored `AnalysisResult` (from the payload column). `404` if the id does not exist
**or belongs to another client id** — the two cases are deliberately indistinguishable.

## DELETE /history/{scan_id}

`204 No Content` on success, `404` if unknown. Deletion is permanent and immediate.

## GET /health

```json
{ "status": "ok", "version": "1.0.0", "environment": "development",
  "ai_provider": "none", "url_reputation_provider": "none",
  "database": "sqlite", "timestamp": "2026-11-04T16:20:11Z" }
```

`ai_provider` and `url_reputation_provider` report `none` when no key is configured — the honest answer
rather than a configured-looking value.

## GET /stats

```json
{ "total_scans": 12, "high_risk_scans": 5,
  "by_risk_level": { "High": 3, "Critical": 2, "Low": 7 },
  "by_category": [ { "category": "phishing", "label": "Phishing", "count": 4 } ],
  "recent": [ … ],
  "demo_data": false,
  "note": "Counts reflect only the scans stored for this browser profile…" }
```

These are the caller's own counts. No platform-wide or invented statistics exist anywhere in the API.

---

## Security response headers

Every response carries `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`,
`Referrer-Policy: no-referrer`, a strict `Content-Security-Policy`, `Permissions-Policy`,
`Cross-Origin-Resource-Policy`, `X-Request-ID`, and `Cache-Control: no-store` for `/api/*`.
`Strict-Transport-Security` is added only over HTTPS.
