import re

def clean_team_name(name):
    # Remove common suffixes
    name = re.sub(r'\s+(FC|AFC|United FC|City FC|Hotspur FC|Wanderers FC|Athletic FC)$', '', name.strip(), flags=re.I)
    # Clean up any trailing punctuation
    name = name.strip().rstrip('?.,')
    return name

def extract_bet_info(question):
    info = {
        "teams": [],
        "market_type": None,
        "line": None,
    }

    # ── Market type detection ──────────────────────────────────────
    if re.search(r'both teams to score', question, re.I):
        info["market_type"] = "btts"

    elif re.search(r'end in a draw', question, re.I):
        info["market_type"] = "draw"

    elif m := re.search(r'O/U\s*([\d.]+)', question, re.I):
        info["market_type"] = "over_under"
        info["line"] = float(m.group(1))

    elif m := re.search(r'Spread:.*?\(([+-][\d.]+)\)', question, re.I):
        info["market_type"] = "spread"
        info["line"] = float(m.group(1))

    elif re.search(r'Exact Score', question, re.I):
        info["market_type"] = "exact_score"
        if m := re.search(r'(\d+)\s*[-–]\s*(\d+)', question):
            info["line"] = f"{m.group(1)}-{m.group(2)}"

    elif re.search(r'Will .+ win', question, re.I):
        info["market_type"] = "match_winner"

    # ── Team extraction ────────────────────────────────────────────
    if m := re.search(r'([A-Z][^:]+?)\s+vs\.?\s+([A-Z][^:]+?)(?:\s*:|$)', question):
        info["teams"] = [
            clean_team_name(m.group(1)),
            clean_team_name(m.group(2))
        ]

    elif m := re.search(r'Will (.+?)\s+win', question, re.I):
        info["teams"] = [clean_team_name(m.group(1))]

    elif m := re.search(r'Spread:\s*(.+?)\s*\(', question, re.I):
        info["teams"] = [clean_team_name(m.group(1))]

    return info

