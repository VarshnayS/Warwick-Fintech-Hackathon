"""
data/speculatorAPI.py
---------------------
Computes cumulative Reddit comment mentions for a prediction market
since it became active.

API strategy:
  1. PullPush.io  /reddit/search/comment/  (primary — has 2025/2026 live data)
     NOTE: total_results is NOT in PullPush metadata, so we paginate and count
     actual returned docs instead.
  2. Arctic Shift /api/comments/search/aggregate  (fallback — archive)

Speculation ratio:
    trades_to_mentions = total_trades_4w / (total_mentions + 1)
"""

import re
import time
import requests
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# API URLs
# ---------------------------------------------------------------------------
PULLPUSH = "https://api.pullpush.io"
ARCTIC   = "https://arctic-shift.photon-reddit.com"
REDDIT   = "https://www.reddit.com"
GAMMA    = "https://gamma-api.polymarket.com"

REDDIT_HEADERS = {"User-Agent": "warwick-fintech-hackathon/0.1 (contact: demo)"}

# PullPush rate limits: soft 15 req/min, hard 30 req/min, 1000 req/hr
PULLPUSH_DELAY = 2.5   # seconds between requests to stay under soft limit

# ---------------------------------------------------------------------------
# Curated EPL subreddits — hardcoded to avoid "football → nfl/CFB" problem
# ---------------------------------------------------------------------------
EPL_SUBREDDITS: List[str] = [
    "PremierLeague",
    "FantasyPL",
    "soccer",
]

# ---------------------------------------------------------------------------
# Team aliases — critical fix for 0-result problem.
# Reddit users write "man city"/"mcfc", never "manchester" alone.
# Keys are lowercased substrings that appear in Polymarket question text.
# ---------------------------------------------------------------------------
TEAM_ALIASES: Dict[str, List[str]] = {
    "manchester city":   ["man city", "mcfc"],
    "manchester united": ["man utd", "mufc"],
    "arsenal":           ["arsenal", "gunners"],
    "liverpool":         ["liverpool", "lfc"],
    "chelsea":           ["chelsea", "cfc"],
    "tottenham":         ["spurs", "tottenham"],
    "newcastle":         ["newcastle", "nufc", "toon"],
    "west ham":          ["west ham", "hammers"],
    "brentford":         ["brentford"],
    "leeds":             ["leeds", "lufc"],
    "burnley":           ["burnley", "clarets"],
    "everton":           ["everton", "toffees"],
    "aston villa":       ["aston villa", "villa"],
    "brighton":          ["brighton", "bhafc"],
    "fulham":            ["fulham"],
    "wolves":            ["wolves", "wwfc"],
    "crystal palace":    ["crystal palace", "cpfc"],
    "nottingham":        ["forest", "nffc"],
    "bournemouth":       ["bournemouth", "afcb"],
    "ipswich":           ["ipswich"],
    "leicester":         ["leicester", "foxes"],
    "southampton":       ["southampton", "saints"],
}

_STOPWORDS = {
    "will", "win", "the", "on", "in", "at", "a", "an", "and", "or", "vs",
    "end", "draw", "over", "under", "score", "first", "last", "next",
    "this", "that", "be", "is", "are", "was", "fc", "afc", "utd",
    "town", "rovers", "wanderers",
}

_JUNK_RE = re.compile(
    r"\d{4}-\d{2}-\d{2}"  # ISO date
    r"|\d{2}:\d{2}"        # time
    r"|[^a-z\s]"           # punctuation / digits
)


# ===========================================================================
# Section 1 – Keyword extraction + alias expansion
# ===========================================================================

def extract_keywords(question: str, max_terms: int = 6) -> List[str]:
    """
    Extract meaningful tokens from a Polymarket question.
    Does NOT strip 'united', 'city', 'west', 'ham' — these are needed
    for alias matching. Stopword list is intentionally minimal here.

    "Will Manchester City FC win on 2026-02-28?" → ["manchester", "city"]
    "Leeds United FC vs. Manchester City FC"     → ["leeds", "united", "manchester", "city"]
    """
    text = _JUNK_RE.sub(" ", question.lower())
    seen: Dict[str, bool] = {}
    result: List[str] = []
    for tok in text.split():
        tok = tok.strip()
        if len(tok) <= 1 or tok in _STOPWORDS:
            continue
        if tok not in seen:
            seen[tok] = True
            result.append(tok)
        if len(result) >= max_terms:
            break
    return result

def _find_team_in_question(question_lower: str) -> Optional[str]:
    """
    Find the best matching team key from TEAM_ALIASES in a question string.
    Tries multi-word keys first (longer matches win).
    Returns the team key or None.
    """
    # Sort by key length descending so "manchester city" matches before "manchester"
    for team in sorted(TEAM_ALIASES.keys(), key=len, reverse=True):
        if team in question_lower:
            return team
    return None


