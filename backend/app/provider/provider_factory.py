from app.models.enums.integrationsServices import IntegrationService
from app.provider.base_provider import IntegrationProvider
from app.provider.services.slack_provider import SlackProvider
from app.provider.services.jira_provider import JiraProvider
from app.provider.services.trello_provider import TrelloProvider


class ProviderFactory:

    @staticmethod
    def get_provider(service: str | IntegrationService) -> IntegrationProvider:
        service_value = service.value if isinstance(service, IntegrationService) else service

        if service_value == IntegrationService.slack.value:
            return SlackProvider()

        if service_value == IntegrationService.jira.value:
            return JiraProvider()

        if service_value == IntegrationService.trello.value:
            return TrelloProvider()

        raise ValueError(f"Provider not supported: {service_value}")