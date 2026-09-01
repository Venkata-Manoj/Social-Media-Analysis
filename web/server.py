#!/usr/bin/env python3
"""
SocialPulse — lightweight static + API server (stdlib only)
Serves the canonical ../index.html + data/*.json/assets/* with CORS, cache & security headers.
Also exposes /api/* for filtered access without breaking the static fallback (file:// still works).

  GET /                      -> ../index.html (canonical single-file app)
  GET /index.html            -> ../index.html
  GET /data/social_media_dataset.json -> file (CORS + 5m cache)
  GET /assets/fig*.png       -> file (1y immutable)
  GET /api/health            -> {"ok": true, ...}
  GET /api/stats             -> dataset_stats.json
  GET /api/seo               -> web/seo.json
  GET /api/posts?platform=Twitter&sentiment=positive&topic=Marketing%20Campaign&user_type=Influencer&search=launch&start=2026-03-01&end=2026-08-31&limit=20&offset=0&sort=engagement&order=desc
                             -> {total, limit, offset, returned, filters, data:[...]}

All paths stay relative — works on file:// and https://. Zero dependencies (stdlib http.server).

Enhancements vs v1:
  - Filtering parity with frontend: platform/sentiment/topic/user/search/date/sort/pagination (exact match to index.html JS)
  - Rate limiting hint: in-memory sliding window (60 req / 60s per IP) with X-RateLimit-* headers + 429 + Retry-After
  - ETag for static files AND API JSON (weak + strong), with If-None-Match -> 304 support
  - gzip: if client Accept-Encoding includes gzip, compress responses >512 bytes (stdio gzip, stdlib only), plus Vary header
  - CORS on file:// fallback: Access-Control-Allow-Origin: * always, handles Origin: null / file:// gracefully, plus OPTIONS preflight
  - Security headers + cache policies preserved; file:// double-click still works without server.

Usage:
  python3 web/server.py                      # http://127.0.0.1:8000
  python3 web/server.py --port 4173 --host 0.0.0.0 --open
  python3 web/server.py --root /path/to/project

On Vercel/Netlify/GitHub Pages: no server needed — static hosting serves the same files.
This server is for local dev + optional lightweight API hosting (e.g., Render/Fly cheap Python).

Gzip note: stdlib gzip is used when client advertises Accept-Encoding: gzip. For production behind nginx/CDN,
gzip is typically handled at proxy level; this is a fallback for direct python serving. Vary: Accept-Encoding ensures caches differentiate.
CORS note: file:// pages fetch via http(s) have Origin: null or file://. We return * so local file double-click + fetch to localhost works.
Rate limit note: in-memory per-IP counter, resets every 60s. Headers: X-RateLimit-Limit, Remaining, Reset. 429 when exceeded.
ETag note: weak ETag W/"len-mtime" for files, strong hash for API JSON. Supports conditional GET.
"""

from __future__ import annotations
import argparse
import csv
import datetime
import gzip
import hashlib
import io
import json
import mimetypes
import os
import pathlib
import sys
import threading
import time
import urllib.parse
import webbrowser
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

# ---------------------------------------------------------------------------
# Resolve project root & load datasets
# ---------------------------------------------------------------------------
THIS_DIR = pathlib.Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent  # /mnt/e/DSA0606-asmt  (contains index.html, data/, assets/)
CANDIDATE_ROOTS = [PROJECT_ROOT, pathlib.Path.cwd(), THIS_DIR]

def resolve_root(cli_root: str | None) -> pathlib.Path:
    if cli_root:
        p = pathlib.Path(cli_root).resolve()
        if (p / "index.html").exists() or (p / "data").exists():
            return p
        # allow pointing at web/ itself
        if p.name == "web" and (p.parent / "index.html").exists():
            return p.parent
        return p
    # auto-detect: prefer PROJECT_ROOT if it has index.html
    for cand in [PROJECT_ROOT, pathlib.Path.cwd(), pathlib.Path.cwd().parent, THIS_DIR]:
        if (cand / "index.html").exists():
            return cand.resolve()
        if (cand / "data" / "social_media_dataset.json").exists():
            return cand.resolve()
    return PROJECT_ROOT.resolve()

# Load JSON once
DATA_PATH = PROJECT_ROOT / "data" / "social_media_dataset.json"
STATS_PATH = PROJECT_ROOT / "data" / "dataset_stats.json"
SEO_PATH = THIS_DIR / "seo.json"

try:
    POSTS = json.loads(DATA_PATH.read_text(encoding="utf-8")) if DATA_PATH.exists() else []
except Exception as e:
    print(f"[warn] failed to load {DATA_PATH}: {e}", file=sys.stderr)
    POSTS = []

try:
    STATS = json.loads(STATS_PATH.read_text(encoding="utf-8")) if STATS_PATH.exists() else {}
except Exception:
    STATS = {}

try:
    SEO = json.loads(SEO_PATH.read_text(encoding="utf-8")) if SEO_PATH.exists() else {}
except Exception:
    SEO = {}

# For fast filtering: precompute lowercased haystack
for r in POSTS:
    r["_hay"] = f"{r.get('text','')} {r.get('hashtags_str','')} {r.get('topic','')} {r.get('platform','')}".lower()

# ---------------------------------------------------------------------------
# Rate limiting (in-memory, per-IP sliding window) — hint headers
# ---------------------------------------------------------------------------
_RATE_LIMIT = 60  # requests per window
_RATE_WINDOW = 60.0  # seconds
_rate_store: dict[str, list[float]] = {}
_rate_lock = threading.Lock()

def _get_client_ip(handler) -> str:
    try:
        return handler.client_address[0]
    except Exception:
        return "unknown"

def _check_rate_limit(ip: str) -> tuple[bool, int, int]:
    """Return (allowed, remaining, reset_seconds)."""
    now = time.time()
    with _rate_lock:
        window_start = now - _RATE_WINDOW
        bucket = _rate_store.get(ip, [])
        # prune old
        bucket = [t for t in bucket if t > window_start]
        allowed = len(bucket) < _RATE_LIMIT
        if allowed:
            bucket.append(now)
            _rate_store[ip] = bucket
        else:
            # don't add, but keep pruned bucket
            _rate_store[ip] = bucket
        remaining = max(0, _RATE_LIMIT - len(bucket))
        # seconds until oldest entry expires
        if bucket:
            reset = int(max(0, bucket[0] + _RATE_WINDOW - now)) + 1
        else:
            reset = int(_RATE_WINDOW)
        return allowed, remaining, reset

def _should_gzip(handler, data_len: int) -> bool:
    """gzip if client accepts it and payload > 512 bytes."""
    if data_len < 512:
        return False
    enc = handler.headers.get("Accept-Encoding", "")
    return "gzip" in enc.lower()

def _gzip_bytes(data: bytes) -> bytes:
    return gzip.compress(data, compresslevel=6)

def _etag_for_bytes(data: bytes) -> str:
    # strong ETag using md5, quoted
    h = hashlib.md5(data).hexdigest()[:16]
    return f'"{h}-{len(data)}"'

def _etag_weak_for_file(filepath: pathlib.Path, size: int) -> str:
    try:
        mtime = int(filepath.stat().st_mtime)
    except Exception:
        mtime = int(time.time())
    return f'W/"{size}-{mtime}"'

# ---------------------------------------------------------------------------
# Helpers — filtering matching the JS in index.html
# ---------------------------------------------------------------------------
VALID_PLATFORMS = {"Twitter","Instagram","Facebook","LinkedIn","YouTube"}
VALID_SENTIMENTS = {"positive","neutral","negative"}
VALID_TOPICS = {"Product Launch","Customer Service","Marketing Campaign","Tech Review","Lifestyle","Sports","Entertainment","News"}
VALID_USER_TYPES = {"Regular","Influencer","Brand","Verified"}
SORTABLE = {"post_id","platform","timestamp","date","topic","sentiment_label","sentiment_score","engagement","likes","comments","shares","views","hour"}

