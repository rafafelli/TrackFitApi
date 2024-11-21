from sqlalchemy import Column, Integer, String, ForeignKey
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

    grupo_muscular_rel = relationship("GrupoMuscular", back_populates="exercicios")
class GrupoMuscular(Base):
    __tablename__ = "grupos_musculares"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False, index=True)

    exercicios = relationship("Exercicio", back_populates="grupo_muscular_rel", cascade="all, delete")