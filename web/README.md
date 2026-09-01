# SocialPulse — Web Deployment Layer (`web/`)

Production-ready hosting configs around the **canonical single-file** `../index.html` (420-post embedded, 8 Chart.js charts).  
`web/` adds: deployment configs, dev servers, SEO/PWA, and an optional lightweight **Python API** — **without breaking the `file://` double-click fallback**.

> Canonical stays at `/index.html` — `web/` is additive. Deploy from repo root (recommended) or from `web/dist` after `npm run sync`.

---

## Structure

```
DSA0606-asmt/
├── index.html                  # ★ canonical — double-click works everywhere
├── data/*.json|csv             # dataset + stats (also embedded in index.html)
├── assets/fig*.png             # 8 print figures
├── web/
│   ├── package.json            # zero-build static hosting (serve + vite)
│   ├── server.py               # stdlib http.server — static + /api/posts (CORS, cache, SPA fallback)
│   ├── seo.json                # structured SEO plan (title, OG, JSON-LD, manifest)
│   ├── SEO_HEAD.html           # drop-in <head> snippet (relative paths)
│   ├── vercel.json             # Vercel headers + rewrites
│   ├── netlify.toml            # Netlify redirects + headers
│   ├── .htaccess               # Apache SPA fallback + cache + CORS
│   ├── .gitignore & requirements-web.txt
│   ├── public/                 # deploy-ready copy of index.html + data/assets + PWA
│   │   ├── index.html          # synced copy (do not edit — regenerate)
│   │   ├── data/ & assets/     # same as ../
│   │   ├── site.webmanifest, favicon.svg, sitemap.xml, robots.txt
│   │   ├── icons/icon-{192,512}.png
│   │   └── seo-loader.js       # runtime SEO injector (file:// safe)
│   └── scripts/
│       ├── sync.mjs            # copy ../index.html+data+assets → dist/
│       └── apply-seo.mjs       # inject SEO_HEAD.html into ../index.html (--write)
└── report/...
```

---

## Quick Start — Local

### 1. File-direct (no server) — fallback always works
Double-click `../index.html` → 8 charts + table + playground appear.  
Works offline; only CDN is Chart.js `cdn.jsdelivr.net` (caches after first open).

### 2. Python API server (recommended for dev — zero install, CORS + `/api/*`)
```bash
python3 web/server.py --port 8000        # http://127.0.0.1:8000
python3 web/server.py --port 4173 --open # auto-open browser
python3 web/server.py --host 0.0.0.0 --port 8000  # LAN exposure
```
Tests: `curl http://127.0.0.1:8000/api/health` | `curl "http://127.0.0.1:8000/api/posts?platform=Instagram&limit=2"` | `curl http://127.0.0.1:8000/api/stats`

**API** (all GET, CORS `*`, `Cache-Control: no-store`):
- `GET /api/health` → `{ok, posts, date_range, endpoints}`
- `GET /api/stats` → `data/dataset_stats.json`
- `GET /api/seo` → `web/seo.json`
- `GET /api/hashtags` → top 20 tags
- `GET /api/posts?platform=Twitter&sentiment=positive&topic=Marketing%20Campaign&user_type=Influencer&search=launch&start=2026-03-01&end=2026-08-31&limit=20&offset=0&sort=engagement&order=desc` → `{total, limit, offset, returned, filters, data:[...]}`  
  Also `&format=csv` or `GET /api/posts.csv?...` → CSV download.

Static: `GET /data/social_media_dataset.json` (CORS, 5 min cache), `GET /assets/*.png` (1 y immutable), `GET /` → index.html with SPA fallback (unknown route → index.html).

### 3. Node `serve` (zero-build static, no API)
```bash
cd web && npm install          # once (gets `serve` + `vite`)
npm run serve                  # npx serve --listen 4173 --single --cors ..  (serves repo root)
npm run py:serve               # same server.py as above (npm alias)
```
### 4. Vite dev (optional, instant HMR — still serves the same static files)
```bash
npm run dev   # vite --host --port 5173
```

