import re

def clean_team_name(name):
    name = re.sub(r'\s+(FC|AFC|United FC|City FC|Hotspur FC|Wanderers FC|Athletic FC)$', '', name.strip(), flags=re.I)
    name = name.strip().rstrip('?.,')
    return name

def extract_teams(question):
    if m := re.search(r'([A-Z][^:]+?)\s+vs\.?\s+([A-Z][^:]+?)(?:\s*:|$)', question):
        return [clean_team_name(m.group(1)), clean_team_name(m.group(2))]

    elif m := re.search(r'Will (.+?)\s+win', question, re.I):
        return [clean_team_name(m.group(1))]

    elif m := re.search(r'Spread:\s*(.+?)\s*\(', question, re.I):
        return [clean_team_name(m.group(1))]

    return []