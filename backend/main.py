"""
LeadFlow CRM - Backend API
FastAPI + PostgreSQL + Redis
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

# Garante que PORT existe
os.environ.setdefault("PORT", "8080")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 LeadFlow API iniciando...")
    yield
    print("👋 LeadFlow API encerrando...")

app = FastAPI(
    title="LeadFlow API",
    description="CRM de Prospecção B2B com IA",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "app": "LeadFlow",
        "version": "1.0.0",
        "status": "online",
        "docs": "/docs",
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "domain": "fhlabs.online"}

# Rotas da API
try:
    from src.api import leads, pipeline, whatsapp, ia, coleta, relatorios
    app.include_router(leads.router, prefix="/api/leads", tags=["Leads"])
    app.include_router(pipeline.router, prefix="/api/pipeline", tags=["Pipeline"])
    app.include_router(whatsapp.router, prefix="/api/whatsapp", tags=["WhatsApp"])
    app.include_router(ia.router, prefix="/api/ia", tags=["IA"])
    app.include_router(coleta.router, prefix="/api/coleta", tags=["Coleta"])
    app.include_router(relatorios.router, prefix="/api/relatorios", tags=["Relatórios"])
except Exception as e:
    print(f"⚠️  Erro ao carregar rotas: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
