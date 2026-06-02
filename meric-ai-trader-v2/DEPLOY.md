# MERIC AI TRADER v2.1 — Cloud Run Deploy

## 1. Klasöre gir
```bash
cd meric-ai-trader-v2/meric-ai-trader-v2
```

## 2. Project seç
```bash
gcloud config set project meric-trader-bot
```

## 3. Deploy — Paper Mode
Aşağıdaki komutta API key/secret ve panel şifreni doldur:

```bash
gcloud run deploy meric-bot \
--source . \
--region europe-west1 \
--allow-unauthenticated \
--set-env-vars="TRADING_MODE=paper,BINANCE_API_KEY=API_KEYIN,BINANCE_API_SECRET=API_SECRETIN,SECRET_KEY=RASTGELE_UZUN_KEY,BOT_USER=meric,BOT_PASSWORD=PANEL_SIFREN"
```

## 4. Panel
Deploy sonrası Cloud Run URL'ini aç:

```text
https://...run.app/
```

Giriş:
- Kullanıcı adı: `BOT_USER`
- Şifre: `BOT_PASSWORD`

## 5. Canlı Trade
Önce en az 24 saat paper modda test et. Canlı emir için:

```bash
gcloud run services update meric-bot \
--region europe-west1 \
--set-env-vars="TRADING_MODE=live"
```

Not: Cloud Run servis güncellemede tek env yazmak bazı mevcut env değerlerini korur, ancak emin olmak için tüm env değerlerini tekrar vermek daha güvenlidir.
