from sqlalchemy import Column, Integer, String, UniqueConstraint, Boolean, ForeignKey, DateTime, func
from flask_login import UserMixin

from models import Base


class Client(Base):
    __tablename__ = "client_table"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    def to_dict(self):
        return {"id": self.id, "name": self.name}