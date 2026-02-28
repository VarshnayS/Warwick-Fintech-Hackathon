

from top50Markets import FindTop50Markets
from speculator import scrape_posts, SUBREDDIT

if __name__ == "__main__":
    bets = FindTop50Markets()

    for bet in bets:
        keyword = bet.question
        start_date = bet.startDate[:10]

        posts = scrape_posts(SUBREDDIT, keyword, start_date)
        match_count = len(posts)
        print(f"  Matches : {match_count}\n")