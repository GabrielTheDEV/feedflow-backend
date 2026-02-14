-- Migration 003: Configurar Supabase Storage para screenshots
-- Data: 2026-02-14
-- Descrição: Criar bucket público para armazenar screenshots dos feedbacks

-- Criar bucket 'screenshots' se não existir
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'screenshots',
    'screenshots',
    true,
    5242880, -- 5MB limit
    ARRAY['image/png', 'image/jpeg', 'image/jpg', 'image/webp']
)
ON CONFLICT (id) DO NOTHING;

-- Política para permitir uploads públicos (anon)
CREATE POLICY "Allow public screenshot uploads"
ON storage.objects
FOR INSERT
TO anon, authenticated
WITH CHECK (
    bucket_id = 'screenshots' AND
    (storage.foldername(name))[1] = 'public'
);

-- Política para permitir leitura pública
CREATE POLICY "Allow public screenshot reads"
ON storage.objects
FOR SELECT
TO anon, authenticated, public
USING (bucket_id = 'screenshots');

-- Política para permitir deletar apenas próprios uploads (authenticated users)
CREATE POLICY "Allow authenticated users to delete own screenshots"
ON storage.objects
FOR DELETE
TO authenticated
USING (
    bucket_id = 'screenshots' AND
    auth.uid()::text = (storage.foldername(name))[1]
);

-- Comentários
COMMENT ON TABLE storage.buckets IS 'Buckets do Supabase Storage - screenshots armazena imagens dos feedbacks';