def build_search_queries(question: str, keywords: List[str]) -> List[str]:
    """
    Given the full question and extracted keywords, return the best
    Reddit search terms using team aliases.

    Matches against the FULL question (not just extracted keywords)
    to avoid partial-match bugs like "west" → tottenham.

    "Will Manchester City FC win?"  → ["man city", "mcfc"]
    "West Ham United FC"            → ["west ham", "hammers"]
    "Leeds United FC vs Man City"   → ["leeds", "lufc"]  (first team found)
    """
    q_lower = question.lower()

    # Find all teams mentioned in the question
    found_aliases: List[str] = []
    seen_teams: set = set()
    for team in sorted(TEAM_ALIASES.keys(), key=len, reverse=True):
        if team in q_lower and team not in seen_teams:
            seen_teams.add(team)
            found_aliases.extend(TEAM_ALIASES[team][:2])  # max 2 aliases per team
        if len(found_aliases) >= 4:
            break

    if found_aliases:
        return found_aliases

    # Fallback: use raw keywords if no team matched
    return [k for k in keywords if len(k) > 3][:3]


# ===========================================================================
# Section 2 – PullPush.io (primary, has 2025/2026 data)
# ===========================================================================

def pullpush_count_term(
    subreddit: str,
    query:     str,
    after_ts:  int,
    before_ts: int,
    max_pages: int = 3,
    page_size: int = 100,
) -> int:
    """
    Count comments matching query in subreddit between after_ts and before_ts.

    PullPush does NOT return total_results in metadata (confirmed broken).
    Instead we paginate through actual results and count them.
    Uses /reddit/search/comment/ endpoint (note trailing slash).

    max_pages=3 × page_size=100 = up to 300 comments counted per term.
    For a 30-day window this is a reasonable upper bound for niche queries.
    """
    url    = f"{PULLPUSH}/reddit/search/comment/"
    total  = 0
    before = before_ts  # paginate backwards using 'before' cursor

    for page in range(max_pages):
        params = {
            "subreddit": subreddit,
            "q":         query,
            "after":     after_ts,
            "before":    before,
            "size":      page_size,
            "sort":      "desc",
            "sort_type": "created_utc",
        }
        try:
            time.sleep(PULLPUSH_DELAY)
            r = requests.get(url, params=params, timeout=(5, 15))
            if r.status_code == 429:
                time.sleep(10)
                continue
            r.raise_for_status()
            data = r.json().get("data", [])
        except Exception as exc:
            break

        if not data:
            break

        total  += len(data)
        # Move cursor back to oldest item in this page for next iteration
        oldest  = min(int(d.get("created_utc", before)) for d in data)
        before  = oldest - 1

        if len(data) < page_size:
            break  # last page

    return total


def pullpush_total(
    subreddit:    str,
    search_terms: List[str],
    after_ts:     int,
    before_ts:    int,
    verbose:      bool = False,
) -> int:
    """Sum PullPush counts across all search terms."""
    total = 0
    for term in search_terms:
        count = pullpush_count_term(subreddit, term, after_ts, before_ts)
        if verbose:
            print(f"      [PullPush] '{term}' → {count}")
        total += count
    return total


# ===========================================================================
# Section 3 – Arctic Shift (fallback, archive data)
# ===========================================================================

def iso_date(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%d")


def _normalize_subreddit(sr: str) -> str:
    sr = sr.strip()
    return sr[2:] if sr.lower().startswith("r/") else sr


def _extract_buckets(payload: Any) -> List[Dict[str, Any]]:
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
    query:     str,
    after:     str,
    before:    str,
    retries:   int = 2,
) -> Optional[Any]:
    params = {
        "aggregate": "created_utc",
        "frequency": "day",
        "subreddit":  _normalize_subreddit(subreddit),
        "body":       query,
        "after":      after,
        "before":     before,
    }
    for attempt in range(retries):
        try:
            r = requests.get(
                f"{ARCTIC}/api/comments/search/aggregate",
                params=params, timeout=(3, 8),
            )
            if r.status_code in (422, 400):
                return None  # not indexed — don't retry
            r.raise_for_status()
            return r.json()
        except Exception:
            time.sleep(0.4 * (2 ** attempt))
    return None


def arctic_total(
    subreddit:    str,
    search_terms: List[str],
    after:        str,
    before:       str,
) -> int:
    total = 0
    for term in search_terms:
        payload = arctic_aggregate_comments(subreddit, term, after, before)
        if payload is None:
            continue
        total += sum(int(b.get("doc_count", 0)) for b in _extract_buckets(payload))
    return total


# ===========================================================================
# Section 4 – Combined mention counter
# ===========================================================================

