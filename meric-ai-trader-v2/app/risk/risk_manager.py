from dataclasses import dataclass
from app.core.config import settings

@dataclass
class RiskDecision:
    allowed: bool
    reason: str = "OK"
    qty: float = 0.0

class RiskManager:
    def __init__(self):
        self.daily_start_balance: float | None = None
        self.consecutive_losses = 0
        self.max_open_positions_override = None
        self.risk_per_trade_pct_override = None
        self.trade_size_usdt_override = None
        self.max_daily_loss_pct_override = None

    def _risk_pct(self):
        return float(self.risk_per_trade_pct_override or settings.risk_per_trade_pct)

    def _max_daily_loss_pct(self):
        return float(self.max_daily_loss_pct_override or settings.max_daily_loss_pct)

    def _max_open_positions(self):
        return int(self.max_open_positions_override or settings.max_open_positions)

    def calculate_qty(self, balance: float, entry: float, sl: float, leverage: int) -> float:
        # Öncelik: panelden seçilen işlem başı USDT limiti.
        # Bu değer margin tutarıdır; gerçek pozisyon büyüklüğü trade_size_usdt * leverage olur.
        fixed_trade_size = self.trade_size_usdt_override
        if fixed_trade_size is not None and fixed_trade_size > 0:
            if fixed_trade_size > balance:
                return 0
            qty = (fixed_trade_size * leverage) / entry
        else:
            risk_usdt = balance * self._risk_pct() / 100
            loss_per_unit = abs(entry - sl)
            if loss_per_unit <= 0: return 0
            qty = risk_usdt / loss_per_unit
            max_notional_qty = (balance * leverage * 0.95) / entry
            qty = min(qty, max_notional_qty)
        if entry >= 1000: return round(qty, 3)
        if entry >= 100: return round(qty, 2)
        if entry >= 1: return round(qty, 1)
        return round(qty, 0)

    def check(self, balance: float, open_count: int, entry: float, sl: float, leverage: int) -> RiskDecision:
        if self.daily_start_balance is None:
            self.daily_start_balance = balance
        dd = (self.daily_start_balance - balance) / self.daily_start_balance * 100 if self.daily_start_balance else 0
        if dd >= self._max_daily_loss_pct():
            return RiskDecision(False, f"Günlük zarar limiti: %{dd:.2f}")
        if self.consecutive_losses >= settings.max_consecutive_losses:
            return RiskDecision(False, "Ardışık zarar limiti")
        if open_count >= self._max_open_positions():
            return RiskDecision(False, "Max açık pozisyon")
        if self.trade_size_usdt_override is not None and self.trade_size_usdt_override > balance:
            return RiskDecision(False, f"İşlem limiti bakiyeden büyük: {self.trade_size_usdt_override:.2f} > {balance:.2f} USDT")
        qty = self.calculate_qty(balance, entry, sl, leverage)
        if qty <= 0:
            return RiskDecision(False, "Miktar hesaplanamadı")
        return RiskDecision(True, qty=qty)

    def register_closed_trade(self, pnl: float):
        self.consecutive_losses = self.consecutive_losses + 1 if pnl < 0 else 0
