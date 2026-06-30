from __future__ import annotations

import json
import math
import time
from datetime import datetime, timezone
from html import escape
from typing import Any, Callable

import requests
from flask import Flask, abort, url_for

app = Flask(__name__)

GAMMA_API = "https://gamma-api.polymarket.com"
DATA_API = "https://data-api.polymarket.com"
REQUEST_TIMEOUT = 8
session = requests.Session()
_cache: dict[tuple[str, Any], tuple[float, Any]] = {}


LEAGUE_CONFIG = {
    "prem": {
        "tag_id": 82,
        "title": "Premier League Markets",
        "logo": "https://upload.wikimedia.org/wikipedia/en/f/f2/Premier_League_Logo.svg",
        "label": "Premier League",
    },
    "nba": {
        "tag_id": 745,
        "title": "NBA Markets",
        "logo": "https://a.espncdn.com/i/teamlogos/leagues/500/nba.png",
        "label": "NBA",
    },
}


CLUB_BADGES = {
    "Arsenal": "https://a.espncdn.com/i/teamlogos/soccer/500/359.png",
    "Aston Villa": "https://a.espncdn.com/i/teamlogos/soccer/500/362.png",
    "Bournemouth": "https://a.espncdn.com/i/teamlogos/soccer/500/349.png",
    "Brentford": "https://a.espncdn.com/i/teamlogos/soccer/500/337.png",
    "Brighton": "https://a.espncdn.com/i/teamlogos/soccer/500/331.png",
    "Chelsea": "https://a.espncdn.com/i/teamlogos/soccer/500/363.png",
    "Crystal Palace": "https://a.espncdn.com/i/teamlogos/soccer/500/384.png",
    "Everton": "https://a.espncdn.com/i/teamlogos/soccer/500/368.png",
    "Fulham": "https://a.espncdn.com/i/teamlogos/soccer/500/370.png",
    "Ipswich Town": "https://a.espncdn.com/i/teamlogos/soccer/500/QuoteIPSWICH.png",
    "Ipswich": "https://a.espncdn.com/i/teamlogos/soccer/500/QuoteIPSWICH.png",
    "Leicester City": "https://a.espncdn.com/i/teamlogos/soccer/500/375.png",
    "Leicester": "https://a.espncdn.com/i/teamlogos/soccer/500/375.png",
    "Liverpool": "https://a.espncdn.com/i/teamlogos/soccer/500/364.png",
    "Manchester City": "https://a.espncdn.com/i/teamlogos/soccer/500/382.png",
    "Man City": "https://a.espncdn.com/i/teamlogos/soccer/500/382.png",
    "Manchester United": "https://a.espncdn.com/i/teamlogos/soccer/500/360.png",
    "Man United": "https://a.espncdn.com/i/teamlogos/soccer/500/360.png",
    "Newcastle United": "https://a.espncdn.com/i/teamlogos/soccer/500/361.png",
    "Newcastle": "https://a.espncdn.com/i/teamlogos/soccer/500/361.png",
    "Nottingham Forest": "https://a.espncdn.com/i/teamlogos/soccer/500/393.png",
    "Southampton": "https://a.espncdn.com/i/teamlogos/soccer/500/376.png",
    "Tottenham Hotspur": "https://a.espncdn.com/i/teamlogos/soccer/500/367.png",
    "Tottenham": "https://a.espncdn.com/i/teamlogos/soccer/500/367.png",
    "Spurs": "https://a.espncdn.com/i/teamlogos/soccer/500/367.png",
    "West Ham United": "https://a.espncdn.com/i/teamlogos/soccer/500/371.png",
    "West Ham": "https://a.espncdn.com/i/teamlogos/soccer/500/371.png",
    "Wolverhampton": "https://a.espncdn.com/i/teamlogos/soccer/500/380.png",
    "Wolves": "https://a.espncdn.com/i/teamlogos/soccer/500/380.png",
}


