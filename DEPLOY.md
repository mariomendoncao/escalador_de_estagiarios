# Guia de Deploy - Escala Estagiários

Sistema de escalonamento de estagiários com deploy automatizado via Docker + Traefik + GitHub Actions.

## 🏗️ Arquitetura

- **Backend**: Python FastAPI + MySQL
- **Frontend**: Vue 3 + Vite + Tailwind CSS
- **Reverse Proxy**: Traefik (HTTPS automático)
- **CI/CD**: GitHub Actions
- **Domínio**: `escala-estagiarios.mmendol.com`

---

## 💻 Desenvolvimento Local

### Requisitos
- Docker e Docker Compose
- Git

### Como rodar

```bash
# Clonar repositório
git clone <repo-url>
cd escala_estagiarios

# Subir aplicação (hot reload habilitado)
docker compose -f docker-compose.dev.yml up

# Rebuild se necessário
docker compose -f docker-compose.dev.yml up --build

# Parar
docker compose -f docker-compose.dev.yml down
```

### Acessar localmente

- **Frontend**: http://localhost
- **API Docs**: http://localhost:8000/docs
- **Adminer**: http://localhost:8080

---

## 🚀 Deploy em Produção (VPS)

### Pré-requisitos na VPS

1. **Traefik configurado e rodando**
   - Rede Docker `proxy` criada
   - Certificados Let's Encrypt configurados
   - Portas 80 e 443 abertas

2. **Usuário `deploy` configurado**
   - Com acesso SSH via chave pública
   - Permissões para Docker

3. **DNS configurado**
   ```
   Tipo: A
   Nome: escala_estagiarios
   Valor: <IP_DA_VPS>
   ```

### Preparação Inicial na VPS

```bash
# Conectar como usuário deploy
ssh deploy@<VPS_HOST>

# Criar diretório do projeto
mkdir -p /srv/docker/escala-estagiarios
cd /srv/docker/escala-estagiarios

# Clonar repositório
git clone <repo-url> .

# Criar arquivo .env com credenciais de produção
cp .env.example .env
nano .env
```

**Editar `.env` com credenciais seguras:**

```bash
MYSQL_DATABASE=intern_schedule
MYSQL_USER=escala_user
MYSQL_PASSWORD=<SENHA_FORTE_ALEATÓRIA>
MYSQL_ROOT_PASSWORD=<SENHA_ROOT_FORTE>
DATABASE_URL=mysql+pymysql://escala_user:<SENHA_FORTE_ALEATÓRIA>@db/intern_schedule
DOMAIN=escala-estagiarios.mmendol.com
```

> ⚠️ **Importante**: Use senhas fortes e diferentes para produção!

### Deploy Manual (Primeira vez)

```bash
cd /srv/docker/escala-estagiarios

# Build e subir containers
docker compose build --no-cache
docker compose up -d

# Verificar logs
docker compose logs -f

# Verificar status
docker compose ps
```

### Configurar GitHub Actions

1. **Adicionar Secrets no GitHub**:
   - Ir em: `Settings` → `Secrets and variables` → `Actions`
   - Adicionar:
     - `VPS_HOST`: IP ou domínio da VPS
     - `VPS_SSH_KEY`: Chave privada SSH do usuário `deploy`

2. **Push para main**:
   ```bash
   git push origin main
   ```

3. **Acompanhar deploy**:
   - GitHub → Actions → Ver workflow rodando
   - VPS: `docker compose logs -f`

### Deploy Automático (após configuração)

Após a configuração inicial, o deploy é **100% automático**:

1. Fazer commit e push para `main`
2. GitHub Actions detecta mudança
3. Conecta via SSH na VPS
4. Atualiza código (`git pull`)
5. Rebuild containers
6. Reinicia aplicação
7. Traefik roteia automaticamente com HTTPS

---

## 🌐 Acessar Aplicação

- **Frontend**: https://escala-estagiarios.mmendol.com
- **API**: https://escala-estagiarios.mmendol.com/api

> ✅ HTTPS automático via Let's Encrypt (Traefik)

---

## 🔍 Troubleshooting

### Verificar containers rodando

```bash
docker compose ps
```

### Ver logs

```bash
# Todos os serviços
docker compose logs -f

# Apenas API
docker compose logs -f api

# Apenas Frontend
docker compose logs -f frontend

# Apenas Database
docker compose logs -f db
```

### Rebuild completo

```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Acessar banco de dados

```bash
# Via docker exec
docker exec -it escala-db mysql -u user -p

# Ou usar Adminer localmente (apenas dev)
# http://localhost:8080
```

### Verificar integração Traefik

```bash
# Ver containers na rede proxy
docker network inspect proxy

# Ver logs do Traefik (se tiver acesso)
docker logs traefik
```

### API não responde

1. Verificar se container está rodando:
   ```bash
   docker compose ps
   ```

2. Ver logs da API:
   ```bash
   docker compose logs api
   ```

3. Testar internamente na VPS:
   ```bash
   curl http://localhost:8000/docs
   ```

### Frontend não carrega

1. Verificar se build foi feito com URL correta:
   ```bash
   docker compose logs frontend
   ```

2. Verificar se VITE_API_URL está correto no build

3. Abrir DevTools do navegador (F12) e ver erros de console

### Certificado HTTPS não funciona

1. Verificar DNS:
   ```bash
   nslookup escala-estagiarios.mmendol.com
   ```

2. Verificar labels Traefik:
   ```bash
   docker inspect escala-frontend | grep traefik
   docker inspect escala-api | grep traefik
   ```

3. Ver logs do Traefik para erros de certificado

---

## 📝 Estrutura de Arquivos

```
escala_estagiarios/
├── .github/
│   └── workflows/
│       └── deploy.yml          # CI/CD automático
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   └── src/
├── docker-compose.yml          # Produção (Traefik)
├── docker-compose.dev.yml      # Desenvolvimento (portas expostas)
├── .env                        # Variáveis de ambiente (não versionado)
├── .env.example                # Template de .env
├── .gitignore
├── DEPLOY.md                   # Este arquivo
└── README.md
```

---

## 🔐 Segurança

- ✅ HTTPS obrigatório em produção
- ✅ Credenciais em variáveis de ambiente
- ✅ `.env` não versionado no Git
- ✅ Banco de dados isolado (rede interna)
- ✅ Adminer removido em produção
- ✅ Deploy via SSH com chave privada

