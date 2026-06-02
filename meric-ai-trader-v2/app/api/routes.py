from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
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
    return {"running":state.running,"mode":settings.trading_mode,"last_scan":state.last_scan,"open_positions":state.open_positions,"signals":state.signals[:20],"log":state.logs[:80],"config":{"min_ai_score":settings.min_ai_score,"risk_per_trade_pct":settings.risk_per_trade_pct,"max_open_positions":settings.max_open_positions}}

@router.post("/start")
async def start(user=Depends(get_current_user)):
    ok=await scanner.start()
    return {"ok":ok}

@router.post("/stop")
async def stop(user=Depends(get_current_user)):
    ok=await scanner.stop()
    return {"ok":ok}

class SymbolsIn(BaseModel):
    symbols: list[str]

@router.post("/symbols")
async def set_symbols(body: SymbolsIn, user=Depends(get_current_user)):
    scanner.symbols=[s.upper().strip() for s in body.symbols if s.strip()]
    return {"ok":True,"symbols":scanner.symbols}
