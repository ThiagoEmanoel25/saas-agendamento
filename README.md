# SaaS de Agendamento

Projeto multi-tenant de agendamentos médicos — agora migrado para **FastAPI**.

## Início Rápido

### 1. Ativar ambiente virtual
```bash
source .venv/bin/activate
```

### 2. Popular banco de dados com dados de teste
```bash
python3 seed.py
```

### 3. Rodar o servidor
Você pode iniciar a aplicação com `python run.py` (inicia `uvicorn`) ou diretamente:
```bash
uvicorn fastapi_app.main:app --reload --port 8000
```

A API estará disponível em: `http://localhost:8000`

## Endpoints principais

### Autenticação

Login (POST): `/auth/login`

Register (POST): `/auth/register`

### Agendamentos (requer JWT token)

Listar agendamentos (GET): `/appointments/`

Ver detalhe de agendamento (GET): `/appointments/{id}`

Criar agendamento (POST): `/appointments/`

Exemplo de chamada (substitua `:8000` e o token):
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"doctor@clinic.com","password":"senha123"}'
```

## Testes

O repositório continha testes legados para Flask; eles foram movidos para `legacy/test_api_flask.py`.

Para rodar testes atuais (quando adicionados para FastAPI):
```bash
pip install pytest
python3 -m pytest -v
```

## Estrutura do Projeto (atual)

```
fastapi_app/                # Novo backend em FastAPI
  ├── main.py
  ├── db.py
  ├── models.py
  ├── routes/
  └── schemas.py

app/                       # Código Flask legado (mantido para referência)
config.py
run.py                     # Entry point (inicia FastAPI via uvicorn)
seed.py                    # Script de seed (atualizado para FastAPI)
legacy/                    # Testes e scripts legados do Flask
requirements.txt
```

## Observações

- O código Flask foi preservado dentro de `app/` para referência e histórico.
- As instruções de execução foram atualizadas para usar FastAPI/uvicorn.
- Próximo passo recomendado: implementar testes automatizados para o backend FastAPI.

## Próximos Passos

- [ ] Implementar testes FastAPI usando `fastapi.testclient` e `pytest`
- [ ] Configurar Alembic para migrações se necessário
- [ ] Scaffolder frontend com Nuxt 3 (Vue 3)

