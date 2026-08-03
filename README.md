# 🚀 LeadFlow - CRM de Prospecção B2B

CRM inteligente com IA para prospecção B2B via WhatsApp.

## ✨ Diferenciais

- **Coleta Automática**: Google Maps, Instagram, LinkedIn, CNPJ
- **Pipeline Visual**: Kanban drag-and-drop
- **WhatsApp-First**: Integração direta via Evolution API
- **IA de Prospecção**: GPT-4 gera mensagens personalizadas
- **Score de Oportunidade**: Classifica leads quente/frio
- **Propostas Automáticas**: IA gera PDF personalizado
- **Intel Competitiva**: Monitora concorrentes
- **Dashboard Real-time**: Métricas e relatórios

## 🛠 Stack

| Camada | Tecnologia |
|--------|------------|
| Frontend | Next.js 14 + Tailwind CSS |
| Backend | Python FastAPI |
| Banco | PostgreSQL + Redis |
| IA | OpenAI GPT-4 |
| WhatsApp | Evolution API |
| Deploy | Docker Compose |

## 📁 Estrutura

```
leadflow/
├── frontend/          # Interface Next.js
├── backend/           # API FastAPI
├── database/          # Schema SQL
├── automacoes/        # Scripts de automação
├── ia/                # Modelos e prompts
├── docker-compose.yml
├── Makefile
└── .env.example
```

## 🚀 Quick Start

### 1. Clone e configure

```bash
cp .env.example .env
# Edite .env com suas chaves de API
```

### 2. Suba com Docker

```bash
make up
```

### 3. Acesse

| Serviço | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| WhatsApp | http://localhost:8080 |

## 📖 Comandos Úteis

```bash
make help           # Lista todos os comandos
make up             # Sobe tudo
make down           # Para tudo
make logs           # Vê logs
make db-shell       # Shell do PostgreSQL
make db-reset       # Reseta banco
make test           # Roda testes
```

## 🔑 APIs Necessárias

| API | Pra quê | Onde conseguir |
|-----|---------|----------------|
| OpenAI | IA de prospecção | https://platform.openai.com |
| Google Maps | Coleta de leads | https://console.cloud.google.com |
| Evolution API | WhatsApp | https://github.com/EvolutionAPI |
| BrasilAPI | CNPJ | Gratuita |

## 📊 Funcionalidades

### Coleta de Leads
- Google Maps: busca por nicho + cidade
- Instagram: coleta por hashtags
- LinkedIn: busca por cargo
- CNPJ: consulta Receita Federal

### Pipeline Kanban
- 6 etapas: Lead → Qualificado → Contato → Call → Proposta → Fechado
- Drag-and-drop
- Métricas por etapa

### WhatsApp Bot
- Envio automático
- Follow-up inteligente
- Detecção de engajamento
- Status de leitura

### IA de Prospecção
- Mensagens personalizadas
- A/B testing automático
- Melhor horário de envio
- Score de oportunidade

## 🔧 Desenvolvimento

```bash
# Só banco e Redis
make dev

# Backend
make dev-backend

# Frontend
make dev-frontend
```

## 📝 Licença

MIT