NBA_BADGES = {
    "Atlanta Hawks": "https://a.espncdn.com/i/teamlogos/nba/500/atl.png",
    "Boston Celtics": "https://a.espncdn.com/i/teamlogos/nba/500/bos.png",
    "Brooklyn Nets": "https://a.espncdn.com/i/teamlogos/nba/500/bkn.png",
    "Charlotte Hornets": "https://a.espncdn.com/i/teamlogos/nba/500/cha.png",
    "Chicago Bulls": "https://a.espncdn.com/i/teamlogos/nba/500/chi.png",
    "Cleveland Cavaliers": "https://a.espncdn.com/i/teamlogos/nba/500/cle.png",
    "Dallas Mavericks": "https://a.espncdn.com/i/teamlogos/nba/500/dal.png",
    "Denver Nuggets": "https://a.espncdn.com/i/teamlogos/nba/500/den.png",
    "Detroit Pistons": "https://a.espncdn.com/i/teamlogos/nba/500/det.png",
    "Golden State Warriors": "https://a.espncdn.com/i/teamlogos/nba/500/gs.png",
    "Houston Rockets": "https://a.espncdn.com/i/teamlogos/nba/500/hou.png",
    "Indiana Pacers": "https://a.espncdn.com/i/teamlogos/nba/500/ind.png",
    "LA Clippers": "https://a.espncdn.com/i/teamlogos/nba/500/lac.png",
    "Los Angeles Clippers": "https://a.espncdn.com/i/teamlogos/nba/500/lac.png",
    "LA Lakers": "https://a.espncdn.com/i/teamlogos/nba/500/lal.png",
    "Los Angeles Lakers": "https://a.espncdn.com/i/teamlogos/nba/500/lal.png",
    "Memphis Grizzlies": "https://a.espncdn.com/i/teamlogos/nba/500/mem.png",
    "Miami Heat": "https://a.espncdn.com/i/teamlogos/nba/500/mia.png",
    "Milwaukee Bucks": "https://a.espncdn.com/i/teamlogos/nba/500/mil.png",
    "Minnesota Timberwolves": "https://a.espncdn.com/i/teamlogos/nba/500/min.png",
    "New Orleans Pelicans": "https://a.espncdn.com/i/teamlogos/nba/500/no.png",
    "New York Knicks": "https://a.espncdn.com/i/teamlogos/nba/500/ny.png",
    "Oklahoma City Thunder": "https://a.espncdn.com/i/teamlogos/nba/500/okc.png",
    "Orlando Magic": "https://a.espncdn.com/i/teamlogos/nba/500/orl.png",
    "Philadelphia 76ers": "https://a.espncdn.com/i/teamlogos/nba/500/phi.png",
    "Phoenix Suns": "https://a.espncdn.com/i/teamlogos/nba/500/phx.png",
    "Portland Trail Blazers": "https://a.espncdn.com/i/teamlogos/nba/500/por.png",
    "Sacramento Kings": "https://a.espncdn.com/i/teamlogos/nba/500/sac.png",
    "San Antonio Spurs": "https://a.espncdn.com/i/teamlogos/nba/500/sa.png",
    "Toronto Raptors": "https://a.espncdn.com/i/teamlogos/nba/500/tor.png",
    "Utah Jazz": "https://a.espncdn.com/i/teamlogos/nba/500/utah.png",
    "Washington Wizards": "https://a.espncdn.com/i/teamlogos/nba/500/wsh.png",
}


ALL_BADGES = {**CLUB_BADGES, **NBA_BADGES}


def cached(key: tuple[str, Any], ttl: int, loader: Callable[[], Any]) -> Any:
    now = time.time()
    cached_value = _cache.get(key)
    if cached_value and now - cached_value[0] < ttl:
        return cached_value[1]
    value = loader()
    _cache[key] = (now, value)
    return value


