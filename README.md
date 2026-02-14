# 🚀 FeedFlow

Sistema SaaS para captura de feedbacks visuais e logs técnicos de lojas Shopify, ajudando lojistas a recuperarem vendas perdidas.

## 📋 Visão Geral

FeedFlow permite que clientes de lojas Shopify reportem problemas visuais capturando screenshots da tela junto com metadados técnicos do navegador, facilitando o diagnóstico e resolução de problemas que podem estar impedindo vendas.

## 🏗️ Arquitetura

### Stack Tecnológica
- **Backend**: Python 3.10+ com FastAPI
- **Banco de Dados**: PostgreSQL com SQLAlchemy ORM
- **Padrão**: Monorepo com Service Layer Pattern (inspirado em Spring Boot)
- **Widget**: Vanilla JavaScript com html2canvas
- **Segurança**: Multi-tenancy baseado em API tokens

### Estrutura do Projeto

```
FeedFlow/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   │   └── models.py          # Entidades SQLAlchemy
│   │   ├── schemas/
│   │   │   └── schemas.py         # DTOs Pydantic
│   │   ├── services/
│   │   │   └── feedback_service.py # Lógica de negócio
│   │   └── database.py            # Configuração do banco
│   ├── main.py                    # API principal
│   ├── requirements.txt
│   └── .env.example
└── widget/
    └── widget.js                  # Widget de captura
```

## 🚀 Instalação e Configuração

### 1. Pré-requisitos
- Python 3.10+
- PostgreSQL 13+
- pip ou poetry

### 2. Configurar Backend

```bash
cd backend

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Edite o .env com suas configurações
```

### 3. Configurar Banco de Dados

```bash
# Criar banco de dados PostgreSQL
createdb feedflow_db

# Ou via SQL
psql -U postgres
CREATE DATABASE feedflow_db;
CREATE USER feedflow_user WITH PASSWORD 'feedflow_pass';
GRANT ALL PRIVILEGES ON DATABASE feedflow_db TO feedflow_user;
```

### 4. Iniciar o Servidor

```bash
# Desenvolvimento
python main.py

# Ou com uvicorn diretamente
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

A API estará disponível em: `http://localhost:8000`
Documentação Swagger: `http://localhost:8000/docs`

## 📱 Integração do Widget

### Instalação no Site

```html
<!-- Adicionar no final do <body> -->
<script src="https://seu-dominio.com/widget/widget.js"></script>
<script>
  FeedFlowWidget.init({
    apiToken: 'seu-token-api-aqui',
    apiUrl: 'http://localhost:8000',
    buttonText: 'Reportar Problema',
    buttonPosition: 'bottom-right',
    primaryColor: '#4F46E5'
  });
</script>
```

### Configurações do Widget

| Opção | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `apiToken` | string | Sim | Token de autenticação do merchant |
| `apiUrl` | string | Sim | URL da API FeedFlow |
| `buttonText` | string | Não | Texto do botão (padrão: "Reportar Problema") |
| `buttonPosition` | string | Não | Posição do botão: bottom-right, bottom-left, top-right, top-left |
| `primaryColor` | string | Não | Cor primária do widget (hex) |

## 🔐 Segurança e Multi-Tenancy

### Gerando API Tokens

Cada merchant (lojista) deve ter um token único. Por enquanto, você pode gerar tokens manualmente:

```python
import secrets
api_token = secrets.token_urlsafe(32)
print(api_token)
```

### Autenticação

O widget envia o token via:
- **Header**: `X-API-Token`
- **Form Field**: `api_token`

O backend valida o token e garante que cada merchant acesse apenas seus próprios dados.

## 📡 API Endpoints

### `POST /api/v1/submit-feedback`

Submete um novo feedback com screenshot.

**Headers:**
```
X-API-Token: seu-token-aqui
Content-Type: multipart/form-data
```

**Body (multipart/form-data):**
- `screenshot` (file): Arquivo de imagem
- `api_token` (string, opcional se via header): Token do merchant
- `customer_email` (string, opcional): Email do cliente
- `customer_message` (string, opcional): Mensagem do cliente
- `metadata` (JSON string, opcional): Metadados técnicos

**Resposta 201:**
```json
{
  "message": "Feedback recebido com sucesso!",
  "data": {
    "feedback_id": 1,
    "status": "pending",
    "created_at": "2026-02-13T10:30:00"
  }
}
```

### `GET /api/v1/feedbacks/{feedback_id}`

Busca um feedback específico.

**Headers:**
```
X-API-Token: seu-token-aqui
```

**Resposta 200:**
```json
{
  "id": 1,
  "merchant_id": 1,
  "screenshot_path": "/uploads/screenshots/1_abc123_1707825000.png",
  "metadata_json": {
    "page_url": "https://loja.com/produto",
    "user_agent": "Mozilla/5.0...",
    "viewport_width": 1920,
    "viewport_height": 1080
  },
  "customer_email": "cliente@email.com",
  "customer_message": "Botão de compra não funciona",
  "status": "pending",
  "created_at": "2026-02-13T10:30:00"
}
```

## 🗃️ Modelo de Dados

### Merchant
- `id`: Primary Key
- `shop_url`: URL da loja Shopify (único)
- `api_token`: Token de autenticação (único)
- `is_active`: Status (1 = ativo, 0 = inativo)
- `created_at`, `updated_at`

### Feedback
- `id`: Primary Key
- `merchant_id`: Foreign Key para Merchant
- `screenshot_path`: Caminho do arquivo de imagem
- `metadata_json`: JSON com dados técnicos
- `customer_email`: Email do cliente (opcional)
- `customer_message`: Mensagem do cliente (opcional)
- `status`: pending | reviewed | resolved
- `created_at`

## 🧪 Testando

### Teste Manual via cURL

```bash
curl -X POST http://localhost:8000/api/v1/submit-feedback \
  -H "X-API-Token: seu-token-aqui" \
  -F "screenshot=@/path/to/image.png" \
  -F "customer_email=teste@email.com" \
  -F "customer_message=Teste de feedback" \
  -F 'metadata={"page_url":"https://teste.com"}'
```

### Teste via Python

```python
import requests

url = "http://localhost:8000/api/v1/submit-feedback"
headers = {"X-API-Token": "seu-token-aqui"}

with open("screenshot.png", "rb") as f:
    files = {"screenshot": f}
    data = {
        "customer_email": "teste@email.com",
        "customer_message": "Teste",
        "metadata": '{"page_url": "https://teste.com"}'
    }
    response = requests.post(url, headers=headers, files=files, data=data)
    print(response.json())
```

## 📈 Próximos Passos

- [ ] Implementar painel administrativo para lojistas
- [ ] Adicionar processamento de imagem com IA (detecção de erros visuais)
- [ ] Integração com Shopify API
- [ ] Sistema de notificações (email/webhook)
- [ ] Analytics e dashboard de feedbacks
- [ ] Suporte a múltiplos idiomas no widget
- [ ] Compressão automática de imagens
- [ ] Rate limiting e proteção DDoS

## 📝 Licença

Proprietary - Todos os direitos reservados

## 👨‍💻 Suporte

Para dúvidas e suporte, entre em contato através de support@feedflow.com
