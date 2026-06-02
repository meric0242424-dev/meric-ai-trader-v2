import time, hmac, hashlib
from urllib.parse import urlencode
import httpx
from app.core.config import settings

class BinanceFuturesClient:
    def __init__(self):
        self.base = settings.binance_base
        self.key = settings.binance_api_key
        self.secret = settings.binance_api_secret

    def _headers(self):
        return {"X-MBX-APIKEY": self.key}

    def _sign(self, params: dict) -> str:
        query = urlencode(params, doseq=True)
        return hmac.new(self.secret.encode(), query.encode(), hashlib.sha256).hexdigest()

    async def request(self, method: str, path: str, params: dict | None = None, signed: bool = False):
        params = params or {}
        if signed:
            params["timestamp"] = int(time.time() * 1000)
            params["signature"] = self._sign(params)
        async with httpx.AsyncClient(timeout=15) as c:
            r = await c.request(method, self.base + path, params=params, headers=self._headers())
            if r.status_code >= 400:
                raise RuntimeError(f"Binance {method} {path} {r.status_code}: {r.text[:300]}")
            return r.json()

    async def price(self, symbol: str) -> float:
        d = await self.request("GET", "/fapi/v1/ticker/price", {"symbol": symbol})
        return float(d["price"])

    async def klines(self, symbol: str, interval: str, limit: int = 150):
        return await self.request("GET", "/fapi/v1/klines", {"symbol": symbol, "interval": interval, "limit": limit})

    async def account_balance(self) -> float:
        d = await self.request("GET", "/fapi/v2/account", signed=True)
        for a in d.get("assets", []):
            if a["asset"] == "USDT":
                return float(a["availableBalance"])
        return 0.0

    async def open_interest(self, symbol: str) -> float:
        d = await self.request("GET", "/fapi/v1/openInterest", {"symbol": symbol})
        return float(d.get("openInterest", 0))

    async def funding_rate(self, symbol: str) -> float:
        d = await self.request("GET", "/fapi/v1/premiumIndex", {"symbol": symbol})
        return float(d.get("lastFundingRate", 0))

    async def exchange_symbols(self) -> list[str]:
        d = await self.request("GET", "/fapi/v1/exchangeInfo")
        return [s["symbol"] for s in d.get("symbols", []) if s.get("contractType") == "PERPETUAL" and s.get("quoteAsset") == "USDT" and s.get("status") == "TRADING"]

    async def set_leverage(self, symbol: str, leverage: int):
        return await self.request("POST", "/fapi/v1/leverage", {"symbol": symbol, "leverage": leverage}, signed=True)

    async def market_order(self, symbol: str, side: str, qty: float, position_side: str, reduce_only: bool = False):
        params = {"symbol": symbol, "side": side, "type": "MARKET", "quantity": qty, "positionSide": position_side}
        if reduce_only:
            params["reduceOnly"] = "true"
        return await self.request("POST", "/fapi/v1/order", params, signed=True)
