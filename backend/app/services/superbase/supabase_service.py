"""
Serviço de integração com Supabase (PostgreSQL + Storage)
"""
from __future__ import annotations

import os
import uuid
import logging

from supabase import Client
from app.database.config import get_supabase_client

logger = logging.getLogger(__name__)


class SupabaseManager:
    """
    Gerencia operações com Supabase Storage e Database
    """

    def __init__(self) -> None:
        self.client: Client = get_supabase_client()

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