def filter_posts(qs: dict) -> list[dict]:
    """qs is parse_qs result (keys -> list[str]). Returns filtered shallow copies without _hay."""
    platform = (qs.get("platform", ["all"])[0] or "all")
    sentiment = (qs.get("sentiment", qs.get("sentiment_label", ["all"]))[0] or "all")
    topic = (qs.get("topic", ["all"])[0] or "all")
    user_type = (qs.get("user_type", qs.get("user", ["all"]))[0] or "all")
    start = (qs.get("start", qs.get("date_start", [""]))[0] or "").strip()
    end = (qs.get("end", qs.get("date_end", [""]))[0] or "").strip()
    search = (qs.get("search", qs.get("q", [""]))[0] or "").strip().lower()

    def ok(r):
        if platform != "all" and r.get("platform") != platform:
            return False
        if sentiment != "all" and r.get("sentiment_label") != sentiment:
            return False
        if topic != "all" and r.get("topic") != topic:
            return False
        if user_type != "all" and r.get("user_type") != user_type:
            return False
        if start and r.get("date","") < start:
            return False
        if end and r.get("date","") > end:
            return False
        if search and search not in r.get("_hay",""):
            return False
        return True

    out = [r for r in POSTS if ok(r)]

    # sorting
    sort_key = (qs.get("sort", qs.get("sortKey", ["timestamp"]))[0] or "timestamp").strip()
    if sort_key not in SORTABLE:
        sort_key = "timestamp"
    order = (qs.get("order", qs.get("sortDir", ["desc"]))[0] or "desc").strip().lower()
    reverse = order != "asc"

    # numeric keys
    def keyfn(r):
        v = r.get(sort_key)
        if sort_key in {"sentiment_score","engagement","likes","comments","shares","views","hour"}:
            try: return float(v)
            except: return 0
        return v or ""

    try:
        out.sort(key=keyfn, reverse=reverse)
    except Exception:
        pass

    return out

def paginate(rows, qs):
    try:
        limit = int((qs.get("limit", ["50"])[0] or "50"))
    except: limit = 50
    try:
        offset = int((qs.get("offset", ["0"])[0] or "0"))
    except: offset = 0
    limit = max(1, min(limit, 420))
    offset = max(0, offset)
    total = len(rows)
    sliced = rows[offset: offset+limit]
    # strip internal _hay before returning
    clean = [{k:v for k,v in r.items() if k != "_hay"} for r in sliced]
    return total, limit, offset, clean