def http_get_json(url: str, **params: Any) -> Any:
    response = session.get(url, params=params, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()


def get_badge_url(question: str) -> str | None:
    q = question.lower()
    for team in sorted(ALL_BADGES.keys(), key=len, reverse=True):
        if team.lower() in q:
            return ALL_BADGES[team]
    return None


def safe_float(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def fmt_money(value: Any) -> str:
    n = safe_float(value)
    if n >= 1_000_000:
        return f"${n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"${n / 1_000:.1f}K"
    return f"${n:.0f}"


def fmt_ratio(value: Any, suffix: str = "") -> str:
    if value in (None, ""):
        return "-"
    try:
        n = float(value)
    except (TypeError, ValueError):
        return "-"
    body = f"{n:.0f}" if n >= 10 else f"{n:.2f}"
    return f"{body}{suffix}"


def parse_outcome_prices(value: Any) -> tuple[float | None, float | None]:
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            value = []
    if not isinstance(value, list) or len(value) < 2:
        return None, None
    try:
        return round(float(value[0]) * 100, 1), round(float(value[1]) * 100, 1)
    except (TypeError, ValueError):
        return None, None


def load_ratios() -> tuple[float | None, float | None]:
    try:
        with open("ratios.txt", "r", encoding="utf-8") as ratio_file:
            lines = [line.strip() for line in ratio_file.readlines() if line.strip()]
        speculation = float(lines[0]) if len(lines) > 0 else None
        whale = float(lines[1]) if len(lines) > 1 else None
        return speculation, whale
    except (OSError, ValueError):
        return 25.0, 25.0


def fetch_markets(league: str) -> list[dict[str, Any]]:
    if league not in LEAGUE_CONFIG:
        abort(404)

    def loader() -> list[dict[str, Any]]:
        cfg = LEAGUE_CONFIG[league]
        events = http_get_json(
            f"{GAMMA_API}/events",
            tag_id=cfg["tag_id"],
            active="true",
            closed="false",
            order="volume",
            ascending="false",
            limit=50,
        )
        markets: list[dict[str, Any]] = []
        for event in events:
            for market in event.get("markets", []):
                markets.append(
                    {
                        "id": market.get("id"),
                        "conditionId": market.get("conditionId"),
                        "question": market.get("question", ""),
                        "volume": safe_float(market.get("volume")),
                        "volume24hr": safe_float(market.get("volume24hr")),
                        "liquidity": safe_float(market.get("liquidity")),
                        "startDate": event.get("startDate", ""),
                        "endDate": market.get("endDate"),
                        "outcomePrices": market.get("outcomePrices"),
                        "bestAsk": market.get("bestAsk"),
                    }
                )
        markets.sort(key=lambda market: market["volume"], reverse=True)
        return markets[:50]

    return cached(("markets", league), 120, loader)


def fetch_market_detail(market_id: str) -> dict[str, Any]:
    return cached(
        ("market", market_id),
        60,
        lambda: http_get_json(f"{GAMMA_API}/markets/{market_id}"),
    )


def single_whale_ratio(condition_id: str | None) -> float | None:
    if not condition_id:
        return None

    def loader() -> float | None:
        try:
            from whalescore import single_whale_ratio as calculate_whale_ratio

            value = calculate_whale_ratio(condition_id)
            return value or None
        except Exception:
            return None

    return cached(("whale", condition_id), 300, loader)


def calc_risk_score(avg_whale: float | None, whale_ratio: float | None) -> float | None:
    if avg_whale in (None, 0) or whale_ratio in (None, 0):
        return None
    k = 0.1
    component = 1 / (1 + math.exp(-k * (float(whale_ratio) - float(avg_whale))))
    return 1 - component


def end_date_label(end_date: Any) -> str:
    if not end_date:
        return "No listed close"
    date_text = str(end_date)[:10]
    try:
        end_dt = datetime.strptime(date_text, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        delta = end_dt - datetime.now(timezone.utc)
        if delta.total_seconds() <= 0:
            return f"Closed {date_text}"
        return f"Closes {date_text} ({delta.days}d {delta.seconds // 3600}h left)"
    except ValueError:
        return f"Closes {date_text}"


def layout(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      color-scheme: dark;
      --bg: #090b10;
      --panel: #111821;
      --panel-strong: #151e29;
      --line: rgba(255,255,255,.09);
      --muted: #8d98a6;
      --text: #f3f7fb;
      --accent: #30b7df;
      --accent-2: #9fd35f;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: "DM Sans", system-ui, sans-serif;
    }}
    a {{ color: inherit; text-decoration: none; }}
    .shell {{ min-height: 100vh; }}
    .hero {{
      min-height: 38vh;
      display: grid;
      place-items: center;
      padding: 56px 20px 34px;
      background:
        linear-gradient(rgba(9,11,16,.18), rgba(9,11,16,.92)),
        url("https://images.unsplash.com/photo-1511882150382-421056c89033?auto=format&fit=crop&w=1800&q=80") center/cover;
      border-bottom: 1px solid var(--line);
    }}
    .hero-inner {{ width: min(1100px, 100%); }}
    .kicker {{
      color: var(--accent-2);
      font-size: .74rem;
      font-weight: 700;
      letter-spacing: .18em;
      text-transform: uppercase;
    }}
    h1 {{
      margin: 10px 0 8px;
      font-family: "Bebas Neue", sans-serif;
      font-size: clamp(3rem, 8vw, 6.5rem);
      line-height: .88;
      font-weight: 400;
    }}
    .subtitle {{ max-width: 680px; color: #d2dae4; line-height: 1.65; margin: 0; }}
    .page {{ width: min(1180px, 100%); margin: 0 auto; padding: 26px 18px 60px; }}
    .topbar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 18px 20px;
      border-bottom: 1px solid var(--line);
      background: rgba(9,11,16,.82);
      position: sticky;
      top: 0;
      z-index: 10;
      backdrop-filter: blur(12px);
    }}
    .brand {{
      font-family: "Bebas Neue", sans-serif;
      font-size: 1.6rem;
      letter-spacing: .07em;
    }}
    .nav {{ display: flex; gap: 10px; flex-wrap: wrap; justify-content: flex-end; }}
    .pill {{
      border: 1px solid var(--line);
      border-radius: 7px;
      padding: 9px 13px;
      color: #d8e2ec;
      background: rgba(255,255,255,.035);
      font-size: .88rem;
    }}
    .pill:hover, .card:hover {{ border-color: rgba(48,183,223,.55); }}
    .section-title {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin: 2px 0 18px;
    }}
    .section-title h2 {{
      margin: 0;
      font-family: "Bebas Neue", sans-serif;
      letter-spacing: .06em;
      font-size: clamp(2rem, 4vw, 3rem);
      font-weight: 400;
    }}
    .league-logo {{ width: 52px; height: 52px; object-fit: contain; }}
    .league-grid, .cards-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 16px;
    }}
    .league-card, .card, .detail-panel, .metric {{
      background: linear-gradient(180deg, var(--panel-strong), var(--panel));
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: 0 18px 44px rgba(0,0,0,.22);
    }}
    .league-card {{
      min-height: 210px;
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      justify-content: flex-end;
      gap: 18px;
      padding: 24px;
    }}
    .league-card img {{ width: 72px; height: 72px; object-fit: contain; }}
    .league-card strong {{
      font-family: "Bebas Neue", sans-serif;
      letter-spacing: .08em;
      font-size: 2rem;
      font-weight: 400;
    }}
    .card {{ display: block; padding: 18px; transition: border-color .18s, transform .18s; }}
    .card:hover {{ transform: translateY(-2px); }}
    .card-head {{ display: flex; gap: 12px; align-items: flex-start; min-height: 76px; }}
    .badge {{ width: 36px; height: 36px; object-fit: contain; flex: 0 0 36px; }}
    .question {{ font-weight: 700; line-height: 1.42; }}
    .stats {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 8px;
      margin-top: 16px;
      padding-top: 14px;
      border-top: 1px solid var(--line);
    }}
    .stat-value {{
      font-family: "Bebas Neue", sans-serif;
      font-size: 1.35rem;
      letter-spacing: .04em;
    }}
    .stat-label {{
      color: var(--muted);
      font-size: .68rem;
      text-transform: uppercase;
      letter-spacing: .08em;
    }}
    .detail-panel {{ padding: 24px; }}
    .detail-head {{ display: flex; gap: 18px; align-items: center; margin-bottom: 22px; }}
    .detail-head img {{ width: 62px; height: 62px; object-fit: contain; }}
    .detail-head h2 {{
      font-family: "Bebas Neue", sans-serif;
      letter-spacing: .05em;
      font-size: clamp(2rem, 4vw, 3.2rem);
      line-height: 1;
      margin: 0 0 8px;
      font-weight: 400;
    }}
    .muted {{ color: var(--muted); }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 12px;
      margin: 20px 0;
    }}
    .metric {{ padding: 16px; }}
    .metric .stat-value {{ color: var(--accent); }}
    .odds-row {{
      display: grid;
      grid-template-columns: 42px 1fr 52px;
      gap: 12px;
      align-items: center;
      margin: 12px 0;
      color: #dfe8f2;
      font-weight: 700;
    }}
    .bar {{ height: 12px; border-radius: 999px; background: rgba(255,255,255,.09); overflow: hidden; }}
    .bar span {{ display: block; height: 100%; background: linear-gradient(90deg, var(--accent), var(--accent-2)); }}
    .description {{ color: #c0cad5; line-height: 1.72; margin-top: 18px; white-space: pre-wrap; }}
    .error {{
      border: 1px solid rgba(255, 180, 80, .28);
      background: rgba(255, 180, 80, .08);
      color: #ffd9a0;
      padding: 16px;
      border-radius: 8px;
    }}
    @media (max-width: 680px) {{
      .topbar {{ align-items: flex-start; flex-direction: column; }}
      .nav {{ justify-content: flex-start; }}
      .hero {{ place-items: end start; min-height: 44vh; }}
      .stats {{ grid-template-columns: 1fr; }}
      .detail-head {{ align-items: flex-start; flex-direction: column; }}
    }}
  </style>
</head>
<body>
  <div class="shell">
    <header class="topbar">
      <a class="brand" href="{url_for("home")}">Polymarket Event Risk</a>
      <nav class="nav">
        <a class="pill" href="{url_for("markets", league="prem")}">Premier League</a>
        <a class="pill" href="{url_for("markets", league="nba")}">NBA</a>
        <a class="pill" href="{url_for("health")}">Health</a>
      </nav>
    </header>
    {body}
  </div>
</body>
</html>"""


def hero() -> str:
    return """
<section class="hero">
  <div class="hero-inner">
    <div class="kicker">Polymarket analytics</div>
    <h1>Event Risk Manager</h1>
    <p class="subtitle">Track live sports markets, compare liquidity and volume, and inspect wallet concentration signals from a Vercel-hosted Python app.</p>
  </div>
</section>"""


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "entrypoint": "app:app"}


@app.get("/")
def home() -> str:
    cards = []
    for key, cfg in LEAGUE_CONFIG.items():
        cards.append(
            f"""<a class="league-card" href="{url_for("markets", league=key)}">
  <img src="{escape(cfg["logo"])}" alt="">
  <strong>{escape(cfg["label"])}</strong>
  <span class="muted">Top 50 active markets</span>
</a>"""
        )
    body = (
        hero()
        + '<main class="page"><div class="league-grid">'
        + "".join(cards)
        + "</div></main>"
    )
    return layout("Polymarket Event Risk Manager", body)


@app.get("/markets/<league>")
def markets(league: str) -> str:
    if league not in LEAGUE_CONFIG:
        abort(404)
    cfg = LEAGUE_CONFIG[league]
    try:
        market_data = fetch_markets(league)
    except requests.RequestException as exc:
        body = f'<main class="page"><div class="error">Could not load Polymarket markets: {escape(str(exc))}</div></main>'
        return layout(cfg["title"], body), 502

    cards = []
    for market in market_data:
        question = str(market.get("question", ""))
        badge = get_badge_url(question)
        badge_html = f'<img class="badge" src="{escape(badge)}" alt="">' if badge else '<div class="badge"></div>'
        cards.append(
            f"""<a class="card" href="{url_for("market_detail", league=league, market_id=market["id"])}">
  <div class="card-head">
    {badge_html}
    <div class="question">{escape(question)}</div>
  </div>
  <div class="stats">
    <div><div class="stat-value">{fmt_money(market["volume"])}</div><div class="stat-label">Volume</div></div>
    <div><div class="stat-value">{fmt_money(market["volume24hr"])}</div><div class="stat-label">24h</div></div>
    <div><div class="stat-value">{fmt_money(market["liquidity"])}</div><div class="stat-label">Liquidity</div></div>
  </div>
</a>"""
        )

    body = f"""
<main class="page">
  <div class="section-title">
    <h2>{escape(cfg["title"])}</h2>
    <img class="league-logo" src="{escape(cfg["logo"])}" alt="">
  </div>
  <div class="cards-grid">{"".join(cards)}</div>
</main>"""
    return layout(cfg["title"], body)


@app.get("/market/<league>/<market_id>")
def market_detail(league: str, market_id: str) -> str:
    if league not in LEAGUE_CONFIG:
        abort(404)
    try:
        market = fetch_market_detail(market_id)
    except requests.RequestException as exc:
        body = f'<main class="page"><div class="error">Could not load market detail: {escape(str(exc))}</div></main>'
        return layout("Market detail", body), 502

    question = str(market.get("question") or "Market detail")
    badge = get_badge_url(question)
    badge_html = f'<img src="{escape(badge)}" alt="">' if badge else ""
    volume = safe_float(market.get("volume"))
    volume24hr = safe_float(market.get("volume24hr"))
    liquidity = safe_float(market.get("liquidity"))
    yes_prob, no_prob = parse_outcome_prices(market.get("outcomePrices"))
    yes_width = max(0, min(100, yes_prob if yes_prob is not None else 50))
    no_width = max(0, min(100, no_prob if no_prob is not None else 50))
    avg_spec, avg_whale = load_ratios()
    whale_ratio = single_whale_ratio(market.get("conditionId"))
    risk_score = calc_risk_score(avg_whale, whale_ratio)
    description = str(market.get("description") or "").strip()
    if len(description) > 900:
        description = description[:900].rstrip() + "..."

    body = f"""
<main class="page">
  <a class="pill" href="{url_for("markets", league=league)}">Back to {escape(LEAGUE_CONFIG[league]["label"])}</a>
  <section class="detail-panel" style="margin-top:18px;">
    <div class="detail-head">
      {badge_html}
      <div>
        <h2>{escape(question)}</h2>
        <div class="muted">{escape(end_date_label(market.get("endDate")))}</div>
      </div>
    </div>
    <div class="metrics">
      <div class="metric"><div class="stat-value">{fmt_money(volume)}</div><div class="stat-label">Total Volume</div></div>
      <div class="metric"><div class="stat-value">{fmt_money(volume24hr)}</div><div class="stat-label">24h Volume</div></div>
      <div class="metric"><div class="stat-value">{fmt_money(liquidity)}</div><div class="stat-label">Liquidity</div></div>
      <div class="metric"><div class="stat-value">{fmt_ratio(whale_ratio, "x")}</div><div class="stat-label">Whale Ratio</div></div>
      <div class="metric"><div class="stat-value">{fmt_ratio(avg_spec)}</div><div class="stat-label">Avg Speculation</div></div>
      <div class="metric"><div class="stat-value">{fmt_ratio(risk_score)}</div><div class="stat-label">Whale Risk Score</div></div>
    </div>
    <div>
      <div class="stat-label">Current Odds</div>
      <div class="odds-row"><span>YES</span><div class="bar"><span style="width:{yes_width}%"></span></div><span>{fmt_ratio(yes_prob, "%")}</span></div>
      <div class="odds-row"><span>NO</span><div class="bar"><span style="width:{no_width}%"></span></div><span>{fmt_ratio(no_prob, "%")}</span></div>
    </div>
    {f'<div class="description">{escape(description)}</div>' if description else ""}
  </section>
</main>"""
    return layout(question, body)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
