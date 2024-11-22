from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi.middleware.cors import CORSMiddleware 
from . import models, schemas
from .database import engine, SessionLocal
import bcrypt
from dotenv import load_dotenv
import os
from typing import List
from sqlalchemy.orm import joinedload


load_dotenv()

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="API de Usuários")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/usuarios/", response_model=schemas.UsuarioOut, status_code=status.HTTP_201_CREATED)
def criar_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):

    usuario_existente = db.query(models.Usuario).filter(
        or_(
            models.Usuario.email.ilike(usuario.email),
            models.Usuario.user.ilike(usuario.user)
        )
    ).first()

    if usuario_existente:
        if usuario_existente.email.lower() == usuario.email.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuário com esse email já existe."
            )
        if usuario_existente.user.lower() == usuario.user.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nome de usuário já está em uso."
            )

    hashed_senha = bcrypt.hashpw(usuario.senha.encode('utf-8'), bcrypt.gensalt())

    novo_usuario = models.Usuario(
        nome=usuario.nome,
        user=usuario.user,
        email=usuario.email,
        senha=hashed_senha.decode('utf-8')
    )

    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    return novo_usuario



@app.get("/usuarios/{usuario_id}", response_model=schemas.UsuarioOut)
def verificar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado."
        )
    return usuario

@app.post("/login", status_code=status.HTTP_200_OK)
def login(usuario: schemas.UsuarioLogin, db: Session = Depends(get_db)):
    
    identificador_normalizado = usuario.identificador.lower()

    usuario_db = db.query(models.Usuario).filter(
        (models.Usuario.user.ilike(identificador_normalizado)) | 
        (models.Usuario.email.ilike(identificador_normalizado))
    ).first()

    if not usuario_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário ou email não encontrado."
        )

    senha_valida = bcrypt.checkpw(usuario.senha.encode('utf-8'), usuario_db.senha.encode('utf-8'))
    if not senha_valida:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Senha incorreta."
        )

    return {"mensagem": "Login realizado com sucesso!"}

@app.post("/grupos-musculares/", response_model=schemas.GrupoMuscularOut, status_code=status.HTTP_201_CREATED)
def criar_grupo_muscular(grupo: schemas.GrupoMuscularCreate, db: Session = Depends(get_db)):

    grupo_existente = db.query(models.GrupoMuscular).filter(
        models.GrupoMuscular.nome.ilike(grupo.nome)
    ).first()

    if grupo_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Grupo muscular com esse nome já existe."
        )

    novo_grupo = models.GrupoMuscular(nome=grupo.nome)

    db.add(novo_grupo)
    db.commit()
    db.refresh(novo_grupo)

    return novo_grupo

@app.get("/grupos-musculares/{grupo_id}", response_model=schemas.GrupoMuscularOut)
def obter_grupo_muscular(grupo_id: int, db: Session = Depends(get_db)):
    grupo = db.query(models.GrupoMuscular).filter(models.GrupoMuscular.id == grupo_id).first()
    if not grupo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo muscular não encontrado."
        )
    return grupo

@app.get("/grupos-musculares-todos", response_model=List[schemas.GrupoMuscularOut])
def listar_todos_grupos_musculares(db: Session = Depends(get_db)):
    grupos = db.query(models.GrupoMuscular).all()
    return grupos

@app.post("/exercicios/", response_model=schemas.ExercicioOut, status_code=status.HTTP_201_CREATED)
def criar_exercicio(exercicio: schemas.ExercicioCreate, db: Session = Depends(get_db)):

    grupo = db.query(models.GrupoMuscular).filter(models.GrupoMuscular.id == exercicio.grupo_muscular).first()
    if not grupo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Grupo muscular especificado não existe."
        )

    exercicio_existente = db.query(models.Exercicio).filter(models.Exercicio.nome.ilike(exercicio.nome)).first()
    if exercicio_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um exercício com esse nome."
        )

    novo_exercicio = models.Exercicio(
        nome=exercicio.nome,
        grupo_muscular=exercicio.grupo_muscular,
        tipo_exercicio=exercicio.tipo_exercicio
    )

    db.add(novo_exercicio)
    db.commit()
    db.refresh(novo_exercicio)

    return novo_exercicio


@app.get("/exercicios/{exercicio_id}", response_model=schemas.ExercicioOut)
def obter_exercicio(exercicio_id: int, db: Session = Depends(get_db)):

    exercicio = db.query(models.Exercicio).filter(models.Exercicio.id == exercicio_id).first()
    
    if not exercicio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercício não encontrado."
        )
    
    return exercicio

@app.get("/exercicios-todos", response_model=List[schemas.ExercicioOut])
def listar_todos_exercicios(db: Session = Depends(get_db)):
    exercicios = db.query(models.Exercicio).options(joinedload(models.Exercicio.grupo_muscular_rel)).all()

    resultado = [
        {
            "id": exercicio.id,
            "nome": exercicio.nome,
            "tipo_exercicio": exercicio.tipo_exercicio,
            "grupo_muscular": {
                "id": exercicio.grupo_muscular_rel.id,
                "nome": exercicio.grupo_muscular_rel.nome,
            }
        }
        for exercicio in exercicios
    ]
    return resultado

@app.put("/exercicios/", response_model=schemas.ExercicioOut)
def editar_exercicio(
    exercicio: schemas.ExercicioUpdate,  # Novo schema que inclui o ID
    db: Session = Depends(get_db)
):
    exercicio_db = db.query(models.Exercicio).filter(models.Exercicio.id == exercicio.id).first()

    if not exercicio_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercício com ID {exercicio.id} não encontrado."
        )

    exercicio_existente = db.query(models.Exercicio).filter(
        models.Exercicio.nome.ilike(exercicio.nome),
        models.Exercicio.id != exercicio.id
    ).first()

    if exercicio_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Exercício com nome '{exercicio.nome}' já existe."
        )

    exercicio_db.nome = exercicio.nome
    exercicio_db.grupo_muscular = exercicio.grupo_muscular
    exercicio_db.tipo_exercicio = exercicio.tipo_exercicio

    db.commit()
    db.refresh(exercicio_db)

    return {
        "id": exercicio_db.id,
        "nome": exercicio_db.nome,
        "tipo_exercicio": exercicio_db.tipo_exercicio,
        "grupo_muscular": {
            "id": exercicio_db.grupo_muscular_rel.id,
            "nome": exercicio_db.grupo_muscular_rel.nome,
        }
    }

@app.delete("/exercicios/{exercicio_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_exercicio(exercicio_id: int, db: Session = Depends(get_db)):

    exercicio = db.query(models.Exercicio).filter(models.Exercicio.id == exercicio_id).first()

    if not exercicio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercício com ID {exercicio_id} não encontrado."
        )

    # Remover o exercício do banco de dados
    db.delete(exercicio)
    db.commit()

    return {"mensagem": "Exercício deletado com sucesso."}