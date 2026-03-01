from bet import Bet
import requests

BASE = "https://gamma-api.polymarket.com"

params = {
    "tag_id": 82,
    "active": "true",
    "closed": "false",
    "order": "volume",
    "ascending": "false",
    "limit": 50,
}

events = requests.get(f"{BASE}/events", params=params).json()

def FindTop50Markets():
    bets = []

    for event in events:
        # 1. Grab the array of markets inside the event container
        markets = event.get("markets", [])
        
        market = markets[0] if markets else None

        condition_id = market.get("conditionId")
        
        if not condition_id:
            continue

        question = market.get("question", event.get("title")) 
        volume = market.get("volume", 0)
        startDate = event.get("startDate")

        bet = Bet(condition_id, question, volume, startDate)
        bets.append(bet)
        
    return bets