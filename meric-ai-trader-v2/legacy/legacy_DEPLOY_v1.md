# MERİC TRADER BOT — Google Cloud Run Deploy

## 1. Önce şifre hash'ini üret
```bash
python3 -c "from passlib.context import CryptContext; print(CryptContext(schemes=['bcrypt']).hash('SIFRENIZ'))"
```
Çıkan hash'i not al.

## 2. Google Cloud'a deploy
```bash
# Cloud Run'a git: console.cloud.google.com/run
# "Create Service" → "Continuously deploy from a repository" YERİNE
# "Deploy one revision from an existing container image" seç

# VEYA Cloud Shell'den:
gcloud run deploy meric-bot \
  --source . \
  --region europe-west1 \
  --allow-unauthenticated \
  --set-env-vars="BINANCE_API_KEY=API_KEYIN,BINANCE_API_SECRET=API_SECRETIN,BOT_USER=meric,BOT_PASS_HASH=HASHIN,SECRET_KEY=RASTGELE_GIZLI_KEY"
```

## 3. Environment Variables (Cloud Run → Edit → Variables)
| Key | Value |
|-----|-------|
| BINANCE_API_KEY | Binance API Key |
| BINANCE_API_SECRET | Binance API Secret |
| BOT_USER | meric (veya istediğin) |
| BOT_PASS_HASH | Adım 1'deki hash |
| SECRET_KEY | rastgele uzun string |

## 4. Binance API Key Ayarları
- Binance → API Management → Create API
- ✅ Enable Futures Trading
- ❌ Withdrawal izni VERME
- IP kısıtlaması: Cloud Run IP'ni ekle

## 5. Giriş
Cloud Run URL'ine git → kullanıcı adı ve şifre ile giriş yap
