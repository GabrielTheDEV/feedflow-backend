# Integrations & Providers — FeedFlow

## Visão Geral

O FeedFlow conecta collections a serviços externos (Slack, Jira, Trello) por meio de **integrações**. Cada integração armazena credenciais e configurações específicas do provider em um campo JSON único (`config_json`), sem necessidade de tabelas separadas por serviço.

---

## Arquitetura

### Camadas

```
Router (integration_router)
  │
  ├─ IntegrationService          ← orquestra CRUD + OAuth
  │     │
  │     ├─ IntegrationRepository ← persistência (SQLModel/PostgreSQL)
  │     └─ ProviderFactory       ← instancia o provider correto
  │           │
  │           ├─ SlackProvider
  │           ├─ JiraProvider
  │           └─ TrelloProvider
  │
  └─ ReportDispatcherService     ← despacha reports para integrações ativas
        │
        └─ ProviderFactory → provider.send_event(config, message)
```

### Diagrama de classes (Provider Pattern)

```mermaid
classDiagram
    class IntegrationProvider {
        <<abstract>>
        +get_authorization_url(state) str
        +exchange_code_for_token(code) dict
        +send_event(config, message) None
        +validate_connection(config) bool
    }

    class SlackProvider {
        -provider_id: str
        -provider_secret: str
        -redirect_uri: str
        +get_authorization_url(state) str
        +exchange_code_for_token(code) dict
        +send_event(config, message) None
        +validate_connection(config) bool
    }

    class JiraProvider {
        -client_id: str
        -client_secret: str
        -redirect_uri: str
        +get_authorization_url(state) str
        +exchange_code_for_token(code) dict
        +send_event(config, message) None
        +validate_connection(config) bool
    }

    class TrelloProvider {
        -api_key: str
        -api_secret: str
        +get_authorization_url(state) str
        +exchange_code_for_token(code) dict
        +send_event(config, message) None
        +validate_connection(config) bool
    }

    class ProviderFactory {
        +get_provider(service)$ IntegrationProvider
    }

    IntegrationProvider <|-- SlackProvider
    IntegrationProvider <|-- JiraProvider
    IntegrationProvider <|-- TrelloProvider
    ProviderFactory ..> IntegrationProvider : creates
```

---

## Model: Integration

| Campo           | Tipo                | Descrição                                                        |
|-----------------|---------------------|------------------------------------------------------------------|
| `id`            | UUID (PK)           | Identificador único                                              |
| `collection_id` | UUID (FK)           | Collection dona da integração                                    |
| `service`       | Enum                | `slack` \| `jira` \| `trello`                                   |
| `active`        | bool                | Se a integração está ativa para despacho                         |
| `config_json`   | JSON                | Credenciais e config específicas do provider (ver tabela abaixo) |
| `external_id`   | str (opcional)      | ID externo no provider (ex.: workspace_id)                       |
| `created_at`    | datetime            | Data de criação                                                  |
| `updated_at`    | datetime            | Data de última atualização                                       |

### Conteúdo do `config_json` por provider

| Provider | Campos esperados                                         |
|----------|----------------------------------------------------------|
| Slack    | `bot_token`, `channel_id`, `team_id`, `team_name`       |
| Jira     | `access_token`, `cloud_id`, `project_key`                |
| Trello   | `token`, `list_id`                                       |

> **Decisão de design:** optamos por manter tudo no `config_json` (desnormalizado) porque o JSON nunca é filtrado/indexado pelo banco — ele é um blob opaco passado diretamente ao provider. Isso elimina migração a cada novo provider e mantém o dispatcher genérico.

---

## Rotas

### CRUD

| Método   | Rota                                          | Descrição                         |
|----------|-----------------------------------------------|-----------------------------------|
| `POST`   | `/integrations/{collection_id}`               | Criar integração manual           |
| `GET`    | `/integrations/{collection_id}`               | Listar integrações da collection  |
| `DELETE` | `/integrations/{collection_id}/{integration_id}` | Remover integração             |

### OAuth

| Método | Rota                                                          | Descrição                                              |
|--------|---------------------------------------------------------------|--------------------------------------------------------|
| `GET`  | `/integrations/{collection_id}/oauth/{provider}/authorize`    | Redireciona (302) para consent screen do provider      |
| `GET`  | `/integrations/{collection_id}/oauth/{provider}/callback`     | Troca code por tokens, cria integração com config_json |

Todas as rotas exigem **JWT Bearer + ownership da collection**.

---

