from sqlalchemy import Column, Integer, String, UniqueConstraint, Boolean, ForeignKey, DateTime
from flask_login import UserMixin

from models import Base


class Sales(Base):
    __tablename__ = "sales_table"

    id = Column(Integer, primary_key=True)
    manager_id = Column(ForeignKey("user_table.id"))
    amount = Column(Integer)
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime)