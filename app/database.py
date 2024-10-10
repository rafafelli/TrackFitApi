# app/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = "postgresql://trackfitdb_owner:BMwS3ubPIgT1@ep-late-band-a4eq9ur4.us-east-1.aws.neon.tech/trackfitdb?sslmode=require" 

engine = create_engine(
    DATABASE_URL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
