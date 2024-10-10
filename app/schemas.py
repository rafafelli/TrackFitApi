from pydantic import BaseModel, EmailStr, Field

class UsuarioCreate(BaseModel):
    nome: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    senha: str = Field(..., min_length=6)

class UsuarioOut(BaseModel):
    id: int
    nome: str
    email: EmailStr

    class Config:
        orm_mode = True
