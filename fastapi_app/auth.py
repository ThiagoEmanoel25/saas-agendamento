from fastapi import Depends, HTTPException, status, Header
from jose import jwt, JWTError
from config import Config
from fastapi_app.db import get_db
from sqlalchemy.orm import Session
from fastapi_app.models import User
from datetime import datetime


def _get_token_from_header(authorization: str):
    if not authorization:
        return None
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != 'bearer':
        return None
    return token or None


def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    token = _get_token_from_header(authorization)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid Authorization header")
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user_id = payload.get('sub') or payload.get('identity') or payload.get('user_id')
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def create_access_token(user_id: int):
    if not Config.JWT_SECRET_KEY:
        raise RuntimeError("JWT_SECRET_KEY not configured")
    expire = datetime.utcnow() + getattr(Config, 'JWT_ACCESS_TOKEN_EXPIRES', None)
    payload = {"sub": str(user_id)}
    if expire is not None:
        payload.update({"exp": expire})
    token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')
    return token
