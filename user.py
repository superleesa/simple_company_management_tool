from sqlalchemy import Column, Integer, String, UniqueConstraint, Boolean
from flask_login import UserMixin

from models import Base

class User(Base, UserMixin):
    __tablename__ = "user_table"
    __table_args__ = (UniqueConstraint("username"),)
    
    id = Column(Integer, primary_key=True)
    username = Column("username", String, nullable=False)
    password = Column(String)
    # profile_img_id = Column(String, nullable=False)
    
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

    email_address = Column(String, nullable=False)
    
    is_admin = Column(Boolean, nullable=False)
    is_working = Column(Boolean, nullable=False)
    
    def get_id(self):
        return str(self.id)
