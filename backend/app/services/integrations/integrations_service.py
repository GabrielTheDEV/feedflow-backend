from uuid import UUID
from datetime import datetime, timezone

from app.models.integrations import Integration
from app.models.enums.integrationsServices import IntegrationService as IntegrationServiceEnum
from app.repositories.collection_repository import CollectionRepository
from app.repositories.integration_repository import IntegrationRepository
from app.provider.provider_factory import ProviderFactory


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

        

    def start_oauth(self, collection_id: UUID, user_id: UUID, service: IntegrationServiceEnum) -> str:
        """Generate the OAuth authorization URL for a provider."""
        self._get_owned_collection(collection_id, user_id)

        # state codifica collection_id + service para o callback
        state = f"{collection_id}:{service.value}"
        provider = ProviderFactory.get_provider(service)
        return provider.get_authorization_url(state=state)


    async def complete_oauth(self, collection_id: UUID, user_id: UUID, service: IntegrationServiceEnum, code: str) -> Integration:
        """Exchange OAuth code for tokens and persist as integration config."""
        self._get_owned_collection(collection_id, user_id)

        provider = ProviderFactory.get_provider(service)
        token_data = await provider.exchange_code_for_token(code)

        integration = Integration(
            collection_id=collection_id,
            service=service,
            config_json=token_data,
        )
        return self.repo.create(integration)


    def delete_integration(self, integration_id: UUID, collection_id: UUID, user_id: UUID) -> None:
        """Delete an integration (validates ownership via collection_id)."""
        self._get_owned_collection(collection_id, user_id)

        integration = self.repo.get_by_id(integration_id)

        if not integration:
            raise ValueError("Integration not found")

        if integration.collection_id != collection_id:
            raise PermissionError("You do not have access to this integration")

        self.repo.delete(integration)