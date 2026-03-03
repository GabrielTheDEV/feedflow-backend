# Autenticação com Supabase Auth

## 📋 Visão Geral

Sistema de autenticação JWT integrado com Supabase Auth para gerenciar usuários do FeedFlow.

## 🚀 Endpoints Disponíveis

### 1. **Criar Conta** - `POST /auth/register`

Cria nova conta de usuário.

**Request:**
```json
{
  "email": "usuario@exemplo.com",
  "password": "senhaSegura123"
}
```

**Response (201):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "usuario@exemplo.com",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

**Erros:**
- `400`: Email já cadastrado ou senha inválida (mínimo 6 caracteres)

---

### 2. **Login** - `POST /auth/login`

Autentica usuário e retorna token de acesso.

**Request:**
```json
{
  "email": "usuario@exemplo.com",
  "password": "senhaSegura123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "usuario@exemplo.com"
  }
}
```

**Erros:**
- `401`: Email ou senha incorretos

---

### 3. **Obter Usuário Atual** - `GET /auth/me`

Retorna dados do usuário autenticado.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200):**
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "usuario@exemplo.com",
    "role": "authenticated",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

**Erros:**
- `401`: Token inválido ou expirado
- `403`: Token não fornecido

---

### 4. **Logout** - `POST /auth/logout`

Invalida sessão atual.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200):**
```json
{
  "message": "Logout realizado com sucesso"
}
```

---

## 🔐 Como Usar Autenticação

### No Frontend

```javascript
// 1. Fazer register/login
const response = await fetch('http://localhost:8000/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'usuario@exemplo.com',
    password: 'senha123'
  })
});

const { access_token, user } = await response.json();

// 2. Salvar token (localStorage, cookies, etc)
localStorage.setItem('token', access_token);
localStorage.setItem('user_id', user.id);

// 3. Usar token em requisições protegidas
const meResponse = await fetch('http://localhost:8000/auth/me', {
  headers: {
    'Authorization': `Bearer ${access_token}`
  }
});

// 4. Conectar Slack (agora usa user_id automático)
window.location.href = 'http://localhost:8000/auth/slack/install';
// Não precisa passar merchant_id, pega do token
```

---

## 🔧 Integração com Slack OAuth

O Slack OAuth agora suporta **autenticação opcional**:

### **Com Autenticação (Recomendado)**
```bash
GET /auth/slack/install
Headers: Authorization: Bearer {access_token}
```
- Usa `user_id` do token automaticamente
- Mais seguro

### **Sem Autenticação (Para testes)**
```bash
GET /auth/slack/install?merchant_id=550e8400-e29b-41d4-a716-446655440000
```
- Requer `merchant_id` válido (UUID)

---

## 🧪 Testando com cURL

### 1. Criar conta
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"senha123"}'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"senha123"}'
```

### 3. Acessar rota protegida
```bash
TOKEN="seu_access_token_aqui"

curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Logout
```bash
curl -X POST http://localhost:8000/auth/logout \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📚 Dependências para Proteger Rotas

### `get_current_user` (Obrigatório)
```python
from app.dependencies.auth_handlers import get_current_user

@router.get("/protected")
async def protected_route(current_user: Dict = Depends(get_current_user)):
    # Requer token válido
    return {"user_id": current_user["id"]}
```

### `get_current_user_optional` (Opcional)
```python
from app.dependencies.auth_handlers import get_current_user_optional

@router.get("/optional-auth")
async def optional_route(current_user: Optional[Dict] = Depends(get_current_user_optional)):
    if current_user:
        return {"user_id": current_user["id"]}
    else:
        return {"message": "Não autenticado"}
```

---

## 🔑 Configuração do Supabase

As credenciais já estão no `.env`:
```env
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua_chave_anon_aqui
```

O Supabase Auth já está habilitado automaticamente, não precisa configurar nada extra!

---

## 📈 Cobertura de Testes

- ✅ 13 testes criados
- ✅ Register, login, logout, get_me
- ✅ Token validation
- ⚠️ 6 testes passando (7 falham porque usam Supabase real em vez de mocks)

Para rodar testes:
```bash
docker exec feedflow_backend python -m pytest tests/test_auth.py -v
```

---

## 🎯 Próximos Passos

1. **Frontend**: Criar tela de login/registro
2. **Protected Routes**: Adicionar autenticação em `/submit-feedback`
3. **User Profile**: Endpoint para atualizar dados do usuário
4. **Password Reset**: Implementar recuperação de senha
5. **Email Verification**: Confirmar email após register
