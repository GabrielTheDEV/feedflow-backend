from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class IntegrationProvider(ABC):

    @abstractmethod
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        pass

    @abstractmethod
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def send_event(self, config: Dict[str, Any], message: str) -> None:
        pass

    @abstractmethod
    async def validate_connection(self, config: Dict[str, Any]) -> bool:
        pass