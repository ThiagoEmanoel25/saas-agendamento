import os
from dotenv import load_dotenv

# 1. Define o caminho absoluto da pasta onde este arquivo está
basedir = os.path.abspath(os.path.dirname(__file__))

load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # 3. Tenta pegar a URL
    uri = os.getenv("DATABASE_URL")

    # Trava de segurança: Se não achar, para tudo e avisa você
    if not uri:
        raise RuntimeError("ERRO CRÍTICO: A variável 'DATABASE_URL' não foi encontrada. "
                           "Verifique se o arquivo .env existe na raiz do projeto e se a variável está escrita corretamente.")


    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "chave-padrao-insegura")