**Relative paths:** all links stay `assets/...`, `data/...`, `web/...` (no leading `/`) so `file://` and any domain both work. Hosting configs only add CORS/cache — they never require absolute paths.

---

## Deploy — Choose One

> All hosts assume publish dir is **repo root** (`../`). If your host requires `web/` as root, first run `npm run sync` (copies `../index.html`+`data`+`assets` → `web/dist`) then publish `web/dist`.

### GitHub Pages (zero-build, recommended)
1. Push repo to GitHub → Settings → Pages → **Source: Deploy from branch** → Branch `main` / folder `/(root)` → Save.
2. Wait ~1 min → site at `https://<user>.github.io/<repo>/`.
3. Verify: open `/`, filter Platform=Instagram, click Export CSV — no 404.  
   Optional custom domain: add `CNAME` at repo root, keep `web/public/sitemap.xml` canonical updated.

*If you prefer `web/dist` as Pages root:* `npm run sync && git add web/dist &&` set Pages → Branch `main` / folder `/web/dist`.

No `gh-pages` branch or Actions required — plain static. For Actions-based Pages, use:
```yaml
# .github/workflows/pages.yml (optional)
on: { push: { branches: [main] }, workflow_dispatch: {} }
permissions: { contents: read, pages: write, id-token: write }
jobs:
  deploy: { runs-on: ubuntu-latest, environment: { name: github-pages, url: ${{ steps.deployment.outputs.page_url }} },
    steps: [{ uses: actions/checkout@v4 }, { uses: actions/configure-pages@v5 }, { uses: actions/upload-pages-artifact@v3, with: { path: '.' } }, { id: deployment, uses: actions/deploy-pages@v4 }] }
```

### Vercel (zero-build)
- **Root deploy (keep canonical):** Import project → Framework: *Other* → Build Command: *(empty)* → Output Directory: *(empty / root)* → Deploy. `web/vercel.json` at root is auto-detected if you copy it: `cp web/vercel.json ./vercel.json` OR set Vercel Project Settings → General → Root Directory = `.` and Vercel will also read `web/vercel.json` via rewrites (dist handles).
- **Web-only deploy:** `npm run sync` → Import `web/dist` as root → Build empty, Output `dist` → Deploy. Headers already set (CORS for data/assets, security, 1 y cache for PNGs).

Test after deploy: `curl -I https://<vercel>/data/social_media_dataset.json` should show `access-control-allow-origin: *` and `cache-control: public, max-age=300`.

### Netlify (zero-build)
- **Root deploy:** New site → pick repo → Build command: *(empty)* → Publish directory: `.` (or empty) → Deploy. Netlify reads `netlify.toml` at root — copy `web/netlify.toml` there: `cp web/netlify.toml ./netlify.toml`.
- **Web-dist deploy:** `npm run sync` → Publish directory: `web/dist` → Build: `npm run sync` (or leave empty if pre-built) → Deploy.

SPAs: the included `[[redirects]] from="/*" to="/index.html" status=200` ensures deep links reload correctly while real files (`/assets/*`, `/data/*`) still serve. To use a real 404 page, create `404.html` and change final redirect to `status=404`.

### Local `http-server` / `npx serve` variants
```bash
npx serve --listen 4173 --single --cors .            # from repo root
npx serve web/dist --listen 4173 --single --cors     # from web/dist after sync
python3 -m http.server 8000 --directory .            # stdlib, but no CORS/SPA — prefer web/server.py
```

### Apache / cPanel shared hosting
Upload `index.html` + `data/` + `assets/` + `web/.htaccess` (as `.htaccess` at docroot). Requires `AllowOverride All` so `.htaccess` rewrites activate. It adds CORS, compression, cache (PNG 1 y, JSON 5 min), and `RewriteRule ^ index.html` SPA fallback.

---

## Build / Sync

Canonical remains `../index.html` (built via `python3 src/build_app.py`).  
`web/dist` is a **deploy copy** — never edit it.

