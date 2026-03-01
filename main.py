import streamlit as st
import requests

st.set_page_config(
    page_title="Polymarket Event Risk Manager",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: #0a0a0f;
    color: #f0f0f0;
    font-family: 'DM Sans', sans-serif;
}
[data-testid="stAppViewContainer"] > .main { background: #0a0a0f; }
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebar"] { display: none; }
[data-testid="collapsedControl"] { display: none; }
div[data-testid="stDecoration"] { display: none; }
.block-container { padding: 0 !important; max-width: 100% !important; }

.menu-wrap {
    min-height: 60vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 80px 0 40px;
    background: radial-gradient(ellipse at 50% 0%, #1a1a2e 0%, #0a0a0f 65%);
    position: relative;
}
.menu-wrap::before {
    content: '';
    position: absolute;
    inset: 0;
    background:
        repeating-linear-gradient(0deg, transparent, transparent 59px, rgba(255,255,255,0.02) 60px),
        repeating-linear-gradient(90deg, transparent, transparent 59px, rgba(255,255,255,0.02) 60px);
    pointer-events: none;
}
.menu-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: clamp(2.4rem, 5vw, 4.2rem);
    letter-spacing: 0.12em;
    color: #fff;
    text-align: center;
    line-height: 1.1;
    position: relative;
    margin-bottom: 8px;
}
.menu-title span { color: #37b8f7; }
.menu-subtitle {
    font-size: 0.85rem;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: #555;
    text-align: center;
    position: relative;
    margin-bottom: 0;
}

.league-card-btn button {
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 12px !important;
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 20px !important;
    padding: 36px 64px !important;
    width: 100% !important;
    height: auto !important;
    min-height: 200px !important;
    color: #e8e8e8 !important;
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 1.4rem !important;
    letter-spacing: 0.1em !important;
    transition: all 0.25s ease !important;
    cursor: pointer !important;
    position: relative !important;
    opacity: 1 !important;
    top: auto !important;
    left: auto !important;
    margin: 0 !important;
    white-space: pre-line !important;
    line-height: 1.6 !important;
}
.league-card-btn button:hover {
    background: rgba(55,184,247,0.08) !important;
    border-color: rgba(55,184,247,0.35) !important;
    transform: translateY(-4px) !important;
    box-shadow: 0 20px 60px rgba(55,184,247,0.12) !important;
    color: #fff !important;
}

.league-header {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 24px 40px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    background: rgba(0,0,0,0.4);
    backdrop-filter: blur(10px);
}
.league-header img { width: 40px; height: 40px; object-fit: contain; }
.league-header-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.8rem;
    letter-spacing: 0.1em;
    color: #fff;
}

.cards-section { padding: 28px 40px; }
.cards-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
}
.bet-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 20px;
    cursor: pointer;
    transition: all 0.2s ease;
    position: relative;
    overflow: hidden;
    height: 100%;
}
.bet-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #37b8f7, #7b5ff5);
    opacity: 0;
    transition: opacity 0.2s;
}
.bet-card:hover {
    background: rgba(55,184,247,0.06);
    border-color: rgba(55,184,247,0.2);
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(0,0,0,0.3);
}
.bet-card:hover::before { opacity: 1; }

/* Badge + question row */
.card-header {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    margin-bottom: 18px;
}
.card-badge {
    width: 32px;
    height: 32px;
    object-fit: contain;
    flex-shrink: 0;
    margin-top: 1px;
}
.card-badge-placeholder {
    width: 32px;
    height: 32px;
    flex-shrink: 0;
}
.card-question {
    font-size: 1.05rem;
    font-weight: 700;
    color: #ffffff;
    line-height: 1.45;
    height: 2.9em;
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    flex: 1;
    text-align: center;
}

.card-stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    border-top: 1px solid rgba(255,255,255,0.06);
    padding-top: 14px;
}
.stat-item { text-align: center; }
.stat-value {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.1rem;
    color: #fff;
    letter-spacing: 0.05em;
}
.stat-label {
    font-size: 0.62rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #555;
    margin-top: 2px;
}



