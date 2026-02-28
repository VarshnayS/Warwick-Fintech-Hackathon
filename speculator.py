
import requests
from datetime import datetime, timezone

BASE_URL= "https://arctic-shift.photon-reddit.com"

# get the start time and read the matches from there till current time

# need to extract the keywords from the question from the bet, and search them in the reddit posts

# for the subredddit, specifically look in the premier league subreddit and the soccer subreddit

SUBREDDIT = "PremierLeague"
KEYWORDS = ["Manchester United"]

SUBREDDIT = "PremierLeague"
SEARCH_TERM = "premier"
# example start date for now
START_DATE = "2024-01-01"           

def todays_date() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")

def scrape_posts(subreddit: str, search_term: str, start_date: str):
    posts = []
    params = {
        "subreddit": subreddit,
        "title": search_term,
        "after": start_date,
        "limit": 100,
        "sort": "asc"
    }

    response = requests.get(f"{BASE_URL}/api/posts/search", params=params, timeout=30)
    print(f"  → {response.url}")
    response.raise_for_status()

    batch = response.json().get("data", [])
    if not batch:
        exit()

    posts.extend(batch)
    print(f"  {len(posts)} posts fetched...")

        # Advance cursor to last post's timestamp
    last_utc = batch[-1]["created_utc"]
    after = datetime.fromtimestamp(last_utc, tz=timezone.utc).strftime("%Y-%m-%d")

        # If we got fewer than the limit, we've exhausted results
    if len(batch) < 100:
        exit()

    print(f"Done — {len(posts)} total posts.\n")
    return posts