from flask import Flask
from flask import redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
app.secret_key = getenv("SECRET_KEY")


db = SQLAlchemy(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if not username or not password or not confirm_password:
            return render_template("register.html", error="Please fill in all fields")
        
        if password != confirm_password:
            return render_template("register.html", error="passwords do not match")
        
        user_check_query = text("SELECT id FROM users WHERE username = :username")
        result = db.session.execute(user_check_query, {"username":username}).fetchone()
        if result:
            return render_template("register.html", error="username already taken")
        
        
        hashed_password = generate_password_hash(password)

    
        insert_user_query = text("INSERT INTO users (username, password_hash, role, created_at)\
            VALUES (:username, :password_hash, 'user', CURRENT_TIMESTAMP)")
        db.session.execute(insert_user_query,{"username":username, "password_hash":hashed_password})
        db.session.commit()
        session["username"] = username

        return redirect("/")
    

    return render_template("register.html")

@app.route("/login",methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    user_check_query = text("SELECT * FROM users WHERE username = :username")
    user_row = db.session.execute(user_check_query,{"username":username})
    user_row = user_row.fetchone()
    if user_row:
        stored_password_hash = user_row[2]

        
        if check_password_hash(stored_password_hash, password):
            
            session["username"] = username
            return redirect("/")
        else:
            return render_template("index.html", error="Invalid username or password")
    else:
        
        return render_template("index.html", error="Invalid username or password")


@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")