.card-overlay-btn button {
    position: absolute !important;
    inset: 0 !important;
    width: 100% !important;
    height: 100% !important;
    opacity: 0 !important;
    cursor: pointer !important;
    z-index: 10 !important;
    margin: 0 !important;
    padding: 0 !important;
    border: none !important;
    background: transparent !important;
    min-height: unset !important;
}
.card-overlay-btn {
    position: relative;
    margin-top: -1px;
}

.back-btn button {
    background: transparent !important;
    border: 1px solid #333 !important;
    color: #666 !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.1em !important;
    border-radius: 8px !important;
    opacity: 1 !important;
    position: relative !important;
    top: auto !important; left: auto !important;
    width: auto !important;
    height: auto !important;
    padding: 8px 18px !important;
}
.back-btn button:hover { color: #fff !important; border-color: #666 !important; }
</style>
""", unsafe_allow_html=True)


# ── Club badge map (ESPN CDN, no API key needed) ───────────────────────────────
CLUB_BADGES = {
    "Arsenal":              "https://a.espncdn.com/i/teamlogos/soccer/500/359.png",
    "Aston Villa":          "https://a.espncdn.com/i/teamlogos/soccer/500/362.png",
    "Bournemouth":          "https://a.espncdn.com/i/teamlogos/soccer/500/349.png",
    "Brentford":            "https://a.espncdn.com/i/teamlogos/soccer/500/337.png",
    "Brighton":             "https://a.espncdn.com/i/teamlogos/soccer/500/331.png",
    "Chelsea":              "https://a.espncdn.com/i/teamlogos/soccer/500/363.png",
    "Crystal Palace":       "https://a.espncdn.com/i/teamlogos/soccer/500/384.png",
    "Everton":              "https://a.espncdn.com/i/teamlogos/soccer/500/368.png",
    "Fulham":               "https://a.espncdn.com/i/teamlogos/soccer/500/370.png",
    "Ipswich Town":         "https://a.espncdn.com/i/teamlogos/soccer/500/QuoteIPSWICH.png",
    "Ipswich":              "https://a.espncdn.com/i/teamlogos/soccer/500/QuoteIPSWICH.png",
    "Leicester City":       "https://a.espncdn.com/i/teamlogos/soccer/500/375.png",
    "Leicester":            "https://a.espncdn.com/i/teamlogos/soccer/500/375.png",
    "Liverpool":            "https://a.espncdn.com/i/teamlogos/soccer/500/364.png",
    "Manchester City":      "https://a.espncdn.com/i/teamlogos/soccer/500/382.png",
    "Man City":             "https://a.espncdn.com/i/teamlogos/soccer/500/382.png",
    "Manchester United":    "https://a.espncdn.com/i/teamlogos/soccer/500/360.png",
    "Man United":           "https://a.espncdn.com/i/teamlogos/soccer/500/360.png",
    "Newcastle United":     "https://a.espncdn.com/i/teamlogos/soccer/500/361.png",
    "Newcastle":            "https://a.espncdn.com/i/teamlogos/soccer/500/361.png",
    "Nottingham Forest":    "https://a.espncdn.com/i/teamlogos/soccer/500/393.png",
    "Southampton":          "https://a.espncdn.com/i/teamlogos/soccer/500/376.png",
    "Tottenham Hotspur":    "https://a.espncdn.com/i/teamlogos/soccer/500/367.png",
    "Tottenham":            "https://a.espncdn.com/i/teamlogos/soccer/500/367.png",
    "Spurs":                "https://a.espncdn.com/i/teamlogos/soccer/500/367.png",
    "West Ham United":      "https://a.espncdn.com/i/teamlogos/soccer/500/371.png",
    "West Ham":             "https://a.espncdn.com/i/teamlogos/soccer/500/371.png",
    "Wolverhampton":        "https://a.espncdn.com/i/teamlogos/soccer/500/380.png",
    "Wolves":               "https://a.espncdn.com/i/teamlogos/soccer/500/380.png",
}

NBA_BADGES = {
    "Atlanta Hawks":        "https://a.espncdn.com/i/teamlogos/nba/500/atl.png",
    "Boston Celtics":       "https://a.espncdn.com/i/teamlogos/nba/500/bos.png",
    "Brooklyn Nets":        "https://a.espncdn.com/i/teamlogos/nba/500/bkn.png",
    "Charlotte Hornets":    "https://a.espncdn.com/i/teamlogos/nba/500/cha.png",
    "Chicago Bulls":        "https://a.espncdn.com/i/teamlogos/nba/500/chi.png",
    "Cleveland Cavaliers":  "https://a.espncdn.com/i/teamlogos/nba/500/cle.png",
    "Dallas Mavericks":     "https://a.espncdn.com/i/teamlogos/nba/500/dal.png",
    "Denver Nuggets":       "https://a.espncdn.com/i/teamlogos/nba/500/den.png",
    "Detroit Pistons":      "https://a.espncdn.com/i/teamlogos/nba/500/det.png",
    "Golden State Warriors":"https://a.espncdn.com/i/teamlogos/nba/500/gs.png",
    "Houston Rockets":      "https://a.espncdn.com/i/teamlogos/nba/500/hou.png",
    "Indiana Pacers":       "https://a.espncdn.com/i/teamlogos/nba/500/ind.png",
    "LA Clippers":          "https://a.espncdn.com/i/teamlogos/nba/500/lac.png",
    "Los Angeles Clippers": "https://a.espncdn.com/i/teamlogos/nba/500/lac.png",
    "LA Lakers":            "https://a.espncdn.com/i/teamlogos/nba/500/lal.png",
    "Los Angeles Lakers":   "https://a.espncdn.com/i/teamlogos/nba/500/lal.png",
    "Memphis Grizzlies":    "https://a.espncdn.com/i/teamlogos/nba/500/mem.png",
    "Miami Heat":           "https://a.espncdn.com/i/teamlogos/nba/500/mia.png",
    "Milwaukee Bucks":      "https://a.espncdn.com/i/teamlogos/nba/500/mil.png",
    "Minnesota Timberwolves":"https://a.espncdn.com/i/teamlogos/nba/500/min.png",
    "New Orleans Pelicans": "https://a.espncdn.com/i/teamlogos/nba/500/no.png",
    "New York Knicks":      "https://a.espncdn.com/i/teamlogos/nba/500/ny.png",
    "Oklahoma City Thunder":"https://a.espncdn.com/i/teamlogos/nba/500/okc.png",
    "Orlando Magic":        "https://a.espncdn.com/i/teamlogos/nba/500/orl.png",
    "Philadelphia 76ers":   "https://a.espncdn.com/i/teamlogos/nba/500/phi.png",
    "Phoenix Suns":         "https://a.espncdn.com/i/teamlogos/nba/500/phx.png",
    "Portland Trail Blazers":"https://a.espncdn.com/i/teamlogos/nba/500/por.png",
    "Sacramento Kings":     "https://a.espncdn.com/i/teamlogos/nba/500/sac.png",
    "San Antonio Spurs":    "https://a.espncdn.com/i/teamlogos/nba/500/sa.png",
    "Toronto Raptors":      "https://a.espncdn.com/i/teamlogos/nba/500/tor.png",
    "Utah Jazz":            "https://a.espncdn.com/i/teamlogos/nba/500/utah.png",
    "Washington Wizards":   "https://a.espncdn.com/i/teamlogos/nba/500/wsh.png",
}

ALL_BADGES = {**CLUB_BADGES, **NBA_BADGES}

def get_badge_url(question: str):
    """Return the first matching team badge URL found in the question, or None."""
    q = question.lower()
    for team in sorted(ALL_BADGES.keys(), key=len, reverse=True):
        if team.lower() in q:
            return ALL_BADGES[team]
    return None


# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=120)
def fetch_markets(tag_id: int = 82):
    BASE = "https://gamma-api.polymarket.com"
    params = {"tag_id": tag_id, "active": "true", "closed": "false",
              "order": "volume", "ascending": "false", "limit": 50}
    events = requests.get(f"{BASE}/events", params=params).json()
    markets = []
    for event in events:
        for market in event.get("markets", []):
            markets.append({
                "id":                 market.get("id"),
                "conditionId":        market.get("conditionId"),   # needed by whalescore trades API
                "question":           market.get("question", ""),
                "volume":             float(market.get("volume")     or 0),
                "volume24hr":         float(market.get("volume24hr") or 0),
                "liquidity":          float(market.get("liquidity")  or 0),
                "startDate":          event.get("startDate", ""),   # needed by speculation ratio
                "bestBid":            market.get("bestBid"),
                "bestAsk":            market.get("bestAsk"),
                "endDate":            market.get("endDate"),
            })
    return sorted(markets, key=lambda m: m["volume"], reverse=True)[:50]

def fmt(n):
    if n >= 1_000_000: return f"${n/1_000_000:.1f}M"
    if n >= 1_000:     return f"${n/1_000:.1f}K"
    return f"${n:.0f}"

def fmt_ratio(r):
    """Format a plain ratio / score. e.g. 4231.5 → '4231.5'"""
    if r is None or r == 0:
        return "—"
    try:
        v = float(r)
        # Show as integer when large, 2 dp when small
        return f"{v:.0f}" if v >= 10 else f"{v:.2f}"
    except (TypeError, ValueError):
        return "—"


# ── Session state ─────────────────────────────────────────────────────────────
if "screen" not in st.session_state:
    st.session_state.screen = "menu"
if "selected_bet" not in st.session_state:
    st.session_state.selected_bet = None
if "league" not in st.session_state:
    st.session_state.league = "prem"  # "prem" or "nba"


# ══════════════════════════════════════════════════════════════════════════════
def menu():
    st.markdown("""
    <div class="menu-wrap">
        <div>
            <div class="menu-title">Polymarket<br><span>Event Risk</span> Manager</div>
            <div class="menu-subtitle">Select a league to explore markets</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    _, col1, gap, col2, _ = st.columns([0.5, 2, 0.2, 2, 0.5])

    with col1:
        st.markdown("""
            <div style="text-align:center; margin-top: 32px; margin-bottom: -16px; position: relative; z-index: 1;">
                <img src="https://upload.wikimedia.org/wikipedia/en/f/f2/Premier_League_Logo.svg"
                     style="width:80px; height:80px; object-fit:contain;
                            filter: drop-shadow(0 4px 20px rgba(55,184,247,0.4));">
            </div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="league-card-btn">', unsafe_allow_html=True)
        if st.button("PREMIER LEAGUE\nTop 50 Markets", key="go_prem", use_container_width=True):
            st.session_state.league = "prem"
            st.session_state.screen = "prem"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div style="text-align:center; margin-top: 32px; margin-bottom: -16px; position: relative; z-index: 1;">
                <img src="https://a.espncdn.com/i/teamlogos/leagues/500/nba.png"
                     style="width:80px; height:80px; object-fit:contain;
                            filter: drop-shadow(0 4px 20px rgba(55,184,247,0.4));">
            </div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="league-card-btn">', unsafe_allow_html=True)
        if st.button("NBA\nTop 50 Markets", key="go_nba", use_container_width=True):
            st.session_state.league = "nba"
            st.session_state.screen = "prem"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
LEAGUE_CONFIG = {
    "prem": {
        "tag_id": 82,
        "title": "Premier League Markets",
        "logo": "https://upload.wikimedia.org/wikipedia/en/f/f2/Premier_League_Logo.svg",
    },
    "nba": {
        "tag_id": 745,
        "title": "NBA Markets",
        "logo": "https://a.espncdn.com/i/teamlogos/leagues/500/nba.png",
    },
}

def load_ratios():
    """Read average speculation_ratio and whale_ratio from ratios.txt."""
    try:
        with open("ratios.txt", "r") as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
        spec  = float(lines[0]) if len(lines) > 0 else None
        whale = float(lines[1]) if len(lines) > 1 else None
        return spec, whale
    except Exception:
        return 25, 25


def prem():
    league = st.session_state.get("league", "prem")
    cfg    = LEAGUE_CONFIG.get(league, LEAGUE_CONFIG["prem"])

    st.markdown(
        '<div class="league-header">' +
        '<img src="' + cfg["logo"] + '">' +
        '<div class="league-header-title">' + cfg["title"] + '</div>' +
        '</div>',
        unsafe_allow_html=True
    )

    # ── Ratios banner ─────────────────────────────────────────────────────────
    avg_spec, avg_whale = load_ratios()

    def _ratio_tile(label, value, fmt_fn):
        val_str = fmt_fn(value) if value is not None else "—"
        color   = "#98d3f0" if value is not None else "#444"
        return (
            '<div style="text-align:center;">' +
            '<div style="font-size:0.6rem;letter-spacing:0.18em;text-transform:uppercase;' +
            'color:#444;margin-bottom:6px;">' + label + '</div>' +
            '<div style="font-family:Bebas Neue,sans-serif;font-size:1.5rem;' +
            'letter-spacing:0.06em;color:' + color + '">' + val_str + '</div>' +
            '</div>'
        )

    spec_str  = (f"{avg_spec:.0f}"  if avg_spec  is not None and avg_spec  >= 10 else (f"{avg_spec:.2f}"  if avg_spec  is not None else "—"))
    whale_str = (f"{avg_whale:.1f}x" if avg_whale is not None else "—")

    st.markdown(
        '<div style="display:flex;align-items:center;justify-content:center;gap:60px;' +
        'padding:16px 40px;background:rgba(55,184,247,0.04);' +
        'border-bottom:1px solid rgba(55,184,247,0.1);">' +
        '<div style="font-size:0.65rem;letter-spacing:0.2em;text-transform:uppercase;color:#333;">Market Averages</div>' +
        _ratio_tile("Avg Speculation Ratio", avg_spec,  lambda v: spec_str)  +
        '<div style="width:1px;height:32px;background:rgba(255,255,255,0.06);"></div>' +
        _ratio_tile("Avg Whale Ratio",       avg_whale, lambda v: whale_str) +
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    back, _ = st.columns([1, 10])
    with back:
        if st.button("← Back", key="back_menu"):
            st.session_state.screen = "menu"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    markets = fetch_markets(cfg["tag_id"])
    st.markdown('<div style="padding: 20px 40px;">', unsafe_allow_html=True)

    cols_per_row = 2
    rows = [markets[i:i+cols_per_row] for i in range(0, len(markets), cols_per_row)]

    for row in rows:
        cols = st.columns(len(row))
        for col, m in zip(cols, row):
            with col:
                badge_url = get_badge_url(m["question"])
                badge_part = '<img class="card-badge" src="' + (badge_url or "") + '" alt="">' if badge_url else '<div class="card-badge-placeholder"></div>'
                card_html = (
                    '<div class="bet-card">'
                    '<div class="card-header">'
                    + badge_part +
                    '<div class="card-question">' + m["question"] + '</div>'
                    '</div>'
                    '<div class="card-stats">'
                    '<div class="stat-item"><div class="stat-value">' + fmt(m["volume"])     + '</div><div class="stat-label">Volume</div></div>'
                    '<div class="stat-item"><div class="stat-value">' + fmt(m["volume24hr"]) + '</div><div class="stat-label">24h</div></div>'
                    '<div class="stat-item"><div class="stat-value">' + fmt(m["liquidity"])  + '</div><div class="stat-label">Liquidity</div></div>'
                    '</div>'
                    '</div>'
                )
                st.markdown(card_html, unsafe_allow_html=True)
                st.markdown('<div class="card-overlay-btn">', unsafe_allow_html=True)
                if st.button("select", key="btn_" + str(m["id"]), use_container_width=True):
                    st.session_state.selected_bet = m
                    st.session_state.screen = "single_bet"
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=60)
def fetch_market_detail(market_id: str):
    BASE = "https://gamma-api.polymarket.com"
    CLOB = "https://clob.polymarket.com"
    try:
        m = requests.get(f"{BASE}/markets/{market_id}", timeout=5).json()
    except Exception:
        m = {}
    try:
        hist = requests.get(f"{CLOB}/prices-history",
                            params={"market": market_id, "interval": "1d", "fidelity": 30},
                            timeout=5).json()
        prices = hist.get("history", [])
    except Exception:
        prices = []
    return m, prices


def single_bet():
    m = st.session_state.get("selected_bet", {})
    if not m:
        st.session_state.screen = "prem"
        st.rerun()

    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    back, _ = st.columns([1, 10])
    with back:
        if st.button("← Back", key="back_prem"):
            st.session_state.screen = "prem"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    question   = m.get("question", "")
    volume     = float(m.get("volume",     0) or 0)
    volume24hr = float(m.get("volume24hr", 0) or 0)
    liquidity  = float(m.get("liquidity",  0) or 0)

    detail, price_history = fetch_market_detail(str(m["id"]))

    import json as _json
    from datetime import datetime, timezone

    def _get(*keys, src=detail, fallback=None):
        for k in keys:
            v = src.get(k)
            if v not in (None, "", "0", 0):
                return v
        return fallback

    end_date    = (_get("endDate", "end_date_iso") or "")[:10]
    description = _get("description") or ""
    out_probs   = _get("outcomePrices") or "[]"
    if isinstance(out_probs, str):
        try:    out_probs = _json.loads(out_probs)
        except: out_probs = []

    yes_prob = no_prob = None
    if len(out_probs) >= 2:
        try:
            yes_prob = round(float(out_probs[0]) * 100, 1)
            no_prob  = round(float(out_probs[1]) * 100, 1)
        except: pass

    # ── Whale Ratio & Speculation Ratio ───────────────────────────────────────
    @st.cache_data(ttl=300, show_spinner=False)
    def _whale(condition_id: str):
        try:
            from whalescore import single_whale_ratio
            return single_whale_ratio(condition_id)
        except Exception as e:
            return ("error", str(e))

    @st.cache_data(ttl=300, show_spinner=False)
    def _speculation(condition_id: str, question: str, volume: float, start_date: str):
        try:
            from speculation import find_single_speculation_ratio

            class _Bet:
                pass
            bet = _Bet()
            bet.id        = condition_id
            bet.question  = question
            bet.volume    = volume
            bet.startDate = start_date
            return find_single_speculation_ratio(bet)
        except Exception as e:
            return ("error", str(e))

    condition_id = m.get("conditionId") or ""
    start_date   = m.get("startDate", "")

    with st.spinner("Computing ratios…"):
        whale_raw = _whale(condition_id)
        spec_raw  = _speculation(condition_id, question, volume, start_date)

    # Surface errors visibly so you know what's failing
    if isinstance(whale_raw, tuple) and whale_raw[0] == "error":
        st.warning(f"Whale ratio error: {whale_raw[1]}")
        whale_raw = None
    if isinstance(spec_raw, tuple) and spec_raw[0] == "error":
        st.warning(f"Speculation ratio error: {spec_raw[1]}")
        spec_raw = None

    # ── Risk Score ────────────────────────────────────────────────────────────
    # Composite of both metrics normalised against their respective market averages:
    #   risk_score = (equations.calc_whale_metric(avg_whale, this_whale)
    #                 + equations.calc_whale_metric(avg_spec, this_spec)) / 2
    avg_spec, avg_whale = load_ratios()

    risk_score_raw = None
    try:
        from equations import calc_whale_metric
        if whale_raw is not None and spec_raw is not None and avg_whale is not None and avg_spec is not None:
            whale_component = calc_whale_metric(avg_whale, float(whale_raw))
            spec_component  = calc_whale_metric(avg_spec,  float(spec_raw))
            risk_score_raw  = 1- (whale_component + spec_component ) /2
    except Exception as e:
        st.warning(f"Risk score error: {e}")

    def fmt_whale(r):
        if r is None or r == 0:
            return "—"
        try:
            return f"{float(r):.1f}x"
        except (TypeError, ValueError):
            return "—"

    def fmt_risk(r):
        if r is None:
            return "—"
        try:
            v = float(r)
            return f"{v:.2f}" if v < 10 else f"{v:.1f}"
        except (TypeError, ValueError):
            return "—"

    whale_ratio_str       = fmt_whale(whale_raw)
    speculation_ratio_str = fmt_ratio(spec_raw)
    risk_score_str        = fmt_risk(risk_score_raw)

    # Countdown
    countdown_str = ""
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            delta  = end_dt - datetime.now(timezone.utc)
            if delta.total_seconds() > 0:
                days  = delta.days
                hours = delta.seconds // 3600
                countdown_str = str(days) + "d " + str(hours) + "h"
            else:
                countdown_str = "Closed"
        except: pass

    badge_url = get_badge_url(question)
    badge_img = ""
    if badge_url:
        badge_img = '<img style="width:56px;height:56px;object-fit:contain;flex-shrink:0;" src="' + badge_url + '" alt="">'

    yes_w     = str(yes_prob) + "%" if yes_prob is not None else "50%"
    no_w      = str(no_prob)  + "%" if no_prob  is not None else "50%"
    yes_label = str(yes_prob) + "%" if yes_prob is not None else "—"
    no_label  = str(no_prob)  + "%" if no_prob  is not None else "—"

    closes_html = ""
    if end_date:
        closes_html = 'Closes &nbsp;<span style="color:#888;">' + end_date + "</span>"
        if countdown_str:
            closes_html += '&nbsp;&nbsp;<span style="color:#37b8f7;font-weight:600;">' + countdown_str + " left</span>"

    desc_block = ""
    if description:
        desc_text = description[:600] + ("…" if len(description) > 600 else "")
        desc_block = (
            '<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);'
            'border-radius:12px;padding:22px 26px;margin-top:4px;">'
            '<div style="font-size:0.62rem;letter-spacing:0.16em;text-transform:uppercase;color:#444;margin-bottom:10px;">About this market</div>'
            '<div style="font-size:0.85rem;color:#777;line-height:1.75;">' + desc_text + '</div>'
            '</div>'
        )

    st.markdown(
        '<div style="padding:24px 40px 0;">'
        '<div style="display:flex;align-items:center;gap:20px;padding:24px 28px;'
        'background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:16px;margin-bottom:20px;">'
        + badge_img +
        '<div>'
        '<div style="font-family:Bebas Neue,sans-serif;font-size:1.8rem;letter-spacing:0.07em;color:#fff;line-height:1.2;margin-bottom:6px;">'
        + question +
        '</div>'
        '<div style="font-size:0.72rem;letter-spacing:0.12em;text-transform:uppercase;color:#555;">'
        + closes_html +
        '</div>'
        '</div></div></div>',
        unsafe_allow_html=True
    )

    # ── Stats rows ─────────────────────────────────────────────────────────────
    # Row 1: volume metrics
    # Row 2: whale ratio, speculation ratio, risk score
    row1 = [(fmt(volume), "Total Volume"), (fmt(volume24hr), "24h Volume"), (fmt(liquidity), "Liquidity")]
    row2 = [
        (whale_ratio_str,       "Whale Ratio"),
        (speculation_ratio_str, "Speculation Ratio"),
        (risk_score_str,        "Risk Score"),
    ]

    def stat_tile(val, label, accent=False):
        value_color = "#37b8f7" if accent and val != "—" else "#fff"
        return (
            '<div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.07);'
            'border-radius:12px;padding:20px;text-align:center;">'
            '<div style="font-family:Bebas Neue,sans-serif;font-size:1.8rem;color:' + value_color + ';letter-spacing:0.05em;">' + val + '</div>'
            '<div style="font-size:0.62rem;letter-spacing:0.14em;text-transform:uppercase;color:#555;margin-top:4px;">' + label + '</div>'
            '</div>'
        )

    for row in [row1, row2]:
        cols = st.columns(3)
        for col, (val, label) in zip(cols, row):
            with col:
                accent = label in ("Whale Ratio", "Speculation Ratio", "Risk Score")
                st.markdown(stat_tile(val, label, accent=accent), unsafe_allow_html=True)

    # Odds
    st.markdown(
        '<div style="padding:20px 40px 0;">'
        '<div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:24px 28px;">'
        '<div style="font-size:0.62rem;letter-spacing:0.16em;text-transform:uppercase;color:#555;margin-bottom:18px;">Current Odds</div>'
        '<div style="display:flex;align-items:center;gap:14px;margin-bottom:12px;">'
        '<div style="font-size:0.82rem;font-weight:600;color:#aaa;width:34px;">YES</div>'
        '<div style="flex:1;height:12px;background:rgba(255,255,255,0.06);border-radius:99px;overflow:hidden;">'
        '<div style="height:100%;width:' + yes_w + ';background:linear-gradient(90deg,#37b8f7,#7b5ff5);border-radius:99px;"></div></div>'
        '<div style="font-family:Bebas Neue,sans-serif;font-size:1.2rem;color:#fff;width:48px;text-align:right;">' + yes_label + '</div>'
        '</div>'
        '<div style="display:flex;align-items:center;gap:14px;">'
        '<div style="font-size:0.82rem;font-weight:600;color:#aaa;width:34px;">NO</div>'
        '<div style="flex:1;height:12px;background:rgba(255,255,255,0.06);border-radius:99px;overflow:hidden;">'
        '<div style="height:100%;width:' + no_w + ';background:rgba(255,255,255,0.2);border-radius:99px;"></div></div>'
        '<div style="font-family:Bebas Neue,sans-serif;font-size:1.2rem;color:#fff;width:48px;text-align:right;">' + no_label + '</div>'
        '</div>'
        '</div></div>'
        + ('<div style="padding:16px 40px 0;">' + desc_block + '</div>' if desc_block else ''),
        unsafe_allow_html=True
    )

    # Price history chart
    if price_history:
        import pandas as pd
        import altair as alt
        df = pd.DataFrame(price_history)
        if len(df.columns) == 2:
            df.columns = ["time", "price"]
        df["time"]  = pd.to_datetime(df["time"], unit="s", errors="coerce")
        df["price"] = pd.to_numeric(df["price"], errors="coerce") * 100
        df = df.dropna()
        if not df.empty:
            chart = (
                alt.Chart(df)
                .mark_area(
                    line={"color": "#37b8f7", "strokeWidth": 2},
                    color=alt.Gradient(
                        gradient="linear",
                        stops=[
                            alt.GradientStop(color="rgba(55,184,247,0.25)", offset=0),
                            alt.GradientStop(color="rgba(55,184,247,0.0)",  offset=1),
                        ],
                        x1=0, x2=0, y1=1, y2=0,
                    ),
                )
                .encode(
                    x=alt.X("time:T", axis=alt.Axis(format="%b %d", labelColor="#555", tickColor="#333", domainColor="#333", gridColor="rgba(255,255,255,0.04)")),
                    y=alt.Y("price:Q", title="YES %", scale=alt.Scale(domain=[0, 100]), axis=alt.Axis(labelColor="#555", tickColor="#333", domainColor="#333", gridColor="rgba(255,255,255,0.04)")),
                    tooltip=[alt.Tooltip("time:T", title="Date", format="%b %d %Y"), alt.Tooltip("price:Q", title="YES %", format=".1f")],
                )
                .properties(height=240, background="transparent")
                .configure_view(strokeWidth=0)
            )
            st.markdown('<div style="padding:20px 40px 0;"><div style="font-size:0.62rem;letter-spacing:0.16em;text-transform:uppercase;color:#444;margin-bottom:8px;">Price History (YES %)</div></div>', unsafe_allow_html=True)
            st.altair_chart(chart, use_container_width=True)
# ══════════════════════════════════════════════════════════════════════════════
screen = st.session_state.screen
if screen == "menu":
    menu()
elif screen == "prem":
    prem()
elif screen == "single_bet":
    single_bet()