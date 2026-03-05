

ME_DOCS = {
    "summary": "Dados do usuário autenticado",
    "description": "Retorna as informações básicas do usuário autenticado pelo token Bearer.",
    "response_description": "Dados do usuário",
    "responses": {
        200: {"description": "Usuário autenticado"},
        401: {"description": "Token inválido ou expirado"},
    },
}