## Fluxo OAuth (authorize → callback → integração criada)

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant Backend as Integration Router
    participant Service as IntegrationService
    participant Factory as ProviderFactory
    participant Provider as SlackProvider / JiraProvider / etc
    participant External as Provider API (Slack, Jira...)

    User->>Frontend: Clica "Conectar Slack"
    Frontend->>Backend: GET /integrations/{coll}/oauth/slack/authorize
    Backend->>Service: start_oauth(collection_id, user_id, slack)
    Service->>Service: _get_owned_collection (valida ownership)
    Service->>Factory: get_provider("slack")
    Factory-->>Service: SlackProvider()
    Service->>Provider: get_authorization_url(state)
    Provider-->>Service: https://slack.com/oauth/v2/authorize?...
    Service-->>Backend: URL
    Backend-->>Frontend: 302 Redirect → Slack

    User->>External: Autoriza no Slack
    External-->>Frontend: Redirect → /oauth/slack/callback?code=abc123

    Frontend->>Backend: GET /integrations/{coll}/oauth/slack/callback?code=abc123
    Backend->>Service: complete_oauth(collection_id, user_id, slack, code)
    Service->>Service: _get_owned_collection (valida ownership)
    Service->>Factory: get_provider("slack")
    Factory-->>Service: SlackProvider()
    Service->>Provider: exchange_code_for_token("abc123")
    Provider->>External: POST https://slack.com/api/oauth.v2.access
    External-->>Provider: { ok: true, access_token: "xoxb-...", team: {...} }
    Provider-->>Service: { bot_token, team_id, team_name, ... }
    Service->>Service: Integration(config_json=token_data)
    Service-->>Backend: IntegrationRead
    Backend-->>Frontend: 200 { id, service: "slack", active: true }
```

---

## Fluxo de Despacho de Reports

```mermaid
sequenceDiagram
    actor Widget
    participant ReportRouter as Report Router
    participant Dispatcher as ReportDispatcherService
    participant Repo as IntegrationRepository
    participant Factory as ProviderFactory
    participant Provider as Provider (Slack/Jira/Trello)
    participant External as API Externa

    Widget->>ReportRouter: POST /reports/?api_key=xxx { payload }
    ReportRouter->>ReportRouter: Valida api_key + origin
    ReportRouter->>Dispatcher: dispatch(collection_id, body, origin)
    Dispatcher->>Repo: get_by_collection(collection_id)
    Repo-->>Dispatcher: [Integration, Integration, ...]
    Dispatcher->>Dispatcher: Filtra apenas active=true

    loop Para cada integração ativa
        Dispatcher->>Factory: get_provider(integration.service)
        Factory-->>Dispatcher: Provider instance
        Dispatcher->>Provider: send_event(config_json, message)
        Provider->>External: POST (chat.postMessage / create issue / create card)
        External-->>Provider: OK
    end

    Dispatcher-->>ReportRouter: delivered_count
    ReportRouter-->>Widget: 204
```

---

## Como adicionar um novo provider

1. **Criar arquivo** em `backend/app/provider/services/` (ex.: `discord_provider.py`)
2. **Implementar** a interface `IntegrationProvider` (4 métodos obrigatórios)
3. **Registrar** no enum `IntegrationService` em `backend/app/models/enums/integrationsServices.py`
4. **Registrar** na `ProviderFactory` em `backend/app/provider/provider_factory.py`
5. **Nenhuma migração de banco** necessária — `config_json` aceita qualquer schema

---

## Variáveis de ambiente por provider

| Provider | Variáveis                                                     |
|----------|---------------------------------------------------------------|
| Slack    | `SLACK_CLIENT_ID`, `SLACK_CLIENT_SECRET`, `SLACK_REDIRECT_URI` |
| Jira     | `JIRA_CLIENT_ID`, `JIRA_CLIENT_SECRET`, `JIRA_REDIRECT_URI`   |
| Trello   | `TRELLO_API_KEY`, `TRELLO_API_SECRET`                          |

---

## Arquivos relacionados

| Arquivo                                            | Responsabilidade                       |
|----------------------------------------------------|----------------------------------------|
| `app/models/integrations.py`                       | Model SQLModel da integração           |
| `app/models/enums/integrationsServices.py`         | Enum dos providers suportados          |
| `app/routes/integration_router.py`                 | Rotas CRUD + OAuth                     |
| `app/services/integrations/integrations_service.py`| Lógica de negócio (CRUD + OAuth)       |
| `app/repositories/integration_repository.py`       | Persistência                           |
| `app/provider/base_provider.py`                    | Interface abstrata dos providers       |
| `app/provider/provider_factory.py`                 | Factory que instancia providers        |
| `app/provider/services/slack_provider.py`          | Provider Slack (App + Bot)             |
| `app/provider/services/jira_provider.py`           | Provider Jira                          |
| `app/provider/services/trello_provider.py`         | Provider Trello                        |
| `app/services/widget/report_dispatcher_service.py` | Despacho de reports para integrações   |
| `app/dtos/schemas.py`                              | DTOs (IntegrationEnable, IntegrationRead) |
