# Migrations - FeedFlow Database

Este diretório contém todas as migrations do banco de dados em ordem cronológica.

## Como Aplicar Migrations

### Supabase (Produção)

1. Acesse o **SQL Editor** no painel do Supabase
2. Execute cada arquivo **em ordem numérica**:

```sql
-- 1. Criar tabela feedbacks
-- Copie e execute: 001_create_feedbacks.sql

-- 2. Criar tabela slack_integrations
-- Copie e execute: 002_create_slack_integrations.sql

-- 3. Configurar Supabase Storage
-- Copie e execute: 003_configure_storage.sql

-- 4. Criar views e funções auxiliares
-- Copie e execute: 004_create_views_and_functions.sql
```

### PostgreSQL Local (Desenvolvimento)

```bash
# Executar todas as migrations em ordem
for file in backend/migrations/*.sql; do
    psql -U postgres -d feedflow -f "$file"
done
```

## Estrutura das Migrations

```
001_create_feedbacks.sql           - Tabela principal de feedbacks
002_create_slack_integrations.sql  - Integrações OAuth do Slack
003_configure_storage.sql          - Bucket de screenshots no Supabase
004_create_views_and_functions.sql - Views e funções auxiliares
```

## Convenção de Nomenclatura

```
{número}_{descrição}.sql
```

- **número**: Sequencial (001, 002, 003...)
- **descrição**: Nome descritivo em snake_case
- Sempre adicionar comentário no topo com data e descrição

## Criando Nova Migration

```sql
-- Migration XXX: Título da mudança
-- Data: YYYY-MM-DD
-- Descrição: Explicação detalhada

-- Seu código SQL aqui
```

## Verificar Status

```sql
-- Ver todas as tabelas criadas
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';

-- Ver todas as functions
SELECT routine_name 
FROM information_schema.routines 
WHERE routine_schema = 'public';

-- Ver todas as views
SELECT table_name 
FROM information_schema.views 
WHERE table_schema = 'public';
```

## Rollback

Para desfazer uma migration, crie um arquivo `XXX_rollback_{nome}.sql`:

```sql
-- Rollback 002: Remover slack_integrations
DROP TABLE IF EXISTS slack_integrations CASCADE;
```

## Backup Antes de Aplicar

```bash
# PostgreSQL local
pg_dump -U postgres feedflow > backup_$(date +%Y%m%d).sql

# Supabase
# Vá em Project Settings > Database > Backup
```

## Atenção

⚠️ **Nunca** modifique migrations já aplicadas em produção  
⚠️ Sempre crie uma **nova migration** para mudanças  
⚠️ Teste localmente antes de aplicar em produção  
⚠️ Faça backup antes de aplicar migrations destrutivas
