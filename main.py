from speculator import *

if __name__ == "__main__":
    all_posts = []

    for kw in KEYWORDS:
        all_posts.extend(scrape_posts(SUBREDDIT, kw, START_DATE))

    # De-duplicate
    seen, unique = set(), []
    for p in all_posts:
        if p["id"] not in seen:
            seen.add(p["id"])
            unique.append(p)

    print(f"Unique posts: {len(unique)}")
    for p in unique[:10]:
        dt = datetime.fromtimestamp(p["created_utc"], tz=timezone.utc).strftime("%Y-%m-%d")
        print(f"  [{dt}] {p.get('title')}")
