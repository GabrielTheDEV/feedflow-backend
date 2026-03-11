ENABLE_INTEGRATION_DOCS = {
    "summary": "Ativar integração",
    "description": "Ativa uma integração para a collection informada.",
    "response_description": "Integração ativa",
}
CREATE_INTEGRATION_DOCS = {
    "summary": "Criar nova integração",
    "description": "Cria uma nova integração (Slack, Jira, Trello) para uma collection. Requer autenticação JWT.",
    "responses": {
        201: {
            "description": "Integração criada com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "collection_id": "550e8400-e29b-41d4-a716-446655440001",
                        "service": "slack",
                        "active": True,
                        "created_at": "2026-03-06T12:00:00Z",
                    }
                }
            },
        },
        400: {"description": "Dados inválidos"},
        401: {"description": "Token ausente ou inválido"},
        403: {"description": "Sem acesso à collection"},
    },
}

LIST_INTEGRATIONS_DOCS = {
    "summary": "Listar integrações de uma collection",
    "description": "Retorna todas as integrações ativas de uma collection. Requer autenticação JWT.",
    "responses": {
        200: {
            "description": "Lista de integrações",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "collection_id": "550e8400-e29b-41d4-a716-446655440001",
                            "service": "slack",
                            "active": True,
                            "created_at": "2026-03-06T12:00:00Z",
                        }
                    ]
                }
            },
        },
        401: {"description": "Token ausente ou inválido"},
        403: {"description": "Sem acesso à collection"},
    },
}

DELETE_INTEGRATION_DOCS = {
    "summary": "Deletar uma integração",
    "description": "Remove uma integração de uma collection. Requer autenticação JWT e ownership da collection.",
    "responses": {
        204: {"description": "Integração deletada com sucesso"},
        401: {"description": "Token ausente ou inválido"},
        403: {"description": "Sem acesso à collection ou integração"},
        404: {"description": "Integração não encontrada"},
    },
}

OAUTH_AUTHORIZE_DOCS = {
    "summary": "Iniciar OAuth do provider",
    "description": (
        "Redireciona o usuário para a tela de consentimento OAuth do provider (Slack, Jira, Trello). "
        "Requer autenticação JWT e ownership da collection."
    ),
    "responses": {
        302: {"description": "Redirect para o provider OAuth"},
        400: {"description": "Provider inválido ou erro de configuração"},
        401: {"description": "Token ausente ou inválido"},
        403: {"description": "Sem acesso à collection"},
    },
}

OAUTH_CALLBACK_DOCS = {
    "summary": "Callback OAuth do provider",
    "description": (
        "Recebe o authorization code do provider, troca por tokens de acesso e cria a integração "
        "com config_json preenchido. Requer autenticação JWT e ownership da collection."
    ),
    "responses": {
        200: {
            "description": "Integração criada com sucesso via OAuth",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "service": "slack",
                        "active": True,
                    }
                }
            },
        },
        400: {"description": "Code ausente, inválido ou falha na troca de token"},
        401: {"description": "Token ausente ou inválido"},
        403: {"description": "Sem acesso à collection"},
    },
}