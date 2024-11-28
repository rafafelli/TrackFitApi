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

@app.post("/exercicios/", response_model=schemas.ExercicioOut)
def criar_exercicio(exercicio: schemas.ExercicioCreate, db: Session = Depends(get_db)):
    novo_exercicio = models.Exercicio(
        nome=exercicio.nome,
        tipo_exercicio=exercicio.tipo_exercicio,
        grupo_muscular=exercicio.grupo_muscular
    )
    db.add(novo_exercicio)
    db.commit()
    db.refresh(novo_exercicio)
    
    grupo_muscular_rel = db.query(models.GrupoMuscular).filter(
        models.GrupoMuscular.id == novo_exercicio.grupo_muscular
    ).first()
    
    return {
        "id": novo_exercicio.id,
        "nome": novo_exercicio.nome,
        "tipo_exercicio": novo_exercicio.tipo_exercicio,
        "grupo_muscular": {
            "id": grupo_muscular_rel.id,
            "nome": grupo_muscular_rel.nome
        }
    }



@app.get("/exercicios/{exercicio_id}", response_model=schemas.ExercicioOut)
def obter_exercicio(exercicio_id: int, db: Session = Depends(get_db)):
    exercicio = db.query(models.Exercicio).options(
        joinedload(models.Exercicio.grupo_muscular_rel)
    ).filter(models.Exercicio.id == exercicio_id).first()
    
    if not exercicio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercício não encontrado."
        )
    
    return {
        "id": exercicio.id,
        "nome": exercicio.nome,
        "tipo_exercicio": exercicio.tipo_exercicio,
        "grupo_muscular": {
            "id": exercicio.grupo_muscular_rel.id,
            "nome": exercicio.grupo_muscular_rel.nome,
        }
    }


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
    exercicio: schemas.ExercicioUpdate,
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

@app.delete("/exercicios/{exercicio_id}", status_code=status.HTTP_200_OK)
def deletar_exercicio(exercicio_id: int, db: Session = Depends(get_db)):
    exercicio = db.query(models.Exercicio).filter(models.Exercicio.id == exercicio_id).first()

    if not exercicio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercício com ID {exercicio_id} não encontrado."
        )

    db.delete(exercicio)
    db.commit()

    return {"mensagem": "Exercício deletado com sucesso.", "exercicio_deletado": exercicio}

@app.post("/rotinas/", response_model=schemas.RotinaOut, status_code=status.HTTP_201_CREATED)
def criar_rotina(rotina: schemas.RotinaCreate, db: Session = Depends(get_db)):
    """
    Cria uma nova rotina com os detalhes associados.
    """
    # Passo 1: Criar a rotina
    nova_rotina = models.Rotina(titulo=rotina.titulo)
    db.add(nova_rotina)
    db.commit()
    db.refresh(nova_rotina)

    # Passo 2: Processar os exercícios e detalhes
    for exercicio in rotina.exercicios:
        # Verificar se o exercício existe no banco
        db_exercicio = db.query(models.Exercicio).filter(models.Exercicio.id == exercicio.id).first()
        if not db_exercicio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exercício com ID {exercicio.id} não encontrado."
            )

        # Criar os detalhes para cada série do exercício
        for detalhe in exercicio.detalhes:
            novo_detalhe = models.Detalhes(
                fk_exercicio=exercicio.id,
                fk_rotina=nova_rotina.id,
                serie=detalhe.serie,
                peso=detalhe.peso,
                repeticao=detalhe.repeticoes,
            )
            db.add(novo_detalhe)

    # Confirmar as alterações no banco
    db.commit()

    # Carregar os detalhes da rotina criada para retorno
    rotina_completa = db.query(models.Rotina).options(
        joinedload(models.Rotina.detalhes).joinedload(models.Detalhes.exercicio_rel)
    ).filter(models.Rotina.id == nova_rotina.id).first()

    return rotina_completa
