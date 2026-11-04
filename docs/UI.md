# UI guide and preview instructions

## Design system

| Token | Value | Use |
| --- | --- | --- |
| Background | `#04060d` + radial mesh gradients | Dark-first canvas |
| Surface | `bg-white/[0.035]` + `backdrop-blur-xl` + `border-white/[0.08]` | Glass cards |
| Accent | `#22d3ee` → `#34d399` gradient | Primary actions, focus rings |
| Risk: Low | `#34d399` | Safe / no pattern |
| Risk: Medium | `#fbbf24` | Verify before acting |
| Risk: High | `#fb923c` | Do not engage |
| Risk: Critical | `#f43f5e` | Multiple strong signals |
| Risk: Uncertain | `#a78bfa` | Not enough signal |
| Type | Inter (UI), JetBrains Mono (scores, evidence, URLs) | Clean, technical |
| Icons | Lucide React | Consistent stroke weight |
| Motion | 400 ms fade-up, 700 ms gauge sweep, pulse rings — all disabled under `prefers-reduced-motion` | Lightweight |

Layout: 256 px sidebar on desktop, collapsible top bar + bottom tab bar on mobile, 1152 px max content
width. Focus-visible rings everywhere, a skip link, `aria-expanded` on disclosures, and labelled SVG
charts.

## Screens

1. **Landing** (`/`) — hero with the tagline, a worked example card, six feature cards, three-step
   explainer, privacy strip, official-resource footer.
2. **Dashboard** (`/dashboard`) — four stat cards (total scans, high-risk, categories seen, privacy mode),
   category donut, risk-level bars, recent analyses list, quick-scan tiles.
3. **Message Scanner** (`/scan/message`) — textarea with a 5,000-character counter, channel and language
   selectors, optional DLT sender id, storage toggle, four one-click samples, "what gets checked" panel.
4. **URL Scanner** (`/scan/url`) — single URL field, storage toggle, four samples, analysis checklist and
   an HTTPS-is-not-safety warning.
5. **Analysis Result** (`/result/:scanId`) — half-circle risk gauge with score and confidence, level badge,
   category, one-paragraph explanation, uncertainty banner, indicator cards with evidence snippets,
   mitigator panel, link-analysis card, numbered action list, redacted content preview, engine panel,
   disclaimer.
6. **Scan History** (`/history`) — risk-level filters, paginated list with badges and redacted previews,
   per-row delete.
7. **Scam Intelligence** (`/intelligence`) — twelve expandable threat profiles: how it works, real-style
   example lines, counter-moves.
8. **Safety Guide** (`/guide`) — seven sections (common scams, phishing, UPI, OTP, fake jobs, safe
   browsing, reporting) plus official resources: cybercrime.gov.in, CERT-In, Sanchar Saathi.
9. **About & Privacy** (`/about`) — pipeline explanation, privacy commitments, limitations, tech stack,
   "forget my local id" control.

## How to capture screenshots

```bash
# 1. Run both services
cd backend  && uvicorn app.main:app --port 8000
cd frontend && npm run dev            # http://localhost:5173

# 2. Open in a 1440×900 browser window at 100% zoom

# 3. Capture, in this order
/                     Landing
/dashboard            Dashboard (run two or three scans first so charts have data)
/scan/message         Message scanner, with the "Fake KYC" sample loaded
/scan/url             URL scanner, with "Lookalike domain" loaded
/result/<scan_id>     Result page for the fake-KYC scan (Critical, 100)
/history              History with three records
/intelligence         Intelligence with the first profile expanded
/guide                Safety guide, top of page
/about                About & privacy
```

Suggested filenames: `docs/screenshots/01-landing.png` … `09-about.png`. Take one mobile capture at
390×844 for the dashboard to show the responsive layout.

## Accessibility notes

- Contrast: body text ≥ 4.5:1 on the dark canvas; large numerals are white on near-black.
- Colour is never the only signal — every risk level carries a text label.
- The gauge has `role="img"` and an `aria-label` stating score and level.
- Charts have text legends and accessible names.
- All interactive elements are reachable by keyboard; the skip link is the first tab stop.
- Animations respect `prefers-reduced-motion`.
