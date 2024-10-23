from pydantic import BaseModel, EmailStr, Field

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

