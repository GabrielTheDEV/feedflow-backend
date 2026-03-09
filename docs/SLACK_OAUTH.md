# Integração OAuth do Slack - FeedFlow

## Visão Geral

Este sistema permite que cada merchant (lojista) conecte seu próprio workspace do Slack ao FeedFlow sem precisar criar webhooks manualmente.

## Configuração Inicial

### 1. Criar Slack App

1. Acesse [https://api.slack.com/apps](https://api.slack.com/apps)
2. Clique em **"Create New App"** → **"From scratch"**
3. Nome: `FeedFlow` (ou o nome do seu produto)
4. Selecione um workspace de desenvolvimento

### 2. Configurar OAuth & Permissions

1. No menu lateral, vá em **"OAuth & Permissions"**
2. Em **"Redirect URLs"**, adicione:
   ```
   http://localhost:8000/auth/slack/callback
   https://seudominio.com/auth/slack/callback
   ```
3. Em **"Scopes" → "Bot Token Scopes"**, adicione:
   - `chat:write`
  - `channels:read`
  - `channels:join`
  - `groups:read`

### 3. Obter Credenciais

1. No menu lateral, vá em **"Basic Information"**
2. Em **"App Credentials"**, copie:
   - **Client ID**
   - **Client Secret**

### 4. Configurar Variáveis de Ambiente

Adicione ao arquivo `.env`:

```env
SLACK_CLIENT_ID=123456789012.123456789012
SLACK_CLIENT_SECRET=abc123def456ghi789jkl012mno345pq
SLACK_REDIRECT_URI=http://localhost:8000/auth/slack/callback
```

### 5. Criar Tabela no Supabase

Execute o SQL em `backend/migrations/create_slack_integrations.sql`:

```sql
CREATE TABLE slack_integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID NOT NULL UNIQUE,
    access_token TEXT NOT NULL,
    team_id TEXT NOT NULL,
    team_name TEXT,
    channel_id TEXT,
    channel_name TEXT,
    scope TEXT,
    bot_user_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 6. Reiniciar Backend

```bash
docker compose down
docker compose up -d --build
```

## Fluxo de Uso

### Para o Merchant (Lojista)

1. **Conectar Slack**
   - Acessar: `http://localhost:8000/auth/slack/install?merchant_id=UUID_DO_MERCHANT`
   - Será redirecionado para autorização do Slack
   - Escolher o canal onde quer receber notificações
   - Clicar em **"Permitir"**

2. **Verificar Status**
   ```bash
   GET /auth/slack/status?merchant_id=UUID_DO_MERCHANT
   ```
   
   Resposta:
   ```json
   {
     "connected": true,
     "team_name": "Meu Workspace",
     "channel_name": "#feedbacks"
   }
   ```

3. **Desconectar**
   ```bash
   DELETE /auth/slack/disconnect?merchant_id=UUID_DO_MERCHANT
   ```

### Para o Sistema

Ao enviar feedback, o widget deve incluir o `merchant_id`:

```javascript
const formData = new FormData();
formData.append('customer_email', email);
formData.append('customer_message', message);
formData.append('merchant_id', 'UUID_DO_MERCHANT'); // Novo campo
formData.append('screenshot', blob);

await fetch('http://localhost:8000/submit-feedback', {
    method: 'POST',
    body: formData
});
```

O backend automaticamente:
1. Busca a integração do merchant no banco
2. Usa o `bot_token` específico daquele merchant
3. Envia a notificação para o canal correto

## Endpoints da API

### GET /auth/slack/install

Inicia o fluxo OAuth redirecionando para o Slack.

**Query Parameters:**
- `merchant_id` (required): UUID do merchant

**Exemplo:**
```
http://localhost:8000/auth/slack/install?merchant_id=550e8400-e29b-41d4-a716-446655440000
```

---

### GET /auth/slack/callback

Callback automático do Slack após autorização.

**Query Parameters:**
- `code` (required): Código de autorização do Slack
- `state` (required): merchant_id passado no /install
- `error` (optional): Erro se autorização foi negada

**Exemplo de resposta bem-sucedida:**
```json
{
  "status": "success",
  "message": "Slack conectado com sucesso!",
  "team_name": "Meu Workspace",
  "channel_name": "#feedbacks"
}
```

---

### GET /auth/slack/status

Verifica se o merchant tem Slack conectado.

**Query Parameters:**
- `merchant_id` (required): UUID do merchant

**Exemplo de resposta:**
```json
{
  "connected": true,
  "team_name": "Meu Workspace",
  "channel_name": "#feedbacks"
}
```

---

### DELETE /auth/slack/disconnect

Remove a integração do Slack.

**Query Parameters:**
- `merchant_id` (required): UUID do merchant

**Exemplo de resposta:**
```json
{
  "status": "success",
  "message": "Slack desconectado com sucesso"
}
```

---

### POST /submit-feedback

Envia feedback com notificação automática para o Slack do merchant.

**Form Data:**
- `customer_email` (required): Email do cliente
- `customer_message` (required): Mensagem do feedback
- `merchant_id` (optional): UUID do merchant para buscar webhook específico
- `screenshot` (optional): Imagem capturada

**Exemplo:**
```bash
curl -X POST http://localhost:8000/submit-feedback \
  -F "customer_email=cliente@exemplo.com" \
  -F "customer_message=Ótimo produto!" \
  -F "merchant_id=550e8400-e29b-41d4-a716-446655440000" \
  -F "screenshot=@screenshot.png"
```

## Tratamento de Erros

### Token Expirado

O Slack não expira tokens OAuth v2 automaticamente, mas se o app for desinstalado pelo usuário, o token se torna inválido.

**Resposta HTTP 400:**
```json
{
  "error": "Slack OAuth failed: invalid_code"
}
```

**Solução:** O merchant precisa reconectar via `/auth/slack/install`.

---

### Acesso Negado

Se o usuário clicar em "Cancelar" na tela de autorização:

**Resposta HTTP 400:**
```json
{
  "error": "Autorização negada pelo usuário: access_denied"
}
```

---

### Canal Slack Não Configurado

Se o merchant não tiver conectado o Slack:

**Comportamento:**
- O sistema não envia para Slack sem `bot_token` e `channel_id` válidos
- O fluxo recomendado é reconectar em `/auth/slack/install` e salvar o canal alvo

## Arquitetura

```
┌──────────────┐
│   Merchant   │
│   (Lojista)  │
└──────┬───────┘
       │
       │ 1. Clica "Conectar Slack"
       ▼
┌──────────────────────┐
│  /auth/slack/install │
│  merchant_id=UUID    │
└──────┬───────────────┘
       │
       │ 2. Redirect para Slack
       ▼
┌──────────────────┐
│  Slack OAuth     │
│  (Autorização)   │
└──────┬───────────┘
       │
       │ 3. Callback com code
       ▼
┌────────────────────────┐
│ /auth/slack/callback   │
│ code=xxx&state=UUID    │
└──────┬─────────────────┘
       │
       │ 4. Troca code por token
       ▼
┌──────────────────────┐
│ slack.com/api/oauth  │
│ .v2.access           │
└──────┬───────────────┘
       │
      │ 5. Retorna bot_token
       ▼
┌────────────────────────┐
│    Supabase            │
│ slack_integrations     │
    │ merchant_id → token    │
└────────────────────────┘
```

## Segurança

1. **State Parameter:** O `merchant_id` é passado como `state` para prevenir CSRF
2. **HTTPS em Produção:** O redirect_uri **DEVE** usar HTTPS em produção
3. **Tokens Criptografados:** Considere criptografar `access_token` no banco
4. **Validação de Merchant:** Adicione autenticação para garantir que apenas o merchant autenticado pode conectar/desconectar

## Próximos Passos

- [ ] Adicionar UI de "Conectar Slack" no painel do merchant
- [ ] Implementar rotação de tokens (refresh_token)
- [ ] Adicionar logs de auditoria para conexões/desconexões
- [ ] Criar testes automatizados para o fluxo OAuth
- [ ] Adicionar suporte para múltiplos canais por merchant
