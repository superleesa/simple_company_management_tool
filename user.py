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

    def get_fullname(self):
        return self.first_name.capitalize() + " " + self.last_name.capitalize()

    def to_dict_without_password(self):
        return {"id": self.id, "username": self.username,
                "first_name": self.first_name,
                "last_name": self.last_name,
                "email_address": self.email_address,
                "is_working": self.is_working}


