#!/usr/bin/env python3
import json
import pathlib

DATA_PATH = pathlib.Path("/mnt/e/DSA0606-asmt/data/social_media_dataset.json")
OUT_PATH = pathlib.Path("/mnt/e/DSA0606-asmt/index.html")

data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
embedded_json = json.dumps(data, ensure_ascii=False)

html_template = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>SocialPulse — Sentiment & Engagement Analytics | Assignment 6</title>
<meta name="description" content="SocialPulse: static, single-file analytics for 420 synthetic social posts — sentiment patterns, engagement drivers and platform behaviors. DSA0606 Assignment 6, offline, no backend."/>
<link rel="canonical" href="https://example.com/socialpulse/"/>
<meta name="theme-color" content="#2563eb" media="(prefers-color-scheme: light)"/>
<meta name="theme-color" content="#0f172a" media="(prefers-color-scheme: dark)"/>
<!-- Open Graph -->
<meta property="og:title" content="SocialPulse — Sentiment & Engagement Analytics"/>
<meta property="og:description" content="From unstructured text to engagement intelligence — 420 posts, 8 charts, live filters, all in one static HTML file."/>
<meta property="og:type" content="website"/>
<meta property="og:url" content="https://example.com/socialpulse/"/>
<meta property="og:image" content="https://example.com/socialpulse/assets/fig3_timeline.png"/>
<meta property="og:image:width" content="1200"/>
<meta property="og:image:height" content="630"/>
<!-- Twitter -->
<meta name="twitter:card" content="summary_large_image"/>
<meta name="twitter:title" content="SocialPulse — Sentiment & Engagement Analytics"/>
<meta name="twitter:description" content="Static offline dashboard for social sentiment & engagement — 420 posts, 9 visualizations, client-side filtering."/>
<meta name="twitter:image" content="https://example.com/socialpulse/assets/fig3_timeline.png"/>
<!-- Favicon & Manifest -->
<link rel="icon" type="image/svg+xml" href="favicon.svg"/>
<link rel="alternate icon" href="favicon.svg"/>
<link rel="manifest" href="site.webmanifest"/>
<link rel="preconnect" href="https://cdn.jsdelivr.net"/>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Dataset",
  "name": "SocialPulse Social Media Sentiment & Engagement (Synthetic, 420 posts)",
  "description": "Synthetic social media dataset for DSA0606 Assignment 6: 420 posts with text, sentiment, engagement metrics, hashtags, topics, platforms, and temporal fields, used to visualize sentiment and engagement patterns.",
  "creator": { "@type": "Organization", "name": "SocialPulse" },
  "keywords": ["sentiment analysis","social media","engagement","unstructured data","visualization","Chart.js"],
  "datePublished": "2026-03-01",
  "temporalCoverage": "2026-03-01/2026-08-31",
  "distribution": [
    { "@type": "DataDownload", "encodingFormat": "application/json", "contentUrl": "data/social_media_dataset.json" },
    { "@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": "data/social_media_dataset.csv" }
  ],
  "variableMeasured": ["sentiment_score","likes","shares","comments","engagement","hashtags","topic","platform"],
  "isAccessibleForFree": true
}
</script>
<style>
:root{
  --bg:#f6f7fb;
  --card:#ffffff;
  --ink:#0f172a;
  --muted:#64748b;
  --line:#e2e8f0;
  --brand:#2563eb;
  --brand-2:#4f46e5;
  --pos:#0e9f6e;
  --neg:#e11d48;
  --neu:#d97706;
  --radius:16px;
  --shadow: 0 8px 24px rgba(15,23,42,.06), 0 1px 3px rgba(15,23,42,.08);
  --shadow-hover: 0 12px 32px rgba(15,23,42,.10), 0 4px 12px rgba(15,23,42,.08);
  --focus:#2563eb;
  --skeleton:#e2e8f0;
  --skeleton-shine:#f1f5f9;
}
[data-theme="dark"]{
  --bg:#0f172a;
  --card:#1e293b;
  --ink:#e2e8f0;
  --muted:#94a3b8;
  --line:#334155;
  --brand:#3b82f6;
  --brand-2:#6366f1;
  --pos:#10b981;
  --neg:#f43f5e;
  --neu:#f59e0b;
  --shadow: 0 8px 24px rgba(0,0,0,.35), 0 1px 3px rgba(0,0,0,.4);
  --shadow-hover: 0 12px 32px rgba(0,0,0,.5);
  --focus:#60a5fa;
  --skeleton:#1e293b;
  --skeleton-shine:#2e3e58;
  color-scheme: dark;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
html,body{margin:0;padding:0;background:var(--bg);color:var(--ink);font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif; -webkit-font-smoothing:antialiased; text-rendering:optimizeLegibility}
a{color:var(--brand);text-decoration:none}
a:hover{text-decoration:underline; text-underline-offset:3px}
a:focus-visible, button:focus-visible, select:focus-visible, input:focus-visible, textarea:focus-visible{outline:2px solid var(--focus); outline-offset:2px; border-radius:6px}
.skip-link{position:absolute;left:-9999px;top:auto;width:1px;height:1px;overflow:hidden;background:var(--ink);color:var(--card);padding:10px 14px;border-radius:10px;font-weight:800;z-index:100}
.skip-link:focus{left:12px;top:12px;width:auto;height:auto;box-shadow:var(--shadow)}
.container{max-width:1280px;margin:0 auto;padding:0 20px}
.topbar{
  position:sticky;top:0;z-index:30;
  backdrop-filter:saturate(180%) blur(12px);
  background:color-mix(in srgb, var(--card) 82%, transparent);
  border-bottom:1px solid var(--line);
}
.topbar-inner{display:flex;align-items:center;justify-content:space-between;padding:14px 0;gap:16px;flex-wrap:wrap}
.brand{display:flex;align-items:center;gap:12px}
.logo{
  width:40px;height:40px;border-radius:12px;
  background:linear-gradient(135deg,var(--brand),var(--brand-2));
  display:grid;place-items:center;color:white;font-weight:800;letter-spacing:.5px;
  box-shadow:0 8px 18px rgba(37,99,235,.28)
}
.brand h1{font-size:18px;line-height:1;margin:0;font-weight:800}
.brand p{margin:2px 0 0;color:var(--muted);font-size:12px}
.topbar-actions{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.pills{display:flex;gap:8px;flex-wrap:wrap}
.pill{font-size:11px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;padding:7px 10px;border-radius:999px;border:1px solid var(--line);background:var(--card);color:var(--muted)}
.pill.brandpill{background:linear-gradient(135deg,var(--brand),var(--brand-2));color:white;border-color:transparent}
.icon-btn{
  width:38px;height:38px;border-radius:10px;border:1px solid var(--line);background:var(--card);display:grid;place-items:center;cursor:pointer;color:var(--ink);transition:.18s;
}
.icon-btn:hover{transform:translateY(-1px);box-shadow:var(--shadow);border-color:var(--brand)}
.hero{padding:22px 0 8px}
.hero-grid{display:grid;grid-template-columns:1.35fr .85fr;gap:16px}
@media (max-width:900px){.hero-grid{grid-template-columns:1fr}}
.hero-card{
  background:linear-gradient(135deg,#2563eb 0%,#4f46e5 55%,#7c3aed 100%);
  color:white;border-radius:20px;padding:22px;position:relative;overflow:hidden;box-shadow:var(--shadow)
}
[data-theme="dark"] .hero-card{box-shadow:var(--shadow)}
.hero-card h2{margin:0 0 8px;font-size:24px;line-height:1.15}
.hero-card p{margin:0;color:rgba(255,255,255,.92);font-size:13.5px;line-height:1.6}
.hero-card .metrics{display:flex;gap:14px;margin-top:16px;flex-wrap:wrap}
.hero-card .metric{background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.18);backdrop-filter:blur(6px);padding:10px 12px;border-radius:12px;min-width:130px}
.hero-card .metric b{display:block;font-size:20px;line-height:1}
.hero-card .metric span{font-size:11px;opacity:.9;letter-spacing:.05em;text-transform:uppercase}
.hero-card:after{
  content:"";position:absolute;right:-30px;top:-30px;width:160px;height:160px;
  background:radial-gradient(circle at 30% 30%, rgba(255,255,255,.28), transparent 60%);
  border-radius:50%
}
.side-card{background:var(--card);border:1px solid var(--line);border-radius:20px;padding:16px;box-shadow:var(--shadow);transition:transform .18s, box-shadow .18s}
.side-card:hover{transform:translateY(-1px);box-shadow:var(--shadow-hover)}
.side-card h3{margin:0 0 10px;font-size:13px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
.legend{display:flex;gap:8px;flex-wrap:wrap}
.legend span{display:inline-flex;align-items:center;gap:6px;font-size:12px;font-weight:600;background:color-mix(in srgb, var(--bg) 80%, var(--card));border:1px solid var(--line);padding:6px 10px;border-radius:999px}
.dot{width:10px;height:10px;border-radius:50%}
.kpi-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:16px 0}
@media (max-width:900px){.kpi-grid{grid-template-columns:repeat(2,1fr)}}
@media (max-width:560px){.kpi-grid{grid-template-columns:1fr}}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:14px;box-shadow:var(--shadow);position:relative;overflow:hidden;transition:transform .18s, box-shadow .18s}
.kpi:hover{transform:translateY(-2px);box-shadow:var(--shadow-hover)}
.kpi h4{margin:0;font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
.kpi .val{margin:8px 0 4px;font-size:26px;font-weight:800;letter-spacing:-.02em}
.kpi .sub{font-size:12px;color:var(--muted)}
.kpi .trend{position:absolute;right:12px;top:12px;font-size:11px;font-weight:800;padding:6px 8px;border-radius:999px;border:1px solid var(--line);background:var(--bg);color:var(--muted)}
.filter-bar{position:sticky;top:66px;z-index:20;background:var(--bg);padding-top:12px;margin:16px 0 6px}
.filter-bar-inner{background:var(--card);border:1px solid var(--line);border-radius:16px;box-shadow:var(--shadow);overflow:hidden}
.filter-bar-head{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:12px 14px;border-bottom:1px solid var(--line);flex-wrap:wrap;background:color-mix(in srgb, var(--card) 96%, var(--bg))}
.filter-meta{display:flex;align-items:center;gap:8px;flex-wrap:wrap;font-size:12px;color:var(--muted)}
.active-chip{background:linear-gradient(135deg,var(--brand),var(--brand-2));color:white;padding:6px 10px;border-radius:999px;font-weight:800;font-size:11px;letter-spacing:.04em;box-shadow:0 4px 10px rgba(37,99,235,.18)}
.filter-head-actions{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.filter-trigger{display:none;align-items:center;gap:6px}
.filters{
  display:grid;grid-template-columns:repeat(4,1fr);gap:12px;align-items:end;padding:14px;
}
@media (min-width:1280px){.filters{grid-template-columns:repeat(7,1fr)}}
@media (max-width:1100px){.filters{grid-template-columns:repeat(3,1fr)}}
@media (max-width:640px){.filters{grid-template-columns:1fr 1fr}}
.filters label{font-size:11px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);display:block;margin:0 0 6px}
.filters select, .filters input{
  width:100%;padding:10px 11px;border-radius:10px;border:1px solid var(--line);background:var(--card);
  font-size:13px;font-weight:600;color:var(--ink);outline:none;transition:border-color .15s, box-shadow .15s, background .15s;
}
.filters select:focus, .filters input:focus{border-color:var(--brand);box-shadow:0 0 0 3px color-mix(in srgb, var(--brand) 18%, transparent)}
.filters select:hover, .filters input:hover{border-color:color-mix(in srgb, var(--line) 60%, var(--muted))}
.btn{
  padding:11px 12px;border-radius:10px;border:1px solid var(--line);background:var(--card);color:var(--ink);
  font-weight:800;font-size:13px;cursor:pointer;transition:transform .12s, filter .15s, box-shadow .15s, background .15s, border-color .15s;
}
.btn:hover{filter:brightness(1.02);box-shadow:0 4px 12px rgba(37,99,235,.12);transform:translateY(-1px)}
.btn:active{transform:translateY(1px) scale(.98)}
.btn.primary{background:linear-gradient(135deg,var(--brand),var(--brand-2));color:white;border-color:transparent;box-shadow:0 6px 16px rgba(37,99,235,.24)}
.btn.primary:hover{filter:brightness(1.06);box-shadow:0 8px 20px rgba(37,99,235,.28)}
.btn:disabled{opacity:.55;cursor:not-allowed;transform:none;box-shadow:none}
.btn-row{display:flex;gap:8px;align-items:end}
@media (max-width:768px){
  .filter-bar{top:60px}
  .filter-trigger{display:inline-flex !important}
  .filters{
    position:fixed;inset:0 0 0 auto;width:min(420px, 92vw);max-width:92vw;height:100dvh;overflow:auto;
    grid-template-columns:1fr !important;align-content:start;gap:14px;
    padding:20px 16px 24px;border-radius:0;border-left:1px solid var(--line);
    transform:translateX(100%);transition:transform .32s cubic-bezier(.4,0,.2,1);
    z-index:41;box-shadow: -12px 0 32px rgba(15,23,42,.18);background:var(--card);
  }
  .filters.open{transform:translateX(0)}
  .backdrop{position:fixed;inset:0;background:rgba(15,23,42,.45);backdrop-filter:blur(3px);z-index:40;opacity:0;pointer-events:none;transition:opacity .22s}
  .backdrop.show{opacity:1;pointer-events:auto}
  .filter-bar-inner{border-radius:16px}
}
.grid{
  display:grid;grid-template-columns:repeat(12,1fr);gap:14px;margin:16px 0;
}
.card{
  background:var(--card);border:1px solid var(--line);border-radius:16px;box-shadow:var(--shadow);padding:14px;
  display:flex;flex-direction:column;min-height:320px;transition:transform .18s, box-shadow .18s, border-color .18s;
  animation: rise .45s ease both;
}
.card:hover{transform:translateY(-2px);box-shadow:var(--shadow-hover);border-color:color-mix(in srgb, var(--line) 70%, var(--brand) 12%)}
.card.half{grid-column:span 6}
.card.third{grid-column:span 4}
.card.two-thirds{grid-column:span 8}
.card.full{grid-column:span 12}
@media (max-width:980px){
  .card.half,.card.third,.card.two-thirds{grid-column:span 12}
}
@keyframes rise{from{opacity:0; transform:translateY(8px)} to{opacity:1; transform:translateY(0)}}
.card:nth-child(1){animation-delay:.02s} .card:nth-child(2){animation-delay:.06s} .card:nth-child(3){animation-delay:.1s} .card:nth-child(4){animation-delay:.14s}
.card-head{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:10px}
.card-head h3{margin:0;font-size:13px;letter-spacing:.02em;font-weight:800}
.card-head p{margin:0;font-size:12px;color:var(--muted)}
.badge{font-size:11px;font-weight:800;letter-spacing:.05em;text-transform:uppercase;padding:6px 8px;border-radius:999px;border:1px solid var(--line);background:var(--bg);color:var(--muted)}
.canvas-wrap{position:relative;flex:1;min-height:260px;transition:opacity .2s}
.canvas-wrap.tall{min-height:300px}
.canvas-wrap canvas{width:100% !important;height:100% !important}
.skeleton{position:absolute;inset:0;border-radius:12px;background:linear-gradient(90deg, var(--skeleton) 25%, var(--skeleton-shine) 50%, var(--skeleton) 75%);background-size:200% 100%;animation:shimmer 1.2s infinite;opacity:0;pointer-events:none;transition:opacity .18s}
.skeleton.show{opacity:1}
@keyframes shimmer{0%{background-position:200% 0} 100%{background-position:-200% 0}}
.cloud{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;align-items:center;padding:10px;min-height:220px}
.cloud span{display:inline-block;padding:6px 10px;border-radius:999px;font-weight:800;line-height:1;transition:transform .15s, box-shadow .15s;cursor:default;border:1px solid var(--line);background:var(--bg)}
.cloud span:hover{transform:scale(1.08) translateY(-1px);box-shadow:var(--shadow)}
.insights{
  display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:6px 0 0;
}
@media (max-width:900px){.insights{grid-template-columns:1fr}}
.insight{
  background:var(--card);border:1px solid var(--line);border-radius:14px;padding:12px;box-shadow:var(--shadow);transition:transform .15s
}
.insight:hover{transform:translateY(-1px)}
.insight h4{margin:0 0 6px;font-size:12px;letter-spacing:.05em;text-transform:uppercase;color:var(--muted)}
.insight p{margin:0;font-size:13px;line-height:1.5}
.pipe{
  background:var(--card);border:1px solid var(--line);border-radius:16px;box-shadow:var(--shadow);padding:16px;margin:16px 0;
}
.pipe h3{margin:0 0 8px}
.pipeline{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-top:10px}
@media (max-width:900px){.pipeline{grid-template-columns:1fr}}
.step{background:var(--bg);border:1px solid var(--line);border-radius:12px;padding:12px;transition:transform .15s}
.step:hover{transform:translateY(-1px)}
.step b{font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--brand)}
.step p{margin:6px 0 0;font-size:13px;line-height:1.5;color:var(--ink)}
.step code{display:block;margin-top:8px;background:var(--card);border:1px solid var(--line);border-radius:8px;padding:8px;font-family:JetBrains Mono, monospace;font-size:11px;white-space:pre-wrap;word-break:break-word;color:var(--ink)}
.playground{
  display:grid;grid-template-columns:1.1fr .9fr;gap:12px;margin-top:12px
}
@media (max-width:900px){.playground{grid-template-columns:1fr}}
.playground textarea{width:100%;min-height:110px;padding:12px;border-radius:12px;border:1px solid var(--line);background:var(--card);color:var(--ink);font-size:13px;line-height:1.5;resize:vertical}
.playground .result{background:#0f172a;color:#e2e8f0;border-radius:12px;padding:12px;font-family:JetBrains Mono,monospace;font-size:12px;line-height:1.6;white-space:pre-wrap;overflow:auto;max-height:360px}
[data-theme="dark"] .playground .result{background:#020617;border:1px solid #1e293b}
.table-wrap{background:var(--card);border:1px solid var(--line);border-radius:16px;box-shadow:var(--shadow);overflow:hidden;margin:16px 0}
.table-head{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:12px 14px;border-bottom:1px solid var(--line);flex-wrap:wrap}
.table-head h3{margin:0;font-size:14px}
.table-actions{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.table-actions input{padding:8px 10px;border-radius:8px;border:1px solid var(--line);background:var(--card);color:var(--ink);font-size:13px}
.table-meta{font-size:12px;color:var(--muted)}
table{width:100%;border-collapse:collapse}
th{font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);text-align:left;padding:10px 12px;background:var(--bg);border-bottom:1px solid var(--line);white-space:nowrap;cursor:pointer;user-select:none;position:relative}
th:hover{color:var(--ink);background:color-mix(in srgb, var(--bg) 80%, var(--line))}
th[aria-sort="ascending"]::after{content:" ▲";font-size:10px}
th[aria-sort="descending"]::after{content:" ▼";font-size:10px}
td{padding:10px 12px;border-bottom:1px solid color-mix(in srgb, var(--line) 70%, transparent);font-size:13px;vertical-align:top}
tr:hover td{background:color-mix(in srgb, var(--bg) 70%, transparent)}
.platform-badge{padding:4px 8px;border-radius:999px;font-size:11px;font-weight:800;border:1px solid var(--line);background:var(--card)}
.sentiment-pill{padding:4px 8px;border-radius:999px;font-size:11px;font-weight:800;color:white;display:inline-block}
.sentiment-pill.positive{background:var(--pos)}
.sentiment-pill.negative{background:var(--neg)}
.sentiment-pill.neutral{background:var(--neu);color:white}
[data-theme="dark"] .sentiment-pill.neutral{color:#0f172a}
.eng{font-weight:800}
.mono{font-family:JetBrains Mono,monospace}
.pagination{display:flex;align-items:center;justify-content:space-between;padding:10px 12px;gap:10px;flex-wrap:wrap}
.pagination button{padding:8px 12px;border-radius:8px;border:1px solid var(--line);background:var(--card);color:var(--ink);font-weight:700;cursor:pointer;transition:.15s}
.pagination button:hover:not(:disabled){border-color:var(--brand);transform:translateY(-1px)}
.pagination button:disabled{opacity:.45;cursor:not-allowed}
.footer{text-align:center;color:var(--muted);font-size:12px;padding:18px 0;line-height:1.6}
.json-view{background:#0f172a;color:#e2e8f0;border-radius:12px;padding:12px;font-family:JetBrains Mono,monospace;font-size:11.5px;line-height:1.6;overflow:auto;max-height:340px;border:1px solid #1e293b}
[data-theme="dark"] .json-view{background:#020617}
.kpi .icon{position:absolute;right:14px;bottom:12px;opacity:.08;font-size:42px;pointer-events:none}
.empty-state{text-align:center;padding:36px 16px;display:grid;place-items:center;gap:14px;color:var(--muted)}
.empty-state .illus{width:88px;height:88px;border-radius:22px;background:linear-gradient(135deg, color-mix(in srgb, var(--brand) 14%, transparent), color-mix(in srgb, var(--brand-2) 14%, transparent));display:grid;place-items:center;font-size:38px;border:1px dashed var(--line)}
.empty-state h4{margin:0;color:var(--ink);font-size:16px}
.empty-state p{margin:0;max-width:440px;line-height:1.6;font-size:13px}
.toast{position:fixed;bottom:18px;left:50%;transform:translateX(-50%) translateY(12px);background:var(--ink);color:var(--card);padding:10px 14px;border-radius:999px;font-size:13px;font-weight:700;box-shadow:var(--shadow);opacity:0;pointer-events:none;transition:opacity .2s, transform .2s;z-index:50;max-width:90vw;text-align:center}
.toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
@media (prefers-reduced-motion: reduce){
  *{animation:none !important;transition:none !important;scroll-behavior:auto !important}
  .card{animation:none}
  .skeleton{animation:none}
}
@media print{
  .topbar, .filter-bar, .playground textarea, .table-actions input, .filter-trigger, .backdrop, .toast, #theme_toggle, #btn_share, .icon-btn{display:none !important}
  body{background:white !important;color:black !important}
  .card, .kpi, .side-card, .table-wrap, .pipe{break-inside:avoid;box-shadow:none !important;border:1px solid #ddd !important;animation:none !important;transform:none !important}
  canvas{max-height:280px !important}
  a{color:black !important}
}
.visually-hidden{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
</style>
</head>
<body>
<a href="#main" class="skip-link">Skip to content</a>
<div class="topbar" role="banner">
  <div class="container">
    <div class="topbar-inner">
      <div class="brand" aria-label="SocialPulse brand">
        <div class="logo" aria-hidden="true">S•P</div>
        <div>
          <h1>SocialPulse</h1>
          <p>Sentiment &amp; Engagement Analytics &nbsp;•&nbsp; Assignment 6 — DSA0606</p>
        </div>
      </div>
      <div class="topbar-actions">
        <div class="pills" aria-label="Dataset summary">
          <span class="pill brandpill">Static • Offline • No Backend</span>
          <span class="pill">420 posts • 2026-03-01 → 2026-08-31</span>
          <span class="pill">Chart.js • Vanilla JS</span>
        </div>
        <button id="theme_toggle" class="icon-btn" type="button" aria-label="Toggle dark mode" title="Toggle theme (saves to localStorage)">
          <span aria-hidden="true" id="theme_icon">🌙</span>
        </button>
      </div>
    </div>
  </div>
</div>

<main id="main" class="container" tabindex="-1">
<div class="hero">
  <div class="hero-grid">
    <div class="hero-card">
      <h2>From unstructured text to engagement intelligence.</h2>
      <p>Handling semi-structured social data (text + likes/shares/comments + hashtags + timestamps) and visualizing sentiment patterns, platform behaviors, and engagement drivers — all in a <b>single static HTML file</b> with embedded data and client-side filtering.</p>
      <div class="metrics">
        <div class="metric"><b id="hero_total">420</b><span>Total posts</span></div>
        <div class="metric"><b id="hero_platforms">5 platforms</b><span>Twitter · Instagram · FB · LinkedIn · YouTube</span></div>
        <div class="metric"><b id="hero_sent">Mixed sentiment</b><span>Positive / Neutral / Negative</span></div>
      </div>
    </div>
    <div class="side-card">
      <h3>How to use — static app</h3>
      <p style="margin:0 0 10px;color:var(--muted);font-size:13px;line-height:1.6">This file works with <b>double-click → open in browser</b>. No install, no server, no API. Use filters below to slice by platform / sentiment / topic / date. All charts and KPIs update instantly. Export filtered views as CSV/JSON.</p>
      <div class="legend" aria-label="Legend">
        <span><i class="dot" style="background:var(--pos)" aria-hidden="true"></i> Positive</span>
        <span><i class="dot" style="background:var(--neu)" aria-hidden="true"></i> Neutral</span>
        <span><i class="dot" style="background:var(--neg)" aria-hidden="true"></i> Negative</span>
        <span><i class="dot" style="background:var(--brand)" aria-hidden="true"></i> Engagement = Likes+Shares+Comments</span>
      </div>
      <div style="margin-top:12px;display:flex;gap:8px;flex-wrap:wrap">
        <button class="btn primary" onclick="document.getElementById('filterBar').scrollIntoView({behavior:'smooth', block:'start'})" aria-label="Scroll to filters">Explore Filters</button>
        <button class="btn" onclick="window.scrollTo({top: document.getElementById('table_anchor').offsetTop-80, behavior:'smooth'})" aria-label="View raw data table">View Raw Data</button>
      </div>
      <p style="margin:10px 0 0;font-size:11px;color:var(--muted)">CO addressed: <b>Handle unstructured/semi-structured data and visualize patterns of engagement and sentiment.</b></p>
    </div>
  </div>
</div>

  <div class="kpi-grid" role="region" aria-label="Key metrics">
    <div class="kpi">
      <h4>Total Posts (filtered)</h4>
      <div class="val" id="kpi_posts" aria-live="polite">—</div>
      <div class="sub" id="kpi_posts_sub">—</div>
      <div class="trend" id="kpi_trend">Live filter</div>
      <div class="icon" aria-hidden="true">📊</div>
    </div>
    <div class="kpi">
      <h4>Avg Engagement / Post</h4>
      <div class="val" id="kpi_eng" aria-live="polite">—</div>
      <div class="sub" id="kpi_eng_sub">Likes + Shares + Comments</div>
    </div>
    <div class="kpi">
      <h4>Avg Sentiment Score</h4>
      <div class="val" id="kpi_sent" aria-live="polite">—</div>
      <div class="sub" id="kpi_sent_sub">-1.0 → +1.0 scale</div>
    </div>
    <div class="kpi">
      <h4>Engagement Rate</h4>
      <div class="val" id="kpi_rate" aria-live="polite">—</div>
      <div class="sub" id="kpi_rate_sub">Engagement / Views</div>
    </div>
  </div>

  <!-- Sticky Filter Bar -->
  <div class="filter-bar" id="filterBar" role="region" aria-label="Filters">
    <div class="filter-bar-inner">
      <div class="filter-bar-head">
        <div class="filter-meta">
          <strong style="color:var(--ink);font-size:13px">Filters</strong>
          <span id="active_count" class="active-chip" aria-live="polite">All posts</span>
          <span id="filter_summary" class="visually-hidden" aria-live="polite"></span>
          <span style="font-size:11px" id="filter_hint">Sticky • URL-synced • Shareable</span>
        </div>
        <div class="filter-head-actions">
          <button class="btn" id="btn_share" type="button" aria-label="Copy shareable link to clipboard">🔗 Share</button>
          <button class="btn filter-trigger" id="btn_filter_open" type="button" aria-expanded="false" aria-controls="filters" aria-label="Open filter drawer">☰ Filters</button>
          <button class="btn" id="btn_reset_top" type="button" aria-label="Reset all filters">Reset</button>
        </div>
      </div>
      <div class="backdrop" id="backdrop" hidden></div>
      <div class="filters" id="filters" role="group" aria-label="Filter controls">
        <div>
          <label for="f_platform">Platform</label>
          <select id="f_platform" aria-label="Filter by platform"><option value="all">All Platforms</option><option>Twitter</option><option>Instagram</option><option>Facebook</option><option>LinkedIn</option><option>YouTube</option></select>
        </div>
        <div>
          <label for="f_sentiment">Sentiment</label>
          <select id="f_sentiment" aria-label="Filter by sentiment"><option value="all">All Sentiments</option><option value="positive">Positive</option><option value="neutral">Neutral</option><option value="negative">Negative</option></select>
        </div>
        <div>
          <label for="f_topic">Topic</label>
          <select id="f_topic" aria-label="Filter by topic"><option value="all">All Topics</option><option>Product Launch</option><option>Customer Service</option><option>Marketing Campaign</option><option>Tech Review</option><option>Lifestyle</option><option>Sports</option><option>Entertainment</option><option>News</option></select>
        </div>
        <div>
          <label for="f_user">User Type</label>
          <select id="f_user" aria-label="Filter by user type"><option value="all">All Users</option><option>Regular</option><option>Influencer</option><option>Brand</option><option>Verified</option></select>
        </div>
        <div>
          <label for="f_start">Start Date</label>
          <input type="date" id="f_start" value="2026-03-01" min="2026-03-01" max="2026-08-31" aria-label="Start date"/>
        </div>
        <div>
          <label for="f_end">End Date</label>
          <input type="date" id="f_end" value="2026-08-31" min="2026-03-01" max="2026-08-31" aria-label="End date"/>
        </div>
        <div>
          <label for="f_search">Search Text / Hashtag</label>
          <input type="text" id="f_search" placeholder="e.g. launch, #TechLaunch" aria-label="Search text or hashtag" autocomplete="off"/>
        </div>
        <div class="btn-row" style="display:flex;gap:8px;align-items:end">
          <button class="btn primary" id="btn_apply" type="button" style="flex:1" aria-label="Apply filters">Apply</button>
          <button class="btn" id="btn_reset" type="button" style="flex:1" aria-label="Reset filters">Reset</button>
        </div>
        <div class="btn-row" style="display:flex;gap:8px;align-items:center;grid-column:1/-1;justify-content:space-between;flex-wrap:wrap;margin-top:2px">
          <span style="font-size:11px;color:var(--muted)">Press <kbd style="border:1px solid var(--line);padding:1px 6px;border-radius:6px;background:var(--bg)">Enter</kbd> in search to apply • Filters sync to URL</span>
          <button class="btn" id="btn_filter_close" type="button" aria-label="Close filter drawer" style="display:none">✕ Close</button>
        </div>
      </div>
    </div>
  </div>

  <div class="grid" role="region" aria-label="Charts">
    <div class="card third">
      <div class="card-head"><h3>Sentiment Distribution</h3><span class="badge" id="b_sent">Donut</span></div>
      <p style="margin:-6px 0 8px;color:var(--muted);font-size:12px">Share of positive / neutral / negative posts in filtered view.</p>
      <div class="canvas-wrap"><div class="skeleton" id="sk_sentiment" aria-hidden="true"></div><canvas id="chart_sentiment" role="img" aria-label="Sentiment distribution donut chart"></canvas></div>
    </div>
    <div class="card third">
      <div class="card-head"><h3>Platform — Avg Engagement</h3><span class="badge">Grouped Bar</span></div>
      <p style="margin:-6px 0 8px;color:var(--muted);font-size:12px">Average likes / shares / comments per post by platform.</p>
      <div class="canvas-wrap"><div class="skeleton" id="sk_platform" aria-hidden="true"></div><canvas id="chart_platform" role="img" aria-label="Platform average engagement grouped bar chart"></canvas></div>
    </div>
    <div class="card third">
      <div class="card-head"><h3>Top 10 Hashtags</h3><span class="badge">Frequency</span></div>
      <p style="margin:-6px 0 8px;color:var(--muted);font-size:12px">Most used hashtags in filtered posts.</p>
      <div class="canvas-wrap"><div class="skeleton" id="sk_hashtags" aria-hidden="true"></div><canvas id="chart_hashtags" role="img" aria-label="Top 10 hashtags frequency chart"></canvas></div>
    </div>

    <div class="card full">
      <div class="card-head"><div><h3>Engagement Over Time — Daily Totals</h3><p style="color:var(--muted)">Likes / Shares / Comments stacked + overall engagement trend. Filter to see campaign peaks.</p></div><span class="badge" id="b_time">Daily • Mar–Aug 2026</span></div>
      <div class="canvas-wrap tall"><div class="skeleton" id="sk_timeline" aria-hidden="true"></div><canvas id="chart_timeline" role="img" aria-label="Engagement over time stacked chart"></canvas></div>
    </div>

    <div class="card half">
      <div class="card-head"><h3>Sentiment vs Engagement (Scatter)</h3><span class="badge">Correlation</span></div>
      <p style="margin:-6px 0 8px;color:var(--muted);font-size:12px">Each dot = post. X = sentiment score (-1 → +1), Y = engagement. Colors = sentiment label. Watch for negative viral outliers.</p>
      <div class="canvas-wrap"><div class="skeleton" id="sk_scatter" aria-hidden="true"></div><canvas id="chart_scatter" role="img" aria-label="Sentiment versus engagement scatter plot"></canvas></div>
    </div>
    <div class="card half">
      <div class="card-head"><h3>Topic × Sentiment — Pattern</h3><span class="badge">Stacked Bar</span></div>
      <p style="margin:-6px 0 8px;color:var(--muted);font-size:12px">How sentiment skew varies by topic (Customer Service skews negative, Campaign skews positive).</p>
      <div class="canvas-wrap"><div class="skeleton" id="sk_topic" aria-hidden="true"></div><canvas id="chart_topic" role="img" aria-label="Topic by sentiment stacked bar chart"></canvas></div>
    </div>

    <div class="card half">
      <div class="card-head"><h3>Engagement by Hour of Day</h3><span class="badge">Line</span></div>
      <p style="margin:-6px 0 8px;color:var(--muted);font-size:12px">When does engagement peak? Aggregated across filtered posts.</p>
      <div class="canvas-wrap"><div class="skeleton" id="sk_hourly" aria-hidden="true"></div><canvas id="chart_hourly" role="img" aria-label="Engagement by hour line chart"></canvas></div>
    </div>
    <div class="card half">
      <div class="card-head"><h3>User Type — Engagement &amp; Share</h3><span class="badge">Bar + Donut inset</span></div>
      <p style="margin:-6px 0 8px;color:var(--muted);font-size:12px">Do influencers/brands drive higher avg engagement vs regular users?</p>
      <div class="canvas-wrap"><div class="skeleton" id="sk_usertype" aria-hidden="true"></div><canvas id="chart_usertype" role="img" aria-label="User type engagement bar chart"></canvas></div>
    </div>
    <div class="card full" id="card_wordcloud">
      <div class="card-head"><div><h3>Hashtag Word Cloud</h3><p style="color:var(--muted)">Sized by frequency in filtered view — bigger = more used. Hover to see count. Lightweight div cloud (no heavy deps).</p></div><span class="badge" id="b_cloud">Cloud</span></div>
      <div class="cloud" id="hashtag_cloud" role="img" aria-label="Hashtag word cloud visualization" aria-live="polite"></div>
      <div style="margin-top:8px;display:flex;gap:8px;flex-wrap:wrap">
        <button class="btn" type="button" onclick="copyHashtagList()" aria-label="Copy hashtag frequencies as text">Copy list</button>
        <span class="table-meta" id="cloud_meta">—</span>
      </div>
    </div>
  </div>

  <div class="insights" id="insights" role="region" aria-label="Auto insights">
    <div class="insight"><h4>🔍 Auto-Insight — Sentiment</h4><p id="ins_sent" aria-live="polite">—</p></div>
    <div class="insight"><h4>📈 Auto-Insight — Engagement</h4><p id="ins_eng" aria-live="polite">—</p></div>
    <div class="insight"><h4>🏷️ Auto-Insight — Platform/Topic</h4><p id="ins_plat" aria-live="polite">—</p></div>
  </div>

  <div class="pipe" role="region" aria-label="Data pipeline">
    <h3 style="font-size:16px">Unstructured → Structured Pipeline (What the report evaluates)</h3>
    <p style="margin:0;color:var(--muted);font-size:13px;line-height:1.6">Raw social posts are <b>unstructured</b> (free text, emojis, mentions, URLs) plus <b>semi-structured</b> metadata (timestamps, platform, likes/shares/comments, hashtags as JSON arrays). The app demonstrates the handling steps required before visualization. Try the playground below.</p>
    <div class="pipeline">
      <div class="step"><b>1 · Ingest</b><p>Semi-structured JSON with mixed types.</p><code>{"post_id":"P0001","text":"Love the new launch! #TechLaunch @brand","likes":1338,...}</code></div>
      <div class="step"><b>2 · Clean</b><p>Lowercase, strip URLs/mentions, remove punctuation, handle hashtags.</p><code>raw → lower → remove URLs → remove @mentions → keep #tags → strip punctuation</code></div>
      <div class="step"><b>3 · Tokenize</b><p>Split into tokens, remove stopwords, keep sentiment-bearing words.</p><code>["love","new","launch","techlaunch"] ← tokens</code></div>
      <div class="step"><b>4 · Score</b><p>Lexicon / rule-based scoring to sentiment_score ∈ [-1, +1] + label.</p><code>score = (pos - neg) / tokens → 0.72 → positive</code></div>
      <div class="step"><b>5 · Visualize</b><p>Aggregate, filter, and map to charts (this dashboard).</p><code>groupBy(platform, sentiment) → Chart.js</code></div>
    </div>
    <div class="playground">
      <div>
        <label for="play_input" style="font-size:11px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)">Try it — type any post text</label>
        <textarea id="play_input" aria-label="Playground input text">Absolutely love the new TechLaunch! The quality is outstanding and delivery was super fast. Highly recommend! #TechLaunch #Innovation</textarea>
        <div style="display:flex;gap:8px;margin-top:8px;flex-wrap:wrap">
          <button class="btn primary" id="play_run" type="button" aria-label="Analyze playground text">Analyze Text</button>
          <button class="btn" id="play_sample" type="button" aria-label="Load negative sample text">Load Negative Sample</button>
        </div>
      </div>
      <div class="result" id="play_output" role="region" aria-live="polite" aria-label="Analysis output">—</div>
    </div>
  </div>

  <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px" class="dual">
    <style>@media(max-width:900px){.dual{grid-template-columns:1fr !important}}</style>
    <div class="side-card">
      <h3>Semi-Structured Example — Raw Record</h3>
      <p style="margin:0 0 8px;color:var(--muted);font-size:12px">Each post mixes unstructured text + structured metrics + array hashtags. This is the exact JSON the app parses.</p>
      <pre class="json-view" id="json_view" tabindex="0" aria-label="Sample JSON record">—</pre>
    </div>
    <div class="side-card">
      <h3>Dataset Schema & Coverage</h3>
      <div style="font-size:13px;line-height:1.6;color:var(--ink)">
        <b>Schema (20 fields):</b> post_id, platform, timestamp, date, hour, text (unstructured), likes, shares, comments, views, engagement, engagement_rate, sentiment_label, sentiment_score, hashtags[ ], hashtags_str, topic, user_type, verified, language<br/>
        <b style="display:inline-block;margin-top:8px">Coverage:</b> 420 posts · 5 platforms · 8 topics · 4 user types · 20 hashtags<br/>
        <b>Date range:</b> 2026-03-01 → 2026-08-31 (daily, with weekend & campaign peaks)<br/>
        <b>Engagement realism:</b> per-platform bases + influencer/viral multipliers + event spikes (Apr 15, May 20, Jun 10, Jul 18)<br/>
        <b>Files:</b> <code>data/social_media_dataset.json</code> + <code>.csv</code> (embedded in this HTML for offline use)
      </div>
      <div style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap">
        <button class="btn" onclick="downloadFiltered('csv')" type="button" aria-label="Export filtered data as CSV">Export Filtered CSV</button>
        <button class="btn" onclick="downloadFiltered('json')" type="button" aria-label="Export filtered data as JSON">Export Filtered JSON</button>
        <button class="btn" onclick="window.print()" type="button" aria-label="Print or save as PDF">Print / Save PDF</button>
      </div>
    </div>
  </div>

  <div class="table-wrap" id="table_anchor" role="region" aria-label="Filtered posts table">
    <div class="table-head">
      <div>
        <h3>Raw Data — Filtered Posts</h3>
        <div class="table-meta" id="table_meta" aria-live="polite">—</div>
      </div>
      <div class="table-actions">
        <label for="table_search" class="visually-hidden">Quick find in table</label>
        <input id="table_search" placeholder="Quick find..." aria-label="Quick find in current table view" autocomplete="off"/>
        <button class="btn" onclick="downloadFiltered('csv')" type="button" aria-label="Export visible table as CSV">Export CSV</button>
      </div>
    </div>
    <div style="overflow:auto;max-height:520px" tabindex="0" aria-label="Scrollable table container">
      <table role="table" aria-label="Posts">
        <thead>
          <tr>
            <th scope="col" data-k="post_id" tabindex="0" role="columnheader" aria-sort="none" aria-label="Sort by Post ID">Post</th>
            <th scope="col" data-k="platform" tabindex="0" role="columnheader" aria-sort="none" aria-label="Sort by Platform">Platform</th>
            <th scope="col" data-k="timestamp" tabindex="0" role="columnheader" aria-sort="descending" aria-label="Sort by Date">Date</th>
            <th scope="col" data-k="topic" tabindex="0" role="columnheader" aria-sort="none" aria-label="Sort by Topic">Topic</th>
            <th scope="col">Text (unstructured)</th>
            <th scope="col" data-k="sentiment_label" tabindex="0" role="columnheader" aria-sort="none" aria-label="Sort by Sentiment">Sentiment</th>
            <th scope="col" data-k="sentiment_score" tabindex="0" role="columnheader" aria-sort="none" aria-label="Sort by Sentiment Score">Score</th>
            <th scope="col" data-k="engagement" tabindex="0" role="columnheader" aria-sort="none" aria-label="Sort by Engagement">Engagement</th>
            <th scope="col" data-k="likes" tabindex="0" role="columnheader" aria-sort="none" aria-label="Sort by Likes">Likes</th>
            <th scope="col" data-k="comments" tabindex="0" role="columnheader" aria-sort="none" aria-label="Sort by Comments">Comments</th>
          </tr>
        </thead>
        <tbody id="tbody"></tbody>
      </table>
    </div>
    <div id="empty_state" class="empty-state" hidden>
      <div class="illus" aria-hidden="true">🔍</div>
      <h4>No posts match your filters</h4>
      <p>Try widening the date range, clearing the search, or resetting all filters. Your current filters returned <b id="empty_count">0</b> results. Need a quick reset?</p>
      <div style="display:flex;gap:8px;flex-wrap:wrap;justify-content:center">
        <button class="btn primary" onclick="resetFilters()" type="button" aria-label="Reset filters to show all posts">Reset filters — show all 420</button>
        <button class="btn" onclick="document.getElementById('filterBar').scrollIntoView({behavior:'smooth'})" type="button">Adjust filters</button>
      </div>
      <p style="font-size:11px;color:var(--muted)">Tip: search supports partial hashtag & text match • e.g. <code>#TechLaunch</code> or <code>launch</code></p>
    </div>
    <div class="pagination" role="navigation" aria-label="Table pagination">
      <div class="table-meta" id="page_info" aria-live="polite">—</div>
      <div style="display:flex;gap:8px">
        <button id="prev_btn" type="button" aria-label="Previous page">‹ Prev</button>
        <button id="next_btn" type="button" aria-label="Next page">Next ›</button>
      </div>
    </div>
  </div>

  <div class="side-card" style="margin-bottom:18px">
    <h3>Interpretation Guide — What patterns to look for</h3>
    <ul style="margin:8px 0 0 18px;color:var(--ink);font-size:13px;line-height:1.7">
      <li><b>Sentiment distribution:</b> Overall ~40% positive / 30% neutral / 30% negative. Filter by <i>Customer Service</i> to see negative skew; filter by <i>Marketing Campaign</i> to see positive lift.</li>
      <li><b>Platform behavior:</b> Instagram & YouTube average higher engagement per post; LinkedIn lower volume but neutral Skews; Twitter more polarized.</li>
      <li><b>Engagement over time:</b> Peaks around <b>Apr 15, May 20, Jun 10, Jul 18</b> (campaign pushes). Weekends uplift on Instagram/YouTube.</li>
      <li><b>Scatter:</b> Negative posts with high engagement = <i>viral complaints</i> — important for brand monitoring. Positive influencer posts also high-engagement but higher score.</li>
      <li><b>Hashtags:</b> Frequency tracks campaign topics; filter by sentiment to see which tags correlate with positive vs negative perception. Check the <b>9th chart (Word Cloud)</b> for sized view.</li>
    </ul>
  </div>

  <div class="footer">
    <div>Built as a <b>static, self-contained HTML file</b> — no backend, no build step, CDN Chart.js only. Data embedded + also shipped as <code>data/social_media_dataset.json/.csv</code>. Academic use — Assignment 6 (DSA0606) • Handle unstructured/semi-structured data and visualize patterns of engagement and sentiment.</div>
    <div style="margin-top:6px">© 2026 SocialPulse • Fonts: Inter • Charts: Chart.js 4 • Data: Synthetic, 420 posts, seed=42 • <span id="build_info">v2 • dark mode • URL persistence • 9 charts incl. word cloud</span></div>
  </div>
</main>
<div id="toast" class="toast" role="status" aria-live="polite" aria-atomic="true"></div>

<script>
// ----- DATA -----
const RAW_DATA = __EMBEDDED_DATA__;

// ----- THEME -----
const THEME_KEY = 'sp-theme';
function getPreferredTheme(){
  const saved = localStorage.getItem(THEME_KEY);
  if(saved==='light' || saved==='dark') return saved;
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}
function setTheme(theme){
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem(THEME_KEY, theme);
  const icon = document.getElementById('theme_icon');
  if(icon) icon.textContent = theme==='dark' ? '☀️' : '🌙';
  const btn = document.getElementById('theme_toggle');
  if(btn) btn.setAttribute('aria-label', theme==='dark' ? 'Switch to light mode' : 'Switch to dark mode');
  // update chart colors if charts exist
  if(typeof charts!=='undefined' && Object.keys(charts||{}).length){
    // re-render with new colors after small delay to let CSS vars settle
    requestAnimationFrame(()=>{ try{ renderCharts(); renderWordCloud(); }catch(e){} });
  }
}
function toggleTheme(){
  const cur = document.documentElement.getAttribute('data-theme') || getPreferredTheme();
  setTheme(cur==='dark' ? 'light' : 'dark');
  showToast(`Theme: ${cur==='dark' ? 'light' : 'dark'} mode`);
}

// ----- HELPERS -----
const $ = s => document.querySelector(s);
const fmt = n => n.toLocaleString('en-IN');
const avg = arr => arr.length ? arr.reduce((a,b)=>a+b,0)/arr.length : 0;
const sum = arr => arr.reduce((a,b)=>a+b,0);
const sentimentColor = {positive:'#10b981', neutral:'#f59e0b', negative:'#ef4444'};
const platformColor = {Twitter:'#1d9bf0', Instagram:'#e4405f', Facebook:'#1877f2', LinkedIn:'#0a66c2', YouTube:'#ff0000'};

let filtered = [...RAW_DATA];
let page = 1, pageSize = 20, sortKey = 'timestamp', sortDir = 'desc';
let charts = {};
let isRestoring = false;

// ----- TOAST -----
let toastTimer=null;
function showToast(msg, ms=2200){
  const el = document.getElementById('toast');
  if(!el) return;
  el.textContent = msg;
  el.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(()=> el.classList.remove('show'), ms);
}

// ----- TEXT PIPELINE DEMO -----
const STOPWORDS = new Set(["the","is","a","an","and","or","but","with","to","of","in","on","for","this","that","was","were","are","be","been","it","its","at","by","as","from","so","very","just","still","here","my","your","our"]);
const LEX = {
  positive: new Set(["love","amazing","outstanding","fast","recommend","awesome","great","fantastic","blown","creative","inspiring","excellent","best","favorite","worth","shoutout","nailed","innovation","smooth","clean","fast","5","stars","above","beyond"]),
  negative: new Set(["disappointed","damaged","worst","poor","broken","crashing","misleading","different","cancelled","delays","chaotic","avoid","issues","refund","overpriced","underwhelming","waste","long","no","not","never","terrible","bad","hate","slow"])
};
function analyzeText(raw){
  const lower = raw.toLowerCase();
  const noUrls = lower.replace(/https?:\/\/\S+/g, "");
  const noMentions = noUrls.replace(/@\w+/g, "");
  const cleaned = noMentions.replace(/[^a-z0-9#\s]/g, " ").replace(/\s+/g," ").trim();
  const tokens = cleaned.split(/\s+/).filter(Boolean);
  const noStop = tokens.filter(t=> !STOPWORDS.has(t.replace(/^#/,"")));
  let pos=0, neg=0;
  for(const t of noStop){
    const w = t.replace(/^#/,"");
    if(LEX.positive.has(w)) pos++;
    if(LEX.negative.has(w)) neg++;
  }
  const score = noStop.length ? (pos - neg) / Math.max(4, noStop.length) : 0;
  let s = Math.max(-1, Math.min(1, score * 2.2));
  if(raw.includes("!") && s>0) s = Math.min(1, s+0.08);
  if(raw.includes("!") && s<0) s = Math.max(-1, s-0.05);
  let label = s>0.25 ? "positive" : s<-0.25 ? "negative" : "neutral";
  return {lower, cleaned, tokens, noStop, pos, neg, score: Math.round(s*1000)/1000, label};
}
function renderPlay(){
  const raw = $("#play_input").value;
  const r = analyzeText(raw);
  const out = [
    `Input: ${raw}`,
    ``,
    `Cleaned: "${r.cleaned}"`,
    `Tokens (${r.tokens.length}): [ ${r.tokens.slice(0,18).join(", ")}${r.tokens.length>18?" …":""} ]`,
    `Without stopwords (${r.noStop.length}): [ ${r.noStop.join(", ")} ]`,
    `Lexicon hits → pos=${r.pos}, neg=${r.neg}`,
    `Score: ${r.score} → label: ${r.label}`,
    ``,
    `Visualization mapping: score is plotted on X-axis of scatter; label colors the dot.`
  ].join("\n");
  $("#play_output").textContent = out;
}

// ----- FILTERING -----
function getFilters(){
  return {
    platform: $("#f_platform").value,
    sentiment: $("#f_sentiment").value,
    topic: $("#f_topic").value,
    user: $("#f_user").value,
    start: $("#f_start").value,
    end: $("#f_end").value,
    search: $("#f_search").value.trim().toLowerCase()
  };
}
function countActiveFilters(){
  const f=getFilters();
  let c=0;
  if(f.platform!=='all') c++;
  if(f.sentiment!=='all') c++;
  if(f.topic!=='all') c++;
  if(f.user!=='all') c++;
  if(f.start!=='2026-03-01') c++;
  if(f.end!=='2026-08-31') c++;
  if(f.search) c++;
  return c;
}
function applyFilters(opts={}){
  const keepPage = opts.keepPage===true;
  const f = getFilters();
  filtered = RAW_DATA.filter(r=>{
    if(f.platform!=="all" && r.platform!==f.platform) return false;
    if(f.sentiment!=="all" && r.sentiment_label!==f.sentiment) return false;
    if(f.topic!=="all" && r.topic!==f.topic) return false;
    if(f.user!=="all" && r.user_type!==f.user) return false;
    if(f.start && r.date < f.start) return false;
    if(f.end && r.date > f.end) return false;
    if(f.search){
      const hay = (r.text + " " + r.hashtags_str + " " + r.topic + " " + r.platform).toLowerCase();
      if(!hay.includes(f.search)) return false;
    }
    return true;
  });
  filtered.sort((a,b)=>{
    let va=a[sortKey], vb=b[sortKey];
    if(sortKey==="sentiment_score" || sortKey==="engagement" || sortKey==="likes" || sortKey==="comments" || sortKey==="views"){
      va = Number(va); vb=Number(vb);
    }
    if(va<vb) return sortDir==="asc"? -1:1;
    if(va>vb) return sortDir==="asc"? 1:-1;
    return 0;
  });
  if(!keepPage) page=1;
  // clamp page after filtering
  const tp = Math.max(1, Math.ceil(filtered.length / pageSize));
  if(page>tp) page=tp;
  if(page<1) page=1;
  updateAll();
  if(!isRestoring) syncURL();
}
function resetFilters(){
  $("#f_platform").value="all"; $("#f_sentiment").value="all"; $("#f_topic").value="all"; $("#f_user").value="all";
  $("#f_start").value="2026-03-01"; $("#f_end").value="2026-08-31"; $("#f_search").value=""; $("#table_search").value="";
  sortKey="timestamp"; sortDir="desc"; page=1;
  // update aria-sort headers
  document.querySelectorAll('th[data-k]').forEach(th=> th.setAttribute('aria-sort','none'));
  const tsTh=document.querySelector('th[data-k="timestamp"]'); if(tsTh) tsTh.setAttribute('aria-sort','descending');
  applyFilters();
  showToast('Filters reset — showing all 420 posts');
}

// ----- URL STATE PERSISTENCE -----
function syncURL(){
  const params = new URLSearchParams();
  const f=getFilters();
  // Always set for shareability, but could omit defaults to keep cleaner. We'll set all 10 explicitly for predictable sharing.
  params.set('platform', f.platform);
  params.set('sentiment', f.sentiment);
  params.set('topic', f.topic);
  params.set('user', f.user);
  params.set('start', f.start);
  params.set('end', f.end);
  params.set('search', f.search);
  params.set('sort', sortKey);
  params.set('order', sortDir);
  params.set('page', String(page));
  const q = $("#table_search").value.trim();
  if(q) params.set('q', q);
  const url = `${location.pathname}?${params.toString()}`;
  history.replaceState(null,'',url);
  // also update active chip
  const active = countActiveFilters();
  const chip = document.getElementById('active_count');
  if(chip){
    if(filtered.length===420 && active===0) chip.textContent='All posts';
    else chip.textContent=`${filtered.length} posts • ${active} filter${active!==1?'s':''}`;
  }
}
function readURL(){
  const params = new URLSearchParams(location.search);
  if(!params.toString()) return false;
  isRestoring = true;
  const setIf = (id, key, fallback) => {
    const v = params.get(key);
    if(v!==null && v!==''){
      const el=document.getElementById(id);
      if(el) el.value=v;
    } else if(fallback!==undefined){
      // keep default
    }
  };
  setIf('f_platform','platform');
  setIf('f_sentiment','sentiment');
  setIf('f_topic','topic');
  setIf('f_user','user');
  setIf('f_start','start');
  setIf('f_end','end');
  setIf('f_search','search');
  if(params.get('sort')) sortKey=params.get('sort');
  if(params.get('order')) sortDir=params.get('order');
  if(params.get('page')) page=Math.max(1, parseInt(params.get('page'),10)||1);
  if(params.get('q')){ const el=document.getElementById('table_search'); if(el) el.value=params.get('q'); }
  // validate dates
  const startEl=$('#f_start'), endEl=$('#f_end');
  if(startEl && !startEl.value) startEl.value='2026-03-01';
  if(endEl && !endEl.value) endEl.value='2026-08-31';
  // update aria-sort
  document.querySelectorAll('th[data-k]').forEach(th=>{
    th.setAttribute('aria-sort', th.dataset.k===sortKey ? (sortDir==='asc'?'ascending':'descending') : 'none');
  });
  isRestoring=false;
  return true;
}
function copyShareLink(){
  const url = location.href;
  if(navigator.clipboard && navigator.clipboard.writeText){
    navigator.clipboard.writeText(url).then(()=> showToast('Link copied — share this view')).catch(()=> fallbackCopy(url));
  } else fallbackCopy(url);
}
function fallbackCopy(text){
  const ta=document.createElement('textarea'); ta.value=text; ta.style.position='fixed'; ta.style.opacity='0';
  document.body.appendChild(ta); ta.select(); try{document.execCommand('copy'); showToast('Link copied — share this view');}catch(e){ prompt('Copy link:', text); } ta.remove();
}
function shareCurrentView(){
  syncURL();
  copyShareLink();
}

// ----- SKELETON -----
function showSkeletons(){
  document.querySelectorAll('.skeleton').forEach(el=> el.classList.add('show'));
  document.querySelectorAll('.canvas-wrap').forEach(el=> el.style.opacity='.42');
}
function hideSkeletons(){
  document.querySelectorAll('.skeleton').forEach(el=> el.classList.remove('show'));
  document.querySelectorAll('.canvas-wrap').forEach(el=> el.style.opacity='1');
}

// ----- KPI + INSIGHTS -----
function updateKPIs(){
  const n = filtered.length;
  const totalEng = sum(filtered.map(r=>r.engagement));
  const avgEng = n? Math.round(totalEng/n):0;
  const avgSent = n? (sum(filtered.map(r=>r.sentiment_score))/n):0;
  const avgRate = n? avg(filtered.map(r=>r.engagement_rate)):0;
  const posPct = n? (filtered.filter(r=>r.sentiment_label==="positive").length/n*100):0;
  $("#kpi_posts").textContent = fmt(n) + " / 420";
  $("#kpi_posts_sub").textContent = n===420 ? "Showing all posts" : `${Math.round(n/420*100)}% of dataset • ${fmt(420-n)} hidden by filter`;
  $("#kpi_eng").textContent = fmt(avgEng);
  $("#kpi_eng_sub").textContent = `Total engagement in view: ${fmt(totalEng)}`;
  $("#kpi_sent").textContent = (avgSent>=0?"+":"")+avgSent.toFixed(3);
  $("#kpi_sent_sub").textContent = `${posPct.toFixed(1)}% positive • ${avgSent>0.15?"Overall positive lean":avgSent<-0.15?"Overall negative lean":"Balanced"}`;
  $("#kpi_rate").textContent = avgRate.toFixed(2)+"%";
  $("#kpi_rate_sub").textContent = `Avg (engagement/views)`;
  const platCounts = {};
  filtered.forEach(r=> platCounts[r.platform]=(platCounts[r.platform]||0)+1);
  const topPlat = Object.entries(platCounts).sort((a,b)=>b[1]-a[1])[0];
  const topPlatStr = topPlat? `${topPlat[0]} (${topPlat[1]} posts, ${Math.round(topPlat[1]/Math.max(1,n)*100)}%)` : "—";
  const topicCounts = {};
  filtered.forEach(r=> topicCounts[r.topic]=(topicCounts[r.topic]||0)+1);
  const topTopic = Object.entries(topicCounts).sort((a,b)=>b[1]-a[1])[0];
  const neg = filtered.filter(r=>r.sentiment_label==="negative").length;
  const neu = filtered.filter(r=>r.sentiment_label==="neutral").length;
  const pos = filtered.filter(r=>r.sentiment_label==="positive").length;
  $("#ins_sent").textContent = n? `In this view: ${pos} positive (${Math.round(pos/n*100)}%), ${neu} neutral (${Math.round(neu/n*100)}%), ${neg} negative (${Math.round(neg/n*100)}%). ${avgSent>0.2?"Sentiment is notably positive — suggests campaign resonance.":avgSent<-0.15?"Negative tilt — check Customer Service & complaint posts.":"Mixed sentiment — opportunity to drill by topic/platform."}` : "No data in filter.";
  const maxEng = filtered.length? Math.max(...filtered.map(r=>r.engagement)) : 0;
  const maxPost = filtered.find(r=>r.engagement===maxEng);
  $("#ins_eng").textContent = n? `Average engagement ${fmt(avgEng)} per post (total ${fmt(totalEng)}). ${maxPost? `Top post: ${maxPost.post_id} on ${maxPost.platform} (${fmt(maxPost.engagement)} eng, ${maxPost.sentiment_label}). `:``}${avgRate>8?"High engagement rate suggests strong audience interaction; platform/ hour filters can reveal why.":"Moderate engagement rate — compare hourly & user-type charts to find drivers."}` : "No data.";
  $("#ins_plat").textContent = n? `Dominant platform: ${topPlatStr}. ${topTopic?`Top topic: ${topTopic[0]} (${topTopic[1]} posts). `:""}Switch Platform filter to compare Instagram vs Twitter vs LinkedIn baselines, and Topic filter to see Campaign vs Service patterns.` : "No data.";
  // filter summary for screen readers
  const summary = document.getElementById('filter_summary');
  if(summary) summary.textContent = `${n} posts match current filters. ${pos} positive, ${neu} neutral, ${neg} negative.`;
}

// ----- WORD CLOUD -----
function computeHashtagFreq(){
  const counter={};
  filtered.forEach(r=> r.hashtags.forEach(h=> counter[h]=(counter[h]||0)+1));
  return Object.entries(counter).sort((a,b)=> b[1]-a[1]);
}
function renderWordCloud(){
  const cloud = document.getElementById('hashtag_cloud');
  const meta = document.getElementById('cloud_meta');
  const badge = document.getElementById('b_cloud');
  if(!cloud) return;
  const top = computeHashtagFreq();
  if(top.length===0){
    cloud.innerHTML = '<div class="empty-state" style="padding:20px"><p>No hashtags in this filtered view</p></div>';
    if(meta) meta.textContent='—';
    if(badge) badge.textContent='Empty';
    return;
  }
  const max = top[0][1], min = top[top.length-1][1];
  const range = Math.max(1, max-min);
  // color palette based on theme
  const colors = ['var(--brand)','var(--brand-2)','#0ea5e9','#7c3aed','#059669','#d97706','#e11d48'];
  cloud.innerHTML = top.slice(0,30).map(([tag,count], i)=>{
    const norm = (count - min)/range;
    const size = 12 + norm*22; // 12 to 34px
    const weight = 600 + Math.round(norm*300);
    const opacity = 0.78 + norm*0.22;
    const color = colors[i % colors.length];
    const bgAlpha = 0.08 + norm*0.12;
    return `<span tabindex="0" role="button" aria-label="${tag} appears ${count} times, click to search" title="${tag}: ${count} posts" style="font-size:${size.toFixed(1)}px;font-weight:${weight};color:${color};opacity:${opacity};background:color-mix(in srgb, ${color} ${Math.round(bgAlpha*100)}%, var(--bg));border-color:color-mix(in srgb, ${color} 22%, var(--line))" data-tag="${tag}">${tag} <small style="font-size:.62em;opacity:.75">×${count}</small></span>`;
  }).join('');
  // click to filter search
  cloud.querySelectorAll('span[data-tag]').forEach(s=>{
    s.addEventListener('click', ()=>{
      const tag=s.dataset.tag;
      document.getElementById('f_search').value=tag;
      applyFilters();
      showToast(`Filtered by ${tag}`);
      document.getElementById('filterBar').scrollIntoView({behavior:'smooth'});
    });
    s.addEventListener('keydown', (e)=>{
      if(e.key==='Enter' || e.key===' '){ e.preventDefault(); s.click(); }
    });
  });
  if(meta) meta.textContent = `${top.length} unique hashtags • top: ${top[0][0]} (${top[0][1]}) • sized by frequency`;
  if(badge) badge.textContent = `${top.length} tags • ${filtered.length} posts`;
}
function copyHashtagList(){
  const list = computeHashtagFreq().map(([k,v])=> `${k}: ${v}`).join('\n');
  if(!list){ showToast('No hashtags to copy'); return; }
  if(navigator.clipboard) navigator.clipboard.writeText(list).then(()=> showToast('Hashtag frequencies copied'));
  else { prompt('Hashtag list', list); }
}
window.copyHashtagList = copyHashtagList;

// ----- CHARTS -----
function destroyCharts(){ Object.values(charts).forEach(c=>{try{c.destroy()}catch(e){}}); charts={}; }
function getChartGridColor(){
  const style=getComputedStyle(document.documentElement);
  const line=style.getPropertyValue('--line').trim() || '#e2e8f0';
  const muted=style.getPropertyValue('--muted').trim() || '#64748b';
  const ink=style.getPropertyValue('--ink').trim() || '#0f172a';
  return {line, muted, ink};
}
function renderCharts(){
  showSkeletons();
  // allow skeleton paint before heavy chart work
  requestAnimationFrame(()=> {
    requestAnimationFrame(()=> {
      destroyCharts();
      const ctx = id => document.getElementById(id);
      const {line, muted, ink} = getChartGridColor();
      const isDark = document.documentElement.getAttribute('data-theme')==='dark';
      Chart.defaults.color = muted;
      Chart.defaults.borderColor = line;
      // 1. Sentiment donut
      {
        const counts = {positive:0, neutral:0, negative:0};
        filtered.forEach(r=> counts[r.sentiment_label]++);
        charts.sentiment = new Chart(ctx('chart_sentiment'), {
          type:'doughnut',
          data:{labels:['Positive','Neutral','Negative'], datasets:[{data:[counts.positive, counts.neutral, counts.negative], backgroundColor:[sentimentColor.positive, sentimentColor.neutral, sentimentColor.negative], borderWidth:0, hoverOffset:6}]},
          options:{responsive:true, maintainAspectRatio:false, cutout:'62%', plugins:{legend:{position:'bottom', labels:{usePointStyle:true, boxWidth:8, font:{weight:700}, color:muted}}, tooltip:{callbacks:{label:c=> ` ${c.label}: ${c.raw} (${filtered.length?Math.round(c.raw/filtered.length*100):0}%)`}}}}
        });
        $("#b_sent").textContent = filtered.length? `${Math.round(counts.positive/Math.max(1,filtered.length)*100)}% pos • ${counts.negative} neg` : "—";
      }
      // 2. Platform avg engagement grouped
      {
        const platforms = ["Twitter","Instagram","Facebook","LinkedIn","YouTube"];
        const avgs = platforms.map(p=>{
          const rows = filtered.filter(r=>r.platform===p);
          return {
            p,
            likes: rows.length? Math.round(avg(rows.map(r=>r.likes))):0,
            shares: rows.length? Math.round(avg(rows.map(r=>r.shares))):0,
            comments: rows.length? Math.round(avg(rows.map(r=>r.comments))):0,
            n: rows.length
          };
        });
        charts.platform = new Chart(ctx('chart_platform'), {
          type:'bar',
          data:{
            labels: platforms.map(p=> p + ` (${avgs.find(a=>a.p===p).n})`),
            datasets:[
              {label:'Avg Likes', data: avgs.map(a=>a.likes), backgroundColor:'#2563eb', borderRadius:4},
              {label:'Avg Shares', data: avgs.map(a=>a.shares), backgroundColor:'#0ea5e9', borderRadius:4},
              {label:'Avg Comments', data: avgs.map(a=>a.comments), backgroundColor:'#7c3aed', borderRadius:4}
            ]
          },
          options:{
            responsive:true, maintainAspectRatio:false,
            plugins:{legend:{position:'bottom', labels:{usePointStyle:true, boxWidth:10, color:muted}}},
            scales:{
              x:{grid:{display:false, color:line}, ticks:{font:{size:10}, color:muted}},
              y:{beginAtZero:true, grid:{color:isDark?'rgba(255,255,255,.06)':'#f1f5f9'}, ticks:{callback:v=>v.toLocaleString(), color:muted}}
            }
          }
        });
      }
      // 3. Hashtags top 10
      {
        const counter = {};
        filtered.forEach(r=> r.hashtags.forEach(h=> counter[h]=(counter[h]||0)+1));
        const top = Object.entries(counter).sort((a,b)=>b[1]-a[1]).slice(0,10);
        charts.hashtags = new Chart(ctx('chart_hashtags'), {
          type:'bar',
          data:{
            labels: top.map(t=>t[0]),
            datasets:[{label:'Count', data: top.map(t=>t[1]), backgroundColor: top.map((_,i)=> `rgba(37,99,235,${0.95 - i*0.06})`), borderRadius:6}]
          },
          options:{
            indexAxis:'y',
            responsive:true, maintainAspectRatio:false,
            plugins:{legend:{display:false}},
            scales:{
              x:{beginAtZero:true, grid:{color:isDark?'rgba(255,255,255,.06)':'#f1f5f9'}, ticks:{color:muted}},
              y:{grid:{display:false}, ticks:{font:{weight:700, size:11}, color:ink}}
            }
          }
        });
      }
      // 4. Timeline daily
      {
        const byDate = {};
        filtered.forEach(r=>{
          if(!byDate[r.date]) byDate[r.date]={likes:0, shares:0, comments:0, engagement:0, count:0};
          byDate[r.date].likes += r.likes;
          byDate[r.date].shares += r.shares;
          byDate[r.date].comments += r.comments;
          byDate[r.date].engagement += r.engagement;
          byDate[r.date].count++;
        });
        const dates = Object.keys(byDate).sort();
        charts.timeline = new Chart(ctx('chart_timeline'), {
          type:'bar',
          data:{
            labels: dates,
            datasets:[
              {type:'bar', label:'Likes', data: dates.map(d=>byDate[d].likes), backgroundColor:'rgba(37,99,235,.85)', stack:'eng', borderRadius:2},
              {type:'bar', label:'Shares', data: dates.map(d=>byDate[d].shares), backgroundColor:'rgba(14,165,233,.85)', stack:'eng', borderRadius:2},
              {type:'bar', label:'Comments', data: dates.map(d=>byDate[d].comments), backgroundColor:'rgba(124,58,237,.85)', stack:'eng', borderRadius:2},
              {type:'line', label:'Total Engagement (line)', data: dates.map(d=>byDate[d].engagement), borderColor: isDark ? '#e2e8f0' : '#0f172a', backgroundColor: isDark ? '#e2e8f0' : '#0f172a', borderWidth:2, pointRadius:0, tension:.25, yAxisID:'y'}
            ]
          },
          options:{
            responsive:true, maintainAspectRatio:false, interaction:{mode:'index', intersect:false},
            plugins:{legend:{position:'bottom', labels:{usePointStyle:true, boxWidth:10, color:muted}}},
            scales:{
              x:{stacked:true, grid:{display:false}, ticks:{maxRotation:0, autoSkip:true, maxTicksLimit:14, font:{size:10}, color:muted}},
              y:{stacked:true, beginAtZero:true, grid:{color:isDark?'rgba(255,255,255,.06)':'#f1f5f9'}, ticks:{callback:v=>Number(v).toLocaleString(), color:muted}}
            }
          }
        });
      }
      // 5. Scatter sentiment vs engagement
      {
        const datasets = ["positive","neutral","negative"].map(label=> {
          const rows = filtered.filter(r=>r.sentiment_label===label);
          return {
            label: label.charAt(0).toUpperCase()+label.slice(1),
            data: rows.map(r=> ({x:r.sentiment_score, y:r.engagement})),
            backgroundColor: sentimentColor[label],
            pointRadius: 3.5,
            pointHoverRadius: 6
          };
        });
        charts.scatter = new Chart(ctx('chart_scatter'), {
          type:'scatter',
          data:{datasets},
          options:{
            responsive:true, maintainAspectRatio:false,
            plugins:{legend:{position:'bottom', labels:{usePointStyle:true, boxWidth:10, color:muted}}, tooltip:{callbacks:{label:c=> ` ${c.dataset.label}: score ${c.parsed.x}, eng ${c.parsed.y.toLocaleString()} `}}},
            scales:{
              x:{min:-1,max:1, grid:{color:isDark?'rgba(255,255,255,.06)':'#f1f5f9'}, title:{display:true, text:'Sentiment Score (-1 → +1)', color:muted}, ticks:{color:muted}},
              y:{beginAtZero:true, grid:{color:isDark?'rgba(255,255,255,.06)':'#f1f5f9'}, title:{display:true, text:'Engagement', color:muted}, ticks:{callback:v=>Number(v).toLocaleString(), color:muted}}
            }
          }
        });
      }
      // 6. Topic x sentiment stacked
      {
        const topics = ["Product Launch","Customer Service","Marketing Campaign","Tech Review","Lifestyle","Sports","Entertainment","News"];
        const counts = topics.map(t=>{
          const rows = filtered.filter(r=>r.topic===t);
          return {
            t,
            pos: rows.filter(r=>r.sentiment_label==="positive").length,
            neu: rows.filter(r=>r.sentiment_label==="neutral").length,
            neg: rows.filter(r=>r.sentiment_label==="negative").length,
            total: rows.length
          };
        });
        charts.topic = new Chart(ctx('chart_topic'), {
          type:'bar',
          data:{
            labels: topics,
            datasets:[
              {label:'Positive', data: counts.map(c=>c.pos), backgroundColor: sentimentColor.positive, stack:'s'},
              {label:'Neutral', data: counts.map(c=>c.neu), backgroundColor: sentimentColor.neutral, stack:'s'},
              {label:'Negative', data: counts.map(c=>c.neg), backgroundColor: sentimentColor.negative, stack:'s'}
            ]
          },
          options:{
            responsive:true, maintainAspectRatio:false,
            plugins:{legend:{position:'bottom', labels:{usePointStyle:true, boxWidth:10, color:muted}}},
            scales:{
              x:{stacked:true, grid:{display:false}, ticks:{font:{size:10}, maxRotation:35, color:muted}},
              y:{stacked:true, beginAtZero:true, grid:{color:isDark?'rgba(255,255,255,.06)':'#f1f5f9'}, ticks:{color:muted}}
            }
          }
        });
      }
      // 7. Hourly engagement
      {
        const byHour = Array.from({length:24}, (_,h)=>{
          const rows = filtered.filter(r=>r.hour===h);
          return {h, avgEng: rows.length? Math.round(avg(rows.map(r=>r.engagement))):0, count: rows.length};
        });
        charts.hourly = new Chart(ctx('chart_hourly'), {
          type:'line',
          data:{
            labels: byHour.map(b=> String(b.h).padStart(2,'0')+":00"),
            datasets:[
              {label:'Avg Engagement', data: byHour.map(b=>b.avgEng), borderColor:'#2563eb', backgroundColor:'rgba(37,99,235,.12)', fill:true, tension:.35, pointRadius:3, borderWidth:2.5},
              {type:'bar', label:'Post Count', data: byHour.map(b=>b.count), backgroundColor:isDark?'rgba(148,163,184,.25)':'rgba(100,116,139,.18)', borderRadius:4, yAxisID:'y1'}
            ]
          },
          options:{
            responsive:true, maintainAspectRatio:false, interaction:{mode:'index', intersect:false},
            plugins:{legend:{position:'bottom', labels:{usePointStyle:true, boxWidth:10, color:muted}}},
            scales:{
              x:{grid:{display:false}, ticks:{font:{size:10}, maxRotation:0, autoSkip:true, maxTicksLimit:12, color:muted}},
              y:{beginAtZero:true, grid:{color:isDark?'rgba(255,255,255,.06)':'#f1f5f9'}, title:{display:true, text:'Avg Engagement', color:muted}, ticks:{color:muted}},
              y1:{position:'right', beginAtZero:true, grid:{display:false}, title:{display:true, text:'Count', color:muted}, ticks:{color:muted}}
            }
          }
        });
      }
      // 8. User type
      {
        const types = ["Regular","Influencer","Brand","Verified"];
        const stats = types.map(t=>{
          const rows = filtered.filter(r=>r.user_type===t);
          return {t, avgEng: rows.length? Math.round(avg(rows.map(r=>r.engagement))):0, n: rows.length};
        });
        charts.usertype = new Chart(ctx('chart_usertype'), {
          type:'bar',
          data:{
            labels: types.map(s=> `${s} (${stats.find(x=>x.t===s).n})`),
            datasets:[{label:'Avg Engagement', data: stats.map(s=>s.avgEng), backgroundColor:['#64748b','#2563eb','#7c3aed','#0ea5e9'], borderRadius:8}]
          },
          options:{
            responsive:true, maintainAspectRatio:false,
            plugins:{legend:{display:false}},
            scales:{
              x:{grid:{display:false}, ticks:{color:ink}},
              y:{beginAtZero:true, grid:{color:isDark?'rgba(255,255,255,.06)':'#f1f5f9'}, ticks:{callback:v=>Number(v).toLocaleString(), color:muted}}
            }
          }
        });
      }
      hideSkeletons();
      renderWordCloud();
    });
  });
}

// ----- TABLE -----
function renderTable(){
  const q = $("#table_search").value.trim().toLowerCase();
  let rows = filtered;
  if(q){
    rows = rows.filter(r=> (r.text+" "+r.post_id+" "+r.topic+" "+r.platform+" "+r.hashtags_str).toLowerCase().includes(q));
  }
  const total = rows.length;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  if(page>totalPages) page=totalPages;
  const start = (page-1)*pageSize;
  const slice = rows.slice(start, start+pageSize);
  const tbody = document.getElementById('tbody');
  const emptyState = document.getElementById('empty_state');
  const tableWrap = document.querySelector('.table-wrap table');
  if(total===0){
    tbody.innerHTML = '';
    if(emptyState){ emptyState.hidden=false; document.getElementById('empty_count').textContent='0'; }
    if(tableWrap) tableWrap.style.display='none';
  } else {
    if(emptyState) emptyState.hidden=true;
    if(tableWrap) tableWrap.style.display='';
    tbody.innerHTML = slice.map(r=> `
      <tr>
        <td class="mono" style="white-space:nowrap"><b>${r.post_id}</b><br/><span style="color:var(--muted);font-size:11px">${r.date}</span></td>
        <td><span class="platform-badge" style="border-color:${platformColor[r.platform]};color:${platformColor[r.platform]}">${r.platform}</span><br/><span style="font-size:11px;color:var(--muted)">${r.user_type}${r.verified?" • ✓":""}</span></td>
        <td style="white-space:nowrap">${r.timestamp.slice(0,16)}<br/><span style="font-size:11px;color:var(--muted)">${r.hour}:00 • ${r.topic}</span></td>
        <td><span style="background:var(--bg);border:1px solid var(--line);padding:3px 7px;border-radius:999px;font-size:11px;font-weight:700">${r.topic}</span></td>
        <td style="max-width:420px"><div style="font-size:13px;line-height:1.5">${escapeHtml(r.text)}</div><div style="margin-top:4px;color:var(--brand);font-size:11px;font-weight:700">${escapeHtml(r.hashtags_str)}</div></td>
        <td><span class="sentiment-pill ${r.sentiment_label}">${r.sentiment_label}</span></td>
        <td class="mono" style="font-weight:700;color:${r.sentiment_score>0?sentimentColor.positive: r.sentiment_score<0?sentimentColor.negative : sentimentColor.neutral}">${r.sentiment_score>0?"+":""}${r.sentiment_score.toFixed(3)}</td>
        <td class="eng">${fmt(r.engagement)}</td>
        <td>${fmt(r.likes)}</td>
        <td>${fmt(r.comments)}</td>
      </tr>
    `).join("");
  }
  $("#page_info").textContent = total? `${start+1}–${Math.min(start+pageSize, total)} of ${fmt(total)} • Page ${page}/${totalPages}` : `0 of 0 • Page 1/1`;
  $("#table_meta").textContent = `${fmt(total)} posts in current view • Sorted by ${sortKey} (${sortDir}) • Click column headers to sort`;
  $("#prev_btn").disabled = page<=1;
  $("#next_btn").disabled = page>=totalPages;
  // a11y pagination
  $("#prev_btn").setAttribute('aria-disabled', page<=1);
  $("#next_btn").setAttribute('aria-disabled', page>=totalPages);
  const sample = filtered[0] || RAW_DATA[0];
  $("#json_view").textContent = JSON.stringify(sample, null, 2);
  // hide pagination if empty
  const pag = document.querySelector('.pagination');
  if(pag) pag.style.display = total===0 ? 'none' : 'flex';
}
function escapeHtml(s){ return s.replace(/[&<>"']/g, m=> ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m])); }

// ----- EXPORT -----
function downloadFiltered(kind){
  const rows = filtered;
  if(!rows.length){ showToast('No data to export — adjust filters'); return; }
  if(kind==="json"){
    const blob = new Blob([JSON.stringify(rows, null, 2)], {type:"application/json"});
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a"); a.href=url; a.download=`socialpulse_filtered_${rows.length}_${new Date().toISOString().slice(0,10)}.json`; a.click(); URL.revokeObjectURL(url);
    showToast(`Exported ${rows.length} posts as JSON`);
  } else {
    const header = Object.keys(rows[0]||{}).join(",");
    const lines = rows.map(r=> Object.values(r).map(v=> {
      let s = Array.isArray(v)? v.join("; "): String(v);
      s = s.replace(/"/g,'""');
      return `"${s}"`;
    }).join(","));
    const csv = header+"\n"+lines.join("\n");
    const blob = new Blob([csv], {type:"text/csv"});
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a"); a.href=url; a.download=`socialpulse_filtered_${rows.length}_${new Date().toISOString().slice(0,10)}.csv`; a.click(); URL.revokeObjectURL(url);
    showToast(`Exported ${rows.length} posts as CSV`);
  }
}
window.downloadFiltered = downloadFiltered;

// ----- BINDING -----
function updateAll(){
  updateKPIs();
  renderCharts();
  renderTable();
  // sync chip
  const active = countActiveFilters();
  const chip=document.getElementById('active_count');
  if(chip){
    if(filtered.length===420 && active===0) chip.textContent='All posts';
    else chip.textContent=`${filtered.length} posts • ${active} filter${active!==1?'s':''}`;
  }
}

// Drawer logic
function openFilters(){
  const f=document.getElementById('filters');
  const b=document.getElementById('backdrop');
  const btn=document.getElementById('btn_filter_open');
  if(!f) return;
  f.classList.add('open');
  if(b){ b.hidden=false; requestAnimationFrame(()=> b.classList.add('show')); }
  if(btn) btn.setAttribute('aria-expanded','true');
  document.getElementById('btn_filter_close').style.display='inline-flex';
  document.body.style.overflow='hidden';
}
function closeFilters(){
  const f=document.getElementById('filters');
  const b=document.getElementById('backdrop');
  const btn=document.getElementById('btn_filter_open');
  if(!f) return;
  f.classList.remove('open');
  if(b){ b.classList.remove('show'); setTimeout(()=> b.hidden=true, 220); }
  if(btn) btn.setAttribute('aria-expanded','false');
  document.getElementById('btn_filter_close').style.display='none';
  document.body.style.overflow='';
}
document.getElementById("btn_apply").addEventListener("click", ()=>{ applyFilters(); closeFilters(); });
const resetBtns = ["btn_reset","btn_reset_top"];
resetBtns.forEach(id=>{
  const el=document.getElementById(id);
  if(el) el.addEventListener("click", ()=>{ resetFilters(); closeFilters(); });
});
["f_platform","f_sentiment","f_topic","f_user","f_start","f_end"].forEach(id=>{
  document.getElementById(id).addEventListener("change", ()=> applyFilters({keepPage:false}));
});
let searchTimer=null;
function debouncedApply(){
  clearTimeout(searchTimer);
  showSkeletons();
  searchTimer=setTimeout(()=> applyFilters(), 350);
}
document.getElementById("f_search").addEventListener("input", debouncedApply);
document.getElementById("f_search").addEventListener("keydown", (e)=>{ if(e.key==='Enter'){ e.preventDefault(); clearTimeout(searchTimer); applyFilters(); }});
let tableSearchTimer=null;
document.getElementById("table_search").addEventListener("input", ()=>{
  clearTimeout(tableSearchTimer);
  tableSearchTimer=setTimeout(()=>{ page=1; renderTable(); syncURL(); }, 250);
});
document.getElementById("prev_btn").addEventListener("click", ()=>{ if(page>1){page--; renderTable(); syncURL(); document.getElementById('table_anchor').scrollIntoView({behavior:'smooth', block:'nearest'});} });
document.getElementById("next_btn").addEventListener("click", ()=>{
  const total = filtered.length; const tp=Math.ceil(total/pageSize);
  if(page<tp){page++; renderTable(); syncURL(); document.getElementById('table_anchor').scrollIntoView({behavior:'smooth', block:'nearest'});}
});
// keyboard pagination
document.addEventListener('keydown', (e)=>{
  if(e.target.tagName==='INPUT' || e.target.tagName==='TEXTAREA' || e.target.isContentEditable) return;
  if(e.key==='ArrowLeft'){ document.getElementById('prev_btn').click(); }
  if(e.key==='ArrowRight'){ document.getElementById('next_btn').click(); }
});
document.querySelectorAll("th[data-k]").forEach(th=>{
  const handler=()=>{
    const k=th.dataset.k;
    if(sortKey===k) sortDir = sortDir==="asc"?"desc":"asc";
    else {sortKey=k; sortDir="desc";}
    document.querySelectorAll('th[data-k]').forEach(x=> x.setAttribute('aria-sort','none'));
    th.setAttribute('aria-sort', sortDir==='asc'?'ascending':'descending');
    applyFilters();
  };
  th.addEventListener("click", handler);
  th.addEventListener("keydown", (e)=>{ if(e.key==='Enter' || e.key===' '){ e.preventDefault(); handler(); }});
});
document.getElementById("play_run").addEventListener("click", renderPlay);
document.getElementById("play_sample").addEventListener("click", ()=>{
  $("#play_input").value = "Really disappointed with customer service. The product arrived damaged and support hasn't replied in 3 days. #CustomerLove #Support";
  renderPlay();
});
document.getElementById('theme_toggle').addEventListener('click', toggleTheme);
document.getElementById('btn_share').addEventListener('click', shareCurrentView);
document.getElementById('btn_filter_open').addEventListener('click', openFilters);
document.getElementById('btn_filter_close').addEventListener('click', closeFilters);
document.getElementById('backdrop').addEventListener('click', closeFilters);
document.addEventListener('keydown', (e)=>{ if(e.key==='Escape') closeFilters(); });
// Share via Web Share API if available (progressive enhancement)
if(navigator.share){
  const origShare = shareCurrentView;
  window.shareCurrentView = async ()=>{
    syncURL();
    try{ await navigator.share({title: document.title, text: 'Check this filtered view on SocialPulse', url: location.href}); showToast('Shared!'); } catch{ copyShareLink(); }
  };
  document.getElementById('btn_share').addEventListener('click', (e)=>{ e.preventDefault(); window.shareCurrentView(); });
}
// init theme
setTheme(getPreferredTheme());
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e)=>{
  if(!localStorage.getItem(THEME_KEY)) setTheme(e.matches ? 'dark' : 'light');
});
// init URL & data
$("#hero_total").textContent = RAW_DATA.length + " posts";
renderPlay();
const hadURL = readURL();
if(hadURL){
  // apply without resetting page and without double sync
  const f=getFilters();
  // manually filter without calling syncURL again immediately? We'll call applyFilters with keepPage and suppress sync via isRestoring
  isRestoring=true;
  applyFilters({keepPage:true});
  isRestoring=false;
  syncURL();
  showToast('Restored filters from URL');
} else {
  applyFilters();
}
// Ensure skeletons hidden after initial
setTimeout(hideSkeletons, 600);
</script>
</body>
</html>
"""

html = html_template.replace("__EMBEDDED_DATA__", embedded_json)
OUT_PATH.write_text(html, encoding="utf-8")
print(f"Wrote {OUT_PATH} ({len(html):,} chars) with {len(data)} embedded posts")
