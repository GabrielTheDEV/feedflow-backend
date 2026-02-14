-- Tabela para armazenar integrações OAuth do Slack por merchant
CREATE TABLE IF NOT EXISTS slack_integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID NOT NULL,
    access_token TEXT NOT NULL,
    webhook_url TEXT,
    team_id TEXT NOT NULL,
    team_name TEXT,
    channel_id TEXT,
    channel_name TEXT,
    scope TEXT,
    bot_user_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraint: um merchant pode ter apenas uma integração ativa
    UNIQUE(merchant_id)
);

-- Index para busca rápida por merchant_id
CREATE INDEX idx_slack_integrations_merchant_id ON slack_integrations(merchant_id);

-- Trigger para atualizar updated_at
CREATE OR REPLACE FUNCTION update_slack_integrations_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_slack_integrations_updated_at
BEFORE UPDATE ON slack_integrations
FOR EACH ROW
EXECUTE FUNCTION update_slack_integrations_updated_at();

-- Comentários
COMMENT ON TABLE slack_integrations IS 'Armazena tokens OAuth do Slack para cada merchant';
COMMENT ON COLUMN slack_integrations.merchant_id IS 'Referência ao usuário (merchant) que autorizou a integração';
COMMENT ON COLUMN slack_integrations.access_token IS 'Token OAuth para envio de mensagens via Slack API';
COMMENT ON COLUMN slack_integrations.webhook_url IS 'URL do Incoming Webhook (opcional, gerado automaticamente pelo Slack)';
