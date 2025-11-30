# Guia de Deploy para VPS Hostinger

## Problema Identificado

O frontend estava configurado com URL hardcoded (`http://localhost:8000`) para a API. Isso fazia com que o navegador do usuário tentasse se conectar ao `localhost` da máquina dele, não do servidor.

## Solução Implementada

A URL da API foi configurada diretamente no docker-compose.yml como `http://mmendol.com:8000`.

## Passos para Deploy na VPS Hostinger (92.112.178.78)

### 1. Fazer upload das alterações para a VPS

Envie os arquivos atualizados:
- `frontend/src/api.js`
- `frontend/Dockerfile`
- `docker-compose.yml`

### 2. Rebuild e restart dos containers

```bash
# Parar os containers
docker-compose down

# Rebuild com a nova configuração
docker-compose build --no-cache frontend

# Subir os containers
docker-compose up -d
```

### 3. Verificar se está funcionando

```bash
# Ver logs do frontend
docker-compose logs frontend

# Ver logs da API
docker-compose logs api

# Ver status
docker-compose ps
```

### 4. Testar no navegador

Acesse: `http://SEU_IP_OU_DOMINIO`

A aplicação deve conseguir se comunicar com a API agora.

## Configuração de Firewall (se necessário)

Certifique-se de que as portas estão abertas:

- Porta 80 (frontend)
- Porta 8000 (API)
- Porta 3306 (MySQL - opcional, apenas se precisar acesso externo)
- Porta 8080 (Adminer - opcional)

## Troubleshooting

### Se a API ainda não responder:

1. Verifique se os containers estão rodando:
   ```bash
   docker-compose ps
   ```

2. Verifique os logs da API:
   ```bash
   docker-compose logs api
   ```

3. Teste se a API responde internamente:
   ```bash
   curl http://localhost:8000/docs
   ```

4. Verifique o firewall:
   ```bash
   # No Ubuntu/Debian
   sudo ufw status

   # Se necessário, abra as portas
   sudo ufw allow 80
   sudo ufw allow 8000
   ```

### Se o frontend não conseguir se conectar à API:

1. Abra o console do navegador (F12) em `http://mmendol.com`
2. Verifique se há erros de CORS ou conexão
3. Confirme que a URL da API no console está correta (`http://mmendol.com:8000`)
4. Verifique se a porta 8000 está aberta no firewall

## Configuração do Domínio

Certifique-se de que o DNS do domínio `mmendol.com` aponta para o IP `92.112.178.78`.

## Nota sobre CORS

O backend já tem CORS configurado para aceitar requisições. Se houver problemas, verifique os logs da API.
