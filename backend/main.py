"""
LeadFlow CRM - Backend API
FastAPI + PostgreSQL + Redis + Frontend
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
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

@app.get("/health")
async def health():
    return {"status": "healthy"}

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

# Serve frontend static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    # Catch-all pra servir o frontend
    @app.get("/{full_path:path}")
    async def serve_frontend(request: Request, full_path: str):
        # Tenta servir arquivo estático primeiro
        file_path = os.path.join(static_dir, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)

        # Senão, serve o index.html (SPA)
        index_path = os.path.join(static_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)

        return HTMLResponse("<h1>LeadFlow - Frontend não encontrado</h1>", status_code=404)
else:
    @app.get("/")
    async def root():
        return {
            "app": "LeadFlow",
            "version": "1.0.0",
            "status": "online",
            "docs": "/docs",
            "frontend": "Não buildado ainda",
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
