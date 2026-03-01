EPL_TEAMS = [
    "Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton",
    "Burnley", "Chelsea", "Crystal Palace", "Everton", "Fulham",
"Ipswich", "Leicester", "Liverpool", "Leeds", "Manchester City",
    "Manchester United", "Newcastle", "Nottingham Forest", "Southampton",
    "Sunderland", "Tottenham", "West Ham", "Wolves", "Luton"
]

PREMIER_LEAGUE_KEYWORDS = ["title", "champion", "win the league", "premier league winner", "win the premier league"]
TOP_4_KEYWORDS = ["top 4", "top four", "finish top", "top-4", "champions league place"]

def extract_teams(question):
    q = question.lower()
    teams = [team for team in EPL_TEAMS if team.lower() in q]

    if any(kw in q for kw in PREMIER_LEAGUE_KEYWORDS):
        return ["Premier League"] + teams

    if any(kw in q for kw in TOP_4_KEYWORDS):
        return ["Top 4"] + teams

    return teams


# # Test
# questions = [
#     "Will Liverpool FC win the Premier League?",
#     "Will Arsenal FC finish top 4?",
#     "Will Liverpool FC win on 2026-02-28?",
#     "Liverpool FC vs. West Ham United FC: O/U 2.5",
#     "Spread: Manchester City FC (-1.5)",
#     "Leeds United FC vs. Manchester City FC: Both Teams to Score",
#     "Exact Score: Fulham FC 2 - 1 West Ham United FC?",
# ]

# for q in questions:
#     print(extract_teams(q), "|", q)
