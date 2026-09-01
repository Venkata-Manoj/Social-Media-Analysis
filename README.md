# SocialPulse — Social Media Sentiment & Engagement Analytics

**Assignment 6 — DSA0606: Handle unstructured/semi-structured data and visualize patterns of engagement and sentiment.**

Static, self-contained application + professional analytical report. No backend, no install, no API keys — double-click to run.

---

## 🚀 Quick Start (30 seconds)

| Step | Action |
|------|--------|
| **1** | Double-click **`index.html`** — opens in any modern browser (Chrome/Edge/Firefox). |
| **2** | Use the 7 filter controls (Platform, Sentiment, Topic, User Type, Date Range, Search) — all charts & KPIs update instantly. |
| **3** | Try the **Text Analysis Playground**: type any sentence → click *Analyze Text* to see cleaning → tokenization → sentiment scoring. |
| **4** | Click **Export Filtered CSV / JSON** to download the current view; or `Ctrl+P` to Print/Save PDF. |

> Offline? Works. The dataset (420 posts) is embedded inside `index.html` and also shipped as `data/*.json` + `data/*.csv`. The only CDN is Chart.js 4.4.1 (`cdn.jsdelivr.net`) — it caches after first open and the file remains inspectable without it.

---

## 📦 Deliverables

| Deliverable | Path | Size / Count | Verify |
|-------------|------|--------------|--------|
| **Static App (single file)** | `index.html` | 286 KB, ~1,100 lines, 420 posts embedded | Double-click → 8 charts + table + playground appear |
| **Dataset — JSON (canonical)** | `data/social_media_dataset.json` | 420 objects, 20 fields | `cat data/*.json \| head -n 30` |
| **Dataset — CSV** | `data/social_media_dataset.csv` | 421 lines (header + 420) | Open in Excel/Sheets |
| **Stats** | `data/dataset_stats.json` | Aggregates | Cross-check report Table 2 |
| **Report (Word)** | `report/Assignment6_Social_Media_Sentiment_Engagement_Report.docx` | ~0.67 MB, ~19–21 pages (A4) | Open → 10 chapters + TOC + 8 figures + 2 appendices |
| **Figures (print fidelity)** | `assets/fig*.png` | 8 PNGs (52–138 KB each) | Also live in app via Chart.js |
| **Generator code** | `data/generate_dataset.py` | Deterministic seed=42 | `python3 data/generate_dataset.py` regenerates byte-identical |
| **Report generator** | `report/generate_report.py` | Builds DOCX + figures | `python3 report/generate_report.py` |
| **App builder** | `src/build_app.py` | Injects JSON into HTML template | `python3 src/build_app.py` |

---

## 🗂️ Project Tree

```
DSA0606-asmt/
├── index.html                  ← ★ THE APP — single-file, double-click
├── data/
│   ├── social_media_dataset.json
│   ├── social_media_dataset.csv
│   ├── dataset_stats.json
│   └── generate_dataset.py     ← deterministic synthetic generator
├── assets/
│   ├── fig1_sentiment.png
│   ├── fig2_platform.png
│   ├── fig3_timeline.png
│   ├── fig4_scatter.png
│   ├── fig5_hashtags.png
│   ├── fig6_topic.png
│   ├── fig7_hourly.png
│   └── fig8_usertype.png
├── report/
│   ├── Assignment6_Social_Media_Sentiment_Engagement_Report.docx  ← THE REPORT
│   └── generate_report.py      ← report + figures builder
├── src/
│   └── build_app.py            ← builds index.html from template
└── README.md                   ← this file
```

---

## 🌐 Web Deployment (static hosting — optional, no build)

The canonical app is `index.html` — it works via `file://` with no server. For hosted review, `web/` adds zero-build deployment configs. See **[`web/README.md`](web/README.md)** for full hosting guide.

| Host | Publish dir (if you deploy) | Config source | Verify after deploy |
|------|-----------------------------|---------------|---------------------|
| **GitHub Pages** (recommended) | repo root `.` (keep single-file canonical) | `netlify.toml` / `vercel.json` copied to root if needed | Open `/` → filter Platform=Instagram → Export CSV (no 404) |
| **Vercel** | root `.` (empty build) or `web/dist` after `npm run sync` | `vercel.json` | `curl -I /data/social_media_dataset.json` → `access-control-allow-origin: *` |
| **Netlify** | root `.` or `web/dist` | `netlify.toml` | Deep link `/` reload still serves `index.html` (SPA fallback) |
| **Python API (local dev)** | `python3 web/server.py --port 8000` | stdlib `http.server` + CORS + `/api/posts` | `curl http://127.0.0.1:8000/api/health` → `{ok:true, posts:420}` |

```bash
# Sync canonical → web/dist (never edit dist directly)
npm --prefix web run sync
# or: python3 src/build_app.py && npm --prefix web run sync
# Local API dev (zero install)
python3 web/server.py --port 8000 --open
```

> All paths stay relative (`assets/...`, `data/...`) so `file://` and any domain both work. Hosting configs only add CORS/cache/SPA fallback — they never require absolute paths.

---

