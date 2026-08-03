"""
LeadFlow - Serviço de Coleta de Leads
"""

import httpx
from typing import List, Optional, Dict
from datetime import datetime
from sqlalchemy.orm import Session
from src.database import SessionLocal
from src.models.lead import Lead
from src.models.empresa import Empresa
from src.config import settings


class ColetaLeads:
    """Serviço de coleta de leads de múltiplas fontes"""

    def __init__(self):
        self.google_maps_key = settings.GOOGLE_MAPS_API_KEY

    async def google_maps(
        self,
        nicho: str,
        cidade: str,
        estado: Optional[str] = None,
        raio_km: int = 10,
        limite: int = 50,
        user_id: str = None,
    ) -> List[Dict]:
        """Coleta leads do Google Maps"""
        db = SessionLocal()
        leads_criados = []

        try:
            # Monta query de busca
            query = f"{nicho} em {cidade}"
            if estado:
                query += f", {estado}"

            # Busca via Places API
            async with httpx.AsyncClient() as client:
                # Primeiro busca o local
                geo_response = await client.get(
                    "https://maps.googleapis.com/maps/api/geocode/json",
                    params={"address": f"{cidade}, {estado}, Brasil", "key": self.google_maps_key},
                )
                geo_data = geo_response.json()

                if not geo_data.get("results"):
                    return []

                location = geo_data["results"][0]["geometry"]["location"]
                lat, lng = location["lat"], location["lng"]

                # Busca empresas próximas
                places_response = await client.get(
                    "https://maps.googleapis.com/maps/api/place/nearbysearch/json",
                    params={
                        "location": f"{lat},{lng}",
                        "radius": raio_km * 1000,
                        "keyword": nicho,
                        "type": "establishment",
                        "key": self.google_maps_key,
                    },
                )
                places_data = places_response.json()

                for place in places_data.get("results", [])[:limite]:
                    # Busca detalhes do lugar
                    details_response = await client.get(
                        "https://maps.googleapis.com/maps/api/place/details/json",
                        params={
                            "place_id": place["place_id"],
                            "fields": "name,formatted_address,formatted_phone_number,website,business_status,rating,user_ratings_total",
                            "key": self.google_maps_key,
                        },
                    )
                    details = details_response.json().get("result", {})

                    # Cria empresa
                    empresa = Empresa(
                        nome_fantasia=details.get("name"),
                        nicho=nicho,
                        cidade=cidade,
                        estado=estado,
                        endereco=details.get("formatted_address"),
                        telefone=details.get("formatted_phone_number"),
                        site=details.get("website"),
                        latitude=lat,
                        longitude=lng,
                    )
                    db.add(empresa)
                    db.flush()

                    # Cria lead
                    lead = Lead(
                        empresa_id=empresa.id,
                        nome=details.get("name", "Empresa"),
                        telefone=details.get("formatted_phone_number"),
                        whatsapp=self._format_phone(details.get("formatted_phone_number")),
                        fonte="google_maps",
                        score=self._calcular_score_inicial(details),
                        responsavel_id=user_id,
                    )
                    db.add(lead)
                    leads_criados.append(lead)

                db.commit()

        except Exception as e:
            db.rollback()
            print(f"Erro na coleta Google Maps: {e}")
        finally:
            db.close()

        return [{"id": str(l.id), "nome": l.nome} for l in leads_criados]

    async def instagram(
        self,
        hashtags: List[str],
        local: Optional[str] = None,
        limite: int = 50,
        user_id: str = None,
    ) -> List[Dict]:
        """Coleta leads do Instagram via hashtags"""
        db = SessionLocal()
        leads_criados = []

        try:
            # Usando Graph API do Meta (precisa de access token)
            access_token = settings.INSTAGRAM_ACCESS_TOKEN if hasattr(settings, 'INSTAGRAM_ACCESS_TOKEN') else None

            if not access_token:
                print("Instagram access token não configurado")
                return []

            async with httpx.AsyncClient() as client:
                for hashtag in hashtags:
                    # Busca hashtag ID
                    hashtag_response = await client.get(
                        f"https://graph.facebook.com/v18.0/ig_hashtag_search",
                        params={
                            "user_id": settings.INSTAGRAM_BUSINESS_ID if hasattr(settings, 'INSTAGRAM_BUSINESS_ID') else "",
                            "q": hashtag,
                            "access_token": access_token,
                        },
                    )
                    hashtag_data = hashtag_response.json()

                    if not hashtag_data.get("data"):
                        continue

                    hashtag_id = hashtag_data["data"][0]["id"]

                    # Busca mídia recente
                    media_response = await client.get(
                        f"https://graph.facebook.com/v18.0/{hashtag_id}/recent_media",
                        params={
                            "user_id": settings.INSTAGRAM_BUSINESS_ID if hasattr(settings, 'INSTAGRAM_BUSINESS_ID') else "",
                            "fields": "id,caption,media_type,media_url,permalink,timestamp,username",
                            "limit": min(limite, 50),
                            "access_token": access_token,
                        },
                    )
                    media_data = media_response.json()

                    for media in media_data.get("data", []):
                        username = media.get("username")
                        if not username:
                            continue

                        # Busca perfil do usuário
                        user_response = await client.get(
                            f"https://graph.facebook.com/v18.0/{settings.INSTAGRAM_BUSINESS_ID if hasattr(settings, 'INSTAGRAM_BUSINESS_ID') else ''}",
                            params={
                                "fields": f"business_discovery.fields(username,name,biography,followers_count,media_count,profile_picture_url,website).where(username='{username}')",
                                "access_token": access_token,
                            },
                        )
                        user_data = user_response.json().get("business_discovery", {})

                        if not user_data:
                            continue

                        # Cria lead
                        lead = Lead(
                            nome=user_data.get("name", username),
                            instagram=f"https://instagram.com/{username}",
                            fonte="instagram",
                            score=min(user_data.get("followers_count", 0) // 100, 50),
                            notas=f"Bio: {user_data.get('biography', '')}",
                            responsavel_id=user_id,
                        )
                        db.add(lead)
                        leads_criados.append(lead)

                db.commit()

        except Exception as e:
            db.rollback()
            print(f"Erro na coleta Instagram: {e}")
        finally:
            db.close()

        return [{"id": str(l.id), "nome": l.nome} for l in leads_criados]

    async def linkedin(
        self,
        cargo: str,
        empresa: Optional[str] = None,
        local: Optional[str] = None,
        limite: int = 50,
        user_id: str = None,
    ) -> List[Dict]:
        """Coleta leads do LinkedIn (via proxy/RapidAPI)"""
        db = SessionLocal()
        leads_criados = []

        try:
            # LinkedIn não tem API pública aberta
            # Opção 1: RapidAPI LinkedIn
            # Opção 2: Proxy com Selenium/Playwright
            # Por enquanto, placeholder

            print("LinkedIn scraping requer configuração de proxy ou RapidAPI")
            return []

        except Exception as e:
            db.rollback()
            print(f"Erro na coleta LinkedIn: {e}")
        finally:
            db.close()

        return leads_criados

    async def consultar_cnpj(self, cnpj: str) -> Optional[Dict]:
        """Consulta CNPJ na Receita Federal via BrasilAPI"""
        try:
            cnpj_limpo = cnpj.replace(".", "").replace("/", "").replace("-", "")

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}",
                    timeout=10.0,
                )

                if response.status_code != 200:
                    return None

                data = response.json()
                return {
                    "cnpj": data.get("cnpj"),
                    "razao_social": data.get("razao_social"),
                    "nome_fantasia": data.get("nome_fantasia"),
                    "cidade": data.get("municipio"),
                    "estado": data.get("uf"),
                    "endereco": f"{data.get('logradouro', '')}, {data.get('numero', '')} - {data.get('bairro', '')}",
                    "telefone": data.get("ddd_telefone_1"),
                    "email": data.get("email"),
                    "situacao": data.get("situacao_cadastral"),
                    "data_abertura": data.get("data_inicio_atividade"),
                    "cnae": data.get("cnae_fiscal_descricao"),
                }

        except Exception as e:
            print(f"Erro ao consultar CNPJ: {e}")
            return None

    async def importar_empresa_cnpj(self, cnpj: str, db: Session) -> Optional[Empresa]:
        """Importa empresa por CNPJ"""
        dados = await self.consultar_cnpj(cnpj)
        if not dados:
            return None

        # Verifica se já existe
        empresa = db.query(Empresa).filter(Empresa.cnpj == cnpj).first()
        if empresa:
            return empresa

        empresa = Empresa(
            cnpj=dados["cnpj"],
            razao_social=dados["razao_social"],
            nome_fantasia=dados.get("nome_fantasia") or dados["razao_social"],
            cidade=dados.get("cidade"),
            estado=dados.get("estado"),
            endereco=dados.get("endereco"),
            telefone=dados.get("telefone"),
            email=dados.get("email"),
            nicho=dados.get("cnae"),
        )
        db.add(empresa)
        db.commit()
        db.refresh(empresa)
        return empresa

    def _format_phone(self, phone: Optional[str]) -> Optional[str]:
        """Formata telefone pra WhatsApp"""
        if not phone:
            return None
        # Remove caracteres especiais
        clean = "".join(filter(str.isdigit, phone))
        if not clean.startswith("55"):
            clean = "55" + clean
        return clean

    def _calcular_score_inicial(self, place_details: dict) -> int:
        """Calcula score inicial baseado nos dados do Google"""
        score = 30  # Base

        # Rating
        rating = place_details.get("rating", 0)
        if rating >= 4.5:
            score += 20
        elif rating >= 4.0:
            score += 15
        elif rating >= 3.5:
            score += 10

        # Total de avaliações
        reviews = place_details.get("user_ratings_total", 0)
        if reviews >= 100:
            score += 15
        elif reviews >= 50:
            score += 10
        elif reviews >= 10:
            score += 5

        # Tem site
        if place_details.get("website"):
            score += 15

        # Tem telefone
        if place_details.get("formatted_phone_number"):
            score += 10

        return min(score, 100)
