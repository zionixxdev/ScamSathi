# Deployment

The frontend and backend deploy independently. Nothing in one needs the other's filesystem.

## 1. Local development

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Health check: `curl localhost:8000/api/v1/health` → `{"status":"ok",…}`. SQLite is created on first
boot (`scamsathi.db`). Swagger UI at `/docs`.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env               # VITE_API_BASE_URL=http://localhost:8000
npm run dev                        # http://localhost:5173
```

Vite's dev server does not proxy the API; the browser calls `VITE_API_BASE_URL` directly, which is why
`ALLOWED_ORIGINS` must include `http://localhost:5173` (it does by default).

### Production build locally

```bash
cd frontend && npm run build && npm run preview
cd backend  && uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 2. Docker

```bash
# Backend
docker build -t scamsathi-api ./backend
docker run -p 8000:8000 -e ALLOWED_ORIGINS=https://your-frontend.example scamsathi-api

# Frontend (nginx, API URL baked at build time)
docker build -t scamsathi-web --build-arg VITE_API_BASE_URL=https://your-api.example ./frontend
docker run -p 8080:80 scamsathi-web
```

Both images run as a non-root user and expose a healthcheck.

## 3. Free-tier hosting

### Backend — Render

1. Push this repository to GitHub.
2. Render → **New → Blueprint** → select the repo. `deploy/render.yaml` creates the service.
3. Set `ALLOWED_ORIGINS` to your frontend URL, e.g. `https://scamsathi.netlify.app`.
4. Note the service URL, e.g. `https://scamsathi-api.onrender.com`.

Free instances sleep when idle; the first request after a sleep takes a few seconds. SQLite on an
ephemeral filesystem is wiped on redeploy — attach a persistent disk, or point `DATABASE_URL` at a free
PostgreSQL instance and the repository layer keeps working unchanged.

### Frontend — Netlify

```bash
npm i -g netlify-cli
cd frontend
netlify deploy --build --prod \
  --build-command "npm run build" \
  --dir dist
```

Set `VITE_API_BASE_URL` in **Site settings → Environment variables** *before* the build (Vite inlines it
at build time). `deploy/netlify.toml` includes the SPA redirect rule that client-side routing needs.

### Frontend — Vercel

```bash
cd frontend && vercel --prod
```

`deploy/vercel.json` supplies the SPA rewrite. Add `VITE_API_BASE_URL` in project settings.

### Frontend — Cloudflare Pages / GitHub Pages

Build command `npm run build`, output directory `dist`, environment variable `VITE_API_BASE_URL`. For
GitHub Pages under a sub-path, set `base` in `vite.config.ts`.

## 4. Post-deployment checklist

- [ ] `GET /api/v1/health` returns `status: ok`
- [ ] `ALLOWED_ORIGINS` contains the exact frontend origin (scheme + host, no trailing slash)
- [ ] A message scan from the deployed UI returns a result and `stored: true`
- [ ] History shows the scan; delete removes it
- [ ] Browser console shows no CORS errors
- [ ] `curl -I` shows `X-Content-Type-Options`, `X-Frame-Options` and `Cache-Control: no-store`
- [ ] No `.env` file is present in the repository
- [ ] Rate limiting behaves (30 analyses per minute per IP by default)

## 5. Continuous integration

`.github/workflows/ci.yml` runs on every push and pull request:

1. Backend — install requirements, run `pytest`.
2. Frontend — `npm ci`, `npm run test`, `npm run build`.

Both jobs must pass before a merge. No secrets are required; the suite runs with `AI_PROVIDER=none`.

## 6. Operations notes

| Concern | Guidance |
| --- | --- |
| Database growth | `scans` grows with usage. Add a retention job (`DELETE FROM scans WHERE created_at < …`) if needed. |
| Multiple instances | Replace the in-process rate limiter with Redis; keep the `check()` interface. |
| Logs | Content-free by design. Ship them anywhere without a privacy review. |
| Secrets | Environment variables only. Never commit `.env`; `.gitignore` blocks it. |
| Key rotation | `AI_API_KEY` and `SAFEBROWSING_API_KEY` can be rotated with a restart; nothing is persisted from them. |
| Backups | `payload` holds the full result, `excerpt` the redacted preview. Back up only if you need history retention. |
