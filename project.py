from sqlalchemy import Column, Integer, String, UniqueConstraint, Boolean, ForeignKey
from flask_login import UserMixin

from models import Base

class Project(Base):
    __tablename__ = "project_table"

    id = Column(Integer, primary_key=True)
    project_name = Column(String)
    manager_id = Column(ForeignKey("user_table.id"))
