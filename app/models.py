from sqlalchemy import Column, Integer, String, ForeignKey, Date
from .database import Base
from sqlalchemy.orm import relationship

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), index=True, nullable=False)
    user = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    senha = Column(String(255), nullable=False)

class Exercicio(Base):
    __tablename__ = "exercicios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False, index=True)
    grupo_muscular = Column(Integer, ForeignKey("grupos_musculares.id"), nullable=False)
    tipo_exercicio = Column(String(50), nullable=False)
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)  # Adicionando user_id

    grupo_muscular_rel = relationship("GrupoMuscular", back_populates="exercicios")
    usuario_rel = relationship("Usuario")  # Relacionando com a tabela Usuario

class GrupoMuscular(Base):
    __tablename__ = "grupos_musculares"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False, index=True)

    exercicios = relationship("Exercicio", back_populates="grupo_muscular_rel", cascade="all, delete")


class Rotina(Base):
    __tablename__ = "rotinas"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    detalhes = relationship("Detalhes", back_populates="rotina", cascade="all, delete")


class Detalhes(Base):
    __tablename__ = "detalhes"

    id = Column(Integer, primary_key=True, index=True)
    fk_exercicio = Column(Integer, ForeignKey("exercicios.id"), nullable=False)
    fk_rotina = Column(Integer, ForeignKey("rotinas.id"), nullable=False)
    serie = Column(String(50), nullable=False)
    repeticao = Column(String(50), nullable=False)
    peso = Column(String(50), nullable=True)
    exercicio_rel = relationship("Exercicio")
    data = Column(Date, nullable=True)
    rotina = relationship("Rotina", back_populates="detalhes")
