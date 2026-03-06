from uuid import UUID

from app.models.integrations import Integration
from app.models.enums.integrationsServices import IntegrationService as IntegrationServiceEnum
from app.repositories.collection_repository import CollectionRepository
from app.repositories.integration_repository import IntegrationRepository


class IntegrationService:
    def __init__(self, repo: IntegrationRepository, collection_repo: CollectionRepository):
        self.repo = repo
        self.collection_repo = collection_repo

    def _get_owned_collection(self, collection_id: UUID, user_id: UUID):
        collection = self.collection_repo.get_by_id(collection_id)

        if not collection:
            raise ValueError("Collection not found")

        if collection.user_id != user_id:
            raise PermissionError("You do not have access to this collection")

        return collection

    def create_integration(
        self,
        collection_id: UUID,
        user_id: UUID,
        service: IntegrationServiceEnum,
        config: dict = None,
    ) -> Integration:
        """Create a new integration for a collection."""
        self._get_owned_collection(collection_id, user_id)

        integration = Integration(
            collection_id=collection_id,
            service=service,
            config_json=config,
        )
        return self.repo.create(integration)

    def list_by_collection(self, collection_id: UUID, user_id: UUID):
        """List all integrations for a collection."""
        self._get_owned_collection(collection_id, user_id)
        return self.repo.get_by_collection(collection_id)

    def delete_integration(self, integration_id: UUID, collection_id: UUID, user_id: UUID) -> None:
        """Delete an integration (validates ownership via collection_id)."""
        self._get_owned_collection(collection_id, user_id)

        integration = self.repo.get_by_id(integration_id)

        if not integration:
            raise ValueError("Integration not found")

        if integration.collection_id != collection_id:
            raise PermissionError("You do not have access to this integration")

        self.repo.delete(integration)