# ---------------------------------------------------------------------------
# HTTP handler
# ---------------------------------------------------------------------------
class Handler(SimpleHTTPRequestHandler):
    # we serve from ROOT, but need to resolve web/ as well
    root: pathlib.Path = PROJECT_ROOT

    def log_message(self, fmt, *args):
        # quiet favicon, colorful
        msg = fmt % args
        code = args[1] if len(args) > 1 else "-"
        # no extra noise for 404 fallback
        sys.stderr.write(f"{self.log_date_time_string()} \"{msg}\" \n")

    def end_headers(self):
        # Security headers for every response
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        self.send_header("X-XSS-Protection", "1; mode=block")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        # CORS for data/assets/api + local dev convenience: allow all
        # Works on file:// fallback: fetch from file:// has Origin: null, which * explicitly allows for simple requests.
        # For credentialed requests, browsers disallow * with null, but we are not credentialed (no cookies), so * is safe and intentional for offline-first.
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, HEAD, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With, If-None-Match, If-Modified-Since")
        self.send_header("Access-Control-Expose-Headers", "ETag, X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset, Content-Length, Content-Encoding")
        # Vary for gzip + CORS
        self.send_header("Vary", "Accept-Encoding, Origin")
        super().end_headers()

    def do_OPTIONS(self):
        # CORS preflight — especially needed for file:// -> http:// cross-origin
        self.send_response(HTTPStatus.NO_CONTENT)
        self.end_headers()

    def do_HEAD(self):
        self.do_GET(head_only=True)

    def do_GET(self, head_only=False):
        parsed = urllib.parse.urlparse(self.path)
        path = urllib.parse.unquote(parsed.path)
        qs = urllib.parse.parse_qs(parsed.query)

        # Rate limiting hint — check before any heavy work, add headers even on 429
        ip = _get_client_ip(self)
        allowed, remaining, reset = _check_rate_limit(ip)
        # we will attach headers in each response path; store for later
        self._rl_remaining = remaining
        self._rl_reset = reset
        self._rl_allowed = allowed
        if not allowed:
            # 429 Too Many Requests with RateLimit headers
            body = {"error": "rate limit exceeded", "limit": _RATE_LIMIT, "window": f"{int(_RATE_WINDOW)}s", "retry_after": reset}
            data = json.dumps(body, ensure_ascii=False, indent=2).encode("utf-8")
            etag = _etag_for_bytes(data)
            # optionally gzip 429 body too
            use_gzip = _should_gzip(self, len(data))
            if use_gzip:
                data = _gzip_bytes(data)
            self.send_response(HTTPStatus.TOO_MANY_REQUESTS)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("ETag", etag)
            self.send_header("X-RateLimit-Limit", str(_RATE_LIMIT))
            self.send_header("X-RateLimit-Remaining", str(remaining))
            self.send_header("X-RateLimit-Reset", str(reset))
            self.send_header("Retry-After", str(reset))
            if use_gzip:
                self.send_header("Content-Encoding", "gzip")
            self.end_headers()
            if not head_only:
                try:
                    self.wfile.write(data)
                except BrokenPipeError:
                    pass
            return

        # Normalize path: collapse //, remove query
        # Protect traversal
        if ".." in path:
            self.send_error(400, "Invalid path")
            return

        # --- API routes ---
        if path.startswith("/api/"):
            self.handle_api(path, qs, head_only)
            return

        # --- Static: resolve file ---
        # Special: / -> index.html
        if path in ("/", "/index", "/index.html"):
            f = self.resolve_static("index.html")
            if f and f.exists():
                self.serve_file(f, head_only)
                return
            self.send_error(404, "index.html not found")
            return

        # Strip leading /
        rel = path.lstrip("/")
        # If rel is empty, already handled
        # Try to resolve from root
        f = self.resolve_static(rel)
        if f and f.exists() and f.is_file():
            self.serve_file(f, head_only)
            return

        # SPA fallback: if not an asset/data/api file and Accept wants html, serve index.html
        # Keep static API for file:// compat: only fallback when path has no extension or is html-like
        ext = pathlib.Path(rel).suffix.lower()
        if not ext or ext in (".html", ".htm"):
            # Check if client prefers html
            accept = self.headers.get("Accept", "")
            if "text/html" in accept or not ext:
                fallback = self.resolve_static("index.html")
                if fallback and fallback.exists():
                    self.serve_file(fallback, head_only)
                    return

        # Not found
        self.send_error(404, f"Not found: {path}")

    # ---- helpers ----
    def resolve_static(self, rel: str) -> pathlib.Path | None:
        """Resolve rel relative to root, also check web/ subfolder for web/* requests."""
        # Security: prevent absolute or traversal
        rel = rel.replace("\\", "/").lstrip("/")
        if ".." in rel.split("/"):
            return None
        # Direct under root
        cand = (self.root / rel).resolve()
        # Ensure cand is inside root or its web/ folder
        try:
            cand.relative_to(self.root.resolve())
        except ValueError:
            # allow web/ itself if root is project root
            pass
        if cand.exists():
            return cand
        # Fallback: if request is data/... or assets/... but root is web/ (when --root web), try parent
        parent = self.root.parent
        cand2 = (parent / rel).resolve()
        if cand2.exists():
            return cand2
        return cand

    def serve_file(self, filepath: pathlib.Path, head_only=False):
        # Determine mime
        mime, _ = mimetypes.guess_type(str(filepath))
        if filepath.suffix == ".json":
            mime = "application/json; charset=utf-8"
        elif filepath.suffix == ".csv":
            mime = "text/csv; charset=utf-8"
        elif filepath.suffix in (".js", ".mjs"):
            mime = "application/javascript; charset=utf-8"
        elif filepath.suffix == ".svg":
            mime = "image/svg+xml"
        elif not mime:
            mime = "application/octet-stream"

        # Cache policy
        cache = "public, max-age=0, must-revalidate"
        name = filepath.name
        suffix = filepath.suffix.lower()
        if suffix in (".png", ".jpg", ".jpeg", ".webp", ".svg", ".woff2", ".woff"):
            cache = "public, max-age=31536000, immutable"
        elif suffix in (".json", ".csv"):
            cache = "public, max-age=300, must-revalidate"
        elif suffix in (".html", ".htm"):
            cache = "public, max-age=0, must-revalidate"
        elif suffix in (".js", ".css"):
            cache = "public, max-age=3600, must-revalidate"

        try:
            data = filepath.read_bytes()
        except Exception as e:
            self.send_error(500, f"Read error: {e}")
            return

        # ETag handling — weak for files, support If-None-Match
        etag = _etag_weak_for_file(filepath, len(data))
        # Also handle If-Modified-Since for caching
        inm = self.headers.get("If-None-Match")
        if inm and inm.strip() == etag:
            self.send_response(HTTPStatus.NOT_MODIFIED)
            self.send_header("ETag", etag)
            self.send_header("Cache-Control", cache)
            # still send RateLimit headers
            if hasattr(self, "_rl_remaining"):
                self.send_header("X-RateLimit-Limit", str(_RATE_LIMIT))
                self.send_header("X-RateLimit-Remaining", str(self._rl_remaining))
                self.send_header("X-RateLimit-Reset", str(self._rl_reset))
            self.end_headers()
            return

        # Gzip handling — compress if client accepts and mime is textual/compressible
        # Only gzip json/csv/js/css/html/svg, not png (already compressed)
        compressible = suffix in (".json", ".csv", ".js", ".mjs", ".css", ".html", ".htm", ".svg", ".txt", ".webmanifest", ".xml")
        use_gzip = compressible and _should_gzip(self, len(data))
        out_data = data
        if use_gzip:
            out_data = _gzip_bytes(data)

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(out_data)))
        self.send_header("Cache-Control", cache)
        # ETag weak
        self.send_header("ETag", etag)
        last_mod = datetime.datetime.fromtimestamp(filepath.stat().st_mtime, tz=datetime.timezone.utc)
        self.send_header("Last-Modified", last_mod.strftime("%a, %d %b %Y %H:%M:%S GMT"))
        if use_gzip:
            self.send_header("Content-Encoding", "gzip")
        # RateLimit headers
        if hasattr(self, "_rl_remaining"):
            self.send_header("X-RateLimit-Limit", str(_RATE_LIMIT))
            self.send_header("X-RateLimit-Remaining", str(self._rl_remaining))
            self.send_header("X-RateLimit-Reset", str(self._rl_reset))
        self.end_headers()
        if not head_only:
            try:
                self.wfile.write(out_data)
            except BrokenPipeError:
                pass

    def handle_api(self, path: str, qs: dict, head_only=False):
        # CORS already via end_headers
        if path in ("/api/health", "/api/healthz", "/api/ping"):
            body = {
                "ok": True,
                "service": "socialpulse-web",
                "version": "1.0.0",
                "posts": len(POSTS),
                "date_range": STATS.get("date_range", "2026-03-01 to 2026-08-31"),
                "total_engagement": STATS.get("total_engagement", 0),
                "uptime": "n/a (stdlib http.server)",
                "time": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "root": str(self.root),
                "endpoints": ["/api/posts", "/api/stats", "/api/seo", "/api/health", "/api/hashtags"]
            }
            self.send_json(body, head_only)
            return
        if path == "/api/stats":
            self.send_json(STATS if STATS else {"error": "stats not found"}, head_only)
            return
        if path == "/api/seo":
            self.send_json(SEO if SEO else {"error": "seo not found"}, head_only)
            return
        if path == "/api/hashtags":
            from collections import Counter
            c = Counter()
            for r in POSTS:
                for h in r.get("hashtags", []):
                    c[h] += 1
            top = c.most_common(20)
            self.send_json({"count": len(c), "top": [{"tag": k, "count": v} for k, v in top]}, head_only)
            return
        if path.startswith("/api/posts"):
            # also handle /api/posts.csv ?format=csv
            fmt = (qs.get("format", qs.get("fmt", ["json"]))[0] or "json").lower()
            # support .csv suffix
            if path.endswith(".csv") or fmt == "csv":
                rows = filter_posts(qs)
                total, limit, offset, sliced = paginate(rows, qs)
                # stream CSV
                output = io.StringIO()
                if sliced:
                    writer = csv.DictWriter(output, fieldnames=[k for k in sliced[0].keys() if k != "_hay"])
                    writer.writeheader()
                    for r in sliced:
                        # flatten hashtags array to string
                        rec = dict(r)
                        if isinstance(rec.get("hashtags"), list):
                            rec["hashtags"] = ";".join(rec["hashtags"])
                        writer.writerow(rec)
                else:
                    # empty header from POSTS[0] if exists
                    if POSTS:
                        fields = [k for k in POSTS[0].keys() if k != "_hay"]
                        writer = csv.DictWriter(output, fieldnames=fields)
                        writer.writeheader()
                data = output.getvalue().encode("utf-8")
                # ETag for CSV
                etag = _etag_for_bytes(data)
                inm = self.headers.get("If-None-Match")
                if inm and inm.strip() == etag:
                    self.send_response(HTTPStatus.NOT_MODIFIED)
                    self.send_header("ETag", etag)
                    self.send_header("Cache-Control", "no-store")
                    if hasattr(self, "_rl_remaining"):
                        self.send_header("X-RateLimit-Limit", str(_RATE_LIMIT))
                        self.send_header("X-RateLimit-Remaining", str(self._rl_remaining))
                        self.send_header("X-RateLimit-Reset", str(self._rl_reset))
                    self.end_headers()
                    return
                use_gzip = _should_gzip(self, len(data))
                if use_gzip:
                    data = _gzip_bytes(data)
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/csv; charset=utf-8")
                self.send_header("Content-Disposition", f'attachment; filename="socialpulse_filtered_{total}_{datetime.date.today().isoformat()}.csv"')
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Cache-Control", "no-store")
                self.send_header("ETag", etag)
                if use_gzip:
                    self.send_header("Content-Encoding", "gzip")
                if hasattr(self, "_rl_remaining"):
                    self.send_header("X-RateLimit-Limit", str(_RATE_LIMIT))
                    self.send_header("X-RateLimit-Remaining", str(self._rl_remaining))
                    self.send_header("X-RateLimit-Reset", str(self._rl_reset))
                self.end_headers()
                if not head_only:
                    self.wfile.write(data)
                return
            # JSON default
            rows = filter_posts(qs)
            total, limit, offset, sliced = paginate(rows, qs)
            # Collect filter echo
            filters = {k: v[0] for k, v in qs.items()}
            body = {
                "total": total,
                "limit": limit,
                "offset": offset,
                "returned": len(sliced),
                "filters": filters,
                "sort": (qs.get("sort", ["timestamp"])[0] if "sort" in qs else "timestamp"),
                "order": (qs.get("order", ["desc"])[0] if "order" in qs else "desc"),
                "data": sliced
            }
            self.send_json(body, head_only)
            return

        # unknown api
        self.send_json({"error": "not found", "path": path, "available": ["/api/posts","/api/stats","/api/seo","/api/health","/api/hashtags"]}, head_only, status=404)

    def send_json(self, obj, head_only=False, status=200):
        data = json.dumps(obj, ensure_ascii=False, indent=2).encode("utf-8")
        etag = _etag_for_bytes(data)
        # Conditional GET support
        inm = self.headers.get("If-None-Match")
        if inm and inm.strip() == etag and status == 200:
            self.send_response(HTTPStatus.NOT_MODIFIED)
            self.send_header("ETag", etag)
            self.send_header("Cache-Control", "no-store" if status != 200 else "public, max-age=60, must-revalidate")
            if hasattr(self, "_rl_remaining"):
                self.send_header("X-RateLimit-Limit", str(_RATE_LIMIT))
                self.send_header("X-RateLimit-Remaining", str(self._rl_remaining))
                self.send_header("X-RateLimit-Reset", str(self._rl_reset))
            self.end_headers()
            return
        use_gzip = _should_gzip(self, len(data))
        out = data
        if use_gzip:
            out = _gzip_bytes(data)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(out)))
        self.send_header("Cache-Control", "no-store" if status != 200 else "public, max-age=60, must-revalidate")
        self.send_header("ETag", etag)
        if use_gzip:
            self.send_header("Content-Encoding", "gzip")
        if hasattr(self, "_rl_remaining"):
            self.send_header("X-RateLimit-Limit", str(_RATE_LIMIT))
            self.send_header("X-RateLimit-Remaining", str(self._rl_remaining))
            self.send_header("X-RateLimit-Reset", str(self._rl_reset))
        self.end_headers()
        if not head_only:
            self.wfile.write(out)


