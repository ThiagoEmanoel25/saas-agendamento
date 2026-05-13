from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_app.db import engine, Base
from fastapi_app.routes import appointments as appointments_module
from fastapi_app.routes import auth as auth_module

# create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SaaS Agendamento - FastAPI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(appointments_module.router, prefix="/appointments", tags=["appointments"]) 
app.include_router(auth_module.router, prefix="/auth", tags=["auth"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("fastapi_app.main:app", host="0.0.0.0", port=8000, reload=True)
