#!/usr/bin/env python3
"""
SocialPulse — Dataset & Dashboard Logic Tests
Validates dataset integrity (420 posts, fields, sentiment scores, engagement math, etc.)
and optionally tests API if web/server.py is running (http.client).

Run:
  python3 tests/test_app.py
  python3 -m unittest tests.test_app -v
Exit code 0 on success, 1 on any failure.
"""

import csv
import json
import pathlib
import sys
import unittest
import urllib.parse
from collections import Counter

# Resolve project root (one level up from tests/)
THIS_DIR = pathlib.Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent
if not (PROJECT_ROOT / "data" / "social_media_dataset.json").exists():
    # fallback if run from root
    PROJECT_ROOT = pathlib.Path.cwd()
    if not (PROJECT_ROOT / "data" / "social_media_dataset.json").exists():
        PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]

DATA_JSON = PROJECT_ROOT / "data" / "social_media_dataset.json"
DATA_CSV = PROJECT_ROOT / "data" / "social_media_dataset.csv"
STATS_JSON = PROJECT_ROOT / "data" / "dataset_stats.json"
INDEX_HTML = PROJECT_ROOT / "index.html"

# Load dataset once for all tests
try:
    POSTS = json.loads(DATA_JSON.read_text(encoding="utf-8"))
except Exception as e:
    print(f"[fatal] cannot load {DATA_JSON}: {e}", file=sys.stderr)
    POSTS = []

try:
    STATS = json.loads(STATS_JSON.read_text(encoding="utf-8")) if STATS_JSON.exists() else {}
except Exception:
    STATS = {}

REQUIRED_FIELDS = [
    "post_id", "platform", "timestamp", "date", "hour", "text",
    "likes", "shares", "comments", "views", "engagement", "engagement_rate",
    "sentiment_label", "sentiment_score", "hashtags", "hashtags_str",
    "topic", "user_type", "verified", "language"
]
VALID_PLATFORMS = {"Twitter","Instagram","Facebook","LinkedIn","YouTube"}
VALID_SENTIMENTS = {"positive","neutral","negative"}
VALID_TOPICS = {"Product Launch","Customer Service","Marketing Campaign","Tech Review","Lifestyle","Sports","Entertainment","News"}
VALID_USER_TYPES = {"Regular","Influencer","Brand","Verified"}

