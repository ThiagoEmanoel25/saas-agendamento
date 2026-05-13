FastAPI scaffold for SaaS Agendamento

Quick start

1. Install deps (recommended in a venv):

```bash
pip install fastapi uvicorn sqlalchemy python-dotenv python-jose[cryptography] psycopg2-binary
```

2. Ensure your `.env` has the same vars used by the Flask app (DATABASE_URL or SQLALCHEMY_DATABASE_URI and JWT_SECRET_KEY).

3. Run:

```bash
uvicorn fastapi_app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000` and OpenAPI docs at `/docs`.

Notes
- This scaffold uses SQLAlchemy sync sessions and Pydantic schemas. It expects the same DB schema as the Flask app (tables `user` and `appointment`).
- Authentication decodes JWTs produced by the Flask app (it checks `sub`/`identity` claims).
