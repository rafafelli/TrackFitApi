# app/main.py

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import models, schemas
from .database import engine, SessionLocal
import bcrypt
import os

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="API de Usuários")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/usuarios/", response_model=schemas.UsuarioOut, status_code=status.HTTP_201_CREATED)
def criar_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    usuario_existente = db.query(models.Usuario).filter(
        (models.Usuario.email == usuario.email)
    ).first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário com esse email já existe."
        )
    
    hashed_senha = bcrypt.hashpw(usuario.senha.encode('utf-8'), bcrypt.gensalt())
    
    novo_usuario = models.Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha=hashed_senha.decode('utf-8')
    )
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return "Usuário criado com sucesso!"

@app.get("/usuarios/{usuario_id}", response_model=schemas.UsuarioOut)
def verificar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado."
        )
    return usuario
