from speculator import *

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
