# LeadFlow - Status do Deploy

## ✅ O que funciona:
- GitHub: https://github.com/eusoufabioh/leadflow
- Railway URL: https://leadflow-production-a43a.up.railway.app
- Railway Health: https://leadflow-production-a43a.up.railway.app/health → OK
- PostgreSQL: Online no Railway
- Backend: Rodando na porta 8080

## ❌ O que não funciona:
- Domínio fhlabs.online → Retorna 502 "Application failed to respond"
- O Railway diz que o domínio tá conectado, mas não responde

## 🔧 Pra continuar amanhã:

### Opção 1 - Usar o link do Railway por enquanto
O site funciona em: https://leadflow-production-a43a.up.railway.app

### Opção 2 - Resolver o domínio
1. No Railway, vai no card Leadflow → Settings → Custom Domains
2. Deleta fhlabs.online
3. Adiciona de novo: fhlabs.online, porta 8080
4. Railway vai gerar novos valores CNAME e TXT
5. Configura no Cloudflare (DNS → Records):
   - CNAME: @ → [valor do Railway], proxy DESLIGADO
   - TXT: @ → [valor do Railway]
6. Espera 5 minutos e testa

### Opção 3 - Criar serviço novo no Railway
1. No Railway, "+ New" → "GitHub Repo" → leadflow
2. Gera domínio: leadflow-production-xxx.up.railway.app
3. Conecta PostgreSQL (Settings → Variables → DATABASE_URL)
4. Adiciona Custom Domain: fhlabs.online
5. Configura DNS no Cloudflare

## 📋 Variáveis de ambiente necessárias no Railway:
- PORT=8080
- DATABASE_URL=[URL do PostgreSQL do Railway]
- APP_ENV=production
- APP_SECRET_KEY=[qualquer string secreta]

## 🔑 Cloudflare:
- Email: fabiohceara12@gmail.com
- Zone ID: f09ce282b9c04b45591c9ecadb46df9d
- API Key: Precisa gerar nova (a anterior foi revogada)

## 📝 Notas:
- O app roda na porta 8080 (Railway define PORT automaticamente)
- O Dockerfile usa: uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
- O Railway gera domínios tipo xxx.up.railway.app
- Cloudflare proxy pode causar 502 com Railway (melhor deixar DNS only)
