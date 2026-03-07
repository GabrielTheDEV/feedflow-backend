import json
from uuid import UUID

from app.provider.provider_factory import ProviderFactory
from app.repositories.integration_repository import IntegrationRepository


class ReportDispatcherService:
    def __init__(self, integration_repo: IntegrationRepository):
        self.integration_repo = integration_repo

    def _build_message(self, report_body: dict, origin: str) -> str:
        return (
            f"FeedFlow report recebido\n"
            f"origin: {origin}\n\n"
            f"payload:\n{json.dumps(report_body, ensure_ascii=False, default=str, indent=2)}"
        )

    async def dispatch(self, collection_id: UUID, report_body: dict, origin: str) -> int:
        integrations = self.integration_repo.get_by_collection(collection_id)
        active_integrations = [integration for integration in integrations if integration.active]

        if not active_integrations:
            raise LookupError("No active integrations for this collection")

        message = self._build_message(report_body, origin)
        delivered = 0

        for integration in active_integrations:
            provider = ProviderFactory.get_provider(integration.service)
            config = integration.config_json or {}

            await provider.send_event(config, message)
            delivered += 1

        return delivered