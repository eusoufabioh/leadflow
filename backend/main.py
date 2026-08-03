"""
LeadFlow CRM - Backend API
FastAPI + PostgreSQL + Redis
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import uvicorn

from src.api import leads, pipeline, whatsapp, ia, coleta, relatorios
from src.database import engine, SessionLocal
from src.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup e shutdown da aplicação"""
    # Startup
    print("🚀 LeadFlow API iniciando...")
    yield
    # Shutdown
    print("👋 LeadFlow API encerrando...")


app = FastAPI(
    title="LeadFlow API",
    description="CRM de Prospecção B2B com IA",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas
app.include_router(leads.router, prefix="/api/leads", tags=["Leads"])
app.include_router(pipeline.router, prefix="/api/pipeline", tags=["Pipeline"])
app.include_router(whatsapp.router, prefix="/api/whatsapp", tags=["WhatsApp"])
app.include_router(ia.router, prefix="/api/ia", tags=["IA"])
app.include_router(coleta.router, prefix="/api/coleta", tags=["Coleta"])
app.include_router(relatorios.router, prefix="/api/relatorios", tags=["Relatórios"])


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
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
