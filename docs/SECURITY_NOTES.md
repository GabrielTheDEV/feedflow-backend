# Security Notes - FeedFlow Widget/API

## Objetivo
Registrar riscos de segurança identificados no fluxo Widget + API para priorização futura.

Status atual: **não será foco imediato**.

## Riscos identificados

### 1) Validação de domínio contornável (alto)
- Local: `backend/app/routes/feedback.py`
- Situação: a validação de domínio depende de `Origin` ou `Referer` estarem presentes.
- Risco: requests sem esses headers podem passar e usar token fora do domínio esperado.

### 2) CORS muito permissivo (alto)
- Local: `backend/main.py`
- Situação: `allow_origins=["*"]`, `allow_methods=["*"]`, `allow_headers=["*"]`.
- Risco: qualquer origem consegue chamar a API no navegador.

### 3) Token no cliente (médio/alto)
- Local: integração do widget por `<script ... data-api-token="...">`.
- Situação: o token fica visível no front-end.
- Risco: extração e abuso do token por terceiros.

### 4) Validação de arquivo insuficiente (médio)
- Local: `backend/app/services/feedback_service.py`
- Situação: validação por extensão e `content-type`.
- Risco: upload de arquivo mascarado (MIME spoofing).

### 5) Ausência de rate limit e anti-spam (médio)
- Local: endpoint `POST /api/v1/submit-feedback`
- Situação: sem limitação por IP/token.
- Risco: abuso automatizado, spam e potencial DoS lógico.

## Recomendações para fase de hardening

1. Exigir validação de domínio sempre
- Rejeitar request sem `Origin`/`Referer` quando token estiver vinculado a domínio.
- Comparar domínio efetivo com domínio do merchant de forma estrita.

2. Restringir CORS
- Permitir apenas domínios aprovados.
- Evitar `*` em produção.

3. Fortalecer modelo de autenticação do widget
- Considerar token de curta duração, rotação e revogação.
- Avaliar assinatura HMAC/nonce para reduzir replay e uso indevido.

4. Validar arquivo por assinatura binária
- Verificar magic bytes para PNG/JPEG/WEBP antes de salvar.

5. Aplicar rate limit
- Limitar por IP + token no `submit-feedback`.
- Adicionar monitoramento e alertas de abuso.

6. Observabilidade de segurança
- Logar tentativas inválidas com contexto mínimo.
- Criar métricas de falhas por token/origem.

## Priorização sugerida

### Curto prazo (alto impacto)
- Validação de domínio obrigatória.
- CORS restritivo para produção.
- Rate limit em `submit-feedback`.

### Médio prazo
- Validação de magic bytes.
- Política de rotação/revogação de token.

### Longo prazo
- Assinatura de requests do widget.
- Camada anti-bot adicional (desafio progressivo).

## Observação
Este documento é um registro técnico para backlog de segurança. Implementação adiada por decisão de escopo atual.
