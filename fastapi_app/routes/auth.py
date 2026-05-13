from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_app.db import get_db
from fastapi_app import models, schemas
from fastapi_app.auth import create_access_token
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash, check_password_hash

router = APIRouter()


@router.post('/register', status_code=201)
def register(payload: schemas.UserRegister, db: Session = Depends(get_db)):
    # validate existence
    if db.query(models.User).filter(models.User.email == payload.email).first():
        raise HTTPException(status_code=409, detail='Email already exists')

    user = models.User(
        email=payload.email,
        name=payload.name,
        password_hash=generate_password_hash(payload.password),
        tenant_id=payload.tenant_id or 1,
        role='patient'
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id)
    return {
        'access_token': token,
        'user_id': user.id,
        'email': user.email,
        'name': user.name
    }


@router.post('/login')
def login(payload: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user or not check_password_hash(user.password_hash, payload.password):
        raise HTTPException(status_code=401, detail='Invalid email or password')
    token = create_access_token(user.id)
    return {
        'access_token': token,
        'user_id': user.id,
        'email': user.email,
        'name': user.name
    }
