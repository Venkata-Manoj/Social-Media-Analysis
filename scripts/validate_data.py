#!/usr/bin/env python3
"""
SocialPulse — CSV/JSON Parity Validator
Checks that data/social_media_dataset.json and .csv are in sync,
and that embedded RAW_DATA in index.html matches the JSON file.

Usage:
  python3 scripts/validate_data.py
  python3 scripts/validate_data.py --verbose
  python3 scripts/validate_data.py --fix   # not implemented — report only

Exit 0 if parity holds, 1 if mismatch.
"""

import csv
import hashlib
import json
import pathlib
import re
import sys

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA_JSON = PROJECT_ROOT / "data" / "social_media_dataset.json"
DATA_CSV = PROJECT_ROOT / "data" / "social_media_dataset.csv"
STATS_JSON = PROJECT_ROOT / "data" / "dataset_stats.json"
INDEX_HTML = PROJECT_ROOT / "index.html"

VERBOSE = "--verbose" in sys.argv or "-v" in sys.argv


def log(msg):
    print(msg)


def verbose(msg):
    if VERBOSE:
        print("  " + msg)


def load_json():
    try:
        data = json.loads(DATA_JSON.read_text(encoding="utf-8"))
        log(f"✓ JSON: {DATA_JSON} -> {len(data)} posts, {DATA_JSON.stat().st_size} bytes")
        return data
    except Exception as e:
        log(f"✗ JSON load failed: {e}")
        return None


