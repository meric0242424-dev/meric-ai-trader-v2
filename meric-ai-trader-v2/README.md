# MERIC AI TRADER BOT v2.0

Profesyonel Binance USDT-M Futures bot mimarisi. Varsayılan mod **PAPER TRADING**'dir; canlı emir için `TRADING_MODE=live` gerekir.

## Öne çıkanlar
- Modüler FastAPI backend
- AI skor motoru: trend, momentum, volatilite, hacim, funding, open interest
- Risk motoru: günlük zarar limiti, ardışık kayıp limiti, max pozisyon, pozisyon başı risk
- Paper/live trade executor ayrımı
- Docker + Cloud Run deploy
- SQLite ile hızlı başlangıç, PostgreSQL'e hazır yapı
- Telegram bildirim altyapısı

## Hızlı başlatma
```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

Panel/API: `http://localhost:8080/docs`

## Önemli
Bu proje kâr garantisi vermez. Canlı kullanımdan önce minimum 2-4 hafta paper trading ve backtest yap.
