import requests
from collections import defaultdict

DATA_BASE = "https://data-api.polymarket.com"

def find_avg_whalescore(bets):
    for bet in bets:
        id = bet.id


