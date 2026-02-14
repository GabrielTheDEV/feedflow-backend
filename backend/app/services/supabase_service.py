"""
Serviço de integração com Supabase (PostgreSQL + Storage)
"""
from __future__ import annotations

import os
import uuid
import logging
from typing import Optional, Dict, Any

from supabase import create_client, Client

logger = logging.getLogger(__name__)


class SupabaseManager:
    """
    Gerencia operações com Supabase Storage e Database
    """

    def __init__(self) -> None:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL e SUPABASE_KEY são obrigatórios")

        self.client: Client = create_client(supabase_url, supabase_key)

    def upload_image(self, image_bytes: bytes, content_type: str = "image/png") -> str:
        """
        Faz upload da imagem para o bucket 'screenshots' e retorna a URL pública.
        """
        try:
            filename = f"{uuid.uuid4().hex}.png"
            storage = self.client.storage.from_("screenshots")

            response = storage.upload(
                path=filename,
                file=image_bytes,
                file_options={"content-type": content_type, "upsert": "false"},
            )

            public_url = storage.get_public_url(filename)
            return public_url
        except Exception as exc:
            logger.error("Erro ao fazer upload no Supabase: %s", str(exc))
            raise

    def save_feedback(
        self,
        email: str,
        comment: str,
        metadata: Optional[Dict[str, Any]],
        image_url: Optional[str],
    ) -> Dict[str, Any]:
        """
        Salva o feedback na tabela 'feedbacks' no PostgreSQL do Supabase.
        """
        try:
            payload = {
                "customer_email": email,
                "comment": comment,
                "metadata": metadata or {},
                "image_url": image_url,
            }

            response = self.client.table("feedbacks").insert(payload).execute()
            if not response.data:
                raise RuntimeError("Falha ao inserir feedback no Supabase")

            return response.data[0]
        except Exception as exc:
            logger.error("Erro ao salvar feedback no Supabase: %s", str(exc))
            raise
