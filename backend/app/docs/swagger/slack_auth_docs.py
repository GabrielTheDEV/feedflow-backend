SLACK_INSTALL_DOCS = {
    "summary": "Iniciar OAuth do Slack",
    "description": "Gera redirecionamento para autorização no Slack usando usuário autenticado ou merchant_id.",
    "response_description": "Redirecionamento para o Slack",
}


SLACK_CALLBACK_DOCS = {
    "summary": "Callback OAuth do Slack",
    "description": "Recebe código OAuth, troca por token e salva integração no banco.",
    "response_description": "Redirecionamento após integração",
}


SLACK_DISCONNECT_DOCS = {
    "summary": "Desconectar Slack",
    "description": "Remove a integração do Slack para um merchant.",
    "response_description": "Status da desconexão",
}


SLACK_STATUS_DOCS = {
    "summary": "Status da integração Slack",
    "description": "Retorna se o merchant possui integração ativa com Slack.",
    "response_description": "Estado da integração",
}
