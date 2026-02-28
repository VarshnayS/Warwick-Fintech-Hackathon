import requests
import bet
BASE = "https://gamma-api.polymarket.com"

params = {
    "tag_id": 82,   # try the more specific tag
    "active": "true",
    "closed": "false",
    "order": "volume",
    "ascending": "false",
    "limit": 50
}
all_markets = []
bet_ids = []
events = requests.get(f"{BASE}/events", params=params).json()
for event in events:
    for market in event.get("markets", []):
        # all_markets.append({
        #     "question": market.get("question"),
        #     "volume": float(market.get("volume") or 0),
        #     "volume24hr": market.get("volume24hr") or 0,
        #     "liquidity": float(market.get("liquidity") or 0),
        #     "event": event.get("title"),
        # })
        all_markets.append(market)
        bet_ids.append(market.get("id"))

top50 = sorted(all_markets, key=lambda m: float(m.get("volume") or 0), reverse=True)[:50]
print("-" * 80)
bets = []
for i, m in enumerate(bet_ids, 1):
    b = bet.Bet(m)
    bets.append(b)
    b.summary()