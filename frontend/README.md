# Frontend Nuxt

Interface em Nuxt 3/Vue 3 para o SaaS de agendamento.

## Rodar localmente

1. Instale as dependencias:

```bash
npm install
```

2. Inicie o backend FastAPI na raiz do projeto:

```bash
uvicorn fastapi_app.main:app --reload --port 8000
```

3. Inicie o frontend:

```bash
npm run dev
```

Por padrao, o frontend usa `http://localhost:8000` como API. Para alterar:

```bash
NUXT_PUBLIC_API_BASE=http://localhost:8000 npm run dev
```

Credenciais do seed:

- `doctor@clinic.com` / `senha123`
- `maria@email.com` / `senha123`
- `carlos@email.com` / `senha123`
