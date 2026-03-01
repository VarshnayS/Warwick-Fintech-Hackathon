from top50Markets import FindTop50Markets
from speculator import scrape_posts, SUBREDDIT
from extractor import extract_teams as extract_teams_
from google import scrape_trends


if __name__ == "__main__":
    bets = FindTop50Markets()

    for bet in bets:
        # keywords = extract_teams(bet.question)
        keywords = extract_teams_(bet.question)
        start_date = bet.startDate[:10]
        seen_fixtures = {}
        cache_key  = (frozenset(keywords), start_date)

        if cache_key in seen_fixtures:
            match_count = seen_fixtures[cache_key]
        
        else:

            total_matches = 0 
            seen = set()    

            for k in keywords: 
                posts = scrape_posts(SUBREDDIT, k, start_date)
                for p in posts: 
                    # dont add already seen posts
                    if p["id"] not in seen:
                        seen.add(p["id"])
                        total_matches += 1
                        
        print(f"------------------REDDIT---------------------")
        print(f"{bet.question} | {start_date} | Matches: {total_matches} | Keywords: {keywords}")

        trends = scrape_trends(k, start_date)
        print(f"------------------GOOGLE------------------------")
        print(
            f"{k} | "
            f"Peak: {trends['peak']} | "
            f"Mean: {trends['mean']} | "
            f"Current: {trends['current']} | "
            f"Related: {trends['related']}"
        )

    # print(f"Bet        : {bet.question}")
    # print(f"Keywords   : {keywords}")
    # print(f"Start date : {start_date}")
    # print(f"Matches    : {total_matches}\n")
            
