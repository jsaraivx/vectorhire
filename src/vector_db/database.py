from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, String, Text
from pgvector.sqlalchemy import Vector

import dotenv, os

dotenv.load_dotenv()

DATABASE_USER = os.getenv("DB_USER")
DATABASE_PASSWORD = os.getenv("DB_PASSWORD")
DATABASE_HOST = os.getenv("DB_HOST")
DATABASE_PORT = os.getenv("DB_PORT")
DATABASE_NAME = os.getenv("DB_NAME")

engine = create_engine(f"postgresql+psycopg2://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}")

## Create vector extension
with engine.begin() as conn:
    conn.exec_driver_sql("CREATE EXTENSION IF NOT EXISTS vector;")


class Base(DeclarativeBase):
    pass


class ResumeChunkModel(Base):
    __tablename__ = 'resume_chunks'

    id = Column(String, primary_key=True)
    session_id = Column(String, nullable=False, index=True)
    file_name = Column(String, nullable=False)
    text_content = Column(Text, nullable=False)
    embedding = Column(Vector(384))  # Matches all-MiniLM-L6-v2 dimensions

Base.metadata.drop_all(engine) # Recreate schema cleanly for the new session_id column
Base.metadata.create_all(engine)