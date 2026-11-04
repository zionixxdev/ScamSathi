# Architecture

ScamSathi is a two-service application: a stateless HTTP API that owns all analysis, and a static
single-page app that owns all presentation. They share nothing but the JSON contract in
[API.md](API.md), so either side can be redeployed, scaled or replaced independently.

## 1. System context

```
Browser (React SPA)
   │  POST /api/v1/analyze/message   X-Client-Id: <random browser id>
   ▼
FastAPI app (app/main.py)
   │  middleware: security headers → request log → CORS
   ▼
API routes (app/api/v1/routes)
   │  dependency: rate limit, client id, repository
   ▼
AnalysisService (app/services/analysis_service.py)
   │
   ├── DetectionEngine ──────────────► AnalysisResult (Pydantic)
   │      ├── rules / nlp / url / categories / scoring / explain
   │      ├── ai provider (optional, outbound HTTPS)
   │      └── reputation provider (optional, outbound HTTPS)
   │
   └── SqlScanRepository ────────────► SQLite / PostgreSQL
```

## 2. Backend modules

| Module | Responsibility |
| --- | --- |
| `app/config.py` | Environment parsing with safe defaults; cached settings object |
| `app/main.py` | App factory, middleware stack, lifespan DB init, router mounting |
| `app/api/deps.py` | Rate limiting, anonymous client identity, repository injection |
| `app/api/v1/routes/analyze.py` | Message and URL analysis endpoints |
| `app/api/v1/routes/history.py` | List, read and delete stored scans |
| `app/api/v1/routes/system.py` | Health and per-client statistics |
| `app/core/security.py` | Sanitisation, redaction, excerpting, hashing, security headers |
| `app/core/ratelimit.py` | Thread-safe sliding window limiter |
| `app/core/errors.py` | `AppError` hierarchy and uniform error envelope |
| `app/core/logging.py` | Content-free request logging middleware |
| `app/db/*` | Engine, ORM model, session helpers, repository protocol + SQL implementation |
| `app/schemas/analysis.py` | Request validation and response contracts |
| `app/services/detection/*` | The engine: rules, NLP, categories, scoring, explanations |
| `app/services/url/*` | Lexical URL analysis and optional reputation lookup |
| `app/services/ai/*` | Provider protocol, null provider, OpenAI-compatible client, factory |
| `app/services/analysis_service.py` | Orchestration and the persistence privacy rules |

### Layering rules

- Routes never contain detection logic; they validate, call the service and return a schema.
- The engine never touches the database; it is pure and therefore trivially testable.
- The service is the only place that decides whether something is persisted.
- Everything outbound (AI, reputation) sits behind a protocol with a null implementation.

## 3. Detection pipeline

```
raw text
  → sanitize_text()            NFKC, control/zero-width strip, length cap
  → detect_language()          hi | hinglish | en
  → match_indicators()         weighted regex rules (negation aware)
  → nlp_indicators()           style/structure signals
  → extract_urls() → analyze_url() per link → url indicators + url_risk
  → match_mitigators()         legitimate-alert signals
  → rank_categories()          category voting (URL findings excluded)
  → aggregate()                diminishing returns + combos + mitigators
  → confidence()               evidence volume, length, ambiguity
  → risk_level()               Low / Medium / High / Critical / Uncertain
  → AI provider (optional)     bounded ±10 adjustment + one rationale sentence
  → build_explanation()        language-aware narrative + actions
  → AnalysisResult
```

### Scoring maths

Weights are sorted descending and multiplied by a decay vector, so the tenth weak signal adds far less
than the first strong one:

```
raw = Σ wᵢ · dᵢ ,  d = [1.0, 0.85, 0.72, 0.6, 0.5, 0.4, 0.4, …]
raw += coherence_bonus      (+4 for two, +8 for three indicators in the winning category)
raw += combo_bonus          (lure+fee, threat+KYC, digital arrest+secrecy, … capped at 28)
raw += url_bonus            (+7 if the best link scores ≥25, +14 if ≥50)
raw -= Σ mitigator_weights
score = clamp(round(raw), 0, 100)
```

The score is deliberately **not** a probability. It is a bounded index of how strongly the content
matches known scam structures. Calibrating it would require a labelled dataset and a held-out
evaluation; neither is claimed here.

### Confidence vs score

| Concept | Question it answers |
| --- | --- |
| `risk_score` | How strongly does this content match scam patterns? |
| `confidence` | How sure is the engine about its own reading? |

A clean, ordinary message scores 0 with confidence ≈0.62 (nothing matched, and that is a reliable
reading). A three-word message with one weak signal scores low with low confidence, and the level
becomes **Uncertain** rather than pretending to know.

## 4. URL analysis

The submitted link is a **string**, never a request. The analyser parses it with `urllib.parse`,
validates the scheme, extracts the host, and scores structural findings:

| Finding | Weight | Why it matters |
| --- | --- | --- |
| `userinfo_trick` | 24 | `sbi.co.in@evil.com` — everything before `@` is ignored |
| `lookalike_domain` | 26 | Registered domain imitates a brand (edit distance ≤1, leet-normalised, or brand embedded) |
| `brand_in_subdomain` | 24 | `sbi.co.in.secure-login.xyz` — the registered domain is not the brand's |
| `shortener` | 26 | Destination hidden behind a redirect |
| `ip_literal_host` | 18 | No domain at all |
| `internal_address` | 20 | Private/loopback target — a probe, never contacted |
| `punycode_host` | 18 | Lookalike Unicode characters |
| `suspicious_tld` | 14 | Cheap, abuse-heavy TLDs |
| `bait_keywords` | 12 | `kyc`, `verify`, `refund`, `prize` inside the host |
| `suspicious_path` | 10 | Credential-shaped paths |
| `no_https` | 8 | Unencrypted — and never treated as proof of safety either way |

Official domains (`sbi.co.in`, `hdfcbank.com`, `uidai.gov.in`, …) produce a **mitigator**, not a pass.

## 5. Storage and privacy boundary

```
AnalysisResult  ──► ScanRecord ──► scans table
                     │  excerpt      redacted, ≤280 chars
                     │  content_hash SHA-256 of the original
                     │  payload      full result JSON (no raw content)
                     │  client_id    anonymous browser id
```

The raw message exists only in memory for the duration of one request. History is scoped by
`client_id` at the SQL level, so cross-client reads are impossible rather than merely forbidden.

## 6. Extension points

| Goal | Change |
| --- | --- |
| New scam pattern | Add a dict to `RULES` in `lexicons.py` (id, label, category, weight, patterns, explanation) |
| New category | Add to `CATEGORIES`, reference it from rules, add actions in `explain.py` |
| New AI provider | Implement the `AIProvider` protocol and register it in `ai/factory.py` |
| New reputation service | Implement `ReputationProvider.lookup()` and register it in `url/reputation.py` |
| PostgreSQL | Set `DATABASE_URL`; SQLAlchemy handles the rest |
| Multi-instance rate limiting | Replace `SlidingWindowLimiter` with a Redis implementation of `check()` |
