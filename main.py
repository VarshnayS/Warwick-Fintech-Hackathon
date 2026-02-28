"""
main.py
-------
Fetches top EPL Polymarket markets, enriches with live trade data
from the Bet class, counts Reddit mentions, ranks by speculation ratio.
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
TAG_ID        = 82    # Polymarket EPL tag ID
TOP_N_MARKETS = 10
LOOKBACK_DAYS = 30
TIME_BUDGET   = 60.0  # seconds of Reddit API time per market

# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("1. Fetching top EPL markets from Polymarket …")
    markets = fetch_top_markets(tag_id=TAG_ID, top_n=TOP_N_MARKETS)
    print_top_markets(markets)

    if not markets:
        print("[ERROR] No markets returned.")
        raise SystemExit(1)

    # -----------------------------------------------------------------------
    # Enrich with live trade data from the Bet class.
    # The Bet constructor signature changed — inspect it and call correctly.
    # -----------------------------------------------------------------------
    print("\n2. Enriching markets with live trade data (Bet class) …")
    try:
        from data.bet import Bet
        import inspect
        bet_params = list(inspect.signature(Bet.__init__).parameters.keys())
        # Remove 'self'; remaining are the required args
        bet_params.remove("self")
        print(f"   Bet.__init__ params: {bet_params}")

        for market in markets:
            try:
                # Support both old Bet(id) and new Bet(id, tradehistory) signatures
                if len(bet_params) == 1:
                    b = Bet(market.id)
                elif len(bet_params) >= 2:
                    # Second param is tradehistory — fetch trades first
                    trade_resp = __import__("requests").get(
                        "https://data-api.polymarket.com/trades",
                        params={"market": market.id, "limit": 1000},
                        timeout=15,
                    )
                    trade_resp.raise_for_status()
                    tradehistory = trade_resp.json()
                    b = Bet(market.id, tradehistory)
                else:
                    b = Bet(market.id)

                market.trades_4w = getattr(b, "total_trades_4w", 0)
                print(f"   ✓ {market.question[:55]:<55}  trades_4w={market.trades_4w}")

            except Exception as e:
                print(f"   ✗ {market.question[:55]:<55}  [{e}]")

    except ImportError:
        print("   [WARN] data.bet not found — skipping trade enrichment.")

    # -----------------------------------------------------------------------
    # Compute Reddit mentions + speculation ratio for each market
    # -----------------------------------------------------------------------
    print("\n3. Computing speculation ratios …\n")

    subreddits = pick_top_subreddits(["premier league", "epl"], k=3, sport="epl")
    print(f"   Subreddits: {subreddits}\n")

    bet_start = datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)
    results   = []

    for market in markets:
        kw = extract_keywords(market.question)
        print(f"── '{market.question}'")
        print(f"   base keywords: {kw}")

        result = speculation_ratio(
            market              = market,
            bet_start_time_utc  = bet_start,
            subreddits          = subreddits,
            time_budget_seconds = TIME_BUDGET,
        )
        results.append(result)
        print()

    # -----------------------------------------------------------------------
    # Summary table
    # -----------------------------------------------------------------------
    print("\n4. Ranked by speculation ratio  (⚠️  = high activity vs low discussion)")
    print(f"{'#':<4} {'Ratio':>12}  {'Activity':>12}  {'Mentions':>9}  Question")
    print("-" * 95)
    for i, r in enumerate(sorted(results, key=lambda x: x["ratio"], reverse=True), 1):
        activity = r["trades_4w"] if r["trades_4w"] > 0 else r["volume"]
        flag = "  ⚠️ " if r["ratio"] > 200 and r["mentions"] < 10 else "     "
        print(
            f"{i:<4} {r['ratio']:>12,.1f}{flag}"
            f"{activity:>12,.0f}  {r['mentions']:>9}  {r['question']}"
        )