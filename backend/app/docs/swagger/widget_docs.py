GENERATE_WIDGET_DOCS = {
    "summary": "Gerar script do widget",
    "description": "Gera token e script de instalação do widget para um domínio informado.",
    "response_description": "Script e token do widget",
    "responses": {
        201: {"description": "Widget gerado"},
        400: {"description": "Domínio já cadastrado ou inválido"},
        500: {"description": "Erro interno na geração"},
    },
}
