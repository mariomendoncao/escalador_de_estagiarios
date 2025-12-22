# Sistema de Escalonamento de Estagiários

Sistema web para gerenciamento e escalonamento automático de estagiários com base em disponibilidade de instrutores.

## 🚀 Tecnologias

- **Backend**: Python 3.12 + FastAPI + SQLAlchemy + Alembic
- **Frontend**: Vue 3 + Vite + Tailwind CSS
- **Database**: MySQL 8.0
- **Deploy**: Docker + Traefik + GitHub Actions
- **HTTPS**: Let's Encrypt (automático)

## 💻 Desenvolvimento Local

### Pré-requisitos

- Docker e Docker Compose
- Git

### Rodando a aplicação

```bash
# Clonar repositório
git clone <repo-url>
cd escala_estagiarios

# Subir aplicação
docker compose -f docker-compose.dev.yml up

# Rebuild (se necessário)
docker compose -f docker-compose.dev.yml up --build
```

### Acessar

- **Frontend**: http://localhost
- **API Docs**: http://localhost:8000/docs
- **Adminer**: http://localhost:8080

### Hot Reload

O ambiente de desenvolvimento está configurado com hot reload:
- Backend: Uvicorn com `--reload`
- Frontend: Vite dev server

## 🌐 Produção

Acesse: **https://escala-estagiarios.mmendol.com**

Deploy automático via GitHub Actions. Ver [DEPLOY.md](DEPLOY.md) para detalhes.

## 📁 Estrutura do Projeto

```
escala_estagiarios/
├── backend/              # FastAPI + Python
│   ├── app/
│   │   ├── main.py      # Aplicação FastAPI
│   │   ├── models/      # Modelos SQLAlchemy
│   │   ├── routes/      # Endpoints da API
│   │   └── database.py  # Configuração DB
│   ├── alembic/         # Migrations
│   └── requirements.txt
│
├── frontend/            # Vue 3 + Vite
│   ├── src/
│   │   ├── components/  # Componentes Vue
│   │   ├── views/       # Páginas
│   │   └── api.js       # Cliente API
│   ├── nginx.conf       # Configuração Nginx
│   └── package.json
│
├── docker-compose.yml       # Produção (Traefik)
├── docker-compose.dev.yml   # Desenvolvimento
└── .github/workflows/       # CI/CD
```

## 🔧 Comandos Úteis

```bash
# Desenvolvimento
docker compose -f docker-compose.dev.yml up        # Subir
docker compose -f docker-compose.dev.yml down      # Parar
docker compose -f docker-compose.dev.yml logs -f   # Ver logs

# Produção (VPS)
docker compose up -d                               # Subir
docker compose down                                # Parar
docker compose logs -f                             # Ver logs

# Banco de dados
docker exec -it escala-db mysql -u user -p         # Acessar MySQL
```

## 📝 Funcionalidades

- Cadastro de estagiários
- Gerenciamento de disponibilidade
- Importação de capacidade de instrutores (HTML)
- Geração automática de escalas mensais
- Visualização de escalas
- Exportação para CSV

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto é privado.

## 👤 Autor

Desenvolvido por [Mario Mendonça](https://github.com/mariomendoncao)
