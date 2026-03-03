LOGOUT_DOCS = {
    "summary": "Logout do usuário",
    "description": "Encerra sessão do usuário autenticado no Supabase Auth.",
    "response_description": "Logout executado",
    "responses": {
        200: {"description": "Logout realizado"},
        401: {"description": "Não autenticado"},
        500: {"description": "Erro interno no logout"},
    },
}


ME_DOCS = {
    "summary": "Dados do usuário autenticado",
    "description": "Retorna as informações básicas do usuário autenticado pelo token Bearer.",
    "response_description": "Dados do usuário",
    "responses": {
        200: {"description": "Usuário autenticado"},
        401: {"description": "Token inválido ou expirado"},
    },
}
