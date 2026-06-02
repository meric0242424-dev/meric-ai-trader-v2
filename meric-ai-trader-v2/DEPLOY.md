# Google Cloud Run Deploy — MERIC AI TRADER v2.0

## 1) Şifre hash üret
```bash
python scripts/make_password_hash.py SIFREN
```
Çıkan bcrypt hash'i `BOT_PASS_HASH` olarak kullan.

## 2) Cloud Run deploy
```bash
gcloud run deploy meric-ai-trader-v2 \
  --source . \
  --region europe-west1 \
  --allow-unauthenticated \
  --set-env-vars="ENV=production,TRADING_MODE=paper,BOT_USER=meric,BOT_PASS_HASH=HASH,SECRET_KEY=UZUN_RANDOM_SECRET,BINANCE_API_KEY=KEY,BINANCE_API_SECRET=SECRET"
```

## 3) Canlı işlem açmadan önce
Varsayılan `TRADING_MODE=paper`.
Canlı emir için bunu bilinçli olarak değiştir:
```bash
TRADING_MODE=live
```

## 4) Binance API güvenliği
- Withdrawal izni verme.
- Sadece Futures Trading izni ver.
- Mümkünse IP kısıtı kullan.
- Önce küçük bakiye ile test et.

## 5) Sağlık kontrolü
```bash
curl https://SERVICE_URL/health
```
