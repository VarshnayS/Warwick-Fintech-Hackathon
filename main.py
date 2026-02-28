"""
main.py
-------
Fetches top EPL Polymarket markets, enriches with live trade data,
counts Reddit mentions, ranks by speculation ratio.
"""

import inspect
import requests
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
TAG_ID        = 82
TOP_N_MARKETS = 10
LOOKBACK_DAYS = 30
TIME_BUDGET   = 120.0   # seconds per market (PullPush is slow, needs headroom)

# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ == "__main__":

    # -----------------------------------------------------------------------
    # Step 1: Fetch markets
    # -----------------------------------------------------------------------
    print("=" * 60)
    print("1. Fetching top EPL markets from Polymarket …")
    markets = fetch_top_markets(tag_id=TAG_ID, top_n=TOP_N_MARKETS)
    print_top_markets(markets)

    if not markets:
        raise SystemExit("[ERROR] No markets returned.")

    # -----------------------------------------------------------------------
    # Step 2: Enrich with Bet trade data
    # -----------------------------------------------------------------------
    print("\n2. Enriching with live trade data …")
    try:
        from data.bet import Bet
        sig    = inspect.signature(Bet.__init__)
        params = [p for p in sig.parameters if p != "self"]

        for market in markets:
            try:
                if len(params) == 1:
                    # Old signature: Bet(id)
                    b = Bet(market.id)
                else:
                    # New signature: Bet(id, tradehistory) — pre-fetch trades
                    resp = requests.get(
                        "https://data-api.polymarket.com/trades",
                        params={"market": market.id, "limit": 1000},
                        timeout=15,
                    )
                    resp.raise_for_status()
                    b = Bet(market.id, resp.json())

                market.trades_4w = getattr(b, "total_trades_4w", 0)
                print(f"   ✓ trades_4w={market.trades_4w:<6}  {market.question[:60]}")

            except Exception as e:
                print(f"   ✗ {market.question[:60]}  [{e}]")

    except ImportError:
        print("   [SKIP] data.bet not importable")

    # -----------------------------------------------------------------------
    # Step 3: Speculation ratios
    # -----------------------------------------------------------------------
    print("\n3. Computing speculation ratios …\n")

    subreddits = pick_top_subreddits(["premier league", "epl"], k=3, sport="epl")
    print(f"   Subreddits: {subreddits}\n")

    bet_start = datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)
    results   = []

    for market in markets:
        print(f"── '{market.question}'")
        result = speculation_ratio(
            market              = market,
            bet_start_time_utc  = bet_start,
            subreddits          = subreddits,
            time_budget_seconds = TIME_BUDGET,
        )
        results.append(result)
        print()

    # -----------------------------------------------------------------------
    # Step 4: Summary table
    # -----------------------------------------------------------------------
    print("\n4. Ranked by speculation ratio")
    print(f"{'#':<4} {'Ratio':>12}  {'Activity':>12}  {'Mentions':>9}  Question")
    print("-" * 95)
    for i, r in enumerate(sorted(results, key=lambda x: x["ratio"], reverse=True), 1):
        activity = r["trades_4w"] if r["trades_4w"] > 0 else r["volume"]
        flag = "  ⚠️ " if r["mentions"] == 0 else "     "
        print(
            f"{i:<4} {r['ratio']:>12,.1f}{flag}"
            f"{activity:>12,.0f}  {r['mentions']:>9}  {r['question']}"
        )