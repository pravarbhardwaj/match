# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
Base = declarative_base()
engine = create_engine(DATABASE_URL, pool_size=10,  # Adjust as needed
    max_overflow=5, 
    pool_timeout=30, 
    connect_args={"timeout": 15})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
