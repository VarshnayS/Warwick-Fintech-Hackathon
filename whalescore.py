import requests
from datetime import datetime, timedelta

BASE = "https://data-api.polymarket.com"

def median(values):
    values = sorted(values)
    n = len(values)
    if n == 0:
        return 0
    mid = n // 2
    if n % 2 == 1:
        return values[mid]
    else:
        return (values[mid - 1] + values[mid]) / 2

def percentile(values, p):
    # p is between 0 and 100
    values = sorted(values)
    n = len(values)
    if n == 0:
        return 0
    index = int((p / 100) * (n - 1))
    return values[index]

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

        totals_list = list(wallet_totals.values())

        c1 = median(totals_list)         # median
        c2 = percentile(totals_list, 95) # 95th percentile

        if c1 == 0:
            continue

        ratio = c2 / c1

        total_ratio += ratio
        count += 1

    if count == 0:
        return 0

    return total_ratio / count
            