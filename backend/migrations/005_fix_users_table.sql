-- Migração 005: Corrigir tabela users
-- Remove campos desnecessários e adiciona RLS

-- 1. Deletar tabela antiga (se existir dados, fazer backup antes)
drop table if exists public.users cascade;

-- 2. Criar tabela profiles vinculada ao auth.users
create table public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  username text unique,
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone default now()
);

-- 3. Habilitar RLS
alter table public.profiles enable row level security;

-- 4. Políticas de segurança
create policy "Users can view own profile"
  on public.profiles for select
  using (auth.uid() = id);

create policy "Users can update own profile"
  on public.profiles for update
  using (auth.uid() = id)
  with check (auth.uid() = id);

create policy "Users can insert own profile"
  on public.profiles for insert
  with check (auth.uid() = id);

-- 5. Trigger para criar profile automaticamente
create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.profiles (id, username, email)
  values (new.id, new.email, new.email)
  on conflict (id) do nothing;
  return new;
end;
$$ language plpgsql security definer;

-- 6. Trigger automático quando novo usuário é criado
drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();

-- 7. Adicionar NOT NULL constraints
alter table public.profiles alter column username set not null;
alter table public.profiles alter column created_at set not null;
alter table public.profiles alter column updated_at set not null;

-- 8. Adicionar coluna email se não existir
alter table public.profiles add column if not exists email text unique;
alter table public.profiles alter column email set not null;
