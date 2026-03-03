from sqlmodel import Session

from app.models.integration import Integration
from app.models.enums import IntegrationService as IntegrationEnum
from app.repositories.integration_repository import IntegrationRepository


class IntegrationService:
    def __init__(self):
        self.repo = IntegrationRepository()

    def enable_integration(
        self,
        session: Session,
        collection_id,
        service: IntegrationEnum,
        config: dict | None = None,
    ) -> Integration:

        existing = self.repo.get_active_by_service(
            session,
            collection_id,
            service,
        )

        if existing:
            return existing

        integration = Integration(
            collection_id=collection_id,
            service=service,
            config_json=config,
            is_active=True,
        )

        return self.repo.create(session, integration)


    def connect_integration(collection_id, service, config)
    def disconnect_integration(integration_id)
    def list_active_integrations(collection_id)
    def send_report_to_integrations(collection_id, payload)