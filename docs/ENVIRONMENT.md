# Environment variables

Copy `backend/.env.example` → `backend/.env` and `frontend/.env.example` → `frontend/.env`.
Everything has a working default; keys are optional.

## Backend

| Variable | Type | Default | Effect |
| --- | --- | --- | --- |
| `APP_ENV` | string | `development` | Environment label; `production`/`prod` enables the production flag |
| `APP_NAME` | string | `ScamSathi API` | Shown in OpenAPI and the root route |
| `APP_VERSION` | string | `1.0.0` | Reported by `/health` |
| `ALLOWED_ORIGINS` | csv | `http://localhost:5173,http://127.0.0.1:5173` | CORS allowlist; exact origins, no trailing slash |
| `DATABASE_URL` | url | `sqlite:///./scamsathi.db` | Any SQLAlchemy URL (`postgresql+psycopg://…` for Postgres) |
| `RATE_LIMIT_ANALYZE` | `n/window` | `30/60` | Analyse requests per IP per window (seconds) |
| `RATE_LIMIT_DEFAULT` | `n/window` | `120/60` | All other endpoints |
| `MAX_MESSAGE_CHARS` | int | `5000` | Message input cap |
| `MAX_URL_CHARS` | int | `2048` | URL input cap |
| `AI_PROVIDER` | enum | `none` | `none` or `openai` (any OpenAI-compatible `/chat/completions`) |
| `AI_API_KEY` | secret | – | Required for the AI layer; absent → layer skipped |
| `AI_BASE_URL` | url | `https://api.openai.com/v1` | Compatible endpoint (OpenAI, Groq, Together, Ollama, vLLM) |
| `AI_MODEL` | string | `gpt-4o-mini` | Model identifier |
| `AI_TIMEOUT_SECONDS` | int | `8` | Per-request timeout; failures degrade silently |
| `URL_REPUTATION_PROVIDER` | enum | `none` | `none` or `google_safebrowsing` |
| `SAFEBROWSING_API_KEY` | secret | – | Required for the reputation lookup |

### Behaviour when a key is missing

| Missing | Result |
| --- | --- |
| `AI_API_KEY` | `ai.used: false`, note explains the local engine produced the result |
| `SAFEBROWSING_API_KEY` | `reputation.checked: false`, note says the URL was not checked against any database |

Neither case degrades the analysis itself — rules, NLP, URL structure and explanations always run.

## Frontend

| Variable | Default | Effect |
| --- | --- | --- |
| `VITE_API_BASE_URL` | `http://localhost:8000` | API origin, no trailing slash. **Inlined at build time** — set it before `npm run build`. |

## Secrets hygiene

- `.env` and `.env.*` are git-ignored (except `.env.example`).
- The frontend never receives a backend key; only `VITE_*` values reach the bundle, and none of them are
  secret.
- Rotate `AI_API_KEY` / `SAFEBROWSING_API_KEY` by changing the environment and restarting.
