import os, time, hmac, hashlib, asyncio
from datetime import datetime, date
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import FileResponse
from pydantic import BaseModel
from jose import jwt, JWTError
import httpx

# ── CONFIG ──
SECRET_KEY = os.getenv("SECRET_KEY", "meric-secret-2026")
ALGORITHM  = "HS256"
TOKEN_EXPIRE = 60 * 24
USERS = {
    os.getenv("BOT_USER", "meric"): os.getenv("BOT_PASS_HASH",
        "e912854e9e50138bb970e1c1d13b04d3:4674be456094be350dea39fe1670ae5995d8f1968aca9c65de84889d11cd477a")
}
BINANCE_API_KEY    = os.getenv("BINANCE_API_KEY", "")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET", "")
BINANCE_BASE       = "https://fapi.binance.com"

app = FastAPI(title="MERIC BOT")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
oauth2 = OAuth2PasswordBearer(tokenUrl="api/login")

# ── BOT STATE ──
bot_state = {
    "running": False,
    "direction": "both",      # both / long / short
    "leverage": 5,
    "trade_amount_usdt": 50,
    "max_open_trades": 3,
    "daily_target_usdt": 300,
    "stop_loss_pct": 2.0,
    "tp1_pct": 1.5,
    "tp2_pct": 3.0,
    "tp3_pct": 5.0,
    "wait_tp2": True,
    "min_score": 65,
    "coins": [
        "0GUSDT",
        "1000BONKUSDT",
        "1000CATUSDT",
        "1000CHEEMSUSDT",
        "1000FLOKIUSDT",
        "1000LUNCUSDT",
        "1000PEPEUSDT",
        "1000RATSUSDT",
        "1000SATSUSDT",
        "1000SHIBUSDT",
        "1000XECUSDT",
        "1INCHUSDT",
        "1MBABYDOGEUSDT",
        "2ZUSDT",
        "4USDT",
        "AAVEUSDT",
        "ACEUSDT",
        "ACHUSDT",
        "ACTUSDT",
        "ACUUSDT",
        "ACXUSDT",
        "ADAUSDT",
        "AERGOUSDT",
        "AEROUSDT",
        "AEVOUSDT",
        "AGLDUSDT",
        "AGTUSDT",
        "AIAUSDT",
        "AIGENSYNUSDT",
        "AINUSDT",
        "AIOTUSDT",
        "AIOUSDT",
        "AIXBTUSDT",
        "AKEUSDT",
        "AKTUSDT",
        "ALCHUSDT",
        "ALGOUSDT",
        "ALICEUSDT",
        "ALLOUSDT",
        "ALLUSDT",
        "ALPINEUSDT",
        "ALTUSDT",
        "ANIMEUSDT",
        "ANKRUSDT",
        "APEUSDT",
        "API3USDT",
        "APRUSDT",
        "APTUSDT",
        "ARBUSDT",
        "ARCUSDT",
        "ARIAUSDT",
        "ARKMUSDT",
        "ARKUSDT",
        "ARPAUSDT",
        "ARUSDT",
        "ASRUSDT",
        "ASTERUSDT",
        "ASTRUSDT",
        "ATHUSDT",
        "ATOMUSDT",
        "ATUSDT",
        "AUCTIONUSDT",
        "AUSDT",
        "AVAAIUSDT",
        "AVAUSDT",
        "AVAXUSDT",
        "AVNTUSDT",
        "AWEUSDT",
        "AXLUSDT",
        "AXSUSDT",
        "AZTECUSDT",
        "B2USDT",
        "BABYUSDT",
        "BANANAS31USDT",
        "BANANAUSDT",
        "BANDUSDT",
        "BANKUSDT",
        "BANUSDT",
        "BARDUSDT",
        "BASEDUSDT",
        "BASUSDT",
        "BATUSDT",
        "BBUSDT",
        "BCHUSDT",
        "BEAMXUSDT",
        "BEATUSDT",
        "BELUSDT",
        "BERAUSDT",
        "BICOUSDT",
        "BIGTIMEUSDT",
        "BILLUSDT",
        "BIOUSDT",
        "BIRBUSDT",
        "BLESSUSDT",
        "BLUAIUSDT",
        "BLURUSDT",
        "BMTUSDT",
        "BNBUSDT",
        "BNTUSDT",
        "BOMEUSDT",
        "BRETTUSDT",
        "BREVUSDT",
        "BROCCOLI714USDT",
        "BROCCOLIF3BUSDT",
        "BRUSDT",
        "BSBUSDT",
        "BSVUSDT",
        "BTCDOMUSDT",
        "BTCUSDT",
        "BTRUSDT",
        "BULLAUSDT",
        "BUSDT",
        "C98USDT",
        "CAKEUSDT",
        "CARVUSDT",
        "CATIUSDT",
        "CCUSDT",
        "CELOUSDT",
        "CELRUSDT",
        "CETUSUSDT",
        "CFGUSDT",
        "CFXUSDT",
        "CGPTUSDT",
        "CHILLGUYUSDT",
        "CHIPUSDT",
        "CHRUSDT",
        "CHZUSDT",
        "CKBUSDT",
        "CLANKERUSDT",
        "CLOUSDT",
        "COAIUSDT",
        "COLLECTUSDT",
        "COMPUSDT",
        "COOKIEUSDT",
        "COSUSDT",
        "COTIUSDT",
        "COWUSDT",
        "CROSSUSDT",
        "CRVUSDT",
        "CTKUSDT",
        "CTRUSDT",
        "CTSIUSDT",
        "CUSDT",
        "CVCUSDT",
        "CVXUSDT",
        "CYBERUSDT",
        "CYSUSDT",
        "DASHUSDT",
        "DEEPUSDT",
        "DEXEUSDT",
        "DIAUSDT",
        "DODOXUSDT",
        "DOGEUSDT",
        "DOGSUSDT",
        "DOLOUSDT",
        "DOODUSDT",
        "DOTUSDT",
        "DRIFTUSDT",
        "DUSDT",
        "DUSKUSDT",
        "DYDXUSDT",
        "DYMUSDT",
        "EDENUSDT",
        "EDGEUSDT",
        "EDUUSDT",
        "EGLDUSDT",
        "EIGENUSDT",
        "ELSAUSDT",
        "ENAUSDT",
        "ENJUSDT",
        "ENSOUSDT",
        "ENSUSDT",
        "EPICUSDT",
        "ERAUSDT",
        "ESPORTSUSDT",
        "ESPUSDT",
        "ETCUSDT",
        "ETHFIUSDT",
        "ETHUSDT",
        "ETHWUSDT",
        "EULUSDT",
        "FARTCOINUSDT",
        "FETUSDT",
        "FFUSDT",
        "FHEUSDT",
        "FIDAUSDT",
        "FIGHTUSDT",
        "FILUSDT",
        "FLOCKUSDT",
        "FLOWUSDT",
        "FLUIDUSDT",
        "FLUXUSDT",
        "FOGOUSDT",
        "FOLKSUSDT",
        "FORMUSDT",
        "FRAXUSDT",
        "FUSDT",
        "GALAUSDT",
        "GASUSDT",
        "GENIUSUSDT",
        "GIGGLEUSDT",
        "GLMUSDT",
        "GMTUSDT",
        "GMXUSDT",
        "GOATUSDT",
        "GPSUSDT",
        "GRASSUSDT",
        "GRIFFAINUSDT",
        "GRTUSDT",
        "GTCUSDT",
        "GUAUSDT",
        "GUNUSDT",
        "GUSDT",
        "GWEIUSDT",
        "HAEDALUSDT",
        "HANAUSDT",
        "HBARUSDT",
        "HEIUSDT",
        "HEMIUSDT",
        "HFTUSDT",
        "HIGHUSDT",
        "HIVEUSDT",
        "HMSTRUSDT",
        "HOLOUSDT",
        "HOMEUSDT",
        "HOTUSDT",
        "HUMAUSDT",
        "HUSDT",
        "HYPERUSDT",
        "HYPEUSDT",
        "ICNTUSDT",
        "ICPUSDT",
        "ICXUSDT",
        "IDOLUSDT",
        "IDUSDT",
        "ILVUSDT",
        "IMXUSDT",
        "INITUSDT",
        "INJUSDT",
        "INUSDT",
        "INXUSDT",
        "IOSTUSDT",
        "IOTAUSDT",
        "IOTXUSDT",
        "IOUSDT",
        "IPUSDT",
        "IRYSUSDT",
        "JASMYUSDT",
        "JCTUSDT",
        "JOEUSDT",
        "JSTUSDT",
        "JTOUSDT",
        "JUPUSDT",
        "KAIAUSDT",
        "KAITOUSDT",
        "KASUSDT",
        "KATUSDT",
        "KAVAUSDT",
        "KERNELUSDT",
        "KGENUSDT",
        "KITEUSDT",
        "KNCUSDT",
        "KOMAUSDT",
        "KSMUSDT",
        "LABUSDT",
        "LAUSDT",
        "LAYERUSDT",
        "LDOUSDT",
        "LIGHTUSDT",
        "LINEAUSDT",
        "LINKUSDT",
        "LISTAUSDT",
        "LITUSDT",
        "LPTUSDT",
        "LQTYUSDT",
        "LSKUSDT",
        "LTCUSDT",
        "LUMIAUSDT",
        "LUNA2USDT",
        "LYNUSDT",
        "MAGICUSDT",
        "MAGMAUSDT",
        "MANAUSDT",
        "MANTAUSDT",
        "MANTRAUSDT",
        "MASKUSDT",
        "MAVIAUSDT",
        "MAVUSDT",
        "MBOXUSDT",
        "MEGAUSDT",
        "MELANIAUSDT",
        "MEMEUSDT",
        "MERLUSDT",
        "METISUSDT",
        "METUSDT",
        "MEUSDT",
        "MEWUSDT",
        "MINAUSDT",
        "MIRAUSDT",
        "MITOUSDT",
        "MMTUSDT",
        "MOCAUSDT",
        "MONUSDT",
        "MOODENGUSDT",
        "MORPHOUSDT",
        "MOVEUSDT",
        "MOVRUSDT",
        "MTLUSDT",
        "MUBARAKUSDT",
        "MUSDT",
        "MYXUSDT",
        "NAORISUSDT",
        "NEARUSDT",
        "NEIROUSDT",
        "NEOUSDT",
        "NEWTUSDT",
        "NFPUSDT",
        "NIGHTUSDT",
        "NILUSDT",
        "NMRUSDT",
        "NOMUSDT",
        "NOTUSDT",
        "NXPCUSDT",
        "OGNUSDT",
        "OGUSDT",
        "ONDOUSDT",
        "ONEUSDT",
        "ONGUSDT",
        "ONTUSDT",
        "ONUSDT",
        "OPENUSDT",
        "OPGUSDT",
        "OPNUSDT",
        "OPUSDT",
        "ORCAUSDT",
        "ORDERUSDT",
        "ORDIUSDT",
        "PARTIUSDT",
        "PAXGUSDT",
        "PENDLEUSDT",
        "PENGUUSDT",
        "PEOPLEUSDT",
        "PHAROSUSDT",
        "PHAUSDT",
        "PIEVERSEUSDT",
        "PIPPINUSDT",
        "PIXELUSDT",
        "PLAYUSDT",
        "PLUMEUSDT",
        "PNUTUSDT",
        "POLUSDT",
        "POLYXUSDT",
        "POPCATUSDT",
        "PORTALUSDT",
        "POWERUSDT",
        "POWRUSDT",
        "PRLUSDT",
        "PROMPTUSDT",
        "PROMUSDT",
        "PROVEUSDT",
        "PTBUSDT",
        "PUMPBTCUSDT",
        "PUMPUSDT",
        "PUNDIXUSDT",
        "PYTHUSDT",
        "QNTUSDT",
        "QTUMUSDT",
        "QUSDT",
        "RAREUSDT",
        "RAVEUSDT",
        "RAYSOLUSDT",
        "RECALLUSDT",
        "REDUSDT",
        "RENDERUSDT",
        "RESOLVUSDT",
        "REZUSDT",
        "RIFUSDT",
        "RIVERUSDT",
        "RLCUSDT",
        "ROBOUSDT",
        "RONINUSDT",
        "ROSEUSDT",
        "RPLUSDT",
        "RSRUSDT",
        "RUNEUSDT",
        "RVNUSDT",
        "SAFEUSDT",
        "SAGAUSDT",
        "SAHARAUSDT",
        "SANDUSDT",
        "SANTOSUSDT",
        "SCRTUSDT",
        "SCRUSDT",
        "SEIUSDT",
        "SENTUSDT",
        "SFPUSDT",
        "SIGNUSDT",
        "SKLUSDT",
        "SKYAIUSDT",
        "SKYUSDT",
        "SLPUSDT",
        "SNXUSDT",
        "SOLUSDT",
        "SOLVUSDT",
        "SONICUSDT",
        "SOONUSDT",
        "SOPHUSDT",
        "SPELLUSDT",
        "SPKUSDT",
        "SSVUSDT",
        "STARUSDT",
        "STGUSDT",
        "STORJUSDT",
        "STOUSDT",
        "STRKUSDT",
        "STXUSDT",
        "SUIUSDT",
        "SUNUSDT",
        "SUPERUSDT",
        "SUSDT",
        "SUSHIUSDT",
        "SWARMSUSDT",
        "SXTUSDT",
        "SYNUSDT",
        "SYRUPUSDT",
        "TACUSDT",
        "TAGUSDT",
        "TAIKOUSDT",
        "TAKEUSDT",
        "TAOUSDT",
        "TAUSDT",
        "THETAUSDT",
        "THEUSDT",
        "TIAUSDT",
        "TLMUSDT",
        "TNSRUSDT",
        "TONUSDT",
        "TOSHIUSDT",
        "TOWNSUSDT",
        "TRBUSDT",
        "TRUMPUSDT",
        "TRUSTUSDT",
        "TRXUSDT",
        "TSTUSDT",
        "TURBOUSDT",
        "TURTLEUSDT",
        "TUSDT",
        "TUTUSDT",
        "TWTUSDT",
        "UAIUSDT",
        "UMAUSDT",
        "UNIUSDT",
        "USDCUSDT",
        "USUALUSDT",
        "VANRYUSDT",
        "VELODROMEUSDT",
        "VETUSDT",
        "VICUSDT",
        "VIRTUALUSDT",
        "VVVUSDT",
        "WALUSDT",
        "WAXPUSDT",
        "WCTUSDT",
        "WIFUSDT",
        "WLDUSDT",
        "WLFIUSDT",
        "WOOUSDT",
        "XAIUSDT",
        "XLMUSDT",
        "XMRUSDT",
        "XRPUSDT",
        "XTZUSDT",
        "XVSUSDT",
        "YFIUSDT",
        "YGGUSDT",
        "ZECUSDT",
        "ZENUSDT",
        "ZEREBROUSDT",
        "ZETAUSDT",
        "ZILUSDT",
        "ZKUSDT",
        "ZORAUSDT",
        "ZROUSDT",
        "ZRXUSDT"
    ],
    "daily_pnl": 0.0,
    "daily_trades": 0,
    "daily_wins": 0,
    "daily_losses": 0,
    "open_positions": {},
    "trade_history": [],
    "cooldown": {},          # {symbol: timestamp} son kapanma zamani
    "cooldown_minutes": 30,  # ayni coine tekrar giris bekleme suresi
    "profit_target_usdt": 1.0,  # islem basina hedef kar (USDT)
    "use_profit_target": True,  # True: sabit USDT kar hedefi kullan
    "log": [],
    "started_at": None,
    "last_scan": None,
    "daily_reset_date": str(date.today()),
}
scan_task = None

