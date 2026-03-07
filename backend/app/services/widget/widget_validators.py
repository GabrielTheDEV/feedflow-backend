from app.models.collections import Collection
from app.services.collections.collections_service import CollectionService
from app.services.collections.domain_service import DomainService


class WidgetValidator:
    def __init__(self, service: CollectionService, domain_service: DomainService):
        self.service = service
        self.domain_service = domain_service

    def validate(self, api_key: str, origin: str) -> Collection:
        if not api_key:
            raise ValueError("api_key is required")

        if not origin:
            raise ValueError("origin is required")

        collection = self.service.get_active_by_api_key(api_key)
        self.domain_service.assert_domain_allowed(collection.id, origin) # se domain não for permitido não retorna a collection

        return collection
