"""
LeadFlow - Serviço WhatsApp (Evolution API)
"""

import httpx
from typing import Optional, Dict, List
from src.config import settings


class WhatsAppBot:
    """Bot de WhatsApp via Evolution API"""

    def __init__(self):
        self.base_url = settings.EVOLUTION_API_URL
        self.api_key = settings.EVOLUTION_API_KEY
        self.instance = settings.EVOLUTION_INSTANCE
        self.headers = {"apikey": self.api_key}

    async def get_status(self) -> Dict:
        """Status da conexão"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/instance/connectionState/{self.instance}",
                headers=self.headers,
            )
            return response.json()

    async def send_message(
        self,
        phone: str,
        message: str,
        media_type: str = "texto",
        media_url: Optional[str] = None,
    ) -> Dict:
        """Envia mensagem"""
        # Limpa telefone
        phone = self._clean_phone(phone)

        endpoint = f"{self.base_url}/message/sendText/{self.instance}"

        payload = {
            "number": phone,
            "text": message,
        }

        if media_type != "texto" and media_url:
            # Envia mídia
            if media_type == "imagem":
                endpoint = f"{self.base_url}/message/sendImage/{self.instance}"
                payload = {"number": phone, "mediatype": "image", "media": media_url, "caption": message}
            elif media_type == "documento":
                endpoint = f"{self.base_url}/message/sendDocument/{self.instance}"
                payload = {"number": phone, "mediatype": "document", "media": media_url, "caption": message}
            elif media_type == "audio":
                endpoint = f"{self.base_url}/message/sendWhatsAppAudio/{self.instance}"
                payload = {"number": phone, "audio": media_url}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                endpoint,
                json=payload,
                headers=self.headers,
                timeout=30.0,
            )
            return response.json()

    async def send_template(
        self,
        phone: str,
        template_name: str,
        variables: List[str],
    ) -> Dict:
        """Envia mensagem usando template"""
        phone = self._clean_phone(phone)

        endpoint = f"{self.base_url}/message/sendTemplate/{self.instance}"

        payload = {
            "number": phone,
            "template": {
                "name": template_name,
                "language": {"code": "pt_BR"},
                "components": [
                    {
                        "type": "body",
                        "parameters": [{"type": "text", "text": v} for v in variables],
                    }
                ],
            },
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                endpoint,
                json=payload,
                headers=self.headers,
                timeout=30.0,
            )
            return response.json()

    async def check_number(self, phone: str) -> Dict:
        """Verifica se número tem WhatsApp"""
        phone = self._clean_phone(phone)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/chat/whatsappNumbers/{self.instance}",
                params={"numbers": phone},
                headers=self.headers,
            )
            return response.json()

    async def get_messages(self, phone: str, limit: int = 20) -> List[Dict]:
        """Busca histórico de mensagens"""
        phone = self._clean_phone(phone)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/chat/findMessages/{self.instance}",
                params={"where": {"key": {"remoteJid": f"{phone}@s.whatsapp.net"}}, "limit": limit},
                headers=self.headers,
            )
            return response.json().get("messages", [])

    async def get_profile(self, phone: str) -> Dict:
        """Busca perfil do contato"""
        phone = self._clean_phone(phone)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/chat/findContacts/{self.instance}",
                params={"where": {"id": f"{phone}@s.whatsapp.net"}},
                headers=self.headers,
            )
            return response.json()

    async def create_instance(self) -> Dict:
        """Cria instância do WhatsApp"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/instance/create",
                json={
                    "instanceName": self.instance,
                    "integration": "WHATSAPP-BAILEYS",
                    "qrcode": True,
                },
                headers=self.headers,
            )
            return response.json()

    async def get_qrcode(self) -> Dict:
        """Pega QR code pra conexão"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/instance/connect/{self.instance}",
                headers=self.headers,
            )
            return response.json()

    def _clean_phone(self, phone: str) -> str:
        """Limpa e formata telefone"""
        if not phone:
            return ""
        # Remove caracteres especiais
        clean = "".join(filter(str.isdigit, phone))
        # Adiciona código do país se não tiver
        if not clean.startswith("55"):
            clean = "55" + clean
        return clean
