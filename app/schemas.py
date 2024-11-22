from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UsuarioCreate(BaseModel):
    nome: str = Field(..., min_length=3, max_length=50)
    user: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    senha: str = Field(..., min_length=6)

class UsuarioOut(BaseModel):
    id: int
    nome: str
    user: str 
    email: EmailStr

    class Config:
        orm_mode = True

class UsuarioLogin(BaseModel):
    identificador: str 
    senha: str

class GrupoMuscularBase(BaseModel):
    nome: str

class GrupoMuscularCreate(GrupoMuscularBase):
    pass

class GrupoMuscularOut(BaseModel):
    id: int
    nome: str

    class Config:
        orm_mode = True

class ExercicioBase(BaseModel):
    nome: str
    grupo_muscular: int
    tipo_exercicio: str
class ExercicioCreate(BaseModel):
    nome: str
    grupo_muscular: int 
    tipo_exercicio: str

class ExercicioOut(BaseModel):
    id: int
    nome: str
    tipo_exercicio: str
    grupo_muscular: GrupoMuscularOut

    class Config:
        orm_mode = True

class ExercicioUpdate(BaseModel):
    id: int
    nome: str
    grupo_muscular: int
    tipo_exercicio: str
