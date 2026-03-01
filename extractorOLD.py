import re

def clean_team_name(name: str) -> str:
    name = name.split(" - ")[0]  # ← strip "More Markets", "Exact Score" etc.
    name = re.sub(r'\s+(FC|AFC|United FC|City FC|Hotspur FC|Wanderers FC|Athletic FC)$', '', name.strip(), flags=re.I)
    name = name.strip().rstrip('?.,')
    return name

def extract_teams(question: str) -> list[str]:
    question = question.split(" - ")[0]  # ← strip suffix from full question too

    if m := re.search(r'([A-Z][^:]+?)\s+vs\.?\s+([A-Z][^:]+?)(?:\s*:|$)', question):
        return [clean_team_name(m.group(1)), clean_team_name(m.group(2))]
    elif m := re.search(r'Will (.+?)\s+win', question, re.I):
        return [clean_team_name(m.group(1))]
    elif m := re.search(r'Spread:\s*(.+?)\s*\(', question, re.I):
        return [clean_team_name(m.group(1))]
    return []