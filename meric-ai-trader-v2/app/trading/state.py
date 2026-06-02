from datetime import datetime, date
from app.core.config import settings

class BotState:
    def __init__(self):
        self.running = False
        self.open_positions = {}
        self.logs = []
        self.last_scan = None
        self.signals = []
        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.daily_wins = 0
        self.daily_losses = 0
        self.daily_reset_date = str(date.today())
        self.config = {
            "symbols": ["BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT","XRPUSDT","ADAUSDT","DOGEUSDT","LINKUSDT","AVAXUSDT","LTCUSDT"],
            "direction": "both",
            "default_leverage": settings.default_leverage,
            "trade_size_usdt": 50.0,
            "risk_per_trade_pct": settings.risk_per_trade_pct,
            "max_open_positions": settings.max_open_positions,
            "min_ai_score": settings.min_ai_score,
            "max_daily_loss_pct": settings.max_daily_loss_pct,
            "profit_target_pct": 1.5,
            "stop_loss_pct": 1.2,
            "scan_interval_sec": 20,
            "per_symbol_delay_sec": 0.25,
        }

    def log(self, msg: str, level: str="INFO"):
        e={"time": datetime.now().strftime("%H:%M:%S"), "level": level, "msg": msg}
        self.logs.insert(0,e)
        self.logs=self.logs[:300]
        print(f"[{e['time']}] {level}: {msg}")

    def reset_daily_if_needed(self):
        today = str(date.today())
        if self.daily_reset_date != today:
            self.daily_pnl = 0.0
            self.daily_trades = 0
            self.daily_wins = 0
            self.daily_losses = 0
            self.daily_reset_date = today
            self.log("Yeni gün: günlük sayaçlar sıfırlandı", "INFO")

state=BotState()
