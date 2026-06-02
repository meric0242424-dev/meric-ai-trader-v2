from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from app.core.config import settings
from app.core.security import verify_password, create_token, get_current_user
from app.trading.scanner import scanner
from app.trading.state import state

router=APIRouter(prefix="/api")

@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    if form.username != settings.bot_user or not verify_password(form.password, settings.bot_pass_hash):
        raise HTTPException(400, "Kullanıcı adı veya şifre hatalı")
    return {"access_token": create_token(form.username), "token_type":"bearer"}

@router.get("/status")
async def status(user=Depends(get_current_user)):
    try:
        binance_balance = await scanner.client.account_balance()
        balance_error = None
    except Exception as e:
        binance_balance = 1000.0 if settings.trading_mode != "live" else 0.0
        balance_error = str(e)[:160]
    try:
        await scanner.refresh_open_positions()
    except Exception:
        pass
    return {
        "binance_balance": binance_balance,
        "balance_error": balance_error,
        "running": state.running,
        "mode": settings.trading_mode,
        "last_scan": state.last_scan,
        "open_positions": list(state.open_positions.values()),
        "signals": state.signals[:50],
        "market": state.market[:200],
        "log": state.logs[:120],
        "daily_pnl": state.daily_pnl,
        "daily_trades": state.daily_trades,
        "daily_wins": state.daily_wins,
        "daily_losses": state.daily_losses,
        "win_rate": round((state.daily_wins/(state.daily_wins+state.daily_losses))*100, 1) if (state.daily_wins+state.daily_losses)>0 else 0,
        "config": state.config,
    }

@router.get("/futures-symbols")
async def futures_symbols(user=Depends(get_current_user)):
    symbols = await scanner.load_futures_symbols()
    return {"symbols": symbols, "selected": state.config.get("symbols", [])}

@router.post("/start")
async def start(user=Depends(get_current_user)):
    ok=await scanner.start()
    return {"ok":ok, "running": state.running}

@router.post("/stop")
async def stop(user=Depends(get_current_user)):
    ok=await scanner.stop()
    return {"ok":ok, "running": state.running}

class BotConfigIn(BaseModel):
    symbols: list[str] | None = None
    direction: str | None = Field(None, pattern="^(both|long|short)$")
    default_leverage: int | None = Field(None, ge=1, le=125)
    trade_size_usdt: float | None = Field(None, ge=1, le=1000000)
    risk_per_trade_pct: float | None = Field(None, ge=0.05, le=10)
    max_open_positions: int | None = Field(None, ge=1, le=50)
    min_ai_score: int | None = Field(None, ge=1, le=100)
    max_daily_loss_pct: float | None = Field(None, ge=0.1, le=50)
    profit_target_pct: float | None = Field(None, ge=0.1, le=100)
    tp1_pct: float | None = Field(None, ge=0.1, le=100)
    tp2_pct: float | None = Field(None, ge=0.1, le=100)
    stop_loss_pct: float | None = Field(None, ge=0.1, le=50)
    scan_interval_sec: int | None = Field(None, ge=5, le=3600)
    per_symbol_delay_sec: float | None = Field(None, ge=0.05, le=10)

@router.post("/config")
async def update_config(body: BotConfigIn, user=Depends(get_current_user)):
    data = body.model_dump(exclude_none=True)
    if "symbols" in data:
        data["symbols"] = [s.upper().strip() for s in data["symbols"] if s and s.strip()]
    if "tp1_pct" in data:
        data["profit_target_pct"] = data["tp1_pct"]
    state.config.update(data)
    scanner.symbols = state.config["symbols"]
    state.log(f"Panel ayarları güncellendi | Coin:{len(state.config.get('symbols', []))}", "INFO")
    return {"ok": True, "config": state.config}

class SymbolsIn(BaseModel):
    symbols: list[str]

@router.post("/symbols")
async def set_symbols(body: SymbolsIn, user=Depends(get_current_user)):
    symbols=[s.upper().strip() for s in body.symbols if s.strip()]
    state.config["symbols"] = symbols
    scanner.symbols=symbols
    state.log(f"Coin listesi güncellendi: {len(symbols)} sembol", "INFO")
    return {"ok":True,"symbols":scanner.symbols}

@router.post("/close/{symbol}")
async def close_position(symbol: str, user=Depends(get_current_user)):
    symbol=symbol.upper()
    if symbol not in state.open_positions:
        raise HTTPException(404, "Pozisyon bulunamadı")
    pos=state.open_positions[symbol]
    try:
        await scanner.executor.close(symbol, pos.get("direction", "LONG"), pos.get("qty", 0))
    finally:
        state.open_positions.pop(symbol, None)
        state.log(f"Pozisyon manuel kapatıldı: {symbol}", "WARN")
    return {"ok": True}

@router.post("/reset-paper")
async def reset_paper(user=Depends(get_current_user)):
    state.open_positions.clear()
    state.signals.clear()
    state.market.clear()
    state.daily_pnl = 0.0
    state.daily_trades = 0
    state.daily_wins = 0
    state.daily_losses = 0
    state.log("Paper veriler sıfırlandı", "WARN")
    return {"ok": True}
