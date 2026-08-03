-- LeadFlow CRM - Schema Completo
-- PostgreSQL

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Enums
CREATE TYPE plano_usuario AS ENUM ('starter', 'pro', 'business');
CREATE TYPE status_lead AS ENUM ('novo', 'contatado', 'qualificado', 'em_proposta', 'fechado', 'perdido');
CREATE TYPE etapa_pipeline AS ENUM ('lead', 'qualificado', 'contato', 'call', 'proposta', 'fechado');
CREATE TYPE tipo_mensagem AS ENUM ('texto', 'imagem', 'documento', 'audio', 'video');
CREATE TYPE status_mensagem AS ENUM ('enviada', 'entregue', 'lida', 'erro');
CREATE TYPE status_proposta AS ENUM ('rascunho', 'enviada', 'visualizada', 'aceita', 'rejeitada');
CREATE TYPE tipo_interacao AS ENUM ('whatsapp', 'email', 'ligacao', 'reuniao', 'nota');

-- Usuarios
CREATE TABLE usuarios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    plano plano_usuario DEFAULT 'starter',
    ativo BOOLEAN DEFAULT true,
    avatar_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Empresas
CREATE TABLE empresas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cnpj VARCHAR(14) UNIQUE,
    razao_social VARCHAR(255),
    nome_fantasia VARCHAR(255),
    nicho VARCHAR(100),
    porte VARCHAR(50),
    cidade VARCHAR(100),
    estado VARCHAR(2),
    endereco TEXT,
    telefone VARCHAR(20),
    email VARCHAR(255),
    site VARCHAR(255),
    instagram VARCHAR(255),
    linkedin VARCHAR(255),
    descricao TEXT,
    funcionarios INTEGER,
    faturamento_estimado DECIMAL(15,2),
    data_fundacao DATE,
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Leads
CREATE TABLE leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    empresa_id UUID REFERENCES empresas(id) ON DELETE SET NULL,
    nome VARCHAR(255) NOT NULL,
    cargo VARCHAR(100),
    email VARCHAR(255),
    telefone VARCHAR(20),
    whatsapp VARCHAR(20),
    linkedin VARCHAR(255),
    instagram VARCHAR(255),
    score INTEGER DEFAULT 0 CHECK (score >= 0 AND score <= 100),
    status status_lead DEFAULT 'novo',
    fonte VARCHAR(100),
    tags TEXT[],
    notas TEXT,
    responsavel_id UUID REFERENCES usuarios(id),
    ultimo_contato TIMESTAMP,
    proximo_followup TIMESTAMP,
    engajamento INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Mensagens
CREATE TABLE mensagens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
    usuario_id UUID REFERENCES usuarios(id),
    conteudo TEXT NOT NULL,
    tipo tipo_mensagem DEFAULT 'texto',
    status status_mensagem DEFAULT 'enviada',
    enviado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    entregue_em TIMESTAMP,
    lido_em TIMESTAMP,
    resposta BOOLEAN DEFAULT false,
    mensagem_original_id UUID REFERENCES mensagens(id),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Pipeline
CREATE TABLE pipeline (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
    etapa etapa_pipeline DEFAULT 'lead',
    responsavel_id UUID REFERENCES usuarios(id),
    valor DECIMAL(15,2),
    moeda VARCHAR(3) DEFAULT 'BRL',
    data_previsao DATE,
    probabilidade INTEGER DEFAULT 0 CHECK (probabilidade >= 0 AND probabilidade <= 100),
    motivo_perda TEXT,
    moved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Propostas
CREATE TABLE propostas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
    usuario_id UUID REFERENCES usuarios(id),
    titulo VARCHAR(255),
    conteudo TEXT,
    valor DECIMAL(15,2),
    moeda VARCHAR(3) DEFAULT 'BRL',
    pdf_url TEXT,
    status status_proposta DEFAULT 'rascunho',
    enviada_em TIMESTAMP,
    visualizada_em TIMESTAMP,
    aberta_em TIMESTAMP,
    aceita_em TIMESTAMP,
    validade DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Interações
CREATE TABLE interacoes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
    usuario_id UUID REFERENCES usuarios(id),
    tipo tipo_interacao NOT NULL,
    conteudo TEXT,
    duracao INTEGER,
    metadata JSONB,
    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Configurações
CREATE TABLE configuracoes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_id UUID REFERENCES usuarios(id),
    chave VARCHAR(100) NOT NULL,
    valor TEXT,
    descricao TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(usuario_id, chave)
);

