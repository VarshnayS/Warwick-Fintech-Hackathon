import requests
import bet
BASE = "https://gamma-api.polymarket.com"

sports = requests.get(f"{BASE}/sports").json()

epl_tags = None

for s in sports:
    if s["sport"].lower() == "epl":
        epl_tags = s["tags"]   # e.g. "1,100149,100639"
        break

print("Raw EPL tags:", epl_tags)


params = {
    "tag_id": 82,   # try the more specific tag
    "active": "true",
    "closed": "false",
    "order": "volume",
    "ascending": "false",
    "limit": 50
}
all_markets = []

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

print(all_markets[0])
# Sort by total volume descending, take top 50
# top50 = sorted(all_markets, key=lambda m: m["volume"], reverse=True)[:50]
top50 = sorted(all_markets, key=lambda m: float(m.get("volume") or 0), reverse=True)[:50]


print(f"{'#':<4} {'Volume (USDC)':<18} {'Question'}")
print("-" * 80)

for i, m in enumerate(top50, 1):
    volume    = float(m.get("volume") or 0)
    vol24hr   = float(m.get("volume24hr") or 0)
    liquidity = float(m.get("liquidity") or 0)
    # question  = m.get("question", "N/A")
    # print(f"{i:<4} ID: {m['id']:<40} {m.get('question')}")
    # print(f"{i:<4} ${volume:<14,.0f} ${vol24hr:<14,.0f} ${liquidity:<14,.0f} {question}")
    b = bet.Bet(m["id"])
    b.summary()
    
# Raw EPL tags: 1,82,306,100639,100350

