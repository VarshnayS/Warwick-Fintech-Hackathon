
import requests
from datetime import datetime, timedelta
import json

class Bet:
    GAMMA = "https://gamma-api.polymarket.com"
    CLOB = "https://clob.polymarket.com"
    
    def __init__(self, id):
        self.conditionId = id

        self.question = None
        self.price = None
        self.volume = None
        self.liquidity = None
        self.token_id = None
    
      # Auto-fetch everything
        self.fetch_market_data()
        self.fetch_orderbook()
        self.fetch_trades()   
    
    def fetch_market_data(self):
        r = requests.get(f"{self.GAMMA}/markets/{self.conditionId}")
        print(r.status_code)
        print(r.text)
        r.raise_for_status()
        data = r.json()

        self.question = data.get("question")
        self.price = data.get("outcomePrices", [])
        self.volume = float(data.get("volume", 0))
        self.liquidity = float(data.get("liquidity", 0))

        token_ids_raw = data.get("clobTokenIds", "[]")
        token_ids = json.loads(token_ids_raw)

        if not token_ids:
            raise Exception("No CLOB token IDs found")

        self.token_id = token_ids[0]

    # def fetch_orderbook(self):
    #     r = requests.get(
    #         f"{self.CLOB}/book",
    #         params={"token_id": self.token_id}
    #     )
    #     r.raise_for_status()
    #     book = r.json()

    #     self.bids = [(float(p), float(s)) for p, s in book.get("bids", [])]
    #     self.asks = [(float(p), float(s)) for p, s in book.get("asks", [])]
    def fetch_orderbook(self):
        r = requests.get(
            f"{self.CLOB}/book",
            params={"token_id": self.token_id}
        )
        r.raise_for_status()
        book = r.json()

        # Each entry is a dict: {"price": "0.53", "size": "150.0"}
        self.bids = [(float(b["price"]), float(b["size"])) for b in book.get("bids", [])]
        self.asks = [(float(a["price"]), float(a["size"])) for a in book.get("asks", [])]
        # -------------------------
    # 3️⃣ Trades (Last 4 Weeks)
    # -------------------------
    def fetch_trades(self):
        r = requests.get(
            "https://data-api.polymarket.com/trades",
            params={"market": self.token_id, "limit": 1000}
        )
        r.raise_for_status()
        trades = r.json()

        four_weeks_ago = datetime.utcnow() - timedelta(weeks=4)
        four_weeks_ago_ts = four_weeks_ago.timestamp()  # convert to Unix

        self.trades_4w = [
            t for t in trades
            if t["timestamp"] > four_weeks_ago_ts
        ]

        self.total_trades_4w = len(self.trades_4w)

    # -------------------------
    # 4️⃣ Useful Metrics
    # -------------------------
    def spread(self):
        if not self.bids or not self.asks:
            return None
        return self.asks[0][0] - self.bids[0][0]

    def depth_to_move_up(self, percent=0.05):
        if not self.asks:
            return 0

        best_ask = self.asks[0][0]
        target_price = best_ask * (1 + percent)

        total_size = 0
        for price, size in self.asks:
            if price <= target_price:
                total_size += size
            else:
                break
        return total_size

    def summary(self):
        print("\n========================")
        print("Market:", self.question)
        print("Price:", self.price)
        print("Volume:", self.volume)
        print("Liquidity:", self.liquidity)
        print("Trades (4w):", self.total_trades_4w)
        print("Spread:", self.spread())
        print("Depth +5%:", self.depth_to_move_up())
        print("========================\n")
    