## 📊 What the App Visualizes (8 Charts)

| # | Chart | Type | Pattern it reveals |
|---|-------|------|--------------------|
| 1 | Sentiment Distribution | Donut | 40% pos / 30% neu / 30% neg overall; flips by topic |
| 2 | Platform — Avg Engagement | Grouped Bar (likes/shares/comments) | Instagram/YouTube highest; LinkedIn lowest but most neutral |
| 3 | Top 10 Hashtags | Horizontal Bar | #TechLaunch etc. shift with sentiment filter |
| 4 | Engagement Over Time | Stacked Bar + Line (daily) | Campaign spikes Apr 15, May 20, Jun 10, Jul 18 |
| 5 | Sentiment vs Engagement | Scatter | Viral complaint cluster (upper-left) vs viral praise (upper-right) |
| 6 | Topic × Sentiment | Stacked Bar | Customer Service negative-dominant; Campaign positive-dominant |
| 7 | Engagement by Hour | Line (avg) + Bar (count) | Evening peak in engagement quality; LinkedIn morning peak |
| 8 | User Type Engagement | Bar | Influencer ~80% higher than Regular |

Plus: 4 live KPI cards, 3 auto-insight cards, sortable/paginated raw table (20/page), and a text-processing playground.

---

## 🔍 How to Demonstrate the CO in 2 Minutes

1. **Unstructured handling**: Scroll to *Pipeline + Playground* → type `“This update broke everything. App keeps crashing!”` → *Analyze Text* → show cleaning/tokens/score → Negative, score ≈ −0.7.
2. **Semi-structured handling**: Show *Raw JSON* viewer (hashtags as array, timestamp parsing) → filter by Platform = Instagram → watch hashtag bar re-aggregate.
3. **Sentiment pattern**: Filter Topic = Customer Service → see sentiment donut flip negative + stacked bar confirm → tie to Table 6 / Fig. 6 in report.
4. **Engagement pattern**: Clear filters → see timeline spikes → hover over spike → filter Date around spike → see platform breakdown shift → tie to Fig. 3.
5. **Correlation / anomaly**: Point to Scatter → upper-left dots are high-engagement negatives → click table, sort by Engagement desc, filter Sentiment=Negative → top rows are those same posts.

Every claim is verifiable in the table below the charts.

---

## 🛠️ Reproduce from Source

```bash
# Regenerate dataset (deterministic)
python3 data/generate_dataset.py
# → overwrites data/social_media_dataset.json + .csv + dataset_stats.json

# Rebuild static app (injects JSON into HTML template)
python3 src/build_app.py
# → overwrites index.html

# Rebuild report + 8 figures (requires python-docx, matplotlib, pillow)
pip install python-docx pillow matplotlib --break-system-packages
python3 report/generate_report.py
# → overwrites assets/fig*.png + report/*.docx
```

Python tested: 3.11, `python-docx 1.2.0`, `matplotlib 3.11.1`, `pillow 12.2.0`.

---

## 🎓 Academic Notes

- **Data is synthetic** (seed=42) — no real user data, no privacy issues, fully reproducible. Real-world limitations and extensions (transformer scorer, live ingestion, multilingual) are discussed in report §9.
- **Source code is the HTML** — no hidden backend. Appendix A in the report excerpts and maps every section; the shipped `index.html` is canonical.
- **Print**: `Ctrl+P` from the app prints a clean, chart-preserving PDF (all charts are canvas). The Word report is A4 with headers/footers/page numbers, ready for PDF export.
- **Course Outcome addressed**: *Handle unstructured/semi-structured data and visualize patterns of engagement and sentiment* — evidenced by the pipeline (§5), the 8 charts (§7), and the filter-driven exploration.

---

## 📄 Report at a Glance

| Chapter | Title | Pages | Key Content |
|---------|-------|-------|-------------|
| 1 | Abstract | 1 | End-to-end summary + keywords |
| 2 | Introduction | 1 | Motivation + static constraint |
| 3 | Problem & Objectives | 1 | 7 objectives mapped to CO & deliverables |
| 4 | Dataset Design | 2 | 20-field schema + 7 generation rules + stats |
| 5 | Handling Data | 2 | Cleaning pipeline + tokenization + lexicon scorer + aggregation |
| 6 | System Design | 2 | Tech choices, filter logic, chart rationale |
| 7 | Visual Analysis | 5 | 8 figures with captions + reasoned interpretation + cross-cutting Table 6 |
| 8–10 | Results / Limitations / Conclusion | 1 | Synthesis + future work |
| A–B | Appendices | 2–3 | Full source-code map + sample JSON/CSV |
| — | References + Checklist | 1 | 8 refs + submission checklist |

Open the `.docx` → Table of Contents → `Ctrl+Click` any entry. All figures are 220 dpi PNG, captioned, with grid and color-blind-aware palette (positive green, negative red, neutral amber, brand blue).

---

**Built for evaluation speed**: every insight in Chapter 7 is one filter click away in the app. If a claim can’t be verified in <15 seconds, the report says so — and it can.

*SocialPulse • Assignment 6 • DSA0606 • Static Vis • 2026*
