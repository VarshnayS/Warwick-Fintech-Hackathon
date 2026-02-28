"""
data/speculatorAPI.py
---------------------
Computes cumulative Reddit comment mentions for a prediction market
since it became active, using the Arctic Shift Reddit API.

Also includes Polymarket helpers to fetch EPL markets and compute a
speculation ratio:

    volume_to_mentions_ratio = total_volume_since_start / (total_mentions_since_start + 1)

A high ratio → lots of trading relative to public discussion →
possibly suspicious / speculative activity.
"""

import re
import time
import requests
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ARCTIC = "https://arctic-shift.photon-reddit.com"
REDDIT = "https://www.reddit.com"
GAMMA  = "https://gamma-api.polymarket.com"

REDDIT_HEADERS = {"User-Agent": "warwick-fintech-hackathon/0.1 (contact: demo)"}

# Curated EPL subreddits — hardcoded to avoid "football → nfl/CFB" discovery bug
EPL_SUBREDDITS: List[str] = [
    "PremierLeague",
    "soccer",
    "football",    # UK-centric sub, not American football
    "FantasyPL",
    "Championship",
]

# Stopwords to strip from Polymarket question text when extracting keywords
_STOPWORDS = {
    "will", "win", "the", "on", "in", "at", "a", "an", "and", "or", "vs",
    "end", "draw", "over", "under", "score", "first", "last", "next",
    "this", "that", "be", "is", "are", "was", "fc", "afc", "utd", "united",
    "city", "town", "rovers", "wanderers", "athletic",
}

# Strip ISO dates, times, and non-alpha characters before keyword extraction
_JUNK_RE = re.compile(
    r"\d{4}-\d{2}-\d{2}"  # ISO date e.g. 2026-02-28
    r"|\d{2}:\d{2}"        # time e.g. 19:30
    r"|[^a-z\s]"           # punctuation, digits, symbols
)


# ===========================================================================
# Section 1 – Keyword extraction
# ===========================================================================

def extract_keywords(question: str, max_terms: int = 4) -> List[str]:
    """
    Extract clean, meaningful keywords from a Polymarket question string.

    Steps:
      1. Lowercase and strip ISO dates, times, punctuation via regex.
      2. Split on whitespace.
      3. Drop stopwords and short tokens (≤ 2 chars).
      4. Deduplicate while preserving order.
      5. Return up to max_terms tokens.

    Examples:
      "Will Manchester City FC win on 2026-02-28?"  → ["manchester"]
      "Leeds United FC vs. Manchester City FC: O/U 2.5" → ["leeds", "manchester"]
    """
    text = _JUNK_RE.sub(" ", question.lower())
    seen: Dict[str, bool] = {}
    result: List[str] = []
    for tok in text.split():
        tok = tok.strip()
        if len(tok) <= 2 or tok in _STOPWORDS:
            continue
        if tok not in seen:
            seen[tok] = True
            result.append(tok)
        if len(result) >= max_terms:
            break
    return result


# ===========================================================================
# Section 2 – Reddit / subreddit helpers
# ===========================================================================

