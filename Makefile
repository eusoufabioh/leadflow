.PHONY: help install dev build start stop clean test seed migrate

# Variáveis
COMPOSE = docker compose
DOCKER = docker

help: ## Mostra esta ajuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ============== SETUP ==============

install: ## Instala dependências
	cd frontend && npm install
	cd backend && pip install -r requirements.txt

env: ## Cria .env a partir do exemplo
	@if [ ! -f .env ]; then cp .env.example .env && echo "✅ .env criado"; else echo "ℹ️  .env já existe"; fi

# ============== DOCKER ==============

up: ## Sobe todos os serviços
	$(COMPOSE) up -d
	@echo "✅ LeadFlow rodando!"
	@echo "   Frontend: http://localhost:3000"
	@echo "   Backend: http://localhost:8000"
	@echo "   Docs: http://localhost:8000/docs"
	@echo "   WhatsApp: http://localhost:8080"

up-build: ## Sobe com rebuild
	$(COMPOSE) up -d --build

down: ## Para todos os serviços
	$(COMPOSE) down

down-volumes: ## Para e remove volumes
	$(COMPOSE) down -v

restart: ## Reinicia serviços
	$(COMPOSE) restart

logs: ## Mostra logs
	$(COMPOSE) logs -f

logs-backend: ## Logs do backend
	$(COMPOSE) logs -f backend

logs-frontend: ## Logs do frontend
	$(COMPOSE) logs -f frontend

ps: ## Lista containers
	$(COMPOSE) ps

# ============== DESENVOLVIMENTO ==============

dev: ## Roda em modo desenvolvimento
	$(COMPOSE) up -d postgres redis
	@echo "⏳ Aguardando banco..."
	@sleep 3
	cd backend && uvicorn main:app --reload --port 8000 &
	cd frontend && npm run dev

dev-backend: ## Só o backend
	$(COMPOSE) up -d postgres redis
	cd backend && uvicorn main:app --reload --port 8000

dev-frontend: ## Só o frontend
	cd frontend && npm run dev

# ============== BUILD ==============

build: ## Build de produção
	cd frontend && npm run build

build-docker: ## Build das imagens Docker
	$(COMPOSE) build

# ============== BANCO DE DADOS ==============

db-shell: ## Abre shell do PostgreSQL
	$(COMPOSE) exec postgres psql -U leadflow -d leadflow

db-reset: ## Reseta banco
	$(COMPOSE) down -v
	$(COMPOSE) up -d postgres
	@sleep 3
	$(COMPOSE) exec postgres psql -U leadflow -d leadflow -f /docker-entrypoint-initdb.d/01-schema.sql
	$(COMPOSE) exec postgres psql -U leadflow -d leadflow -f /docker-entrypoint-initdb.d/02-seeds.sql
	@echo "✅ Banco resetado"

db-seed: ## Popula com dados de teste
	$(COMPOSE) exec postgres psql -U leadflow -d leadflow -f /docker-entrypoint-initdb.d/02-seeds.sql

# ============== AUTOMAÇÕES ==============

coleta-google: ## Coleta leads do Google Maps
	cd backend && python -c "import asyncio; from automacoes.coleta.google_maps import coletar_leads_google_maps; asyncio.run(coletar_leads_google_maps('restaurante', 'São Paulo', 'SP', 5, 10))"

coleta-instagram: ## Coleta leads do Instagram
	cd backend && python -c "import asyncio; from automacoes.coleta.instagram import coletar_por_hashtags; asyncio.run(coletar_por_hashtags(['restaurante', 'sp'], 'São Paulo', 10))"

follow-up: ## Executa follow-ups automáticos
	cd backend && python -c "import asyncio; from automacoes.prospeccao.follow_up import main; asyncio.run(main())"

exportar: ## Exporta dados
	cd backend && python -c "import asyncio; from automacoes.relatorios.exportar import main; asyncio.run(main())"

dashboard: ## Gera dashboard
	cd backend && python -c "import asyncio; from automacoes.relatorios.dashboard import main; asyncio.run(main())"

# ============== TESTES ==============

test: ## Roda testes
	cd backend && pytest

test-verbose: ## Testes com verbose
	cd backend && pytest -v

# ============== UTILIDADES ==============

clean: ## Remove arquivos temporários
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf frontend/.next frontend/node_modules
	rm -rf backend/.pytest_cache
	@echo "✅ Limpeza concluída"

status: ## Status do sistema
	@echo "📊 LeadFlow Status"
	@echo "==================="
	@$(COMPOSE) ps
	@echo ""
	@echo "🐳 Docker:"
	@$(DOCKER) ps --filter "name=leadflow" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

backup: ## Backup do banco
	@mkdir -p backups
	$(COMPOSE) exec postgres pg_dump -U leadflow leadflow > backups/leadflow_$$(date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup salvo em backups/"

restore: ## Restaura backup (use: make restore FILE=backups/arquivo.sql)
	@if [ -z "$(FILE)" ]; then echo "❌ Use: make restore FILE=backups/arquivo.sql"; exit 1; fi
	$(COMPOSE) exec -T postgres psql -U leadflow leadflow < $(FILE)
	@echo "✅ Backup restaurado"