def cumulative_mentions_since_start(
    bet_start_time_utc:  datetime,
    subreddits:          List[str],
    question:            str,
    query_terms:         Optional[List[str]] = None,
    time_budget_seconds: float = 60.0,
    verbose:             bool  = True,
) -> int:
    """
    Count Reddit comments mentioning the market's team(s) across subreddits
    since bet_start_time_utc.

    Pass the full `question` string for accurate alias matching.
    `query_terms` are base keywords; aliases are expanded automatically.

    Uses PullPush (primary) then Arctic Shift (fallback).
    """
    after_dt  = bet_start_time_utc.astimezone(timezone.utc)
    before_dt = datetime.now(timezone.utc)
    after_ts  = int(after_dt.timestamp())
    before_ts = int(before_dt.timestamp())
    after_str = iso_date(after_dt)
    before_str= iso_date(before_dt)

    kw = query_terms or extract_keywords(question)
    search_terms = build_search_queries(question, kw)

    if not search_terms:
        print("[WARN] No search terms found – returning 0.")
        return 0

    if verbose:
        print(f"   [Reddit] search_terms={search_terms}")
        print(f"            after={after_str}  before={before_str}")

    deadline = time.time() + time_budget_seconds
    total    = 0

    for sr in subreddits:
        if time.time() > deadline:
            print(f"[WARN] Time budget exhausted after r/{sr}.")
            break

        t0 = time.time()

        # Try PullPush first
        count = pullpush_total(sr, search_terms, after_ts, before_ts, verbose=verbose)

        # Arctic Shift fallback only if PullPush gave 0
        if count == 0:
            count = arctic_total(sr, search_terms, after_str, before_str)

        elapsed = time.time() - t0
        total  += count

        if verbose:
            print(f"   [Reddit] r/{sr:<22}  {count:>6} mentions  ({elapsed:.1f}s)")

    if verbose:
        print(f"   [Reddit] TOTAL mentions: {total}")

    return total


# ===========================================================================
# Section 5 – Reddit subreddit helpers
# ===========================================================================

def subreddit_search(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    r = requests.get(
        f"{REDDIT}/subreddits/search.json",
        params={"q": query, "limit": limit},
        headers=REDDIT_HEADERS, timeout=20,
    )
    r.raise_for_status()
    return [c["data"] for c in r.json()["data"]["children"]]


def pick_top_subreddits(
    seed_queries: List[str],
    k: int = 3,
    sport: str = "epl",
) -> List[str]:
    if sport.lower() == "epl":
        return list(EPL_SUBREDDITS[:k])
    seen: Dict[str, int] = {}
    for q in seed_queries:
        try:
            for sr in subreddit_search(q, limit=15):
                name = sr.get("display_name", "")
                if not name or sr.get("over18"):
                    continue
                subs = int(sr.get("subscribers") or 0)
                if name not in seen or subs > seen[name]:
                    seen[name] = subs
        except Exception:
            pass
    return [n for n, _ in sorted(seen.items(), key=lambda x: x[1], reverse=True)[:k]]


# ===========================================================================
# Section 6 – Polymarket data structures
# ===========================================================================

@dataclass
class PolymarketMarket:
    id:          str
    question:    str
    volume:      float
    volume_24hr: float
    liquidity:   float
    event_title: str
    trades_4w:   int = 0   # populated from data.bet.Bet.total_trades_4w
    raw:         Dict[str, Any] = field(repr=False, default_factory=dict)


def fetch_polymarket_events(
    tag_id: int  = 82,
    active: bool = True,
    closed: bool = False,
    order:  str  = "volume",
    ascending: bool = False,
    limit:  int  = 200,
) -> List[Dict[str, Any]]:
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
    print(f"{'#':<4} {'Volume (USDC)':<18} {'24h Vol':<14} {'Liquidity':<14} Question")
    print("-" * 100)
    for i, m in enumerate(markets, 1):
        print(
            f"{i:<4} ${m.volume:<16,.0f} ${m.volume_24hr:<12,.0f} "
            f"${m.liquidity:<12,.0f} {m.question}"
        )


# ===========================================================================
# Section 7 – Speculation ratio
# ===========================================================================

def speculation_ratio(
    market:              PolymarketMarket,
    bet_start_time_utc:  datetime,
    subreddits:          List[str],
    time_budget_seconds: float = 60.0,
) -> Dict[str, Any]:
    """
    ratio = trades_4w / (mentions + 1)

    Uses trades_4w from Bet class if available, otherwise USDC volume.
    High ratio = lots of trading relative to Reddit discussion = suspicious.
    """
    kw = extract_keywords(market.question)
    mentions = cumulative_mentions_since_start(
        bet_start_time_utc  = bet_start_time_utc,
        subreddits          = subreddits,
        question            = market.question,
        query_terms         = kw,
        time_budget_seconds = time_budget_seconds,
    )

    if market.trades_4w > 0:
        activity = float(market.trades_4w)
        label    = "trades_to_mentions"
    else:
        activity = market.volume
        label    = "volume_to_mentions"

    return {
        "market_id": market.id,
        "question":  market.question,
        "volume":    market.volume,
        "trades_4w": market.trades_4w,
        "mentions":  mentions,
        "ratio":     activity / (mentions + 1),
        "label":     label,
    }