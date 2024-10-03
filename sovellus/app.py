from flask import Flask
from flask import redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
app.secret_key = getenv("SECRET_KEY")


db = SQLAlchemy(app)

@app.route("/")
def index():

    sql_query = text("""SELECT 
                    da.id,
                    da.name,
                    da.description,
                    COUNT(DISTINCt t.id) AS thread_count,
                    COUNT(m.id) AS message_count
                 FROM
                    discussion_areas da
                 LEFT JOIN threads t ON da.id = t.discussion_area_id
                 LEFT JOIN messages m ON t.id = m.thread_id
                 GROUP BY da.id
                 
                 
                 """)
    result = db.session.execute(sql_query)
    areas = result.fetchall()
    return render_template("index.html", areas=areas) 


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
        if username == "admin":
            insert_user_query = text("INSERT INTO users (username, password_hash, role, created_at)\
            VALUES (:username, :password_hash, 'admin', CURRENT_TIMESTAMP)")
        else:
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
        #For some reason user_row["password_hash"] doesn't work
        stored_password_hash = user_row[2]

        
        if check_password_hash(stored_password_hash, password):
            
            session["username"] = username
            session["role"] = user_row[3]
            session["user_id"] = user_row[0]
            return redirect("/")
        else:
            return render_template("index.html", error="Invalid username or password")
    else:
        
        return render_template("index.html", error="Invalid username or password")

@app.route("/new")
def new():
    return render_template("new.html")

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/send", methods=["POST"])
def send():
    content = request.form["content"]
    sql = text("INSERT INTO messages (user_id, content, created_at, updated_at) VALUES (:user_id, :content, :created_at, :updated_at)")
    created_at = datetime.now()
    db.session.execute(sql, {
        "user_id":session["user_id"],
        "content":content,
        "create_at":created_at,
        "updated_at":created_at})
    db.session.commit()
    return redirect("/")

@app.route("/new_area")
def new_area():
    return render_template("new_area.html")


@app.route("/create_area", methods=["POST"])
def create_area():
    name = request.form["name"]
    description = request.form["description"]
    is_secret = request.form.get("is_secret") == "on"
    created_at = datetime.now()
    sql = text("""
        INSERT INTO discussion_areas (name, description, is_secret, created_at)
        VALUES (:name, :description, :is_secret, :created_at)
    """)
    db.session.execute(sql, {"name": name, "description": description, "is_secret": is_secret, "created_at": created_at})
    
    db.session.commit()

    return redirect("/")