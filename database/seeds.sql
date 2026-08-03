-- LeadFlow CRM - Dados de Teste

-- Usuário admin
INSERT INTO usuarios (nome, email, senha_hash, plano) VALUES
('Admin LeadFlow', 'admin@leadflow.com', '$2b$12$LJ3m4ys3Lg7VXv2RMiKwhu0HNp5GQXn9bWKHp5VE4r5Cn1YMGe3CO', 'business'),
('Vendedor Teste', 'vendedor@leadflow.com', '$2b$12$LJ3m4ys3Lg7VXv2RMiKwhu0HNp5GQXn9bWKHp5VE4r5Cn1YMGe3CO', 'pro');

-- Empresas
INSERT INTO empresas (cnpj, razao_social, nome_fantasia, nicho, porte, cidade, estado, telefone, email, site, funcionarios) VALUES
('11222333000181', 'Tech Solutions LTDA', 'TechSol', 'Tecnologia', 'media', 'São Paulo', 'SP', '11999887766', 'contato@techsol.com.br', 'https://techsol.com.br', 50),
('22333444000162', 'Marketing Digital Pro ME', 'MD Pro', 'Marketing', 'pequena', 'Rio de Janeiro', 'RJ', '21988776655', 'hello@mdpro.com.br', 'https://mdpro.com.br', 15),
('33444555000143', 'Consultoria Financeira ABC', 'FinABC', 'Financeiro', 'grande', 'Belo Horizonte', 'MG', '31977665544', 'contato@finabc.com.br', 'https://finabc.com.br', 200),
('44555666000124', 'E-commerce Express LTDA', 'EcomEx', 'E-commerce', 'media', 'Curitiba', 'PR', '41966554433', 'vendas@ecomex.com.br', 'https://ecomex.com.br', 35),
('55666777000105', 'Saúde Digital S.A.', 'SaúdeDig', 'Saúde', 'grande', 'Brasília', 'DF', '61955443322', 'contato@saudedig.com.br', 'https://saudedig.com.br', 500);

-- Leads
INSERT INTO leads (empresa_id, nome, cargo, email, telefone, whatsapp, score, status, fonte) VALUES
((SELECT id FROM empresas WHERE cnpj = '11222333000181'), 'Carlos Silva', 'CTO', 'carlos@techsol.com.br', '11999887700', '5511999887700', 85, 'qualificado', 'google_maps'),
((SELECT id FROM empresas WHERE cnpj = '22333444000162'), 'Ana Santos', 'CEO', 'ana@mdpro.com.br', '21988776600', '5521988776600', 72, 'contatado', 'instagram'),
((SELECT id FROM empresas WHERE cnpj = '33444555000143'), 'Roberto Lima', 'Diretor Comercial', 'roberto@finabc.com.br', '31977665500', '5531977665500', 91, 'em_proposta', 'linkedin'),
((SELECT id FROM empresas WHERE cnpj = '44555666000124'), 'Mariana Costa', 'Head de Growth', 'mariana@ecomex.com.br', '41966554400', '5541966554400', 63, 'novo', 'google_maps'),
((SELECT id FROM empresas WHERE cnpj = '55666777000105'), 'Pedro Almeida', 'VP de Tecnologia', 'pedro@saudedig.com.br', '61955443300', '5561955443300', 78, 'qualificado', 'receita_federal');

-- Pipeline
INSERT INTO pipeline (lead_id, etapa, valor, probabilidade, data_previsao) VALUES
((SELECT id FROM leads WHERE email = 'carlos@techsol.com.br'), 'qualificado', 15000.00, 60, CURRENT_DATE + INTERVAL '30 days'),
((SELECT id FROM leads WHERE email = 'ana@mdpro.com.br'), 'contato', 5000.00, 30, CURRENT_DATE + INTERVAL '45 days'),
((SELECT id FROM leads WHERE email = 'roberto@finabc.com.br'), 'proposta', 50000.00, 75, CURRENT_DATE + INTERVAL '15 days'),
((SELECT id FROM leads WHERE email = 'mariana@ecomex.com.br'), 'lead', 8000.00, 15, CURRENT_DATE + INTERVAL '60 days'),
((SELECT id FROM leads WHERE email = 'pedro@saudedig.com.br'), 'qualificado', 30000.00, 50, CURRENT_DATE + INTERVAL '30 days');

-- Templates de mensagem
INSERT INTO templates_mensagem (usuario_id, nome, conteudo, variaveis) VALUES
((SELECT id FROM usuarios WHERE email = 'admin@leadflow.com'), 'Primeiro Contato', 'Olá {nome}! 👋

Sou da LeadFlow e notei que a {empresa} pode se beneficiar de uma solução de prospecção inteligente.

Podemos conversar 15 minutos sobre como aumentar seus resultados?

Abraço!', ARRAY['nome', 'empresa']),
((SELECT id FROM usuarios WHERE email = 'admin@leadflow.com'), 'Follow-up 1', 'Oi {nome}!

Enviei uma mensagem há alguns dias sobre como a LeadFlow pode ajudar a {empresa}.

Você teve chance de ver? Posso enviar mais detalhes?', ARRAY['nome', 'empresa']),
((SELECT id FROM usuarios WHERE email = 'admin@leadflow.com'), 'Follow-up 2', 'Olá {nome},

Ainda acredito que faz sentido conversarmos. Empresas como a {empresa} no setor de {nicho} costumam ter ótimos resultados com nossa solução.

Se preferir, posso enviar um case study por aqui mesmo.', ARRAY['nome', 'empresa', 'nicho']);

-- Concorrentes
INSERT INTO concorrentes (nome, site, nicho, diferenciais, fraquezas) VALUES
('Salesforce', 'https://salesforce.com', 'CRM', ARRAY['Maior player do mercado', 'Ecossistema completo'], ARRAY['Caro', 'Complexo de configurar']),
('HubSpot', 'https://hubspot.com', 'CRM/Marketing', ARRAY['Freemium', 'Bom pra inbound'], ARRAY['Limitado pra B2B', 'WhatsApp nativo ruim']),
('RD Station', 'https://rdstation.com', 'Marketing', ARRAY['Focado no Brasil', 'Suporte em PT-BR'], ARRAY['CRM fraco', 'Automação limitada']);
