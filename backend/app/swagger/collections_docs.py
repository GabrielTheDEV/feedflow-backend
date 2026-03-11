GET_COLLECTION_BY_ID_DOCS = {
    "summary": "Buscar collection por ID",
    "description": "Retorna os dados de uma collection específica do usuário autenticado.",
    "response_description": "Dados da collection",
    "responses": {
        403: {"description": "Usuário sem permissão para esta collection"},
        404: {"description": "Collection não encontrada"},
    },
}
CREATE_COLLECTION_DOCS = {
    "summary": "Criar collection",
    "description": "Cria uma collection para o usuário autenticado e gera API key inicial.",
    "response_description": "Collection criada",
}


LIST_COLLECTIONS_DOCS = {
    "summary": "Listar collections",
    "description": "Lista todas as collections do usuário autenticado.",
    "response_description": "Lista de collections",
}


DEACTIVATE_COLLECTION_DOCS = {
    "summary": "Desativar collection",
    "description": "Marca uma collection como inativa.",
    "response_description": "Collection desativada",
}


ACTIVATE_COLLECTION_DOCS = {
    "summary": "Ativar collection",
    "description": "Marca uma collection como ativa.",
    "response_description": "Collection ativada",
}


DELETE_COLLECTION_DOCS = {
    "summary": "Excluir collection",
    "description": "Remove definitivamente uma collection do usuário autenticado.",
    "response_description": "Collection removida",
    "responses": {
        403: {
            "description": "Usuário sem permissão para esta collection",
        },
        404: {
            "description": "Collection não encontrada",
        },
    },
}


ROTATE_COLLECTION_KEY_DOCS = {
    "summary": "Rotacionar API key",
    "description": "Gera uma nova API key para a collection.",
    "response_description": "Collection com nova API key",
    "responses": {
        403: {
            "description": "Usuário sem permissão para esta collection",
        },
        404: {
            "description": "Collection não encontrada",
        },
    },
}
