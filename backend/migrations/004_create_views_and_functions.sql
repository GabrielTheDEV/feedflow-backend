-- Migration 004: Criar views e funções auxiliares
-- Data: 2026-02-14
-- Descrição: Views e funções úteis para análise de feedbacks

-- View: Estatísticas de feedbacks por merchant
CREATE OR REPLACE VIEW feedback_stats_by_merchant AS
SELECT
    merchant_id,
    COUNT(*) AS total_feedbacks,
    COUNT(*) FILTER (WHERE status = 'pending') AS pending_count,
    COUNT(*) FILTER (WHERE status = 'read') AS read_count,
    COUNT(*) FILTER (WHERE status = 'resolved') AS resolved_count,
    COUNT(*) FILTER (WHERE image_url IS NOT NULL) AS with_screenshot_count,
    AVG(length(customer_message)) AS avg_message_length,
    MIN(created_at) AS first_feedback_date,
    MAX(created_at) AS last_feedback_date
FROM feedbacks
WHERE merchant_id IS NOT NULL
GROUP BY merchant_id;

COMMENT ON VIEW feedback_stats_by_merchant IS 'Estatísticas agregadas de feedbacks por merchant';

-- View: Feedbacks recentes (últimos 30 dias)
CREATE OR REPLACE VIEW recent_feedbacks AS
SELECT
    id,
    merchant_id,
    customer_email,
    customer_message,
    page_url,
    image_url,
    status,
    created_at
FROM feedbacks
WHERE created_at >= NOW() - INTERVAL '30 days'
ORDER BY created_at DESC;

COMMENT ON VIEW recent_feedbacks IS 'Feedbacks dos últimos 30 dias ordenados por data';

-- Função: Buscar feedbacks por merchant com paginação
CREATE OR REPLACE FUNCTION get_merchant_feedbacks(
    p_merchant_id UUID,
    p_limit INTEGER DEFAULT 50,
    p_offset INTEGER DEFAULT 0,
    p_status TEXT DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    customer_email TEXT,
    customer_message TEXT,
    page_url TEXT,
    image_url TEXT,
    status TEXT,
    created_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        f.id,
        f.customer_email,
        f.customer_message,
        f.page_url,
        f.image_url,
        f.status,
        f.created_at
    FROM feedbacks f
    WHERE f.merchant_id = p_merchant_id
        AND (p_status IS NULL OR f.status = p_status)
    ORDER BY f.created_at DESC
    LIMIT p_limit
    OFFSET p_offset;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION get_merchant_feedbacks IS 'Retorna feedbacks de um merchant com paginação e filtro opcional por status';

-- Função: Marcar feedback como lido
CREATE OR REPLACE FUNCTION mark_feedback_as_read(p_feedback_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE feedbacks
    SET status = 'read', updated_at = NOW()
    WHERE id = p_feedback_id AND status = 'pending';
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION mark_feedback_as_read IS 'Marca um feedback como lido se estiver com status pending';

-- Função: Contar feedbacks não lidos por merchant
CREATE OR REPLACE FUNCTION count_unread_feedbacks(p_merchant_id UUID)
RETURNS INTEGER AS $$
BEGIN
    RETURN (
        SELECT COUNT(*)::INTEGER
        FROM feedbacks
        WHERE merchant_id = p_merchant_id AND status = 'pending'
    );
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION count_unread_feedbacks IS 'Retorna o número de feedbacks não lidos (pending) de um merchant';
