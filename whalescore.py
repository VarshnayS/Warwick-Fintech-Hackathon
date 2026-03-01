import requests
from datetime import datetime, timedelta

BASE = "https://data-api.polymarket.com"

def average_whale_ratio(bets):
    total_ratio = 0
    count = 0

    four_weeks_ago = datetime.utcnow() - timedelta(weeks=4)
    cutoff = four_weeks_ago.timestamp()

    for bet in bets:
        conditionId = bet.id
        r = requests.get(f"{BASE}/trades",params={"market": conditionId, "limit": 1000})
        r.raise_for_status()
        trades = r.json()
        
        trades_4w = []
        for t in trades:
            if t.get("timestamp", 0) >= cutoff:
                trades_4w.append(t)
        wallet_totals = {}

    for t in trades_4w:
        wallet = t.get("proxyWallet")
        size = t.get("size", 0)

        if wallet is None:
            continue

        if wallet not in wallet_totals:
            wallet_totals[wallet] = 0

        wallet_totals[wallet] = wallet_totals[wallet] + float(size)
        