```bash
npm run sync            # copies ../index.html + data + assets + web configs → web/dist
npm run sync -- --public # also syncs to web/public (Netlify publish = public)
python3 src/build_app.py && npm run sync  # full rebuild after dataset change
```

---

## SEO Plan (`web/seo.json` + `SEO_HEAD.html`)

`seo.json` is the single source for title/description/OG/twitter/JSON-LD/manifest. `SEO_HEAD.html` is the drop-in snippet.

**Plan — required meta (relative-friendly):**
- `charset`, `viewport`, `<title>`, `description`, `canonical`, `theme-color`, `color-scheme`
- `og:*` (title, desc, type, url, image 1200×630, locale), `twitter:card=summary_large_image`
- `link rel=icon` (svg) + `apple-touch-icon` (192) + `manifest` → `web/public/site.webmanifest`
- `script type=application/ld+json` — WebApplication + Dataset (see `seo.json:jsonLd*`)
- `robots` + `sitemap.xml` + `robots.txt`

**How to apply (choose one — do not duplicate):**
1. **Manual (auditable, reversible):** paste `SEO_HEAD.html` contents into `../index.html` `<head>` right after `<title>` and before `cdn.jsdelivr` preconnect. Validate at https://search.google.com/test/rich-results.
2. **Automated:** `node web/scripts/apply-seo.mjs --write` (idempotent, wraps markers; revert via `--revert`).
3. **Runtime (no file edit, file:// safe):** add `<script src="web/public/seo-loader.js" defer></script>` to `../index.html` — fetches `seo.json` over http/https only, patches title/canonical/OG at runtime.

All paths are relative (`assets/...`, `web/seo.json`) so `file://` still loads locally — canonical becomes `location.origin + pathname` at runtime only when `http(s)`.

Run `node web/scripts/apply-seo.mjs` dry-run first; commit only if you intend search indexing.

---

## PWA (optional, offline-ready)

`public/site.webmanifest` + `public/icons/icon-{192,512}.png` + `favicon.svg` are ready. To make PWA installable:
1. Ensure `SEO_HEAD.html` manifest link is present.
2. Add a service worker (not included — keeps zero-build) — e.g., `workbox` or simple cache-first for `index.html`/`data/*.json`/`assets/*.png`.
3. Test Lighthouse → PWA → Installable.

Icons are pillow-generated placeholders — replace with branded 192/512 before store submission.

---

## Versioning & Cache

- **HTML:** `Cache-Control: no-cache, must-revalidate` (ensures new deploys show immediately).
- **Data JSON/CSV:** `300s must-revalidate` + CORS — fresh enough for filters, but CDN-friendly.
- **Assets PNG:** `31536000 immutable` + CORS — long-lived; bump filename if changing.
- **API:** `no-store` — always live filtered view.

Deploys are atomic on Vercel/Netlify; rollbacks are one click.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `file://` shows blank / Chart.js missing | CDN offline — wait or locally vendor `chart.umd.min.js`; all else works offline. |
| GitHub Pages 404 on refresh `/some/route` | SPA fallback missing — ensure `vercel.json`/`netlify.toml`/`.htaccess` is at publish root, or deploy via root (no prefix). |
| `python3 web/server.py` port busy | It auto-retries 4173/3000/8001/8080; or `python3 web/server.py -p 5000`. |
| CORS error fetching `data/*.json` remotely | Confirm host sends `access-control-allow-origin: *` (check `curl -I`). Local: use `server.py` or `npx serve --cors`. |
| Icons look blurry on install | Replace `public/icons/*.png` with true 192/512 exports from Figma. |

---

## Keeping `index.html` Canonical

- **Do edit:** `src/build_app.py` template → `python3 src/build_app.py` → regenerates `index.html` + `web/public/index.html` via `npm run sync`.
- **Do not edit:** `web/dist/index.html` or `web/public/index.html` directly — they are copies.
- **Verify after any change:** `grep -c Chart.js ../index.html` (should be ≥1), `ls -lh ../index.html` (~286 KB), double-click still opens.

---

*SocialPulse • DSA0606 Assignment 6 • Static-first, API-optional, deploy anywhere.*
