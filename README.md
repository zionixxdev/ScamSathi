# ScamSathi

**Understand the scam before it catches you.**

ScamSathi is an AI-assisted digital safety platform for Indian users. Paste a suspicious SMS, WhatsApp
message, email, job offer, payment request or link and it returns a risk score, the scam category, the
exact indicators that fired (with evidence), a plain-language explanation and the safest next actions —
in English, Hindi or Hinglish.

It is a working application, not a landing page: a FastAPI service with a hybrid detection engine, a
React dashboard with nine screens, a real SQLite persistence layer, a test suite on both sides and
deployment configuration for free-tier hosting.

---

## Table of contents

- [What it does](#what-it-does)
- [Architecture](#architecture)
- [Detection engine](#detection-engine)
- [Quick start](#quick-start)
- [Configuration](#configuration)
- [API](#api)
- [Testing](#testing)
- [Deployment](#deployment)
- [Privacy](#privacy)
- [Honest limitations](#honest-limitations)
- [Project structure](#project-structure)
- [Documentation](#documentation)

---

## What it does

| Capability | Detail |
| --- | --- |
| **Message scanner** | SMS, WhatsApp, email, job offers, payment requests, bank/KYC notices, scheme messages. English, Hindi and Hinglish. |
| **URL scanner** | Domain structure, lookalike brands, shorteners, punycode, raw IPs, bait paths. The link is **never opened**. |
| **Explainable risk** | 0–100 score, five levels (Low / Medium / High / Critical / Uncertain), every indicator with its evidence snippet and reason. |
| **12 scam categories** | Bank/KYC, UPI/payment, phishing, fake job, lottery/reward, government impersonation, OTP takeover, investment, delivery/parcel, fake customer support, malicious URL, unclassified. |
| **Safety actions** | Category-specific next steps plus India-specific reporting routes (cybercrime.gov.in, 1930, 1909 Chakshu). |
| **Scan history** | Optional, per-browser, redacted, deletable record by record. |
| **Education** | Scam intelligence library and a safety guide with official resources. |
| **Privacy mode** | No accounts at all. No client id, no stored scans. |

The risk score is a **heuristic index, not a probability**. The API and UI say so explicitly, and no
accuracy figure is claimed anywhere because the engine has not been validated on a labelled production
dataset.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│  React + TypeScript + Vite + Tailwind (independently deployable)     │
│  Landing · Dashboard · Message Scanner · URL Scanner · Result        │
│  History · Scam Intelligence · Safety Guide · About & Privacy        │
└───────────────────────────────┬──────────────────────────────────────┘
                                │  JSON over HTTPS, X-Client-Id header
┌───────────────────────────────▼──────────────────────────────────────┐
│  FastAPI  ·  /api/v1  ·  Pydantic validation  ·  rate limiting       │
│  security headers  ·  CORS allowlist  ·  uniform error envelope      │
├──────────────────────────────────────────────────────────────────────┤
│  AnalysisService                                                     │
│   ├── DetectionEngine                                                │
│   │    ├── rules.py      weighted regex indicators (EN/HI/Hinglish)  │
│   │    ├── nlp.py        script, caps, punctuation, link density     │
│   │    ├── url/analyzer  lexical URL analysis (no network)           │
│   │    ├── categories.py category voting + ambiguity detection       │
│   │    ├── scoring.py    diminishing returns, combos, mitigators     │
│   │    └── explain.py    evidence-based explanation in 3 languages   │
│   ├── ai/                optional OpenAI-compatible provider (±10)   │
│   └── url/reputation.py  optional Safe Browsing lookup               │
├──────────────────────────────────────────────────────────────────────┤
│  Repository interface  →  SQLAlchemy  →  SQLite (PostgreSQL ready)   │
└──────────────────────────────────────────────────────────────────────┘
```

Two design rules keep this honest and portable:

1. **The deterministic engine is the product.** AI and reputation services are plugins. Remove both and
   every endpoint still returns a complete, explained result.
2. **Storage sits behind a repository interface.** Swapping SQLite for PostgreSQL is a `DATABASE_URL`
   change, not a rewrite.

---

## Detection engine

Each stage is deterministic and inspectable.

1. **Sanitise** — NFKC normalisation, control and zero-width characters stripped, hard length cap.
2. **Language detection** — Devanagari ratio for Hindi, Hinglish marker vocabulary, else English.
3. **Rule layer** — 30+ compiled regular expressions, each with an id, category, weight, severity and a
   human explanation. Negation-aware: *"never share your OTP"* is not read as a request to share it.
4. **NLP layer** — capitalisation, punctuation floods, link density, hidden/lookalike characters,
   multiple phone numbers.
5. **Link layer** — every URL in the message is analysed lexically (domain, TLD, brand imitation, bait
   path). Findings feed the score but never hijack the category: a KYC SMS with a link stays a KYC scam.
6. **Mitigators** — genuine-alert markers (transaction template, "never share your OTP", DLT sender id,
   "if this was not you, call…") *reduce* the score so a normal bank debit alert stays Low.
7. **Category** — indicators vote by weight; close runners-up are reported as secondary.
8. **Scoring** — indicators are sorted and applied with diminishing returns
   (`1.0, 0.85, 0.72, 0.6, 0.5, 0.4…`), plus coherence and known-combination bonuses, minus mitigators,
   clamped to 0–100.
9. **Confidence** — separate from the score: evidence volume, message length, category ambiguity. Low
   confidence in an ambiguous middle band reports the level as **Uncertain**.
10. **Explanation** — composed from the indicators that actually matched, in the requested language.

### Risk bands

| Score | Level | Meaning |
| --- | --- | --- |
| 0–24 | Low | No meaningful pattern matched |
| 25–49 | Medium | Some warning signs, verify before acting |
| 50–74 | High | Strong scam pattern, do not engage |
| 75–100 | Critical | Multiple strong, mutually reinforcing signs |
| any | Uncertain | Engine confidence below 0.45 in the 12–49 band |

---

## Quick start

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                  # defaults work as-is
uvicorn app.main:app --reload --port 8000
```

- API: <http://localhost:8000/api/v1/health>
- Interactive docs: <http://localhost:8000/docs>

### Frontend

```bash
cd frontend
npm install
cp .env.example .env        # VITE_API_BASE_URL=http://localhost:8000
npm run dev
```

Open <http://localhost:5173>. Full instructions, including production builds, are in
[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

---

## Configuration

Everything is optional — the defaults run the full product with no keys.

| Variable | Default | Purpose |
| --- | --- | --- |
| `APP_ENV` | `development` | Environment label |
| `ALLOWED_ORIGINS` | `http://localhost:5173,…` | CORS allowlist (comma separated) |
| `DATABASE_URL` | `sqlite:///./scamsathi.db` | Any SQLAlchemy URL |
| `RATE_LIMIT_ANALYZE` | `30/60` | Analyse requests per window per IP |
| `RATE_LIMIT_DEFAULT` | `120/60` | All other endpoints |
| `MAX_MESSAGE_CHARS` | `5000` | Input cap |
| `MAX_URL_CHARS` | `2048` | Input cap |
| `AI_PROVIDER` | `none` | `none` or `openai` (any OpenAI-compatible endpoint) |
| `AI_API_KEY` | – | Provider key; without it the AI layer is skipped |
| `AI_BASE_URL` | `https://api.openai.com/v1` | Compatible endpoint |
| `AI_MODEL` | `gpt-4o-mini` | Model name |
| `URL_REPUTATION_PROVIDER` | `none` | `none` or `google_safebrowsing` |
| `SAFEBROWSING_API_KEY` | – | Key for the reputation lookup |

Frontend: `VITE_API_BASE_URL` only. Details in [docs/ENVIRONMENT.md](docs/ENVIRONMENT.md).

---

## API

Base path `/api/v1`. Full schemas, examples and error codes in [docs/API.md](docs/API.md).

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/analyze/message` | Analyse message text |
| `POST` | `/analyze/url` | Analyse a URL (never fetched) |
| `GET` | `/history` | Paginated history for this client id |
| `GET` | `/history/{scan_id}` | One stored analysis |
| `DELETE` | `/history/{scan_id}` | Delete one record |
| `GET` | `/health` | Service and provider status |
| `GET` | `/stats` | Aggregates for this client id |

```bash
curl -X POST http://localhost:8000/api/v1/analyze/message \
  -H 'Content-Type: application/json' \
  -H 'X-Client-Id: demo-client-0001' \
  -d '{"content":"Dear Customer, your SBI account will be blocked today. Complete your KYC immediately at http://sbi-kyc-verify.top/update","channel":"sms"}'
```

---

## Testing

```bash
# Backend — 69 tests
cd backend && pip install -r requirements-dev.txt && pytest

# Frontend — 19 tests
cd frontend && npm test

# Type check + production build
cd frontend && npm run build
```

Coverage includes legitimate bank alerts, fake KYC, fake jobs, UPI collect traps, lottery, government
impersonation, Hinglish and Devanagari phishing, digital-arrest calls, safe and hostile URLs, malformed
input, rate limiting, client isolation, redaction and false-positive control. See
[docs/TESTING.md](docs/TESTING.md).

---

## Deployment

Frontend and backend deploy independently:

- **Backend** — any Python host (Render, Railway, Fly.io, a VM). `backend/Dockerfile` and
  `deploy/render.yaml` are included.
- **Frontend** — any static host (Netlify, Vercel, Cloudflare Pages, GitHub Pages). `deploy/netlify.toml`,
  `deploy/vercel.json` and `frontend/Dockerfile` (nginx) are included.

Set `ALLOWED_ORIGINS` on the backend to the deployed frontend origin, and `VITE_API_BASE_URL` on the
frontend to the deployed API. Step-by-step in [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

---

## Privacy

- No accounts, no email, no phone number, no analytics, no third-party trackers.
- Scans are tied to a random id in browser `localStorage`; clear it and the link is gone.
- Only a **redacted** preview is stored (OTP, card, Aadhaar/PAN, email, phone and long digit runs masked)
  plus a SHA-256 hash of the content — never the full message.
- Submitted URLs are never fetched, resolved or screenshotted; query strings and fragments are dropped.
- Logs contain route, status and timing — never message content.
- Any record can be deleted from the UI, permanently.

Full text in [docs/PRIVACY.md](docs/PRIVACY.md).

---

## Honest limitations

- The engine cannot verify who sent a message, whether a phone number is real, or what a website does.
- Rules can miss novel scams and can be fooled by careful wording.
- No accuracy, precision or recall figure is claimed. This is not a validated model.
- "Low risk" means *no known pattern matched*, never *proven safe*.
- Without a configured reputation key, no URL is checked against any external database — and the result
  says so instead of implying otherwise.
- The tool is educational. It is not legal, financial or medical advice, and it does not replace your
  bank, the police or a licensed professional.

---

## Project structure

```
ScamSathi/
├── backend/
│   ├── app/
│   │   ├── api/          # v1 routes + dependencies
│   │   ├── core/         # security, errors, rate limiting, logging
│   │   ├── db/           # engine, models, repository, sessions
│   │   ├── schemas/      # Pydantic request/response models
│   │   ├── services/
│   │   │   ├── detection/  # rules, nlp, categories, scoring, explain, engine
│   │   │   ├── url/        # lexical analyzer + reputation provider
│   │   │   └── ai/         # provider abstraction + OpenAI-compatible client
│   │   ├── config.py
│   │   └── main.py
│   ├── tests/            # pytest suite
│   ├── requirements*.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/   # layout, gauge, indicators, charts, states
│   │   ├── pages/        # 9 screens
│   │   ├── lib/          # api client, types, formatting, cache
│   │   └── test/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── .env.example
├── deploy/               # render.yaml, netlify.toml, vercel.json
├── docs/                 # architecture, api, deployment, security, privacy, testing, ui
└── .github/workflows/    # CI: pytest + vitest + build
```

---

## Documentation

| Document | Contents |
| --- | --- |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Modules, data flow, scoring maths, extension points |
| [docs/API.md](docs/API.md) | Every endpoint, schema, error code and example |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Local setup, Docker, Render/Netlify/Vercel, CI |
| [docs/SECURITY.md](docs/SECURITY.md) | Threat model, SSRF stance, input handling, secrets |
| [docs/PRIVACY.md](docs/PRIVACY.md) | What is stored, what is not, how to erase it |
| [docs/TESTING.md](docs/TESTING.md) | Test inventory and how to add cases |
| [docs/ENVIRONMENT.md](docs/ENVIRONMENT.md) | Every variable, its effect and defaults |
| [docs/UI.md](docs/UI.md) | Screen-by-screen preview and design system |

---

## Licence

MIT — see [LICENSE](LICENSE).

Built as an AI engineering capstone project. Report real fraud at
[cybercrime.gov.in](https://cybercrime.gov.in/) or call **1930**.
