import datetime as dt
from speculator import scrape_posts
from extractor import extract_teams
from google import scrape_trends


def find_single_speculation_ratio(bet):
    teams = extract_teams(bet.question)

    if not teams:
        return 0
    
    start_date = bet.startDate[:10]
    reddit_matches = scrape_posts("Soccer", teams[0], start_date)
    google_trends = scrape_trends(teams[0], start_date)

    social_buzz = (reddit_matches + 1) * (google_trends + 1)

    ratio = float(bet.volume) / social_buzz

    return ratio

def find_average_speculation_ratio(bets):
    total_ratio = 0
    count = 0

    for bet in bets:
        ratio = find_single_speculation_ratio(bet)

        if ratio == 0:
            continue

        total_ratio += ratio
        count += 1

    if count == 0:
        return 0

    return total_ratio / count

from top50Markets import FindTop50Markets

bets = FindTop50Markets()
average_ratio = find_average_speculation_ratio(bets)
print(f"Average Speculation Ratio: {average_ratio:.4f}")