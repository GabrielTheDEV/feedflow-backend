SUBMIT_FEEDBACK_DOCS = {
    "summary": "Enviar feedback visual",
    "description": "Recebe screenshot, mensagem e metadados do widget. Valida token e domínio autorizado.",
    "response_description": "Feedback recebido com sucesso",
    "responses": {
        201: {"description": "Feedback criado"},
        401: {"description": "Token ausente ou inválido"},
        403: {"description": "Domínio não autorizado"},
        500: {"description": "Erro interno ao processar feedback"},
    },
}


GET_FEEDBACK_DOCS = {
    "summary": "Buscar feedback por ID",
    "description": "Retorna um feedback específico do merchant autenticado via token de API.",
    "response_description": "Feedback encontrado",
    "responses": {
        200: {"description": "Feedback retornado"},
        401: {"description": "Token ausente ou inválido"},
        404: {"description": "Feedback não encontrado"},
    },
}
