from extractor import extract_teams
from top50Markets import FindTop50Markets
from speculator import scrape_posts, SUBREDDIT

if __name__ == "__main__":
    bets = FindTop50Markets()

    for bet in bets:
        keywords = extract_teams(bet.question)
        start_date = bet.startDate[:10]

        total_matches = 0 
        seen = set()    

        for k in keywords: 
            posts = scrape_posts(SUBREDDIT, k, start_date)
            for p in posts: 
                # dont add already seen posts
                if p["id"] not in seen:
                    seen.add(p["id"])
                    total_matches += 1

    print(f"Bet        : {bet.question}")
    print(f"Keywords   : {keywords}")
    print(f"Start date : {start_date}")
    print(f"Matches    : {total_matches}\n")
            