import sys
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
if len(sys.argv) != 2:
    print("Kullanım: python scripts/make_password_hash.py SIFRE")
    raise SystemExit(1)
print(pwd_context.hash(sys.argv[1]))
