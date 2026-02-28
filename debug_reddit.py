"""
debug_reddit.py
---------------
Run this FIRST before main.py to diagnose which Reddit APIs are working
and what response format they return for your date range.

Usage:
    python debug_reddit.py
"""

import requests, json, time
from datetime import datetime, timezone, timedelta

PULLPUSH = "https://api.pullpush.io"
ARCTIC   = "https://arctic-shift.photon-reddit.com"

after_dt  = datetime.now(timezone.utc) - timedelta(days=30)
before_dt = datetime.now(timezone.utc)
after_ts  = int(after_dt.timestamp())
before_ts = int(before_dt.timestamp())
after_str = after_dt.strftime("%Y-%m-%d")
before_str= before_dt.strftime("%Y-%m-%d")

print(f"Date range: {after_str} → {before_str}")
print(f"Timestamps: {after_ts} → {before_ts}\n")

# ============================================================
# Test 1: PullPush with relative '30d' param (recommended)
# ============================================================
print("=" * 60)
print("TEST 1: PullPush – relative after=30d")
try:
    r = requests.get(
        f"{PULLPUSH}/reddit/search/comment/",
        params={"q": "man city", "subreddit": "PremierLeague",
                "after": "30d", "size": 5},
        timeout=(5, 15),
    )
    print(f"  Status: {r.status_code}")
    print(f"  Headers: {dict(r.headers)}")
    print(f"  Body: {r.text[:500]}")
except Exception as e:
    print(f"  ERROR: {e}")

time.sleep(3)

# ============================================================
# Test 2: PullPush with unix timestamp param
# ============================================================
print("\n" + "=" * 60)
print("TEST 2: PullPush – unix timestamp after/before")
try:
    r = requests.get(
        f"{PULLPUSH}/reddit/search/comment/",
        params={"q": "man city", "subreddit": "PremierLeague",
                "after": after_ts, "before": before_ts, "size": 5},
        timeout=(5, 15),
    )
    print(f"  Status: {r.status_code}")
    print(f"  Body: {r.text[:500]}")
except Exception as e:
    print(f"  ERROR: {e}")

time.sleep(3)

# ============================================================
# Test 3: PullPush WITHOUT subreddit filter (site-wide)
# ============================================================
print("\n" + "=" * 60)
print("TEST 3: PullPush – no subreddit, just keyword")
try:
    r = requests.get(
        f"{PULLPUSH}/reddit/search/comment/",
        params={"q": "manchester city", "after": "30d", "size": 5},
        timeout=(5, 15),
    )
    print(f"  Status: {r.status_code}")
    print(f"  Body: {r.text[:500]}")
except Exception as e:
    print(f"  ERROR: {e}")

time.sleep(3)

# ============================================================
# Test 4: Arctic Shift – PremierLeague subreddit
# ============================================================
print("\n" + "=" * 60)
print("TEST 4: Arctic Shift – PremierLeague / man city")
try:
    r = requests.get(
        f"{ARCTIC}/api/comments/search/aggregate",
        params={"aggregate": "created_utc", "frequency": "day",
                "subreddit": "PremierLeague", "body": "man city",
                "after": after_str, "before": before_str},
        timeout=(5, 15),
    )
    print(f"  Status: {r.status_code}")
    print(f"  Body: {r.text[:500]}")
except Exception as e:
    print(f"  ERROR: {e}")

time.sleep(3)

# ============================================================
# Test 5: Arctic Shift – broader date range (2025)
# ============================================================
print("\n" + "=" * 60)
print("TEST 5: Arctic Shift – broader 2025 date range")
try:
    r = requests.get(
        f"{ARCTIC}/api/comments/search/aggregate",
        params={"aggregate": "created_utc", "frequency": "day",
                "subreddit": "PremierLeague", "body": "man city",
                "after": "2025-01-01", "before": "2025-12-31"},
        timeout=(5, 15),
    )
    print(f"  Status: {r.status_code}")
    print(f"  Body: {r.text[:800]}")
except Exception as e:
    print(f"  ERROR: {e}")

time.sleep(3)

# ============================================================
# Test 6: Arctic Shift – check what their latest date is
# ============================================================
print("\n" + "=" * 60)
print("TEST 6: Arctic Shift – no date filter (get latest data available)")
try:
    r = requests.get(
        f"{ARCTIC}/api/comments/search",
        params={"subreddit": "PremierLeague", "body": "man city",
                "limit": 3, "sort": "desc"},
        timeout=(5, 15),
    )
    print(f"  Status: {r.status_code}")
    data = r.json()
    for item in data.get("data", [])[:3]:
        ts = item.get("created_utc", 0)
        print(f"  → created_utc={ts}  date={datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d')}  body={item.get('body','')[:60]}")
except Exception as e:
    print(f"  ERROR: {e}")

print("\n\nDone. Paste the output above so we can see what's working.")