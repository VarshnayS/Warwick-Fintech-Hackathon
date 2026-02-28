"""
main.py
-------
Entry point. Fetches top EPL Polymarket markets, computes Reddit mention
counts since market launch, and ranks them by speculation ratio.
"""

from datetime import datetime, timezone, timedelta

from data.speculatorAPI import (
    EPL_SUBREDDITS,
    PolymarketMarket,
    extract_keywords,
    fetch_top_markets,
    pick_top_subreddits,
    print_top_markets,
    speculation_ratio,
)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

TAG_ID        = 82          # Polymarket EPL tag
TOP_N_MARKETS = 10
LOOKBACK_DAYS = 30          # treat market as "active since" N days ago
TIME_BUDGET   = 30.0        # seconds per market for Reddit calls

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("1. Fetching top EPL markets from Polymarket …")
    markets = fetch_top_markets(tag_id=TAG_ID, top_n=TOP_N_MARKETS)
    print_top_markets(markets)

    if not markets:
        print("[ERROR] No markets returned – check Polymarket tag_id or network.")
        raise SystemExit(1)

    print("\n2. Computing speculation ratios for all markets …\n")

    # Curated EPL subreddits – avoids the "football → nfl/CFB" problem
    subreddits = pick_top_subreddits(
        seed_queries=["premier league", "epl"],
        k=5,
        sport="epl",
    )
    print(f"   Subreddits: {subreddits}\n")

    bet_start = datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)

    results = []
    for market in markets:
        # Proper keyword extraction: strips dates, punctuation, FC boilerplate
        query_terms = extract_keywords(market.question, max_terms=4)
        print(f"── '{market.question}'")
        print(f"   keywords: {query_terms}")

        result = speculation_ratio(
            market             = market,
            bet_start_time_utc = bet_start,
            subreddits         = subreddits,
            query_terms        = query_terms,
            time_budget_seconds= TIME_BUDGET,
        )
        results.append(result)
        print()

    # ---------------------------------------------------------------------------
    # Summary table sorted by ratio (highest = most suspicious)
    # ---------------------------------------------------------------------------
    print("\n3. Speculation ratio summary  (high ratio = lots of trading vs public discussion)")
    print(f"{'#':<4} {'Ratio':>12}  {'Volume':>12}  {'Mentions':>9}  Question")
    print("-" * 95)
    for i, r in enumerate(
        sorted(results, key=lambda x: x["ratio"], reverse=True), 1
    ):
        flag = "  ⚠️ " if r["ratio"] > 500_000 else "     "
        print(
            f"{i:<4} {r['ratio']:>12,.0f}{flag}"
            f"${r['volume']:>12,.0f}  {r['mentions']:>9}  {r['question']}"
        )