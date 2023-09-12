from sqlalchemy import Column, Integer, String, UniqueConstraint, Boolean, ForeignKey
from flask_login import UserMixin

from models import Base

class Contribution(Base):
    __tablename__ = "contribution_table"

    user_id = Column(ForeignKey("user_table.id"), primary_key=True)
    project_id = Column(ForeignKey("project_table.id"), primary_key=True)


