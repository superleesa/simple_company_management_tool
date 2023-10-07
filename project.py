from sqlalchemy import Column, Integer, String, UniqueConstraint, Boolean, ForeignKey, DateTime, func
from flask_login import UserMixin

from models import Base

from config import Session

class Project(Base):
    __tablename__ = "project_table"

    id = Column(Integer, primary_key=True)
    manager_id = Column(ForeignKey("user_table.id"))
    earnings = Column(Integer)
    start_datetime = Column(DateTime, nullable=False)
    received_earning_datetime = Column(DateTime)

