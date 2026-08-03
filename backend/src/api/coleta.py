"""
LeadFlow - API de Coleta de Leads
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from src.database import get_db
from src.schemas import ColetaGoogleMaps, ColetaInstagram, ColetaLinkedIn, ColetaCNPJ
from src.auth import get_current_user
from src.services.coleta_leads import ColetaLeads

router = APIRouter()
coleta = ColetaLeads()


@router.post("/google-maps")
async def coletar_google_maps(
    data: ColetaGoogleMaps,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Coleta leads do Google Maps"""
    background_tasks.add_task(
        coleta.google_maps,
        nicho=data.nicho,
        cidade=data.cidade,
        estado=data.estado,
        raio_km=data.raio_km,
        limite=data.limite,
        user_id=user["id"],
    )
    return {
        "message": f"Coleta iniciada: {data.nicho} em {data.cidade}",
        "status": "processando",
    }


@router.post("/instagram")
async def coletar_instagram(
    data: ColetaInstagram,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Coleta leads do Instagram"""
    background_tasks.add_task(
        coleta.instagram,
        hashtags=data.hashtags,
        local=data.local,
        limite=data.limite,
        user_id=user["id"],
    )
    return {
        "message": f"Coleta iniciada: hashtags {data.hashtags}",
        "status": "processando",
    }


@router.post("/linkedin")
async def coletar_linkedin(
    data: ColetaLinkedIn,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Coleta leads do LinkedIn"""
    background_tasks.add_task(
        coleta.linkedin,
        cargo=data.cargo,
        empresa=data.empresa,
        local=data.local,
        limite=data.limite,
        user_id=user["id"],
    )
    return {
        "message": f"Coleta iniciada: {data.cargo}",
        "status": "processando",
    }


@router.post("/cnpj")
async def consultar_cnpj(
    data: ColetaCNPJ,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Consulta dados de CNPJ na Receita Federal"""
    resultado = await coleta.consultar_cnpj(data.cnpj)
    if not resultado:
        raise HTTPException(status_code=404, detail="CNPJ não encontrado")
    return resultado


@router.post("/cnpj/{cnpj}/importar")
async def importar_cnpj(
    cnpj: str,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Importa empresa por CNPJ"""
    empresa = await coleta.importar_empresa_cnpj(cnpj, db)
    if not empresa:
        raise HTTPException(status_code=404, detail="CNPJ não encontrado ou erro na importação")
    return {"message": "Empresa importada", "empresa_id": str(empresa.id)}
