-- Migration 001: Criar tabela feedbacks
-- Data: 2026-02-14
-- Descrição: Tabela principal para armazenar feedbacks dos clientes

CREATE TABLE IF NOT EXISTS feedbacks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID,
    customer_email TEXT NOT NULL,
    customer_message TEXT NOT NULL CHECK (length(customer_message) <= 550),
    page_url TEXT,
    user_agent TEXT,
    viewport TEXT,
    image_url TEXT,
    metadata JSONB,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Validações
    CONSTRAINT valid_email CHECK (customer_email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'),
    CONSTRAINT valid_status CHECK (status IN ('pending', 'read', 'resolved', 'archived'))
);

-- Índices para performance
CREATE INDEX idx_feedbacks_merchant_id ON feedbacks(merchant_id);
CREATE INDEX idx_feedbacks_created_at ON feedbacks(created_at DESC);
CREATE INDEX idx_feedbacks_status ON feedbacks(status);
CREATE INDEX idx_feedbacks_email ON feedbacks(customer_email);

-- Trigger para atualizar updated_at
CREATE OR REPLACE FUNCTION update_feedbacks_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_feedbacks_updated_at
BEFORE UPDATE ON feedbacks
FOR EACH ROW
EXECUTE FUNCTION update_feedbacks_updated_at();

-- Comentários
COMMENT ON TABLE feedbacks IS 'Armazena todos os feedbacks enviados pelos clientes através do widget';
COMMENT ON COLUMN feedbacks.merchant_id IS 'UUID do merchant (lojista) que recebeu o feedback';
COMMENT ON COLUMN feedbacks.customer_email IS 'Email do cliente que enviou o feedback';
COMMENT ON COLUMN feedbacks.customer_message IS 'Mensagem/comentário do feedback (máximo 550 caracteres)';
COMMENT ON COLUMN feedbacks.page_url IS 'URL da página onde o feedback foi enviado';
COMMENT ON COLUMN feedbacks.user_agent IS 'User agent do navegador do cliente';
COMMENT ON COLUMN feedbacks.viewport IS 'Resolução da tela no momento do feedback';
COMMENT ON COLUMN feedbacks.image_url IS 'URL pública da screenshot capturada (armazenada no Supabase Storage)';
COMMENT ON COLUMN feedbacks.metadata IS 'Metadados adicionais em formato JSON';
COMMENT ON COLUMN feedbacks.status IS 'Status do feedback: pending, read, resolved, archived';
