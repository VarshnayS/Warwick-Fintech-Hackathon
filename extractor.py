import re

def clean_team_name(name):
    name = name.strip().rstrip('?.,')
    # Remove suffixes at end
    name = re.sub(r'\s+(FC|AFC|United|City|Hotspur|Wanderers|Athletic)$', '', name, flags=re.I)
    # Remove prefixes at start
    name = re.sub(r'^(AFC|FC)\s+', '', name, flags=re.I)
    return name.strip()

def extract_teams(question):
    # "Team A vs Team B: ..."
    if m := re.search(r'Will (.+?)\s+vs\.?\s+(.+?)\s+end in', question, re.I):
        return [clean_team_name(m.group(1)), clean_team_name(m.group(2))]

    # "Team A vs Team B: O/U ..."
    elif m := re.search(r'^([A-Z].+?)\s+vs\.?\s+([A-Z].+?):', question):
        return [clean_team_name(m.group(1)), clean_team_name(m.group(2))]

    # "Will Team win ..."
    elif m := re.search(r'Will (.+?)\s+win', question, re.I):
        return [clean_team_name(m.group(1))]

    # "Spread: Team (-1.5)"
    elif m := re.search(r'Spread:\s*(.+?)\s*\(', question, re.I):
        return [clean_team_name(m.group(1))]

    return []

# # Tests
# print(extract_teams("Will AFC Bournemouth win on 2026-02-28?"))       # ['Bournemouth']
# print(extract_teams("Will Liverpool FC vs. West Ham United FC end in a draw?"))  # ['Liverpool', 'West Ham']
# print(extract_teams("Liverpool FC vs. West Ham United FC: O/U 2.5"))  # ['Liverpool', 'West Ham']
# print(extract_teams("Spread: Liverpool FC (-1.5)"))   