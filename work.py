from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, desc, func, desc
from sqlalchemy.ext.declarative import declarative_base

from models import Base


class Work(Base):
    __tablename__ = "work_table"
    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("user_table.id"), nullable=False)
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime)
    worked_hours = Column(Integer)
