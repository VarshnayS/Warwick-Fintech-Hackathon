import requests
from dataclasses import dataclass
from typing import List, Dict, Any

REDDIT = "https://www.reddit.com"
HEADERS = {"User-Agent": "warwick-fintech-hackathon/0.1 (contact: demo)"}

def subreddit_search(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    url = f"{REDDIT}/subreddits/search.json"
    r = requests.get(url, params={"q": query, "limit": limit}, headers=HEADERS, timeout=20)
    r.raise_for_status()
    children = r.json()["data"]["children"]
    return [c["data"] for c in children]

def pick_top_subreddits(seed_queries: List[str], k: int = 5) -> List[str]:
    seen = {}
    for q in seed_queries:
        for sr in subreddit_search(q, limit=15):
            name = sr.get("display_name")  # e.g. "PremierLeague"
            if not name:
                continue
            if sr.get("over18") is True:
                continue
            subs = int(sr.get("subscribers") or 0)
            # keep best (highest subscribers) if duplicates appear
            if name not in seen or subs > seen[name]["subscribers"]:
                seen[name] = {"subscribers": subs}

    # rank by subscribers desc
    ranked = sorted(seen.items(), key=lambda x: x[1]["subscribers"], reverse=True)
    return [name for name, _ in ranked[:k]]

# Example:
# subreddits = pick_top_subreddits(["premier league", "epl", "soccer", "football"], k=5)
# print(subreddits)