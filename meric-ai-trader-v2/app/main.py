from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.api.routes import router
from app.database.session import init_db

app=FastAPI(title=settings.app_name)
origins=["*"] if settings.cors_origins == "*" else [x.strip() for x in settings.cors_origins.split(",")]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.on_event("startup")
async def startup():
    await init_db()

@app.get("/health")
async def health():
    return {"ok": True, "name": settings.app_name, "mode": settings.trading_mode}

@app.get("/")
async def root():
    return FileResponse("app/static/index.html")
