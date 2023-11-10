# to avoid circular importing

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from work import Work
from user import User
from project import Project
from contrubution import Contribution
from project import Project
from client import Client