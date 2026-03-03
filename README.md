# 🚀 FeedFlow

SaaS para captura de feedback visual via widget, com envio de screenshot + metadados técnicos para o backend.

## 📌 Estado atual do projeto

O projeto está em migração de arquitetura (legado + nova estrutura por camadas). Você vai encontrar:

- código legado com SQLAlchemy em alguns módulos;
- código novo com SQLModel + Repository + Service em outros;
- rotas em estabilização para `collections/domains/integrations/widget`.

Este README descreve o estado **real** do repositório hoje, sem assumir migração 100% concluída.

---

## 🧱 Stack

- Backend: FastAPI (Python 3.10+)
- ORM/DB: SQLModel + SQLAlchemy
- Banco: PostgreSQL (via `DATABASE_URL`)
- Auth: Supabase Auth
- Integrações: Slack OAuth
- Frontend embutido: Widget em Vanilla JS + Vite/Vitest

---

## 📁 Estrutura principal

```text
FeedFlow/
├── backend/
│   ├── main.py
│   ├── app/
│   │   ├── database/
│   │   ├── dtos/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── routes/
│   │   ├── services/
│   │   └── static/
│   └── tests/
├── widget/
│   ├── src/
│   └── tests/
└── docker-compose.yml
```

---

## ▶️ Execução local (backend)

### 1) Requisitos

- Python 3.10+
- pip
- PostgreSQL disponível (local ou remoto)

### 2) Instalar dependências

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3) Variáveis de ambiente

Crie um `.env` dentro de `backend/` com no mínimo:

```env
DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@HOST:5432/DB_NAME
SUPABASE_URL=...
SUPABASE_KEY=...
SLACK_CLIENT_ID=...
SLACK_CLIENT_SECRET=...
SLACK_REDIRECT_URI=...
```

### 4) Subir API

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- Swagger: `http://localhost:8000/docs`

---

## 🐳 Execução com Docker

No diretório raiz:

```bash
docker compose up --build
```

Se seu ambiente ainda usa o binário legado, tente:

```bash
docker-compose up --build
```

---

## 🌐 Arquivos estáticos e widget

O backend serve arquivos estáticos em `/static`:

- `GET /static/widget.js`

Isso é configurado em `backend/main.py` com `app.mount("/static", ...)`.

### Exemplo de uso do widget no site cliente

```html
<script src="https://SEU_BACKEND/static/widget.js"
        data-api-token="SEU_TOKEN"
        data-api-url="https://SEU_BACKEND/api/v1"
        data-button-text="Reportar Problema"
        data-button-position="bottom-right"
        data-primary-color="#4F46E5">
</script>
```

---

## 🔌 Endpoints principais

### Feedback

- `POST /api/v1/submit-feedback`
- `GET /api/v1/feedbacks/{feedback_id}`

### Health

- `GET /api/v1/`
- `GET /api/v1/health`

### Auth

- `POST /auth/logout`
- `GET /auth/me`

### Slack OAuth

- `GET /auth/slack/install`
- `GET /auth/slack/callback`
- `DELETE /auth/slack/disconnect`
- `GET /auth/slack/status`

### Domains

- Rotas de domínio existem, mas parte delas está em processo de consolidação arquitetural.

---

## 🧪 Testes

### Backend

```bash
cd backend
pytest -q
```

### Widget

```bash
cd widget
npm install
npm run test
```

---

## ⚠️ Observações importantes

- Existem módulos ainda em transição de nome/caminho (ex.: `collection` vs `collections`).
- Parte das rotas de `collections/domains/integrations/widget` ainda passa por estabilização.
- O README será atualizado novamente quando a migração para a arquitetura final for concluída.

---

## 📝 Licença

Proprietary - Todos os direitos reservados.
