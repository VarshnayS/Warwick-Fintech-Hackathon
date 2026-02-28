
import requests
import category 
from datetime import datetime, timezone

BASE_URL= " https://arctic-shift.photon-reddit.com"

# get the start time and read the matches from there till current time

# need to extract the keywords from the question from the bet, and search them in the reddit posts

# for the subredddit, specifically look in the premier league subreddit and the soccer subreddit

SUBREDDIT = "PremierLeague"
KEYWWORD = ["Manchester United"]

SUBREDDIT = "PremierLeague"
START_DATE = "2024-08-01"          # <── change this to your desired start date (YYYY-MM-DD)
SEARCH_TERM = "premier"            

def date_to_unix(date_str: str) -> int:
    """Convert a YYYY-MM-DD string to a UTC Unix timestamp."""
    dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return int(dt.timestamp())

def scrape_posts(subreddit: str, search_term: str, start_date: str) -> list[dict]:
    """
    Fetch all posts from a subreddit matching a search term
    from start_date up to now, using the Arctic Shift API.
    """
    start_ts = date_to_unix(start_date)
    end_ts = int(datetime.now(timezone.utc).timestamp())

    posts = []
    after = start_ts  # cursor for pagination

    print(f"Scraping r/{subreddit} for '{search_term}' from {start_date} to now...")

    while True:
        params = {
            "subreddit": subreddit,
            "q": search_term,
            "after": after,
            "before": end_ts,
            "limit": 100,           # max per request
            "sort": "created_utc",
            "order": "asc",
        }

        response = requests.get(f"{BASE_URL}/posts/search", params=params)
        response.raise_for_status()
        data = response.json()

        batch = data.get("data", [])
        if not batch:
            break  # no more results

        posts.extend(batch)
        print(f"  Fetched {len(posts)} posts so far...")

        # Arctic Shift returns posts sorted by date; advance cursor past the last one
        last_ts = batch[-1]["created_utc"]
        if last_ts <= after:
            break  # guard against infinite loop
        after = last_ts

        # Stop if we've passed the end window
        if last_ts >= end_ts:
            break

    print(f"Done. Total posts fetched: {len(posts)}")
    return posts


# ── RUN ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    matching_posts = scrape_posts(
        subreddit=SUBREDDIT,
        search_term=SEARCH_TERM,
        start_date=START_DATE,
    )

    # Example: print titles of first 10 results
    for post in matching_posts[:10]:
        created = datetime.fromtimestamp(post["created_utc"], tz=timezone.utc).strftime("%Y-%m-%d")
        print(f"[{created}] {post.get('title', 'N/A')}")
