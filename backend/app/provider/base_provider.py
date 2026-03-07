from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

# INTERFACE : base para os providers de integração
class IntegrationProvider(ABC):

    @abstractmethod
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """Gera URL de autorização OAuth do provedor.

        Args:
            state: Valor opcional para proteção/controle do fluxo OAuth.

        Returns:
            URL completa para redirecionamento do usuário.
        """
        pass

    @abstractmethod
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Troca o código de autorização por token de acesso.

        Args:
            code: Código retornado pelo provedor após autorização.

        Returns:
            Payload com tokens e metadados específicos do provedor.
        """
        pass

    @abstractmethod
    async def send_event(self, config: Dict[str, Any], message: str) -> None:
        """Envia um evento/mensagem para o serviço de integração.

        Args:
            config: Configuração necessária para envio no provedor.
            message: Conteúdo do evento a ser enviado.
        """
        pass

    @abstractmethod
    async def validate_connection(self, config: Dict[str, Any]) -> bool:
        """Valida se a conexão/configuração do provedor está funcional.

        Args:
            config: Configuração de autenticação e conexão.

        Returns:
            True quando a integração está válida; False caso contrário.
        """
        pass