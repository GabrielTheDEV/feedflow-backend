# Guia de Rotas da API (FeedFlow)

Este documento descreve as rotas ativas do backend para facilitar onboarding e desenvolvimento.

## Base URL

- Local (exemplo): `http://localhost:8000`

## Tipos de autenticação

### 1) JWT Bearer (usuário autenticado)

Usado nas rotas de collections, domains (exceto verify), integrations e `/api/v1/me`.

Header:

```http
Authorization: Bearer <supabase_jwt>
```

### 2) API key da collection (widget)

Usado na rota de ingestão de reports do widget.

- Query param obrigatório: `api_key`
- O backend também valida `Origin`/`Referer` contra os domínios permitidos da collection.

## Health

### GET `/api/v1/`

- Objetivo: verificar se a API está online.
- Auth: não exige.
- Resposta `200`:

```json
{
  "message": "Hello World",
  "status": "online",
  "service": "FeedFlow_API-0.1",
  "version": "1.0.0"
}
```

---

## User Context

### GET `/api/v1/me`

- Objetivo: validar token e retornar `user_id` autenticado.
- Auth: JWT Bearer obrigatório.
- Resposta `200`:

```json
{
  "user_id": "<uuid>"
}
```

Erros comuns:
- `401 Invalid or expired token`
- `500 Erro ao obter informações do usuário`

---

## Collections

### POST `/collections/`

- Objetivo: criar collection e gerar API key.
- Auth: JWT Bearer.
- Body:

```json
{
  "name": "Minha Collection"
}
```

- Resposta: `201 CollectionRead`.

### GET `/collections/`

- Objetivo: listar collections do usuário.
- Auth: JWT Bearer.
- Resposta: `200 [CollectionRead]`.

### PATCH `/collections/{collection_id}/deactivate`

- Objetivo: desativar collection.
- Auth: JWT Bearer + ownership.
- Resposta: `200 CollectionRead`.
- Erros: `403`, `404`.

### PATCH `/collections/{collection_id}/activate`

- Objetivo: ativar collection.
- Auth: JWT Bearer + ownership.
- Resposta: `200 CollectionRead`.
- Erros: `403`, `404`.

### POST/PATCH `/collections/{collection_id}/rotate-key`

- Objetivo: rotacionar API key da collection.
- Auth: JWT Bearer + ownership.
- Resposta: `200 CollectionRead`.
- Erros: `403`, `404`.

### DELETE `/collections/{collection_id}`

- Objetivo: remover collection.
- Auth: JWT Bearer + ownership.
- Resposta: `204`.
- Erros: `403`, `404`.

---

## Domains

### POST `/domains/{collection_id}`

- Objetivo: adicionar domínio permitido para a collection.
- Auth: JWT Bearer + ownership da collection.
- Body:

```json
{
  "domain": "example.com"
}
```

- Resposta: `200 DomainRead`.
- Erros: `400`, `403`, `404`.

### GET `/domains/{collection_id}`

- Objetivo: listar domínios da collection.
- Auth: JWT Bearer + ownership.
- Resposta: `200 [DomainRead]`.

### PATCH `/domains/{domain_id}/verify`

- Objetivo: marcar domínio como verificado.
- Auth: atualmente sem JWT (rota pública no estado atual).
- Resposta: `200 DomainRead`.
- Erro: `404`.

### PATCH `/domains/{domain_id}/deactivate`

- Objetivo: desativar domínio.
- Auth: JWT Bearer + ownership.
- Resposta: `200 DomainRead`.

### PATCH `/domains/{domain_id}/activate`

- Objetivo: ativar domínio.
- Auth: JWT Bearer + ownership.
- Resposta: `200 DomainRead`.

### DELETE `/domains/{domain_id}`

- Objetivo: remover domínio.
- Auth: JWT Bearer + ownership.
- Resposta: `204`.

---

## Integrations

### POST `/integrations/{collection_id}`

- Objetivo: criar integração para collection.
- Auth: JWT Bearer + ownership.
- Body:

```json
{
  "service": "slack",
  "config": {}
}
```

- `service` aceita: `slack`, `jira`, `trello`.
- Resposta: `201 IntegrationRead`.
- Erros: `403`, `404`.

### GET `/integrations/{collection_id}`

- Objetivo: listar integrações da collection.
- Auth: JWT Bearer + ownership.
- Resposta: `200 [IntegrationRead]`.

### DELETE `/integrations/{collection_id}/{integration_id}`

- Objetivo: remover integração.
- Auth: JWT Bearer + ownership.
- Resposta: `204`.
- Erros: `403`, `404`.

### GET `/integrations/{collection_id}/oauth/{provider}/authorize`

- Objetivo: gerar URL de autorização OAuth do provider.
- Auth: JWT Bearer + ownership.
- `provider` aceita: `slack`, `jira`, `trello`.
- Query params opcionais:
  - `redirect` (bool, default `true`): se `true`, redireciona (302) para o provider. Se `false`, retorna JSON com a URL.
- Resposta com `redirect=true` (default): `302` redirect para o provider.
- Resposta com `redirect=false`: `200`

```json
{
  "authorization_url": "https://slack.com/oauth/v2/authorize?..."
}
```

- Erros: `400`, `403`.

### GET `/integrations/{collection_id}/oauth/{provider}/callback?code=<auth_code>`

- Objetivo: receber o authorization code do provider, trocar por tokens e criar a integração com `config_json` preenchido.
- Auth: JWT Bearer + ownership.
- Query param obrigatório: `code` (retornado pelo provider após autorização).
- Resposta: `200 IntegrationRead`.
- Erros: `400` (code inválido ou falha na troca de token), `403`.

**Fluxo OAuth resumido:**

1. Frontend chama `/oauth/{provider}/authorize` → backend redireciona (302) para o provider.
2. Usuário autoriza → provider redireciona para `/oauth/{provider}/callback?code=xxx`.
3. Backend troca code por tokens → salva em `config_json` → retorna `IntegrationRead`.

---

## Reports (Widget - fluxo atual)

### POST `/reports/?api_key=<collection_api_key>`

- Objetivo: receber report do widget e despachar para integrações ativas.
- Auth: API key da collection (query param), sem JWT.
- Validação adicional: domínio da request (`Origin`/`Referer`) precisa estar autorizado.
- Body: JSON livre (objeto). Exemplo recomendado:

```json
{
  "title": "Widget report",
  "message": "Erro ao finalizar checkout",
  "email": "qa@empresa.com",
  "page": "https://site.com/checkout",
  "metadata": {
    "browser": "Chrome"
  },
  "has_screenshot": false
}
```

Respostas:
- `204`: enviado com sucesso para integrações ativas.
- `400`: `api_key` ausente, `origin` ausente ou payload inválido.
- `403`: API key inválida/inativa ou domínio não permitido.
- `404`: nenhuma integração ativa para a collection.
- `500`: erro interno.

---

## Arquivo estático do widget

### GET `/static/widget.js`

- Objetivo: servir script do widget para sites clientes.
- Auth: não exige.
- Cache: desabilitado para atualização imediata (`Cache-Control: no-cache, no-store, must-revalidate`).

---

## Dicas para dev


- Antes de testar `/reports`, garanta:
  1. collection ativa,
  2. domínio ativo + verificado,
  3. ao menos uma integração ativa com `config` válido.
- Para validar contratos atualizados, abra o Swagger local (`/docs`).