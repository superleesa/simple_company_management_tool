from sqlalchemy import Column, Integer, String, UniqueConstraint, Boolean, ForeignKey, DateTime, func, Date
from flask_login import UserMixin

from models import Base

class Project(Base):
    __tablename__ = "project_table"

    id = Column(Integer, primary_key=True)
    client_id = Column(ForeignKey("client_table.id"))
    manager_id = Column(ForeignKey("user_table.id"))
    earnings = Column(Integer)
    start_date = Column(Date, nullable=False)
    received_earning_datetime = Column(DateTime)

