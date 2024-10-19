from os import getenv
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

from app import app

load_dotenv()

app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)
