"""
database.py
------------
Sets up a simple SQLite database using SQLAlchemy.
SQLite needs no separate install/server — it's just a file (study_planner.db)
that gets created automatically the first time you run the app.
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./study_planner.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class StudyPlan(Base):
    __tablename__ = "study_plans"

    id = Column(Integer, primary_key=True, index=True)
    subjects = Column(String)          # e.g. "Maths, Physics, DBMS"
    exam_date = Column(String)         # e.g. "2026-11-15"
    hours_per_day = Column(Integer)    # e.g. 4
    plan_text = Column(Text)           # the AI-generated plan
    created_at = Column(DateTime, default=datetime.utcnow)


# Creates the table(s) if they don't already exist.
def init_db():
    Base.metadata.create_all(bind=engine)


# Gives each request its own DB session and closes it afterwards.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
