import pytrends
from pytrends.request import TrendReq
import time

pytrends = TrendReq(hl='en-GB', tz=0)


def scrape_trends(keyword: str, start_date: str) -> dict:
    """
    Get Google Trends data for a keyword from start_date to now.
    Returns dict with interest scores and related queries.
    """
    try:
        pytrends.build_payload(
            kw_list   = [keyword],
            timeframe = f"{start_date} {time.strftime('%Y-%m-%d')}",
            geo       = "GB",          # UK-focused since Premier League
        )

        interest    = pytrends.interest_over_time()
        related     = pytrends.related_queries()

        if interest.empty:
            return {"peak": 0, "mean": 0, "current": 0, "related": []}

        scores = interest[keyword].tolist()

        return {
            "peak":    max(scores),
            "mean":    round(sum(scores) / len(scores), 2),
            "current": scores[-1],                              # most recent value
            "related": related[keyword]["top"]["query"].tolist()[:5] if related[keyword]["top"] is not None else []
        }

    except Exception as e:
        print(f"  Trends error for '{keyword}': {e}")
        return {"peak": 0, "mean": 0, "current": 0, "related": []}