-- Templates de mensagem
CREATE TABLE templates_mensagem (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_id UUID REFERENCES usuarios(id),
    nome VARCHAR(100) NOT NULL,
    conteudo TEXT NOT NULL,
    variaveis TEXT[],
    ativo BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Campanhas
CREATE TABLE campanhas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_id UUID REFERENCES usuarios(id),
    nome VARCHAR(255) NOT NULL,
    descricao TEXT,
    template_id UUID REFERENCES templates_mensagem(id),
    filtros JSONB,
    status VARCHAR(20) DEFAULT 'rascunho',
    total_leads INTEGER DEFAULT 0,
    enviados INTEGER DEFAULT 0,
    respostas INTEGER DEFAULT 0,
    conversoes INTEGER DEFAULT 0,
    iniciada_em TIMESTAMP,
    finalizada_em TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Concorrentes
CREATE TABLE concorrentes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome VARCHAR(255) NOT NULL,
    site VARCHAR(255),
    nicho VARCHAR(100),
    diferenciais TEXT[],
    fraquezas TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Intel competitiva
CREATE TABLE intel_competitiva (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
    concorrente_id UUID REFERENCES concorrentes(id) ON DELETE CASCADE,
    tipo VARCHAR(50),
    detalhes TEXT,
    fonte VARCHAR(100),
    data DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Logs de IA
CREATE TABLE logs_ia (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID REFERENCES leads(id),
    tipo VARCHAR(50),
    prompt TEXT,
    resposta TEXT,
    modelo VARCHAR(50),
    tokens_utilizados INTEGER,
    tempo_resposta INTEGER,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX idx_leads_score ON leads(score DESC);
CREATE INDEX idx_leads_status ON leads(status);
CREATE INDEX idx_leads_responsavel ON leads(responsavel_id);
CREATE INDEX idx_leads_empresa ON leads(empresa_id);
CREATE INDEX idx_leads_telefone ON leads(telefone);
CREATE INDEX idx_leads_whatsapp ON leads(whatsapp);
CREATE INDEX idx_mensagens_lead ON mensagens(lead_id);
CREATE INDEX idx_mensagens_status ON mensagens(status);
CREATE INDEX idx_pipeline_lead ON pipeline(lead_id);
CREATE INDEX idx_pipeline_etapa ON pipeline(etapa);
CREATE INDEX idx_pipeline_responsavel ON pipeline(responsavel_id);
CREATE INDEX idx_interacoes_lead ON interacoes(lead_id);
CREATE INDEX idx_propostas_lead ON propostas(lead_id);
CREATE INDEX idx_intel_lead ON intel_competitiva(lead_id);
CREATE INDEX idx_empresas_cnpj ON empresas(cnpj);
CREATE INDEX idx_empresas_nicho ON empresas(nicho);

-- Função updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers
CREATE TRIGGER update_usuarios_updated_at BEFORE UPDATE ON usuarios FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_empresas_updated_at BEFORE UPDATE ON empresas FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_leads_updated_at BEFORE UPDATE ON leads FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_pipeline_updated_at BEFORE UPDATE ON pipeline FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_propostas_updated_at BEFORE UPDATE ON propostas FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_configuracoes_updated_at BEFORE UPDATE ON configuracoes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_templates_updated_at BEFORE UPDATE ON templates_mensagem FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_campanhas_updated_at BEFORE UPDATE ON campanhas FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_concorrentes_updated_at BEFORE UPDATE ON concorrentes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Views
CREATE VIEW vw_pipeline_metrics AS
SELECT
    p.etapa,
    COUNT(*) as total_leads,
    SUM(p.valor) as valor_total,
    AVG(p.probabilidade) as probabilidade_media,
    COUNT(CASE WHEN p.moved_at >= CURRENT_DATE - INTERVAL '7 days' THEN 1 END) as novos_7dias
FROM pipeline p
GROUP BY p.etapa;

CREATE VIEW vw_mensagens_metrics AS
SELECT
    DATE_TRUNC('day', enviado_em) as dia,
    COUNT(*) as total_enviadas,
    COUNT(CASE WHEN status = 'lida' THEN 1 END) as total_lidas,
    COUNT(CASE WHEN resposta = true THEN 1 END) as total_respostas,
    ROUND(COUNT(CASE WHEN status = 'lida' THEN 1 END)::DECIMAL / NULLIF(COUNT(*), 0) * 100, 2) as taxa_leitura,
    ROUND(COUNT(CASE WHEN resposta = true THEN 1 END)::DECIMAL / NULLIF(COUNT(*), 0) * 100, 2) as taxa_resposta
FROM mensagens
GROUP BY DATE_TRUNC('day', enviado_em)
ORDER BY dia DESC;
