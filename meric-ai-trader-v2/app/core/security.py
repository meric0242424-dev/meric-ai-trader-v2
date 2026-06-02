import time
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings

ALGORITHM = "HS256"
TOKEN_EXPIRE_MIN = 60 * 24
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

def verify_password(plain: str, hashed: str) -> bool:
    if not hashed:
        return False
    try:
        return pwd_context.verify(plain, hashed)
    except Exception:
        return False

def create_token(username: str) -> str:
    return jwt.encode({"sub": username, "exp": time.time() + TOKEN_EXPIRE_MIN * 60}, settings.secret_key, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username != settings.bot_user:
            raise HTTPException(status_code=401, detail="Geçersiz token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Geçersiz token")