# ── AUTH ──
def verify_password(plain, hashed):
    try:
        salt, h = hashed.split(":")
        return hashlib.sha256((salt + plain).encode()).hexdigest() == h
    except:
        return False

def create_token(username):
    return jwt.encode(
        {"sub": username, "exp": time.time() + TOKEN_EXPIRE * 60},
        SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username or username not in USERS:
            raise HTTPException(status_code=401, detail="Gecersiz token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Gecersiz token")

# ── BINANCE API ──
def sign(params):
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return hmac.new(BINANCE_API_SECRET.encode(), query.encode(), hashlib.sha256).hexdigest()

def bheaders():
    return {"X-MBX-APIKEY": BINANCE_API_KEY}

async def bget(path, params=None, signed=False):
    params = params or {}
    if signed:
        params["timestamp"] = int(time.time() * 1000)
        params["signature"] = sign(params)
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.get(BINANCE_BASE + path, params=params, headers=bheaders())
        if r.status_code != 200:
            raise Exception(f"GET {r.status_code}: {r.text[:200]}")
        return r.json()

async def bpost(path, params):
    params["timestamp"] = int(time.time() * 1000)
    params["signature"] = sign(params)
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.post(BINANCE_BASE + path, params=params, headers=bheaders())
        if r.status_code != 200:
            raise Exception(f"POST {r.status_code}: {r.text[:200]}")
        return r.json()

# ── TEKNİK ANALİZ (Analiz sitesiyle aynı motor) ──
def calc_rsi(closes, period=14):
    if len(closes) < period + 1:
        return 50.0
    gains, losses = [], []
    for i in range(len(closes) - period, len(closes)):
        d = closes[i] - closes[i-1]
        gains.append(max(d, 0))
        losses.append(max(-d, 0))
    avg_g = sum(gains) / period
    avg_l = sum(losses) / period
    if avg_l == 0: return 100.0
    return round(100 - 100 / (1 + avg_g / avg_l), 1)

def calc_ema(closes, period):
    if len(closes) < period:
        return closes[-1]
    k = 2 / (period + 1)
    ema = sum(closes[:period]) / period
    for c in closes[period:]:
        ema = c * k + ema * (1 - k)
    return ema

def calc_macd(closes):
    return calc_ema(closes, 12) - calc_ema(closes, 26)

def calc_bb(closes, period=20, mult=2.0):
    sl = closes[-period:]
    mean = sum(sl) / period
    std = (sum((x - mean)**2 for x in sl) / period) ** 0.5
    return {"upper": mean + mult*std, "lower": mean - mult*std, "mid": mean}

def calc_stoch_rsi(closes, period=14):
    rsis = []
    for i in range(period, len(closes)):
        rsis.append(calc_rsi(closes[i-period:i+1], period))
    if len(rsis) < period:
        return 50.0
    recent = rsis[-period:]
    mn, mx = min(recent), max(recent)
    if mx == mn: return 50.0
    return round((rsis[-1] - mn) / (mx - mn) * 100, 1)

def find_sr(highs, lows, price):
    sups, ress = [], []
    for i in range(2, len(highs)-2):
        if highs[i] > highs[i-1] and highs[i] > highs[i-2] and highs[i] > highs[i+1] and highs[i] > highs[i+2]:
            ress.append(highs[i])
        if lows[i] < lows[i-1] and lows[i] < lows[i-2] and lows[i] < lows[i+1] and lows[i] < lows[i+2]:
            sups.append(lows[i])
    sups = sorted([s for s in sups if s < price * 0.999], reverse=True)
    ress = sorted([r for r in ress if r > price * 1.001])
    return {
        "support":    sups[0] if sups else price * 0.97,
        "resistance": ress[0] if ress else price * 1.03,
        "sup2":       sups[1] if len(sups)>1 else price * 0.94,
        "res2":       ress[1] if len(ress)>1 else price * 1.06,
    }

def analyze(k15, k1h, price, k4h=None):
    """
    Profesyonel Confluence Analiz Motoru
    ---
    Kullanilan indiktorler:
      - RSI(14) 15m + 1h
      - EMA 7/21/50 stack (15m) + EMA 7/21 (1h)
      - EMA 99 (1h) — ana trend filtresi
      - MACD (15m + 1h)
      - Bollinger Band (20,2) — volatilite
      - Stochastic RSI (14) — momentum
      - Hacim analizi — konfirmasyon
      - Mum pattern — giris zamanlama
      - 4h trend filtresi — ana yonu dogrula
    Scoring: Bull ve Bear puanlari esit agirlikta,
    hic biri diger tarafin puanini iptal etmiyor.
    """
    # Veri hazirla
    c15  = [float(k[4]) for k in k15]
    h15  = [float(k[2]) for k in k15]
    l15  = [float(k[3]) for k in k15]
    v15  = [float(k[5]) for k in k15]
    o15  = [float(k[1]) for k in k15]
    c1h  = [float(k[4]) for k in k1h]
    h1h  = [float(k[2]) for k in k1h]
    l1h  = [float(k[3]) for k in k1h]

    # Indiktorler
    rsi_15   = calc_rsi(c15, 14)
    rsi_6    = calc_rsi(c15, 6)
    rsi_1h   = calc_rsi(c1h, 14)
    ema7_15  = calc_ema(c15, 7)
    ema21_15 = calc_ema(c15, 21)
    ema50_15 = calc_ema(c15, min(50, len(c15)-1))
    ema7_1h  = calc_ema(c1h, 7)
    ema21_1h = calc_ema(c1h, 21)
    ema50_1h = calc_ema(c1h, min(50, len(c1h)-1))
    ema99_1h = calc_ema(c1h, min(99, len(c1h)-1))
    macd_15  = calc_macd(c15)
    macd_1h  = calc_macd(c1h)
    bb       = calc_bb(c15, 20, 2)
    stoch    = calc_stoch_rsi(c15, 14)
    sr       = find_sr(h15, l15, price)

    # Hacim analizi
    avg_vol   = sum(v15[-20:]) / 20 if len(v15) >= 20 else sum(v15) / len(v15)
    vol_ratio = v15[-1] / avg_vol if avg_vol > 0 else 1
    vol_label = "YUKSEK" if vol_ratio > 1.5 else "DUSUK" if vol_ratio < 0.7 else "NORMAL"

    # Fiyat momentum (son 10 mum)
    momentum_10 = (c15[-1] - c15[-10]) / c15[-10] * 100 if len(c15) >= 10 else 0
    # 24h momentum
    momentum_24h = (price - float(k1h[-24][4])) / float(k1h[-24][4]) * 100 if len(k1h) >= 24 else 0

    bull, bear = 0, 0
    signals = []

    # ── 1. RSI 15m — agirlik arttirildi (hizli tepki) ──
    if   rsi_15 < 20:  bull += 35; signals.append("RSI Asiri Satim")
    elif rsi_15 < 30:  bull += 25; signals.append("RSI Oversold")
    elif rsi_15 < 40:  bull += 14
    elif rsi_15 < 48:  bull += 5
    elif rsi_15 > 80:  bear += 35; signals.append("RSI Asiri Alim")
    elif rsi_15 > 70:  bear += 25; signals.append("RSI Overbought")
    elif rsi_15 > 60:  bear += 14
    elif rsi_15 > 52:  bear += 5

    # ── 2. RSI 1h — agirlik arttirildi ──
    if   rsi_1h < 25:  bull += 30; signals.append("RSI1H Asiri Satim")
    elif rsi_1h < 35:  bull += 18
    elif rsi_1h < 45:  bull += 8
    elif rsi_1h > 75:  bear += 30; signals.append("RSI1H Asiri Alim")
    elif rsi_1h > 65:  bear += 18
    elif rsi_1h > 55:  bear += 8

    # ── 3. EMA Stack 15m — agirlik azaltildi (gecikme sorunu) ──
    ema_bull_15 = ema7_15 > ema21_15 and ema21_15 > ema50_15
    ema_bear_15 = ema7_15 < ema21_15 and ema21_15 < ema50_15
    if   ema_bull_15: bull += 12; signals.append("EMA Bullish Stack")
    elif ema_bear_15: bear += 12; signals.append("EMA Bearish Stack")
    elif ema7_15 > ema21_15: bull += 5
    elif ema7_15 < ema21_15: bear += 5

    # ── 4. EMA 1h trend — agirlik azaltildi ──
    if   ema7_1h > ema21_1h and ema21_1h > ema50_1h: bull += 10
    elif ema7_1h < ema21_1h and ema21_1h < ema50_1h: bear += 10
    elif ema7_1h > ema21_1h: bull += 5
    elif ema7_1h < ema21_1h: bear += 5

    # ── 5. EMA99 Ana Trend Filtresi (max 10 puan) ──
    if   price > ema99_1h * 1.002: bull += 10; signals.append("EMA99 Ustu")
    elif price < ema99_1h * 0.998: bear += 10; signals.append("EMA99 Alti")
    # Yakinda ise puan yok — nötr

    # ── 6. MACD (max 16 puan) ──
    # 15m ve 1h ayri degerlendir, konfirmasyon bonus
    if   macd_15 > 0: bull += 7
    elif macd_15 < 0: bear += 7
    if   macd_1h  > 0: bull += 7
    elif macd_1h  < 0: bear += 7
    # Cift konfirmasyon bonus
    if macd_15 > 0 and macd_1h > 0:
        bull += 2; signals.append("MACD Pozitif")
    elif macd_15 < 0 and macd_1h < 0:
        bear += 2; signals.append("MACD Negatif")

    # ── 7. Bollinger Band (max 15 puan) ──
    bb_range = bb["upper"] - bb["lower"]
    bb_pct   = (price - bb["lower"]) / bb_range if bb_range > 0 else 0.5
    if   bb_pct < 0.1:  bull += 15; signals.append("BB Alt Bant")
    elif bb_pct < 0.25: bull += 8
    elif bb_pct < 0.4:  bull += 3
    elif bb_pct > 0.9:  bear += 15; signals.append("BB Ust Bant")
    elif bb_pct > 0.75: bear += 8
    elif bb_pct > 0.6:  bear += 3

    # ── 8. Stochastic RSI (max 12 puan) ──
    if   stoch < 10:  bull += 12; signals.append("StochRSI Asiri Satim")
    elif stoch < 25:  bull += 8;  signals.append("StochRSI Oversold")
    elif stoch < 40:  bull += 3
    elif stoch > 90:  bear += 12; signals.append("StochRSI Asiri Alim")
    elif stoch > 75:  bear += 8;  signals.append("StochRSI Overbought")
    elif stoch > 60:  bear += 3

    # ── 9. Momentum (max 10 puan) ──
    if   momentum_24h > 8:   bull += 10; signals.append("Guclu Yukselis Trend")
    elif momentum_24h > 4:   bull += 6
    elif momentum_24h > 1.5: bull += 3
    elif momentum_24h < -8:  bear += 10; signals.append("Guclu Dusus Trend")
    elif momentum_24h < -4:  bear += 6
    elif momentum_24h < -1.5:bear += 3

    # ── 10. Hacim Konfirmasyonu (max 10 puan) ──
    if vol_ratio > 3.0:
        if momentum_10 > 0: bull += 10; signals.append("Dev Hacim LONG")
        else:               bear += 10; signals.append("Dev Hacim SHORT")
    elif vol_ratio > 2.0:
        if momentum_10 > 0: bull += 7
        else:               bear += 7
    elif vol_ratio > 1.5:
        if momentum_10 > 0: bull += 4
        else:               bear += 4
    elif vol_ratio < 0.5:
        # Dusuk hacim — sinyal guvenilmez, her iki taraf ceza alir
        bull -= 5; bear -= 5

    # ── 11. Mum Pattern (max 15 puan) ──
    if len(k15) >= 4:
        # Son 3 mum
        op1 = o15[-1]; cl1 = c15[-1]; hi1 = h15[-1]; lo1 = l15[-1]
        op2 = o15[-2]; cl2 = c15[-2]; hi2 = h15[-2]; lo2 = l15[-2]
        op3 = o15[-3]; cl3 = c15[-3]
        body1 = abs(cl1 - op1)
        body2 = abs(cl2 - op2)
        upper_wick1 = hi1 - max(op1, cl1)
        lower_wick1 = min(op1, cl1) - lo1

        # Bull Engulfing
        if cl1 > op1 and cl1 > op2 and op1 < cl2 and body1 > body2 * 1.2:
            bull += 15; signals.append("Bull Engulfing")
        # Bear Engulfing
        elif cl1 < op1 and cl1 < op2 and op1 > cl2 and body1 > body2 * 1.2:
            bear += 15; signals.append("Bear Engulfing")
        # Hammer (alt fitil uzun, ust fitil kisa, bullish)
        elif (body1 > 0 and lower_wick1 > body1 * 2
              and upper_wick1 < body1 * 0.5 and cl1 > op1):
            bull += 10; signals.append("Hammer")
        # Shooting Star (ust fitil uzun, alt fitil kisa, bearish)
        elif (body1 > 0 and upper_wick1 > body1 * 2
              and lower_wick1 < body1 * 0.5 and cl1 < op1):
            bear += 10; signals.append("Shooting Star")
        # Doji (belirsizlik)
        elif body1 < (hi1 - lo1) * 0.1:
            pass  # Doji nötr, puan yok

        # 3 ardisik yukselen mum = momentum
        if cl1 > op1 and cl2 > op2 and cl3 > op3:
            bull += 5; signals.append("3 Yukselen Mum")
        elif cl1 < op1 and cl2 < op2 and cl3 < op3:
            bear += 5; signals.append("3 Dusen Mum")

    # ── 12. Destek/Direnc Yakinligi (max 8 puan) ──
    dist_to_sup = (price - sr["support"]) / price * 100
    dist_to_res = (sr["resistance"] - price) / price * 100
    if   dist_to_sup < 0.5:  bull += 8; signals.append("Destek Yakin")
    elif dist_to_sup < 1.5:  bull += 4
    if   dist_to_res < 0.5:  bear += 8; signals.append("Direnc Yakin")
    elif dist_to_res < 1.5:  bear += 4

    # ── SKOR HESAPLA ──
    bull = max(0, bull)
    bear = max(0, bear)
    total = bull + bear
    if total == 0:
        score = 50
    else:
        score = round(bull / total * 100)

    # ── YON KARARI ──
    # Guclu sinyal: 65+, Zayif sinyal: 60-64 (daha dusuk guven)
    if   score >= 65: direction = "LONG";    confidence = "YUKSEK" if score >= 75 else "ORTA"
    elif score >= 60: direction = "LONG";    confidence = "DUSUK"
    elif score <= 35: direction = "SHORT";   confidence = "YUKSEK" if score <= 25 else "ORTA"
    elif score <= 40: direction = "SHORT";   confidence = "DUSUK"
    else:             direction = "NEUTRAL"; confidence = "YOK"

    # ── SEVIYELER ──
    sl_pct  = bot_state["stop_loss_pct"] / 100
    tp1_pct = bot_state["tp1_pct"] / 100
    tp2_pct = bot_state["tp2_pct"] / 100
    tp3_pct = bot_state["tp3_pct"] / 100
    is_long = direction == "LONG"

    if is_long:
        entry = min(price, sr["support"] * 1.002) if dist_to_sup < 2 else price
        sl    = round(max(sr["support"] * 0.998, price * (1 - sl_pct)), 8)
        tp1   = round(min(sr["resistance"] * 0.998, price * (1 + tp1_pct)), 8)
        tp2   = round(price * (1 + tp2_pct), 8)
        tp3   = round(price * (1 + tp3_pct), 8)
    else:
        entry = max(price, sr["resistance"] * 0.998) if dist_to_res < 2 else price
        sl    = round(min(sr["resistance"] * 1.002, price * (1 + sl_pct)), 8)
        tp1   = round(max(sr["support"] * 1.002, price * (1 - tp1_pct)), 8)
        tp2   = round(price * (1 - tp2_pct), 8)
        tp3   = round(price * (1 - tp3_pct), 8)

    # ── 4H TREND FİLTRESİ ──
    # 4h verisi varsa ana trend kontrolü yap
    # 4h SHORT iken 15m LONG sinyali = zayıf, iptal et
    # 4h LONG iken 15m SHORT sinyali = zayıf, iptal et
    if k4h is not None and len(k4h) >= 50:
        c4h = [float(k[4]) for k in k4h]
        ema7_4h  = calc_ema(c4h, 7)
        ema21_4h = calc_ema(c4h, 21)
        rsi_4h   = calc_rsi(c4h, 14)
        macd_4h  = calc_macd(c4h)

        trend_4h_bull = ema7_4h > ema21_4h and macd_4h > 0
        trend_4h_bear = ema7_4h < ema21_4h and macd_4h < 0

        if direction == "LONG" and trend_4h_bear and rsi_4h > 60:
            # 4h aşağı trend, LONG sinyali zayıf — iptal
            direction = "NEUTRAL"
            confidence = "YOK"
            signals.append("4H Trend Karsi — IPTAL")
        elif direction == "SHORT" and trend_4h_bull and rsi_4h < 40:
            # 4h yukarı trend, SHORT sinyali zayıf — iptal
            direction = "NEUTRAL"
            confidence = "YOK"
            signals.append("4H Trend Karsi — IPTAL")
        elif direction == "LONG" and trend_4h_bull:
            # 4h de LONG — sinyal güçlü
            bull += 15
            score = round(bull / (bull + bear) * 100) if (bull + bear) > 0 else 50
            signals.append("4H Konfirmasyon")
        elif direction == "SHORT" and trend_4h_bear:
            # 4h de SHORT — sinyal güçlü
            bear += 15
            score = round(bull / (bull + bear) * 100) if (bull + bear) > 0 else 50
            signals.append("4H Konfirmasyon")

    return {
        "direction":   direction,
        "confidence":  confidence,
        "score":       score,
        "bull":        bull,
        "bear":        bear,
        "signals":     signals[:6],
        "entry":       price,
        "sl":          sl,
        "tp1":         tp1,
        "tp2":         tp2,
        "tp3":         tp3,
        "rsi_15":      rsi_15,
        "rsi_1h":      rsi_1h,
        "stoch":       stoch,
        "ema_trend":   "YUKARI" if ema7_15 > ema21_15 else "ASAGI",
        "macd":        "POZITIF" if macd_15 > 0 else "NEGATIF",
        "vol_label":   vol_label,
        "vol_ratio":   round(vol_ratio, 2),
        "support":     sr["support"],
        "resistance":  sr["resistance"],
        "bb_pct":      round(bb_pct * 100, 1),
        "momentum_24h":round(momentum_24h, 2),
    }


# ── BOT HELPERS ──
def bot_log(msg, level="INFO"):
    entry = {"time": datetime.now().strftime("%H:%M:%S"), "msg": msg, "level": level}
    bot_state["log"].insert(0, entry)
    if len(bot_state["log"]) > 200:
        bot_state["log"].pop()
    print(f"[{entry['time']}] {level}: {msg}")

def reset_daily():
    today = str(date.today())
    if bot_state["daily_reset_date"] != today:
        bot_state["daily_pnl"]        = 0.0
        bot_state["daily_trades"]     = 0
        bot_state["daily_wins"]       = 0
        bot_state["daily_losses"]     = 0
        bot_state["daily_reset_date"] = today
        bot_log("Yeni gun: sayaclar sifirlandi")

async def get_price(symbol):
    d = await bget("/fapi/v1/ticker/price", {"symbol": symbol})
    return float(d["price"])

async def get_klines(symbol, interval, limit=150):
    return await bget("/fapi/v1/klines", {
        "symbol": symbol, "interval": interval, "limit": limit
    })

async def get_balance():
    d = await bget("/fapi/v2/account", signed=True)
    for a in d.get("assets", []):
        if a["asset"] == "USDT":
            return float(a["availableBalance"])
    return 0.0

async def set_leverage(symbol, leverage):
    try:
        await bpost("/fapi/v1/leverage", {"symbol": symbol, "leverage": leverage})
    except Exception as e:
        bot_log(f"Kaldirac hatasi {symbol}: {e}", "WARN")

def calc_qty(amount, leverage, price):
    raw = (amount * leverage) / price
    if   price >= 10000: return round(raw, 3)
    elif price >= 1000:  return round(raw, 3)
    elif price >= 100:   return round(raw, 2)
    elif price >= 10:    return round(raw, 1)
    elif price >= 1:     return round(raw, 0)
    else:                return round(raw, 0)

async def open_position(symbol, A):
    direction = A["direction"]
    side      = "BUY" if direction == "LONG" else "SELL"
    pos_side  = direction  # LONG veya SHORT (Hedge Mode)
    amount    = bot_state["trade_amount_usdt"]
    leverage  = bot_state["leverage"]
    price     = A["entry"]
    qty       = calc_qty(amount, leverage, price)

    if qty <= 0:
        bot_log(f"Gecersiz miktar {symbol}", "WARN")
        return False

    try:
        await set_leverage(symbol, leverage)
        order = await bpost("/fapi/v1/order", {
            "symbol":       symbol,
            "side":         side,
            "type":         "MARKET",
            "quantity":     qty,
            "positionSide": pos_side,
        })
        bot_state["open_positions"][symbol] = {
            "symbol":    symbol,
            "direction": direction,
            "entry":     price,
            "qty":       qty,
            "leverage":  leverage,
            "sl":        A["sl"],
            "tp1":       A["tp1"],
            "tp2":       A["tp2"],
            "tp3":       A["tp3"],
            "score":     A["score"],
            "signals":   A.get("signals", []),
            "tp1_hit":   False,
            "order_id":  order.get("orderId"),
            "opened_at": datetime.now().strftime("%H:%M:%S"),
            "amount":    amount,
        }
        bot_state["daily_trades"] += 1
        bot_log(f"ACILDI: {direction} {symbol} x{leverage} | {qty} @ {price:.4f}", "SUCCESS")
        return True
    except Exception as e:
        bot_log(f"Pozisyon acma hatasi {symbol}: {e}", "ERROR")
        return False

async def close_position(symbol, reason="SINYAL"):
    pos = bot_state["open_positions"].get(symbol)
    if not pos:
        return
    side     = "SELL" if pos["direction"] == "LONG" else "BUY"
    pos_side = pos["direction"]
    try:
        await bpost("/fapi/v1/order", {
            "symbol":       symbol,
            "side":         side,
            "type":         "MARKET",
            "quantity":     pos["qty"],
            "positionSide": pos_side,
        })
        cur = await get_price(symbol)
        if pos["direction"] == "LONG":
            pnl = (cur - pos["entry"]) / pos["entry"] * pos["amount"] * pos["leverage"]
        else:
            pnl = (pos["entry"] - cur) / pos["entry"] * pos["amount"] * pos["leverage"]
        pnl = round(pnl, 4)

        bot_state["daily_pnl"] = round(bot_state["daily_pnl"] + pnl, 4)
        if pnl >= 0: bot_state["daily_wins"] += 1
        else:        bot_state["daily_losses"] += 1

        bot_state["trade_history"].insert(0, {
            "symbol":    symbol,
            "direction": pos["direction"],
            "entry":     pos["entry"],
            "exit":      cur,
            "pnl":       pnl,
            "reason":    reason,
            "time":      datetime.now().strftime("%H:%M:%S"),
            "leverage":  pos["leverage"],
        })
        if len(bot_state["trade_history"]) > 100:
            bot_state["trade_history"].pop()

        del bot_state["open_positions"][symbol]
        bot_state["cooldown"][symbol] = time.time()  # cooldown baslat
        bot_log(f"KAPATILDI: {symbol} | {reason} | PNL: {'+' if pnl>=0 else ''}{pnl:.2f}$",
                "SUCCESS" if pnl >= 0 else "WARN")
    except Exception as e:
        bot_log(f"Kapatma hatasi {symbol}: {e}", "ERROR")

async def check_positions():
    """Her taramada açık pozisyonları kontrol et"""
    # Binance ile senkronize et
    try:
        real_pos  = await bget("/fapi/v2/positionRisk", signed=True)
        real_syms = {p["symbol"] for p in real_pos if abs(float(p["positionAmt"])) > 0}
        for sym in list(bot_state["open_positions"].keys()):
            if sym not in real_syms:
                bot_log(f"SYNC: {sym} Binance'te kapali, silindi")
                del bot_state["open_positions"][sym]
    except Exception as e:
        bot_log(f"Sync hatasi: {e}", "WARN")

    # SL/TP kontrolü
    for symbol, pos in list(bot_state["open_positions"].items()):
        try:
            price   = await get_price(symbol)
            is_long = pos["direction"] == "LONG"

            # Stop Loss
            if is_long  and price <= pos["sl"]:
                await close_position(symbol, "STOP LOSS"); continue
            if not is_long and price >= pos["sl"]:
                await close_position(symbol, "STOP LOSS"); continue

            # Sabit USDT kar hedefi kontrolu
            if bot_state.get("use_profit_target", False):
                cur_pnl = 0
                if is_long:
                    cur_pnl = (price - pos["entry"]) / pos["entry"] * pos["amount"] * pos["leverage"]
                else:
                    cur_pnl = (pos["entry"] - price) / pos["entry"] * pos["amount"] * pos["leverage"]
                if cur_pnl >= bot_state.get("profit_target_usdt", 1.0):
                    await close_position(symbol, f"KAR HEDEFI +${cur_pnl:.2f}")
                    continue
                # Sabit hedef aktifken TP1/TP2/TP3 kontrolunu atla
                continue

            # TP1
            if not pos["tp1_hit"]:
                if (is_long and price >= pos["tp1"]) or (not is_long and price <= pos["tp1"]):
                    pos["tp1_hit"] = True
                    bot_log(f"TP1 TUTTU: {symbol} @ {price:.4f}", "SUCCESS")
                    if not bot_state["wait_tp2"]:
                        await close_position(symbol, "TP1")
                        continue

            # TP2
            if pos["tp1_hit"] and bot_state["wait_tp2"]:
                if (is_long and price >= pos["tp2"]) or (not is_long and price <= pos["tp2"]):
                    await close_position(symbol, "TP2")
                    continue

            # TP3
            if (is_long and price >= pos["tp3"]) or (not is_long and price <= pos["tp3"]):
                await close_position(symbol, "TP3")

        except Exception as e:
            bot_log(f"Pozisyon kontrol hatasi {symbol}: {e}", "WARN")

async def scan_and_trade():
    """Ana bot döngüsü"""
    while bot_state["running"]:
        try:
            reset_daily()

            # Günlük hedef kontrolü
            if bot_state["daily_pnl"] >= bot_state["daily_target_usdt"]:
                bot_log(f"GUNLUK HEDEF! +{bot_state['daily_pnl']:.2f}$", "SUCCESS")
                bot_state["running"] = False
                break

            # Pozisyon kontrolü
            await check_positions()

            # Max pozisyon kontrolü
            if len(bot_state["open_positions"]) >= bot_state["max_open_trades"]:
                bot_state["last_scan"] = datetime.now().strftime("%H:%M:%S")
                await asyncio.sleep(10)
                continue

            # Bakiye kontrolü
            balance = await get_balance()
            if balance < bot_state["trade_amount_usdt"]:
                bot_log(f"Yetersiz bakiye: {balance:.2f}$", "WARN")
                await asyncio.sleep(30)
                continue

            # Coin tarama
            direction_filter = bot_state["direction"]  # both / long / short

            for symbol in bot_state["coins"]:
                if not bot_state["running"]:
                    break
                if symbol in bot_state["open_positions"]:
                    continue
                # Cooldown kontrolu — ayni coine tekrar giris engelle
                if symbol in bot_state["cooldown"]:
                    cooldown_secs = bot_state["cooldown_minutes"] * 60
                    if time.time() - bot_state["cooldown"][symbol] < cooldown_secs:
                        continue
                if len(bot_state["open_positions"]) >= bot_state["max_open_trades"]:
                    break

                try:
                    price = await get_price(symbol)
                    k15   = await get_klines(symbol, "15m", 150)
                    k1h   = await get_klines(symbol, "1h",  100)
                    k4h   = await get_klines(symbol, "4h",  50)
                    A     = analyze(k15, k1h, price, k4h)

                    if A["direction"] == "NEUTRAL":
                        continue

                    # Yön filtresi — kesin kontrol
                    if direction_filter == "long"  and A["direction"] != "LONG":
                        continue
                    if direction_filter == "short" and A["direction"] != "SHORT":
                        continue

                    # Minimum skor kontrolü
                    if A["score"] < bot_state["min_score"]:
                        continue

                    bot_log(
                        f"SINYAL: {A['direction']} {symbol} | "
                        f"Skor:{A['score']} Bull:{A['bull']} Bear:{A['bear']} | "
                        f"RSI:{A['rsi_15']} | {A['signals']}"
                    )
                    # ── GİRİŞ ZAMANLAMA FİLTRESİ ──
                    # Fiyat momentum kontrolü — zirve/dip yerine geri çekilmede gir
                    entry_ok = True
                    last_closes = [float(k[4]) for k in k15[-5:]]
                    last_price  = last_closes[-1]
                    ema7_now    = sum(last_closes) / len(last_closes)  # basit ortalama yaklaşık

                    if A["direction"] == "LONG":
                        # LONG: son 2 mumda fiyat düşüyorsa veya EMA7 üzerindeyse gir
                        # Fiyat son mumda yukarı spike yapmışsa (>%1.5) bekle
                        last_candle_move = (last_closes[-1] - last_closes[-2]) / last_closes[-2] * 100
                        if last_candle_move > 1.5:
                            bot_log(f"BEKLEME: {symbol} LONG — son mum cok yukseldi ({last_candle_move:.1f}%), geri cekilme bekleniyor", "INFO")
                            entry_ok = False
                        # RSI 15m 75 uzerindeyse LONG'a girme — asiri alim
                        if A["rsi_15"] > 75:
                            bot_log(f"BEKLEME: {symbol} LONG — RSI cok yuksek ({A['rsi_15']})", "INFO")
                            entry_ok = False

                    elif A["direction"] == "SHORT":
                        # SHORT: son mumda fiyat düşüyorsa veya spike aşağıysa bekle
                        last_candle_move = (last_closes[-1] - last_closes[-2]) / last_closes[-2] * 100
                        if last_candle_move < -1.5:
                            bot_log(f"BEKLEME: {symbol} SHORT — son mum cok dustu ({last_candle_move:.1f}%), yukselis bekleniyor", "INFO")
                            entry_ok = False
                        # RSI 15m 25 altindaysa SHORT'a girme — asiri satim
                        if A["rsi_15"] < 25:
                            bot_log(f"BEKLEME: {symbol} SHORT — RSI cok dusuk ({A['rsi_15']})", "INFO")
                            entry_ok = False

                    if entry_ok:
                        await open_position(symbol, A)
                        await asyncio.sleep(2)
                    else:
                        await asyncio.sleep(0.5)

                except Exception as e:
                    bot_log(f"Tarama hatasi {symbol}: {e}", "WARN")
                    await asyncio.sleep(0.5)

            bot_state["last_scan"] = datetime.now().strftime("%H:%M:%S")

        except Exception as e:
            bot_log(f"Ana dongu hatasi: {e}", "ERROR")

        await asyncio.sleep(20)

# ── API ENDPOINTS ──
@app.post("/api/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user_hash = USERS.get(form.username)
    if not user_hash or not verify_password(form.password, user_hash):
        raise HTTPException(status_code=400, detail="Kullanici adi veya sifre hatali")
    return {"access_token": create_token(form.username), "token_type": "bearer"}

@app.get("/api/status")
async def get_status(user=Depends(get_current_user)):
    wins  = bot_state["daily_wins"]
    losses = bot_state["daily_losses"]
    total  = wins + losses
    return {
        "running":        bot_state["running"],
        "direction":      bot_state["direction"],
        "daily_pnl":      bot_state["daily_pnl"],
        "daily_trades":   bot_state["daily_trades"],
        "daily_wins":     bot_state["daily_wins"],
        "daily_losses":   bot_state["daily_losses"],
        "win_rate":       round(wins/total*100, 1) if total > 0 else 0,
        "daily_target":   bot_state["daily_target_usdt"],
        "open_positions": list(bot_state["open_positions"].values()),
        "log":            bot_state["log"][:50],
        "last_scan":      bot_state["last_scan"],
        "trades":         bot_state["trade_history"][:50],
        "config": {
            "direction":       bot_state["direction"],
            "leverage":        bot_state["leverage"],
            "trade_amount":    bot_state["trade_amount_usdt"],
            "max_open_trades": bot_state["max_open_trades"],
            "daily_target":    bot_state["daily_target_usdt"],
            "stop_loss_pct":   bot_state["stop_loss_pct"],
            "tp1_pct":         bot_state["tp1_pct"],
            "tp2_pct":         bot_state["tp2_pct"],
            "tp3_pct":         bot_state["tp3_pct"],
            "wait_tp2":        bot_state["wait_tp2"],
            "min_score":          bot_state["min_score"],
            "coins":              bot_state["coins"],
            "cooldown_minutes":   bot_state["cooldown_minutes"],
            "profit_target_usdt": bot_state.get("profit_target_usdt", 1.0),
            "use_profit_target":  bot_state.get("use_profit_target", True),
        }
    }

@app.get("/api/trades")
async def get_trades(user=Depends(get_current_user)):
    return {"trades": bot_state["trade_history"]}

@app.get("/api/balance")
async def get_bal(user=Depends(get_current_user)):
    try:
        return {"balance": await get_balance()}
    except Exception as e:
        return {"balance": 0, "error": str(e)}

class BotConfig(BaseModel):
    direction:       Optional[str]   = None
    leverage:        Optional[int]   = None
    trade_amount:    Optional[float] = None
    max_open_trades: Optional[int]   = None
    daily_target:    Optional[float] = None
    stop_loss_pct:   Optional[float] = None
    tp1_pct:         Optional[float] = None
    tp2_pct:         Optional[float] = None
    tp3_pct:         Optional[float] = None
    wait_tp2:           Optional[bool]  = None
    min_score:          Optional[int]   = None
    coins:              Optional[list]  = None
    cooldown_minutes:   Optional[int]   = None
    profit_target_usdt: Optional[float] = None
    use_profit_target:  Optional[bool]  = None

@app.post("/api/config")
async def update_config(cfg: BotConfig, user=Depends(get_current_user)):
    if cfg.direction       is not None: bot_state["direction"]          = cfg.direction
    if cfg.leverage        is not None: bot_state["leverage"]           = max(1, min(125, cfg.leverage))
    if cfg.trade_amount    is not None: bot_state["trade_amount_usdt"]  = max(1, cfg.trade_amount)
    if cfg.max_open_trades is not None: bot_state["max_open_trades"]    = max(1, min(20, cfg.max_open_trades))
    if cfg.daily_target    is not None: bot_state["daily_target_usdt"]  = max(1, cfg.daily_target)
    if cfg.stop_loss_pct   is not None: bot_state["stop_loss_pct"]      = max(0.1, min(10, cfg.stop_loss_pct))
    if cfg.tp1_pct         is not None: bot_state["tp1_pct"]            = max(0.1, cfg.tp1_pct)
    if cfg.tp2_pct         is not None: bot_state["tp2_pct"]            = max(0.1, cfg.tp2_pct)
    if cfg.tp3_pct         is not None: bot_state["tp3_pct"]            = max(0.1, cfg.tp3_pct)
    if cfg.wait_tp2        is not None: bot_state["wait_tp2"]           = cfg.wait_tp2
    if cfg.min_score       is not None: bot_state["min_score"]          = max(50, min(90, cfg.min_score))
    if cfg.coins               is not None: bot_state["coins"]                = cfg.coins
    if cfg.cooldown_minutes    is not None: bot_state["cooldown_minutes"]      = max(1, cfg.cooldown_minutes)
    if cfg.profit_target_usdt  is not None: bot_state["profit_target_usdt"]    = max(0.1, cfg.profit_target_usdt)
    if cfg.use_profit_target   is not None: bot_state["use_profit_target"]     = cfg.use_profit_target
    bot_log(f"Ayarlar guncellendi: yon={bot_state['direction']} kaldirac={bot_state['leverage']}x")
    return {"ok": True}

@app.post("/api/start")
async def start_bot(user=Depends(get_current_user)):
    global scan_task
    if bot_state["running"]:
        return {"ok": False, "msg": "Bot zaten calisiyor"}
    if not BINANCE_API_KEY or not BINANCE_API_SECRET:
        return {"ok": False, "msg": "API Key eksik"}
    bot_state["running"]    = True
    bot_state["started_at"] = datetime.now().strftime("%H:%M:%S")
    bot_log(
        f"BOT BASLATILDI | Yon: {bot_state['direction']} | "
        f"Kaldirac: {bot_state['leverage']}x | "
        f"Min Skor: {bot_state['min_score']}"
    )
    scan_task = asyncio.create_task(scan_and_trade())
    return {"ok": True}

@app.post("/api/stop")
async def stop_bot(user=Depends(get_current_user)):
    bot_state["running"] = False
    if scan_task:
        scan_task.cancel()
    bot_log("BOT DURDURULDU")
    return {"ok": True}

@app.post("/api/close/{symbol}")
async def close_pos(symbol: str, user=Depends(get_current_user)):
    if symbol not in bot_state["open_positions"]:
        raise HTTPException(404, "Pozisyon bulunamadi")
    await close_position(symbol, "MANUEL")
    return {"ok": True}

@app.get("/")
async def root():
    return FileResponse("panel.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
