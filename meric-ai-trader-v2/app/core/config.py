from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "MERIC AI TRADER v2"
    env: str = "production"
    secret_key: str = "CHANGE_ME"
    bot_user: str = "meric"
    bot_pass_hash: str = ""
    bot_password: str = ""  # optional plain password for quick deploy; prefer BOT_PASS_HASH in production
    binance_api_key: str = ""
    binance_api_secret: str = ""
    binance_base: str = "https://fapi.binance.com"
    trading_mode: str = "paper"  # paper/live
    database_url: str = "sqlite+aiosqlite:///./trader.db"
    cors_origins: str = "*"
    default_leverage: int = 5
    risk_per_trade_pct: float = 1.0
    max_daily_loss_pct: float = 3.0
    max_consecutive_losses: int = 3
    max_open_positions: int = 3
    min_ai_score: int = 72
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