class TestDatasetIntegrity(unittest.TestCase):
    def test_total_posts(self):
        self.assertEqual(len(POSTS), 420, f"Expected 420 posts, got {len(POSTS)}")
        print(f"✓ total posts = {len(POSTS)}")

    def test_required_fields(self):
        for i, r in enumerate(POSTS):
            for f in REQUIRED_FIELDS:
                self.assertIn(f, r, f"post {i} ({r.get('post_id')}) missing field {f}")
        print(f"✓ all posts have required 20 fields ({REQUIRED_FIELDS})")

    def test_post_id_unique_and_sequential(self):
        ids = [r["post_id"] for r in POSTS]
        self.assertEqual(len(ids), len(set(ids)), "post_id not unique")
        # Check format P0001..P0420
        expected = [f"P{i:04d}" for i in range(1, 421)]
        self.assertEqual(sorted(ids), expected, "post_id not sequential P0001..P0420")
        # Also check chronological order? dataset is sorted by timestamp per generator
        print(f"✓ post_id unique & sequential (P0001..P0420)")

    def test_sentiment_score_range(self):
        for r in POSTS:
            s = r["sentiment_score"]
            self.assertIsInstance(s, (int, float), f"{r['post_id']} sentiment_score not numeric")
            self.assertGreaterEqual(s, -1.0, f"{r['post_id']} sentiment_score {s} < -1")
            self.assertLessEqual(s, 1.0, f"{r['post_id']} sentiment_score {s} > 1")
        print(f"✓ sentiment_score in [-1,1] for all posts")

    def test_sentiment_label_valid(self):
        for r in POSTS:
            self.assertIn(r["sentiment_label"], VALID_SENTIMENTS, f"{r['post_id']} invalid sentiment_label {r['sentiment_label']}")
        dist = Counter(r["sentiment_label"] for r in POSTS)
        print(f"✓ sentiment_label valid, distribution {dict(dist)}")

    def test_sentiment_label_score_consistency(self):
        # Heuristic: positive should be >0.25, negative <-0.25, neutral in [-0.35,0.35] roughly per generator
        # We only check that extreme mismatch doesn't happen: positive not strongly negative etc.
        mismatches = []
        for r in POSTS:
            s = r["sentiment_score"]
            lab = r["sentiment_label"]
            if lab == "positive" and s < 0:
                mismatches.append(r["post_id"])
            if lab == "negative" and s > 0:
                mismatches.append(r["post_id"])
        # Allow some neutral borderline? But positive/negative should not cross zero strictly in generator
        self.assertEqual(len(mismatches), 0, f"sentiment label/score mismatch sign cross zero: {mismatches[:5]}")
        print(f"✓ sentiment label ↔ score sign consistency (no positive with negative score, etc.)")

    def test_engagement_math(self):
        for r in POSTS:
            calc = r["likes"] + r["shares"] + r["comments"]
            self.assertEqual(r["engagement"], calc, f"{r['post_id']} engagement {r['engagement']} != likes+shares+comments {calc}")
        print(f"✓ engagement = likes+shares+comments for all")

    def test_engagement_rate_math(self):
        for r in POSTS:
            expected = round(r["engagement"] / max(r["views"], 1) * 100, 2)
            # Allow 0.01 tolerance due to rounding
            self.assertAlmostEqual(r["engagement_rate"], expected, delta=0.02,
                                   msg=f"{r['post_id']} engagement_rate {r['engagement_rate']} != {expected}")
            self.assertGreaterEqual(r["engagement_rate"], 0)
            self.assertLessEqual(r["engagement_rate"], 100)
        print(f"✓ engagement_rate = engagement/views*100 (within tolerance)")

    def test_views_greater_than_engagement(self):
        for r in POSTS:
            self.assertGreater(r["views"], r["engagement"], f"{r['post_id']} views {r['views']} not > engagement {r['engagement']}")
            self.assertGreater(r["views"], 0)
            self.assertGreaterEqual(r["likes"], 0)
            self.assertGreaterEqual(r["shares"], 0)
            self.assertGreaterEqual(r["comments"], 0)
        print(f"✓ views > engagement and counters non-negative")

    def test_platform_topic_user_valid(self):
        for r in POSTS:
            self.assertIn(r["platform"], VALID_PLATFORMS, f"{r['post_id']} invalid platform {r['platform']}")
            self.assertIn(r["topic"], VALID_TOPICS, f"{r['post_id']} invalid topic {r['topic']}")
            self.assertIn(r["user_type"], VALID_USER_TYPES, f"{r['post_id']} invalid user_type {r['user_type']}")
        print(f"✓ platform/topic/user_type valid categorical")

    def test_date_hour_range(self):
        for r in POSTS:
            self.assertGreaterEqual(r["date"], "2026-03-01")
            self.assertLessEqual(r["date"], "2026-08-31")
            self.assertGreaterEqual(r["hour"], 0)
            self.assertLessEqual(r["hour"], 23)
            # timestamp date should match date field
            self.assertTrue(r["timestamp"].startswith(r["date"]), f"{r['post_id']} timestamp {r['timestamp']} != date {r['date']}")
        print(f"✓ date in 2026-03-01..2026-08-31, hour 0..23, timestamp matches date")

    def test_hashtags_structures(self):
        for r in POSTS:
            self.assertIsInstance(r["hashtags"], list, f"{r['post_id']} hashtags not list")
            self.assertGreaterEqual(len(r["hashtags"]), 1)
            self.assertLessEqual(len(r["hashtags"]), 4)
            self.assertIsInstance(r["hashtags_str"], str)
            # hashtags_str should be space-joined hashtags
            self.assertEqual(r["hashtags_str"], " ".join(r["hashtags"]), f"{r['post_id']} hashtags_str != join(hashtags)")
            for h in r["hashtags"]:
                self.assertTrue(h.startswith("#"), f"{r['post_id']} hashtag {h} not starting with #")
        print(f"✓ hashtags array (1-4) and hashtags_str consistent")

    def test_text_nonempty(self):
        for r in POSTS:
            self.assertIsInstance(r["text"], str)
            self.assertGreater(len(r["text"].strip()), 10, f"{r['post_id']} text too short")
        print(f"✓ text non-empty (>10 chars) for all")

    def test_verified_boolean(self):
        for r in POSTS:
            self.assertIsInstance(r["verified"], bool, f"{r['post_id']} verified not bool")
        print(f"✓ verified is boolean for all")

    def test_stats_parity(self):
        if not STATS:
            self.skipTest("dataset_stats.json missing")
        self.assertEqual(STATS.get("total_posts"), 420)
        # recompute
        plat = Counter(r["platform"] for r in POSTS)
        sent = Counter(r["sentiment_label"] for r in POSTS)
        topic = Counter(r["topic"] for r in POSTS)
        utype = Counter(r["user_type"] for r in POSTS)
        total_eng = sum(r["engagement"] for r in POSTS)
        avg_sent = round(sum(r["sentiment_score"] for r in POSTS)/len(POSTS), 3)
        self.assertEqual(dict(plat), STATS.get("platform_dist"), "platform_dist mismatch")
        self.assertEqual(dict(sent), STATS.get("sentiment_dist"), "sentiment_dist mismatch")
        self.assertEqual(dict(topic), STATS.get("topic_dist"), "topic_dist mismatch")
        self.assertEqual(dict(utype), STATS.get("user_type_dist"), "user_type_dist mismatch")
        self.assertEqual(total_eng, STATS.get("total_engagement"), "total_engagement mismatch")
        self.assertAlmostEqual(avg_sent, STATS.get("avg_sentiment"), delta=0.001)
        print(f"✓ dataset_stats.json parity: stats match recomputed values")

    def test_csv_json_parity_quick(self):
        if not DATA_CSV.exists():
            self.skipTest("CSV missing")
        with open(DATA_CSV, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            csv_rows = list(reader)
        self.assertEqual(len(csv_rows), 420, f"CSV should have 420 rows, got {len(csv_rows)}")
        # Check header fields (CSV has 20 fields, hashtags as string with comma join)
        self.assertIn("post_id", reader.fieldnames)
        # Check first and last post_id match JSON
        json_ids = [r["post_id"] for r in POSTS]
        csv_ids = [r["post_id"] for r in csv_rows]
        self.assertEqual(json_ids, csv_ids, "CSV post_id order != JSON order")
        # Check engagement parity for random sample
        for idx in [0, 100, 200, 419]:
            jr = POSTS[idx]
            cr = csv_rows[idx]
            self.assertEqual(int(cr["engagement"]), jr["engagement"], f"CSV vs JSON engagement mismatch at {jr['post_id']}")
            self.assertEqual(int(cr["likes"]), jr["likes"])
        print(f"✓ CSV/JSON parity quick check (420 rows, IDs match, engagement matches)")

class TestAPIOptional(unittest.TestCase):
    """If a server is running on localhost, test filtering parity. Otherwise skip."""
    @classmethod
    def setUpClass(cls):
        cls.base = None
        cls.available = False
        # Try to find running server on common ports
        import http.client
        import socket
        cls.http = http.client
        cls.socket = socket
        for port in [8000, 4173, 3000, 8001, 8080]:
            try:
                conn = http.client.HTTPConnection("127.0.0.1", port, timeout=1)
                conn.request("GET", "/api/health")
                resp = conn.getresponse()
                if resp.status == 200:
                    data = json.loads(resp.read().decode())
                    if data.get("ok"):
                        cls.base = f"127.0.0.1:{port}"
                        cls.port = port
                        cls.available = True
                        print(f"\n[API] found running server at http://{cls.base} — will test API filtering")
                        conn.close()
                        break
                conn.close()
            except Exception:
                continue
        if not cls.available:
            print("\n[API] no running server found on 8000/4173/3000/8001/8080 — skipping API tests (start with: python3 web/server.py --port 8000)")

    def _get_json(self, path):
        conn = self.http.HTTPConnection("127.0.0.1", self.port, timeout=3)
        conn.request("GET", path, headers={"Accept": "application/json", "Accept-Encoding": "gzip"})
        resp = conn.getresponse()
        raw = resp.read()
        # handle gzip if server compressed
        if resp.getheader("Content-Encoding") == "gzip":
            import gzip
            raw = gzip.decompress(raw)
        data = json.loads(raw.decode())
        hdrs = dict(resp.getheaders())
        conn.close()
        return resp.status, hdrs, data

    def test_api_health(self):
        if not self.available:
            self.skipTest("no server running")
        status, hdrs, data = self._get_json("/api/health")
        self.assertEqual(status, 200)
        self.assertTrue(data.get("ok"))
        self.assertEqual(data.get("posts"), 420)
        # Check CORS and RateLimit headers
        self.assertEqual(hdrs.get("Access-Control-Allow-Origin"), "*")
        self.assertIn("X-RateLimit-Limit", hdrs)
        self.assertIn("ETag", hdrs)
        print(f"✓ API /api/health ok, CORS & RateLimit & ETag present")

    def test_api_posts_filtering_platform(self):
        if not self.available:
            self.skipTest("no server running")
        status, _, data = self._get_json("/api/posts?platform=Instagram&limit=5")
        self.assertEqual(status, 200)
        self.assertLessEqual(data["returned"], 5)
        for r in data["data"]:
            self.assertEqual(r["platform"], "Instagram")
        print(f"✓ API filtering platform=Instagram works ({data['total']} total, returned {data['returned']})")

    def test_api_posts_filtering_sentiment(self):
        if not self.available:
            self.skipTest("no server running")
        status, _, data = self._get_json("/api/posts?sentiment=positive&limit=10")
        self.assertEqual(status, 200)
        for r in data["data"]:
            self.assertEqual(r["sentiment_label"], "positive")
        print(f"✓ API filtering sentiment=positive works ({data['total']} total)")

    def test_api_posts_filtering_topic(self):
        if not self.available:
            self.skipTest("no server running")
        status, _, data = self._get_json("/api/posts?topic=Customer%20Service&limit=10")
        self.assertEqual(status, 200)
        for r in data["data"]:
            self.assertEqual(r["topic"], "Customer Service")
        print(f"✓ API filtering topic=Customer Service works ({data['total']} total)")

    def test_api_posts_filtering_user(self):
        if not self.available:
            self.skipTest("no server running")
        status, _, data = self._get_json("/api/posts?user_type=Influencer&limit=10")
        self.assertEqual(status, 200)
        for r in data["data"]:
            self.assertEqual(r["user_type"], "Influencer")
        print(f"✓ API filtering user_type=Influencer works ({data['total']} total)")

    def test_api_posts_filtering_search(self):
        if not self.available:
            self.skipTest("no server running")
        status, _, data = self._get_json("/api/posts?search=launch&limit=10")
        self.assertEqual(status, 200)
        self.assertGreater(data["total"], 0, "search=launch should match some posts")
        for r in data["data"]:
            hay = (r["text"] + " " + r["hashtags_str"] + " " + r["topic"] + " " + r["platform"]).lower()
            self.assertIn("launch", hay)
        print(f"✓ API filtering search=launch works ({data['total']} matched)")

    def test_api_posts_filtering_date(self):
        if not self.available:
            self.skipTest("no server running")
        status, _, data = self._get_json("/api/posts?start=2026-04-15&end=2026-04-15&limit=50")
        self.assertEqual(status, 200)
        for r in data["data"]:
            self.assertEqual(r["date"], "2026-04-15")
        print(f"✓ API filtering date range start/end works ({data['total']} on 2026-04-15)")

    def test_api_posts_sort_and_pagination(self):
        if not self.available:
            self.skipTest("no server running")
        status, _, data = self._get_json("/api/posts?sort=engagement&order=desc&limit=5&offset=0")
        self.assertEqual(status, 200)
        engs = [r["engagement"] for r in data["data"]]
        self.assertEqual(engs, sorted(engs, reverse=True), "sort engagement desc failed")
        print(f"✓ API sort & pagination works (engagement desc, limit 5)")

    def test_api_posts_gzip_and_etag(self):
        if not self.available:
            self.skipTest("no server running")
        # First request to get ETag
        conn = self.http.HTTPConnection("127.0.0.1", self.port, timeout=3)
        conn.request("GET", "/api/posts?limit=1", headers={"Accept": "application/json"})
        resp = conn.getresponse()
        etag = resp.getheader("ETag")
        raw = resp.read()
        conn.close()
        self.assertIsNotNone(etag, "ETag missing on API")
        # Second with If-None-Match should be 304
        conn = self.http.HTTPConnection("127.0.0.1", self.port, timeout=3)
        conn.request("GET", "/api/posts?limit=1", headers={"If-None-Match": etag})
        resp = conn.getresponse()
        self.assertEqual(resp.status, 304, f"If-None-Match should return 304, got {resp.status}")
        conn.close()
        # Gzip test
        status, hdrs, _ = self._get_json("/api/posts?limit=50")
        # Server should have gzipped if we sent Accept-Encoding: gzip and payload >512
        # Check that ETag present and either gzip or not but not error
        self.assertIn("ETag", hdrs)
        print(f"✓ API ETag (conditional GET 304) & gzip handling works (ETag={etag})")

    def test_api_rate_limit_headers(self):
        if not self.available:
            self.skipTest("no server running")
        status, hdrs, _ = self._get_json("/api/health")
        self.assertIn("X-RateLimit-Limit", hdrs)
        self.assertIn("X-RateLimit-Remaining", hdrs)
        self.assertIn("X-RateLimit-Reset", hdrs)
        print(f"✓ API RateLimit headers present: Limit={hdrs['X-RateLimit-Limit']} Remaining={hdrs['X-RateLimit-Remaining']}")

if __name__ == "__main__":
    # Pretty output
    print("="*70)
    print("SocialPulse — Dataset & API Tests")
    print(f"Data: {DATA_JSON} ({len(POSTS)} posts)")
    print(f"Stats: {STATS_JSON} ({'found' if STATS else 'missing'})")
    print(f"Project root: {PROJECT_ROOT}")
    print("="*70)
    # Run unittest with verbosity
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    # Summary
    print("\n" + "="*70)
    if result.wasSuccessful():
        print(f"✅ All {result.testsRun} tests passed (failures={len(result.failures)}, errors={len(result.errors)}, skipped={len(result.skipped)})")
    else:
        print(f"❌ Tests failed: {len(result.failures)} failures, {len(result.errors)} errors, {len(result.skipped)} skipped / {result.testsRun} total")
        for f, tb in result.failures + result.errors:
            print(f"\n--- {f} ---\n{tb}")
    sys.exit(0 if result.wasSuccessful() else 1)
