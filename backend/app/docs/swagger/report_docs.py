SEND_REPORT_BODY_EXAMPLE = {
    "title": "Botão de checkout não responde",
    "message": "Ao clicar em finalizar compra, nada acontece.",
    "page": "https://store.example.com/checkout",
    "metadata": {
        "browser": "Chrome",
        "viewport": "1920x1080",
    },
}


SEND_REPORT_DOCS = {
    "summary": "Receber report do widget",
    "description": (
        "Recebe um report enviado pelo widget, valida api_key e domínio de origem, "
        "e despacha o evento para as integrações ativas da collection."
    ),
    "response_description": "Report processado",
    "responses": {
        204: {"description": "Report enviado com sucesso"},
        400: {"description": "Payload inválido, api_key ausente ou origin ausente"},
        403: {"description": "API key inválida/inativa ou domínio não permitido"},
        404: {"description": "Nenhuma integração ativa para a collection"},
        500: {"description": "Erro interno no processamento do report"},
    },
}