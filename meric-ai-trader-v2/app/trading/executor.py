from app.core.config import settings
from app.exchange.binance import BinanceFuturesClient

class TradeExecutor:
    def __init__(self, client: BinanceFuturesClient):
        self.client=client

    async def open(self, symbol: str, direction: str, qty: float, leverage: int):
        side="BUY" if direction=="LONG" else "SELL"
        if settings.trading_mode != "live":
            return {"paper": True, "symbol": symbol, "side": side, "qty": qty}
        await self.client.set_leverage(symbol, leverage)
        return await self.client.market_order(symbol, side, qty, direction)

    async def close(self, symbol: str, direction: str, qty: float):
        side="SELL" if direction=="LONG" else "BUY"
        if settings.trading_mode != "live":
            return {"paper": True, "symbol": symbol, "side": side, "qty": qty, "reduceOnly": True}
        return await self.client.market_order(symbol, side, qty, direction, reduce_only=True)
