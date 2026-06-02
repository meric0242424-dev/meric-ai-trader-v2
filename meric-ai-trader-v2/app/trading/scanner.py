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

    async def load_futures_symbols(self):
        if state.futures_symbols_cache:
            return state.futures_symbols_cache
        try:
            state.futures_symbols_cache = await self.client.exchange_symbols()
        except Exception as e:
            state.log(f"Futures sembol listesi alınamadı: {e}", "WARN")
            state.futures_symbols_cache = DEFAULT_SYMBOLS
        return state.futures_symbols_cache

    async def start(self):
        if state.running: return False
        if not state.config.get("symbols"):
            state.config["symbols"] = await self.load_futures_symbols()
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

    def apply_panel_levels(self, sig: dict) -> dict:
        price = float(sig.get("price", 0) or 0)
        direction = sig.get("direction")
        if not price or direction not in {"LONG", "SHORT"}:
            return sig
        sl_pct = float(state.config.get("stop_loss_pct", 1.0)) / 100
        tp1_pct = float(state.config.get("tp1_pct", state.config.get("profit_target_pct", 1.5))) / 100
        tp2_pct = float(state.config.get("tp2_pct", max(tp1_pct * 2, tp1_pct + 0.01) * 100)) / 100
        if direction == "LONG":
            sig["sl"] = round(price * (1 - sl_pct), 8)
            sig["tp"] = round(price * (1 + tp1_pct), 8)
            sig["tp1"] = sig["tp"]
            sig["tp2"] = round(price * (1 + tp2_pct), 8)
        else:
            sig["sl"] = round(price * (1 + sl_pct), 8)
            sig["tp"] = round(price * (1 - tp1_pct), 8)
            sig["tp1"] = sig["tp"]
            sig["tp2"] = round(price * (1 - tp2_pct), 8)
        return sig

    async def scan_symbol(self, symbol: str):
        price_now = await self.client.price(symbol)
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
        sig["price"] = round(price_now, 8)
        sig = self.apply_panel_levels(sig)
        state.signals.insert(0,sig); state.signals=state.signals[:150]
        # Market tablosu için son veriyi sakla
        prev = None
        try:
            c15=[float(k[4]) for k in k15]
            change24 = ((price_now - float(k1h[-24][4])) / float(k1h[-24][4]) * 100) if len(k1h) >= 24 else 0
            volume24 = sum(float(k[5]) for k in k15[-96:]) if len(k15) >= 96 else 0
            prev={"symbol":symbol,"price":round(price_now,8),"change24":round(change24,2),"volume24":round(volume24,2),"direction":sig.get("direction"),"score":sig.get("score")}
        except Exception:
            prev={"symbol":symbol,"price":round(price_now,8),"change24":0,"volume24":0,"direction":sig.get("direction"),"score":sig.get("score")}
        state.market=[m for m in state.market if m.get("symbol") != symbol]
        state.market.insert(0, prev)
        state.market=state.market[:500]

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
        state.open_positions[symbol]={**sig,"entry":sig["price"],"current_price":sig["price"],"qty":rd.qty,"trade_size_usdt":state.config.get("trade_size_usdt",50.0),"notional_usdt":round(rd.qty*sig["price"],4),"pnl_usdt":0.0,"pnl_pct":0.0,"order":order,"opened_at":datetime.datetime.now().strftime("%H:%M:%S"),"leverage":leverage}
        state.daily_trades += 1
        msg=f"{sig['direction']} {symbol} | AI:{sig['score']} | Entry:{sig['price']} SL:{sig['sl']} TP1:{sig.get('tp1', sig['tp'])} TP2:{sig.get('tp2')} Qty:{rd.qty}"
        state.log(msg, "SUCCESS")
        await telegram_send(msg)

    async def refresh_open_positions(self):
        for symbol, pos in list(state.open_positions.items()):
            try:
                cur = await self.client.price(symbol)
                entry = float(pos.get("entry", pos.get("price", cur)))
                qty = float(pos.get("qty", 0))
                lev = float(pos.get("leverage", state.config.get("default_leverage", 1)))
                margin = float(pos.get("trade_size_usdt", 0))
                if pos.get("direction") == "LONG":
                    pnl = (cur-entry) * qty
                    pnl_pct = ((cur-entry)/entry*100*lev) if entry else 0
                else:
                    pnl = (entry-cur) * qty
                    pnl_pct = ((entry-cur)/entry*100*lev) if entry else 0
                pos["current_price"] = round(cur, 8)
                pos["pnl_usdt"] = round(pnl, 4)
                pos["pnl_pct"] = round(pnl_pct, 2)
                pos["notional_usdt"] = round(cur * qty, 4)
                pos["margin_usdt"] = margin
            except Exception as e:
                state.log(f"Pozisyon fiyat güncelleme hatası {symbol}: {e}", "WARN")

    async def loop(self):
        while state.running:
            state.reset_daily_if_needed()
            self.risk.max_open_positions_override = state.config.get("max_open_positions")
            self.risk.trade_size_usdt_override = state.config.get("trade_size_usdt")
            self.risk.risk_per_trade_pct_override = state.config.get("risk_per_trade_pct")
            self.risk.max_daily_loss_pct_override = state.config.get("max_daily_loss_pct")
            await self.refresh_open_positions()
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
