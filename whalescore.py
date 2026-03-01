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
    values = sorted(values)
    n = len(values)
    if n == 0:
        return 0
    if n == 1:
        return values[0]
    
    index = round((p / 100) * (n - 1))
    return values[index]




def single_whale_ratio(id):
    four_weeks_ago = datetime.now() - timedelta(weeks=4)
    cutoff = four_weeks_ago.timestamp()

    r = requests.get(f"{BASE}/trades",params={"market": id, "limit": 1000})
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

    if len(totals_list) < 5:
        return 0

    c1 = median(totals_list)         # median
    c2 = percentile(totals_list, 95) # 95th percentile

    if c1 == 0:
        return 0

    ratio = c2 / c1
    return ratio 


    

def average_whale_ratio(bets):
    total_ratio = 0
    count = 0

    for bet in bets:

        conditionId = bet.id
        _ratio = single_whale_ratio(conditionId)

        if _ratio == 0:
            continue

        total_ratio += _ratio
        count += 1

    if count == 0:
        return 0

    return total_ratio / count