def subreddit_search(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Search Reddit for subreddits matching query."""
    r = requests.get(
        f"{REDDIT}/subreddits/search.json",
        params={"q": query, "limit": limit},
        headers=REDDIT_HEADERS,
        timeout=20,
    )
    r.raise_for_status()
    return [c["data"] for c in r.json()["data"]["children"]]


def pick_top_subreddits(
    seed_queries: List[str],
    k: int = 5,
    sport: str = "epl",
) -> List[str]:
    """
    Return k subreddits relevant to sport.

    For EPL: uses the curated EPL_SUBREDDITS list directly (avoids American
    football communities appearing from generic "football" searches).

    For other sports: ranks discovered subreddits by subscriber count.
    """
    if sport.lower() == "epl":
        base = list(EPL_SUBREDDITS[:k])
        if len(base) >= k:
            return base
        # Top up via discovery only if more than 5 are requested
        seen: Dict[str, int] = {sr: 9_999_999 for sr in base}
        for q in seed_queries:
            try:
                for sr in subreddit_search(q, limit=10):
                    name = sr.get("display_name", "")
                    if not name or sr.get("over18"):
                        continue
                    if name not in seen:
                        seen[name] = int(sr.get("subscribers") or 0)
            except Exception:
                pass
        return [n for n, _ in sorted(seen.items(), key=lambda x: x[1], reverse=True)[:k]]

    # Generic path for non-EPL sports
    seen2: Dict[str, int] = {}
    for q in seed_queries:
        try:
            for sr in subreddit_search(q, limit=15):
                name = sr.get("display_name", "")
                if not name or sr.get("over18"):
                    continue
                subs = int(sr.get("subscribers") or 0)
                if name not in seen2 or subs > seen2[name]:
                    seen2[name] = subs
        except Exception:
            pass
    return [n for n, _ in sorted(seen2.items(), key=lambda x: x[1], reverse=True)[:k]]


# ===========================================================================
# Section 3 – Arctic Shift (Reddit comment aggregation)
# ===========================================================================

def iso_date(dt: datetime) -> str:
    """Return UTC date string 'YYYY-MM-DD'."""
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%d")


def _normalize_subreddit(sr: str) -> str:
    """Convert 'r/soccer' → 'soccer'."""
    sr = sr.strip()
    return sr[2:] if sr.lower().startswith("r/") else sr


def _extract_buckets(payload: Any) -> List[Dict[str, Any]]:
    """
    Extract daily bucket list from Arctic Shift aggregate response.
    Handles three possible shapes:
      - raw list of buckets
      - {"buckets": [...]}
      - {"aggregations": {field: {"buckets": [...]}}}
    """
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        if isinstance(payload.get("buckets"), list):
            return payload["buckets"]
        aggs = payload.get("aggregations")
        if isinstance(aggs, dict):
            for inner in aggs.values():
                if isinstance(inner, dict) and isinstance(inner.get("buckets"), list):
                    return inner["buckets"]
    return []


def arctic_aggregate_comments(
    subreddit: str,
    query: str,
    after: str,
    before: str,
    retries: int = 2,
) -> Optional[Any]:
    """
    Call GET /api/comments/search/aggregate on Arctic Shift.
    Returns parsed JSON or None if all attempts fail.
    Uses (3s connect, 8s read) timeouts with exponential back-off.
    """
    params = {
        "aggregate": "created_utc",
        "frequency": "day",
        "subreddit": _normalize_subreddit(subreddit),
        "body": query,
        "after": after,
        "before": before,
    }
    last_err: Optional[Exception] = None
    for attempt in range(retries):
        try:
            r = requests.get(
                f"{ARCTIC}/api/comments/search/aggregate",
                params=params,
                timeout=(3, 8),
            )
            r.raise_for_status()
            return r.json()
        except Exception as exc:
            last_err = exc
            time.sleep(0.4 * (2 ** attempt))  # 0.4s, then 0.8s

    print(f"[WARN] Arctic Shift failed for r/{subreddit} query='{query}': {last_err}")
    return None


def cumulative_mentions_since_start(
    bet_start_time_utc: datetime,
    subreddits: List[str],
    query_terms: List[str],
    time_budget_seconds: float = 30.0,
    verbose: bool = True,
) -> int:
    """
    Total Reddit comments mentioning query_terms across all subreddits
    since bet_start_time_utc. One HTTP request per subreddit.

    Stops early if time_budget_seconds is exhausted.
    """
    after  = iso_date(bet_start_time_utc)
    before = iso_date(datetime.now(timezone.utc))
    query  = " ".join(t.strip() for t in query_terms if t.strip())

    if not query:
        print("[WARN] No query terms supplied – returning 0 mentions.")
        return 0

    if verbose:
        print(f"   [Reddit] query='{query}'  after={after}  before={before}")

    deadline = time.time() + time_budget_seconds
    total    = 0

    for sr in subreddits:
        if time.time() > deadline:
            print("[WARN] Time budget exhausted; skipping remaining subreddits.")
            break

        t0      = time.time()
        payload = arctic_aggregate_comments(sr, query, after, before)
        elapsed = time.time() - t0

        if payload is None:
            if verbose:
                print(f"   [Reddit] r/{sr:<20}  FAILED  ({elapsed:.1f}s)")
            continue

        count  = sum(int(b.get("doc_count", 0)) for b in _extract_buckets(payload))
        total += count

        if verbose:
            print(f"   [Reddit] r/{sr:<20}  {count:>6} mentions  ({elapsed:.1f}s)")

    if verbose:
        print(f"   [Reddit] TOTAL mentions: {total}")

    return total


# ===========================================================================
# Section 4 – Polymarket helpers
# ===========================================================================

@dataclass
class PolymarketMarket:
    id:          str
    question:    str
    volume:      float
    volume_24hr: float
    liquidity:   float
    event_title: str
    raw:         Dict[str, Any] = field(repr=False, default_factory=dict)


def fetch_polymarket_events(
    tag_id:    int  = 82,
    active:    bool = True,
    closed:    bool = False,
    order:     str  = "volume",
    ascending: bool = False,
    limit:     int  = 200,
) -> List[Dict[str, Any]]:
    """Fetch raw event objects from Gamma /events. Returns [] on failure."""
    params = {
        "tag_id":    tag_id,
        "active":    str(active).lower(),
        "closed":    str(closed).lower(),
        "order":     order,
        "ascending": str(ascending).lower(),
        "limit":     limit,
    }
    try:
        r = requests.get(f"{GAMMA}/events", params=params, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as exc:
        print(f"[WARN] Gamma /events failed (tag_id={tag_id}): {exc}")
        return []


def fetch_top_markets(
    tag_id: int  = 82,
    top_n:  int  = 50,
    active: bool = True,
    closed: bool = False,
) -> List[PolymarketMarket]:
    """
    Return top_n markets by volume for the given Polymarket tag_id.
    Flattens all markets across all events, sorts by volume descending.
    """
    markets: List[PolymarketMarket] = []
    for event in fetch_polymarket_events(tag_id=tag_id, active=active, closed=closed):
        title = event.get("title", "")
        for m in event.get("markets", []):
            markets.append(PolymarketMarket(
                id          = m.get("id", ""),
                question    = m.get("question", ""),
                volume      = float(m.get("volume")     or 0),
                volume_24hr = float(m.get("volume24hr") or 0),
                liquidity   = float(m.get("liquidity")  or 0),
                event_title = title,
                raw         = m,
            ))
    markets.sort(key=lambda m: m.volume, reverse=True)
    return markets[:top_n]


def print_top_markets(markets: List[PolymarketMarket]) -> None:
    """Pretty-print a ranked market table."""
    print(f"{'#':<4} {'Volume (USDC)':<18} {'24h Vol':<14} {'Liquidity':<14} Question")
    print("-" * 100)
    for i, m in enumerate(markets, 1):
        print(
            f"{i:<4} ${m.volume:<16,.0f} ${m.volume_24hr:<12,.0f} "
            f"${m.liquidity:<12,.0f} {m.question}"
        )


# ===========================================================================
# Section 5 – Speculation ratio
# ===========================================================================

def speculation_ratio(
    market:              PolymarketMarket,
    bet_start_time_utc:  datetime,
    subreddits:          List[str],
    query_terms:         List[str],
    use_volume:          bool  = True,
    time_budget_seconds: float = 30.0,
) -> Dict[str, Any]:
    """
    Compute: ratio = volume_since_start / (mentions_since_start + 1)

    High ratio → lots of trading vs little public discussion →
    potentially suspicious speculative activity.

    Returns a dict with all intermediate values for transparency.
    """
    mentions = cumulative_mentions_since_start(
        bet_start_time_utc  = bet_start_time_utc,
        subreddits          = subreddits,
        query_terms         = query_terms,
        time_budget_seconds = time_budget_seconds,
    )
    activity = market.volume if use_volume else float(
        market.raw.get("outcomeTokensTradedCount") or market.volume
    )
    return {
        "market_id": market.id,
        "question":  market.question,
        "volume":    market.volume,
        "mentions":  mentions,
        "ratio":     activity / (mentions + 1),
        "label":     "volume_to_mentions" if use_volume else "trades_to_mentions",
    }