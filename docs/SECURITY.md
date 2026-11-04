# Security considerations

The design assumption is that **everything a user submits is hostile input**. Submitted content is
data: it is never executed, rendered as HTML, interpreted as a template, or used to build a request to
the target it describes.

## 1. Threat model

| Threat | Mitigation |
| --- | --- |
| SSRF via submitted URL | The scanner never fetches the URL. There is no HTTP client in the analysis path for user input. |
| Drive-by / malware via link | No navigation, no rendering, no screenshots. The URL is a string to parse. |
| XSS through message content | The API returns JSON; React escapes by default; no `dangerouslySetInnerHTML` anywhere; the API sends `default-src 'none'`. |
| Injection into storage | SQLAlchemy parameterises all queries; no string-built SQL. |
| Credential leakage in logs | Log middleware records method, path, status, duration and a request id only. |
| OTP/card/account leakage in storage | `redact()` masks card numbers, OTPs, Aadhaar, PAN, emails, phones and long digit runs before any persistence. |
| Secret exposure | Keys come from environment variables only; the frontend never receives a key; `.gitignore` blocks `.env`. |
| Abuse / scraping | Per-IP sliding-window rate limits on analysis and general endpoints. |
| Enumeration of other users' scans | History is scoped by `client_id` in the `WHERE` clause; unknown and foreign ids both return 404. |
| Malicious AI response | Treated as untrusted data: JSON-parsed, adjustment clamped to ±10, category checked against an allowlist, rationale length-capped. |
| Frame clickjacking | `X-Frame-Options: DENY` + CSP `frame-ancestors 'none'`. |
| MIME sniffing | `X-Content-Type-Options: nosniff`. |
| Error-message information leak | Uniform envelope; unexpected exceptions return a generic 500 with no trace. |

## 2. Input handling

```python
sanitize_text(raw)   # NFKC normalise → strip zero-width and control chars → collapse → hard length cap
normalize_url(raw)   # scheme allowlist (http/https) → hostname validation → IDNA check
                     # → userinfo recorded, query string and fragment dropped
redact(text)         # card / OTP / Aadhaar / PAN / email / phone / long-digit masking
make_excerpt(text)   # redacted, whitespace-collapsed, ≤280 characters
```

Limits: `MAX_MESSAGE_CHARS` (5000), `MAX_URL_CHARS` (2048), Pydantic field caps, request body size capped
by the ASGI server. Non-http(s) schemes are rejected with `400 invalid_scheme` — including `javascript:`,
`data:`, `file:`, `ftp:` and `vbscript:`.

## 3. Outbound network policy

Only two optional integrations make outbound calls, both after an explicit operator opt-in:

| Integration | What is sent | What is never sent |
| --- | --- | --- |
| AI provider | redacted message text (≤1500 chars), score, category | raw content, OTPs, card/account numbers, client id, IP |
| Safe Browsing | normalised URL with query string and fragment removed | page content, query parameters, headers, cookies |

Both are wrapped in `try/except` with timeouts and degrade to "not used"/"not checked" — never to a
fabricated verdict.

## 4. Authentication and identity

There is no authentication, by design: no accounts, no passwords, no sessions, no cookies. The
`X-Client-Id` header is a client-generated random string, not a credential; it grants access only to the
scans stored under it, and it can be regenerated at will from the UI.

If you deploy ScamSathi for an organisation, put it behind your own SSO reverse proxy — the app will work
unchanged.

## 5. Rate limiting

`SlidingWindowLimiter` is a thread-safe, monotonic-clock, in-process sliding window with opportunistic
cleanup. Defaults: 30 analyses/minute and 120 requests/minute per IP. Behind a proxy the limiter keys on
the first `X-Forwarded-For` hop, so the proxy must strip client-supplied values for that header.

For multi-instance deployments, replace the limiter with a Redis-backed implementation of the same
`check(key) -> (allowed, retry_after)` interface.

## 6. Response headers

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: no-referrer
Permissions-Policy: geolocation=(), microphone=(), camera=(), payment=()
Content-Security-Policy: default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'
Cross-Origin-Resource-Policy: same-site
Cross-Origin-Opener-Policy: same-origin
Cache-Control: no-store            (API responses)
Strict-Transport-Security: max-age=31536000; includeSubDomains   (HTTPS only)
```

## 7. CORS

Explicit allowlist from `ALLOWED_ORIGINS`; credentials disabled; methods limited to
`GET, POST, DELETE, OPTIONS`; headers limited to `Content-Type, X-Client-Id, X-Request-Id`. Unknown
origins receive no `Access-Control-Allow-Origin` header.

## 8. Known limitations

- The rule engine can be evaded by novel wording; it is not a classifier trained on a labelled corpus.
- Without a reputation key, no external URL check happens at all — the response says so.
- SQLite on an ephemeral host loses history on redeploy (by design, and it is only redacted data).
- The in-process rate limiter does not coordinate across instances.
- No anti-automation challenge (CAPTCHA) is implemented; the rate limit is the only control.

## 9. Reporting a vulnerability

Open a private security advisory on the repository, or contact the maintainer directly. Please include
the endpoint, a reproduction and the impact. Do not open a public issue for a live vulnerability.
