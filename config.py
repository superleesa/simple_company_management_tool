from flask import Flask
from flask_login import LoginManager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base


app = Flask(__name__)
app.secret_key = "oiwehiorhehgrughreughrgrforeji"

# Database configuration
engine = create_engine("sqlite:///company_database.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# Login Manager configuration
login_manager = LoginManager()
login_manager.init_app(app)