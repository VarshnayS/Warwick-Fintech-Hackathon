import time
import requests
from datetime import datetime, timezone
from top50Markets import FindTop50Markets

BASE_URL= "https://arctic-shift.photon-reddit.com"
SUBREDDIT = "soccer"        
bets = FindTop50Markets()

def scrape_posts(subreddit: str, keyword: str, start_date: str) -> list[dict]:
    all_posts = []
    after = start_date

    while True:
        params = {
            "subreddit": subreddit,
            "title":     keyword,
            "after":     after,
            "limit":     10,
            "sort":      "asc",
        }
        
        time.sleep(1)

        response = requests.get(f"{BASE_URL}/api/posts/search", params=params, timeout=30)
        if response.status_code == 429:
            time.sleep(5)
            continue
        response.raise_for_status()

        batch = response.json().get("data", [])
        all_posts.extend(batch)

        if len(batch) < 100:
            break

        last_utc = batch[-1]["created_utc"]
        after = datetime.fromtimestamp(last_utc, tz=timezone.utc).strftime("%Y-%m-%d")

    return all_posts