from bet import Bet
import requests

BASE = "https://gamma-api.polymarket.com"

params = {
    "tag_id": 82,
    "active": "true",
    "closed": "false",
    "order": "volume",
    "ascending": "false",
    "limit": 50
}

events = requests.get(f"{BASE}/events", params=params).json()
def FindTop50Markets():
    bets = []

    for event in events:
        id = event["id"]
        question = event["title"]
        volume = event["volume"]
        startDate = event["startDate"]

        bet = Bet(id, question, volume, startDate)

        bets.append(bet)
        
    return bets
    