def load_csv():
    try:
        with open(DATA_CSV, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            log(f"✓ CSV: {DATA_CSV} -> {len(rows)} rows, {DATA_CSV.stat().st_size} bytes, fields={reader.fieldnames}")
            # Check fieldnames
            expected = [
                "post_id",
                "platform",
                "timestamp",
                "date",
                "hour",
                "text",
                "likes",
                "shares",
                "comments",
                "views",
                "engagement",
                "engagement_rate",
                "sentiment_label",
                "sentiment_score",
                "hashtags",
                "hashtags_str",
                "topic",
                "user_type",
                "verified",
                "language",
            ]
            # CSV hashtags is string with ", " join, not array, but header same
            missing = [fn for fn in expected if fn not in reader.fieldnames]
            if missing:
                log(f"  ✗ CSV missing fields: {missing}")
            return rows, reader.fieldnames
    except Exception as e:
        log(f"✗ CSV load failed: {e}")
        return None, None


def check_parity(json_data, csv_rows):
    errors = 0
    # Count
    if len(json_data) != len(csv_rows):
        log(f"✗ COUNT MISMATCH: JSON {len(json_data)} vs CSV {len(csv_rows)}")
        errors += 1
    else:
        log(f"✓ Count parity: both {len(json_data)}")

    # Check IDs order
    j_ids = [r["post_id"] for r in json_data]
    c_ids = [r["post_id"] for r in csv_rows]
    if j_ids != c_ids:
        log(f"✗ ID ORDER MISMATCH: first JSON {j_ids[:3]} vs CSV {c_ids[:3]}")
        # Find diff
        for i, (j, c) in enumerate(zip(j_ids, c_ids)):
            if j != c:
                log(f"  first diff at index {i}: JSON {j} vs CSV {c}")
                break
        errors += 1
    else:
        log(f"✓ ID order parity: P0001..P{len(json_data):04d} matches")

    # Sample field parity (first, middle, last)
    for idx in [0, len(json_data) // 2, len(json_data) - 1]:
        j = json_data[idx]
        c = csv_rows[idx]
        for field in ["platform", "timestamp", "date", "topic", "sentiment_label"]:
            if str(j[field]) != str(c[field]):
                log(f"✗ FIELD MISMATCH idx {idx} {j['post_id']} {field}: JSON {j[field]!r} vs CSV {c[field]!r}")
                errors += 1
        # engagement numeric
        for num_field in ["likes", "shares", "comments", "views", "engagement", "hour"]:
            if int(c[num_field]) != int(j[num_field]):
                log(f"✗ NUMERIC MISMATCH idx {idx} {num_field}: JSON {j[num_field]} vs CSV {c[num_field]}")
                errors += 1
        # hashtag check: JSON array vs CSV string ", ".join
        j_tags = ", ".join(j["hashtags"])
        if j_tags != c["hashtags"]:
            log(f"✗ HASHTAG MISMATCH idx {idx} {j['post_id']}: JSON {j_tags!r} vs CSV {c['hashtags']!r}")
            errors += 1
        verbose(f"sample idx {idx} {j['post_id']} parity ok")

    # Full engagement math check via CSV too
    for i, (j, c) in enumerate(zip(json_data, csv_rows)):
        if int(c["engagement"]) != int(j["engagement"]):
            log(f"✗ engagement mismatch at {i} {j['post_id']}")
            errors += 1
            if errors > 5:
                break
    if errors == 0:
        log(f"✓ Full field parity sample ok (checked {len(json_data)} rows engagement etc.)")
    return errors


def check_stats(json_data):
    errors = 0
    if not STATS_JSON.exists():
        log(f"⚠ stats missing: {STATS_JSON}")
        return 0
    stats = json.loads(STATS_JSON.read_text(encoding="utf-8"))
    log(
        f"✓ Stats: {STATS_JSON} -> total_posts {stats.get('total_posts')}, total_engagement {stats.get('total_engagement')}"
    )
    from collections import Counter

    # recompute
    total = len(json_data)
    if stats.get("total_posts") != total:
        log(f"✗ stats total_posts {stats.get('total_posts')} != {total}")
        errors += 1
    total_eng = sum(r["engagement"] for r in json_data)
    if stats.get("total_engagement") != total_eng:
        log(f"✗ stats total_engagement {stats.get('total_engagement')} != {total_eng}")
        errors += 1
    # platform dist
    plat = Counter(r["platform"] for r in json_data)
    if dict(plat) != stats.get("platform_dist"):
        log(f"✗ platform_dist mismatch: {dict(plat)} vs {stats.get('platform_dist')}")
        errors += 1
    else:
        verbose(f"platform_dist ok {dict(plat)}")
    # sentiment
    sent = Counter(r["sentiment_label"] for r in json_data)
    if dict(sent) != stats.get("sentiment_dist"):
        log("✗ sentiment_dist mismatch")
        errors += 1
    else:
        verbose(f"sentiment_dist ok {dict(sent)}")
    if errors == 0:
        log("✓ stats parity ok")
    return errors


def check_index_html_embedded(json_data):
    errors = 0
    if not INDEX_HTML.exists():
        log(f"⚠ index.html missing at {INDEX_HTML}")
        return 0
    text = INDEX_HTML.read_text(encoding="utf-8")
    # Find RAW_DATA = [...] embedded
    # The file has const RAW_DATA = [{...}, ...];
    # Use regex to extract JSON array length via counting post_id occurrences
    count_embedded = text.count('"post_id"')
    # Should be 420*? Actually RAW_DATA + maybe other post_id in template? But we can count RAWDATA block
    # Try to extract via regex: const RAW_DATA = (\[.*?\]);  with DOTALL lazy, but file is large (321KB)
    m = re.search(r"const RAW_DATA\s*=\s*(\[.*?\]);", text, re.DOTALL)
    if m:
        try:
            embedded = json.loads(m.group(1))
            log(f"✓ index.html embedded RAW_DATA: {len(embedded)} posts (counted via JSON parse)")
            if len(embedded) != len(json_data):
                log(f"✗ embedded count {len(embedded)} != JSON {len(json_data)}")
                errors += 1
            else:
                # Check first and last post_id
                if embedded[0]["post_id"] != json_data[0]["post_id"]:
                    log(f"✗ embedded first post_id {embedded[0]['post_id']} != JSON {json_data[0]['post_id']}")
                    errors += 1
                if embedded[-1]["post_id"] != json_data[-1]["post_id"]:
                    log("✗ embedded last post_id mismatch")
                    errors += 1
                else:
                    log(
                        f"✓ index.html embedded parity: first {embedded[0]['post_id']}, last {embedded[-1]['post_id']} match JSON"
                    )
                # Check one field engagement
                for idx in [0, 100, 419]:
                    if embedded[idx]["engagement"] != json_data[idx]["engagement"]:
                        log(f"✗ embedded engagement mismatch idx {idx}")
                        errors += 1
        except Exception as e:
            log(f"⚠ could not parse embedded RAW_DATA JSON: {e} — falling back to string count")
            # fallback to string count check
            if count_embedded != len(json_data):
                # Might have duplicates due to template? Just warn
                log(
                    f"⚠ string count post_id occurrences {count_embedded} vs {len(json_data)} (template may have extra)"
                )
            else:
                log(f"✓ string count parity {count_embedded}")
    else:
        log(f"⚠ could not find const RAW_DATA = [...] in index.html, counted string occurrences: {count_embedded}")
        if count_embedded < 420:
            log(f"✗ embedded post_id count {count_embedded} < 420")
            errors += 1
    # Check that service worker registration exists and is file:// graceful
    if "serviceWorker" in text:
        log("✓ index.html has serviceWorker registration (PWA)")
        if "file://" in text or "protocol" in text:
            log("✓ file:// grace present in SW registration")
        else:
            log("⚠ SW registration may not handle file:// gracefully")
    else:
        log("⚠ index.html missing serviceWorker registration (expected after PWA enhancement)")
    # Check manifest link
    if "site.webmanifest" in text:
        log("✓ manifest link present (site.webmanifest)")
    else:
        log("⚠ manifest link missing")
    return errors


def check_hashes():
    # Optional: show hashes for reproducibility
    for p in [DATA_JSON, DATA_CSV]:
        if p.exists():
            h = hashlib.md5(p.read_bytes()).hexdigest()
            log(f"  hash {p.name}: md5 {h} size {p.stat().st_size}")
    return 0


def main():
    print("=" * 70)
    print("SocialPulse — CSV/JSON Parity Validator")
    print(f"Root: {PROJECT_ROOT}")
    print(f"JSON: {DATA_JSON}")
    print(f"CSV:  {DATA_CSV}")
    print(f"Stats:{STATS_JSON}")
    print(f"Index:{INDEX_HTML}")
    print("=" * 70)
    json_data = load_json()
    if json_data is None:
        sys.exit(1)
    csv_rows, fields = load_csv()
    if csv_rows is None:
        sys.exit(1)

    errors = 0
    errors += check_parity(json_data, csv_rows)
    errors += check_stats(json_data)
    errors += check_index_html_embedded(json_data)
    check_hashes()

    print("=" * 70)
    if errors == 0:
        print("✅ All parity checks passed (0 errors)")
        sys.exit(0)
    else:
        print(f"❌ Parity checks failed: {errors} error(s)")
        sys.exit(1)


if __name__ == "__main__":
    main()
