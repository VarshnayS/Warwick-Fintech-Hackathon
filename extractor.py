import re

# ── Canonical team name map ───────────────────────────────────────────────────
# Maps any common variant → the short name Reddit actually uses in post titles
TEAM_ALIASES = {
    # Arsenal
    "Arsenal":                          "Arsenal",
    # Aston Villa
    "Aston Villa":                      "Aston Villa",
    # Bournemouth
    "AFC Bournemouth":                  "Bournemouth",
    "Bournemouth":                      "Bournemouth",
    # Brentford
    "Brentford":                        "Brentford",
    # Brighton
    "Brighton & Hove Albion":           "Brighton",
    "Brighton and Hove Albion":         "Brighton",
    "Brighton":                         "Brighton",
    # Burnley
    "Burnley":                          "Burnley",
    # Chelsea
    "Chelsea":                          "Chelsea",
    # Crystal Palace
    "Crystal Palace":                   "Crystal Palace",
    # Everton
    "Everton":                          "Everton",
    # Fulham
    "Fulham":                           "Fulham",
    # Leeds
    "Leeds United":                     "Leeds United",
    "Leeds":                            "Leeds United",
    # Leicester
    "Leicester City":                   "Leicester",
    "Leicester":                        "Leicester",
    # Liverpool
    "Liverpool":                        "Liverpool",
    # Luton
    "Luton Town":                       "Luton",
    "Luton":                            "Luton",
    # Man City  ← CRITICAL: keep distinct from Man United
    "Manchester City":                  "Manchester City",
    "Man City":                         "Manchester City",
    # Man United ← CRITICAL: keep distinct from Man City
    "Manchester United":                "Manchester United",
    "Man United":                       "Manchester United",
    "Man Utd":                          "Manchester United",
    # Newcastle
    "Newcastle United":                 "Newcastle",
    "Newcastle":                        "Newcastle",
    # Nottingham Forest
    "Nottingham Forest":                "Nottingham Forest",
    "Nottm Forest":                     "Nottingham Forest",
    # Sheffield United
    "Sheffield United":                 "Sheffield United",
    "Sheffield":                        "Sheffield United",
    # Southampton
    "Southampton":                      "Southampton",
    # Sunderland
    "Sunderland":                       "Sunderland",
    # Tottenham
    "Tottenham Hotspur":                "Tottenham",
    "Tottenham":                        "Tottenham",
    "Spurs":                            "Tottenham",
    # West Ham
    "West Ham United":                  "West Ham",
    "West Ham":                         "West Ham",
    # Wolves
    "Wolverhampton Wanderers":          "Wolves",
    "Wolverhampton":                    "Wolves",
    "Wolves":                           "Wolves",
}

# Suffixes to strip from team names
_SUFFIXES = re.compile(
    r'\s+(FC|AFC|F\.C\.|A\.F\.C\.|United FC|City FC|Hotspur FC|'
    r'Wanderers FC|Athletic FC|Town FC|Rovers FC|County FC|'
    r'Albion FC|Villa FC|Palace FC|Forest FC|United|City|Hotspur|'
    r'Wanderers|Athletic|Town|Rovers|County|Albion)$',
    re.IGNORECASE
)

# Market type suffixes to strip from the full question
_MARKET_SUFFIXES = re.compile(
    r'\s*[-–]\s*(More Markets|Exact Score|Player Props|'
    r'Total Corners|Halftime Result|First Goal|Anytime Score|'
    r'Both Teams to Score|Asian Handicap|Double Chance|'
    r'Draw No Bet|Clean Sheet|Match Result|Spread|Moneyline|'
    r'Over Under|Over\/Under|\d+\.\d+).*$',
    re.IGNORECASE
)


def _strip_suffixes(name: str) -> str:
    """Remove FC/AFC and common suffixes from a team name."""
    name = name.strip()
    # Iteratively strip suffixes (e.g. "Manchester United FC" -> "Manchester United" -> done)
    prev = None
    while prev != name:
        prev = name
        name = _SUFFIXES.sub("", name).strip()
    return name.rstrip("?.,;:-")


def _resolve_alias(name: str) -> str:
    """Look up canonical Reddit-friendly team name."""
    # Try exact match first
    if name in TEAM_ALIASES:
        return TEAM_ALIASES[name]
    # Try after stripping suffixes
    stripped = _strip_suffixes(name)
    if stripped in TEAM_ALIASES:
        return TEAM_ALIASES[stripped]
    # Fuzzy: check if any alias key is contained within the name
    for key, canonical in TEAM_ALIASES.items():
        if key.lower() in name.lower():
            return canonical
    # Fallback: return stripped name
    return stripped


def extract_teams(question: str) -> list[str]:
    """
    Extract clean, Reddit-searchable team name keywords from a bet question.

    Examples:
      "Arsenal FC vs. Chelsea FC - More Markets"    → ["Arsenal", "Chelsea"]
      "Manchester City FC vs. Nottingham Forest FC" → ["Manchester City", "Nottingham Forest"]
      "Will Liverpool win the Premier League?"      → ["Liverpool"]
      "Premier League Winner"                       → ["Premier League"]
    """
    # 1. Strip market type suffix
    clean_q = _MARKET_SUFFIXES.sub("", question).strip()

    # 2. Try "X vs. Y" or "X vs Y" pattern
    vs_match = re.search(
        r'^(.+?)\s+vs\.?\s+(.+?)$',
        clean_q,
        re.IGNORECASE
    )
    if vs_match:
        team_a = _resolve_alias(vs_match.group(1).strip())
        team_b = _resolve_alias(vs_match.group(2).strip())
        return [team_a, team_b]

    # 3. "Will X win..." pattern
    will_match = re.search(r'Will\s+(.+?)\s+(?:win|beat|score)', clean_q, re.IGNORECASE)
    if will_match:
        return [_resolve_alias(will_match.group(1))]

    # 4. "X to win" pattern
    to_win_match = re.search(r'(.+?)\s+to\s+win', clean_q, re.IGNORECASE)
    if to_win_match:
        candidate = _resolve_alias(to_win_match.group(1))
        # Only return if it looks like a team name (not "Premier League Winner to win")
        if len(candidate.split()) <= 4:
            return [candidate]

    # 5. Fallback: return the cleaned question as a single search term
    fallback = _strip_suffixes(clean_q)
    return [fallback] if fallback else []
