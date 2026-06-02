import asyncio
import datetime
from app.core.config import settings
from app.exchange.binance import BinanceFuturesClient
from app.ai.score_engine import AIScoreEngine
from app.risk.risk_manager import RiskManager
from app.trading.executor import TradeExecutor
from app.trading.state import state
from app.notifications.telegram import telegram_send

DEFAULT_SYMBOLS=["BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT","XRPUSDT","ADAUSDT","DOGEUSDT","LINKUSDT","AVAXUSDT","LTCUSDT"]

class ScannerService:
    def __init__(self):
        self.client=BinanceFuturesClient()
        self.ai=AIScoreEngine()
        self.risk=RiskManager()
        self.executor=TradeExecutor(self.client)
        self.task=None
        self.symbols=state.config.get("symbols", DEFAULT_SYMBOLS)

    async def start(self):
        if state.running: return False
        state.running=True
        self.symbols=state.config.get("symbols", DEFAULT_SYMBOLS)
        state.log(f"Bot başlatıldı | Mod:{settings.trading_mode} | Coin:{len(self.symbols)}", "SUCCESS")
        self.task=asyncio.create_task(self.loop())
        return True

    async def stop(self):
        state.running=False
        if self.task: self.task.cancel()
        state.log("Bot durduruldu", "WARN")
        return True

    async def scan_symbol(self, symbol: str):
        k15,k1h,k4h = await asyncio.gather(
            self.client.klines(symbol,"15m",150),
            self.client.klines(symbol,"1h",150),
            self.client.klines(symbol,"4h",120),
        )
        funding=0.0; oi=0.0
        try: funding = await self.client.funding_rate(symbol)
        except Exception: pass
        try: oi = await self.client.open_interest(symbol)
        except Exception: pass
        sig=self.ai.analyze(symbol,k15,k1h,k4h,funding,oi)
        state.signals.insert(0,sig); state.signals=state.signals[:150]
        direction_filter = state.config.get("direction", "both")
        if sig["direction"]=="NEUTRAL":
            return
        if direction_filter == "long" and sig["direction"] != "LONG":
            return
        if direction_filter == "short" and sig["direction"] != "SHORT":
            return
        if sig["score"] < state.config.get("min_ai_score", settings.min_ai_score):
            return
        balance=1000.0 if settings.trading_mode != "live" else await self.client.account_balance()
        leverage = int(state.config.get("default_leverage", settings.default_leverage))
        rd=self.risk.check(balance, len(state.open_positions), sig["price"], sig["sl"], leverage)
        if not rd.allowed:
            state.log(f"Risk reddi {symbol}: {rd.reason}", "WARN")
            return
        order=await self.executor.open(symbol, sig["direction"], rd.qty, leverage)
        state.open_positions[symbol]={**sig,"qty":rd.qty,"order":order,"opened_at":datetime.datetime.now().strftime("%H:%M:%S"),"leverage":leverage}
        state.daily_trades += 1
        msg=f"{sig['direction']} {symbol} | AI:{sig['score']} | Entry:{sig['price']} SL:{sig['sl']} TP:{sig['tp']} Qty:{rd.qty}"
        state.log(msg, "SUCCESS")
        await telegram_send(msg)

    async def loop(self):
        while state.running:
            state.reset_daily_if_needed()
            self.risk.max_open_positions_override = state.config.get("max_open_positions")
            self.risk.risk_per_trade_pct_override = state.config.get("risk_per_trade_pct")
            self.risk.max_daily_loss_pct_override = state.config.get("max_daily_loss_pct")
            for sym in list(state.config.get("symbols", self.symbols)):
                if not state.running: break
                if sym in state.open_positions: continue
                try:
                    await self.scan_symbol(sym)
                except Exception as e:
                    state.log(f"Tarama hatası {sym}: {e}", "WARN")
                await asyncio.sleep(float(state.config.get("per_symbol_delay_sec", 0.25)))
            state.last_scan=datetime.datetime.now().strftime("%H:%M:%S")
            await asyncio.sleep(int(state.config.get("scan_interval_sec", 20)))

scanner=ScannerService()