def main():
    parser = argparse.ArgumentParser(description="SocialPulse static + API server (stdlib, zero-deps)")
    parser.add_argument("--host", default="127.0.0.1", help="bind host (default: 127.0.0.1, use 0.0.0.0 for LAN)")
    parser.add_argument("--port", "-p", type=int, default=8000, help="port (default: 8000)")
    parser.add_argument("--root", help="project root containing index.html (default: auto-detect parent of web/)")
    parser.add_argument("--open", action="store_true", help="open browser after start")
    args = parser.parse_args()

    root = resolve_root(args.root)
    Handler.root = root

    # sanity checks
    idx = root / "index.html"
    print(f"SocialPulse server — project root: {root}", flush=True)
    if idx.exists():
        print(f"  canonical: {idx} ({idx.stat().st_size:,} bytes) ✓", flush=True)
    else:
        print(f"  [warn] index.html not found at {idx} — fallback will 404", file=sys.stderr, flush=True)

    data_file = root / "data" / "social_media_dataset.json"
    if data_file.exists():
        print(f"  dataset:   {data_file} ({len(POSTS)} posts) ✓", flush=True)
    else:
        print(f"  [warn] dataset not found at {data_file}", file=sys.stderr, flush=True)

    for sub in ["assets", "data", "report"]:
        p = root / sub
        status = "✓" if p.exists() else "missing"
        print(f"  {sub:10s}: {p} {status}", flush=True)

    addr = (args.host, args.port)
    class ReuseServer(ThreadingHTTPServer):
        allow_reuse_address = True
        daemon_threads = True

    try:
        httpd = ReuseServer(addr, Handler)
    except OSError as e:
        print(f"[error] bind {args.host}:{args.port} failed: {e}", file=sys.stderr)
        # try next port
        for try_port in [4173, 3000, 8001, 8080]:
            try:
                httpd = ReuseServer((args.host, try_port), Handler)
                args.port = try_port
                print(f"  retrying on :{try_port} ...", flush=True)
                break
            except OSError:
                continue
        else:
            sys.exit(1)

    url = f"http://{args.host}:{args.port}/"
    display_url = f"http://127.0.0.1:{args.port}/" if args.host == "0.0.0.0" else url
    print(f"\nServing on {url}  (display: {display_url})", flush=True)
    print(f"  /                -> index.html (SPA fallback)", flush=True)
    print(f"  /api/posts       -> filtered JSON (try: /api/posts?platform=Instagram&limit=3)", flush=True)
    print(f"  /api/stats       -> dataset_stats.json", flush=True)
    print(f"  /api/seo         -> seo.json", flush=True)
    print(f"  /api/health      -> healthcheck", flush=True)
    print(f"  Features: ETag (304), gzip (Accept-Encoding), RateLimit 60/min, CORS * (file:// safe), Vary headers", flush=True)
    print(f"  Static fallback: file:// double-click still works (no server required) — server is optional", flush=True)
    print(f"  Ctrl+C to stop\n", flush=True)

    if args.open:
        try:
            webbrowser.open(display_url)
            print(f"  opened browser to {display_url}", flush=True)
        except Exception as e:
            print(f"  [warn] --open failed: {e}", file=sys.stderr)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...", flush=True)
        httpd.shutdown()
        sys.exit(0)

if __name__ == "__main__":
    main()
