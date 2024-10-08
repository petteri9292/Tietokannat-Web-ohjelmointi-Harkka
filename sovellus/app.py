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
    """
    Index page to display all discussion areas along with metadata.

    This function handles the "/" route and queries the database for all 
    discussion areas. For each discussion area, it retrieves:
      - The name and description of the area
      - The number of threads in the area
      - The number of messages across all threads in the area
      - The date of the latest message
      - The variable is_hidden
      - The variable is_secret
    The results are passed to the 'index.html' template for rendering.

    Returns:
        A rendered HTML template showing the list of discussion areas, 
        along with their thread and message counts and the latest message date.
    """
    sql_query = text("""SELECT 
                    da.id,
                    da.name,
                    da.description,
                    da.is_hidden,
                    da.is_secret,
                    COUNT(DISTINCt t.id) AS thread_count,
                    COUNT(m.id) AS message_count,
                    MAX(m.created_at) AS last_message_date
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


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/send", methods=["POST"])
def send():
    content = request.form["content"]
    sql = text("INSERT INTO messages (user_id, content, created_at, updated_at) VALUES (:user_id, :content, NOW(), NOW())")
    db.session.execute(sql, {
        "user_id":session["user_id"],
        "content":content})
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
    sql = text("""
        INSERT INTO discussion_areas (name, description, is_secret, created_at)
        VALUES (:name, :description, :is_secret, NOW())
    """)
    db.session.execute(sql, {"name": name, "description": description, "is_secret": is_secret})
    
    db.session.commit()

    return redirect("/")


@app.route("/discussion/<int:area_id>")
def discussion_area(area_id):
    """
    Discussion area function
    
    """
    query = text("""
        SELECT id,name FROM discussion_areas WHERE id = :area_id
    """)
    area = db.session.execute(query,{"area_id":area_id}).fetchone()
    if area:
        threads_query = text("""
            SELECT 
                t.id,
                t.title,
                t.created_at,
                u.username AS author,
                COUNT(m.id) AS message_count
                    
            FROM 
                threads t
            JOIN users u ON t.user_id = u.id
            LEFT JOIN messages m ON t.id = m.thread_id
            WHERE t.discussion_area_id = :area_id
            GROUP BY t.id, u.username
            ORDER BY t.created_at DESC
        """)
        threads = db.session.execute(threads_query,{"area_id":area_id}).fetchall()
        return render_template("discussion_area.html", threads=threads, area=area)
    else:
        return "Discussion area not found", 404


@app.route("/new_thread", methods=["GET", "POST"])
def create_thread():
    area_id = request.args.get("area_id")
    if request.method == "POST":
        title = request.form["title"]
        first_message = request.form["First_message"]
        user_id = session.get("user_id")

        area_id = request.form.get("area_id")

        insert_thread_query = text("""
            INSERT INTO threads (title, user_id, discussion_area_id, created_at, updated_at)
            VALUES (:title, :user_id, :discussion_area_id, NOW(), NOW())
            RETURNING id
        """)

        result = db.session.execute(insert_thread_query, {
            "title": title,
            "user_id": user_id,
            "discussion_area_id": area_id

        })
        thread_id = result.fetchone()[0]
        db.session.commit()

        insert_message_query = text("""
            INSERT INTO messages (content, thread_id, user_id, created_at, updated_at)
            VALUES (:content, :thread_id, :user_id, NOW(), NOW())
        """)
        
        db.session.execute(insert_message_query, {
            "content": first_message,
            "thread_id": thread_id,
            "user_id": user_id
        })
        db.session.commit()

        return redirect(f"/thread/{thread_id}")
    
    # If GET request, render the thread creation form
    return render_template("new_thread.html", area_id=area_id)



@app.route("/thread/<int:thread_id>")
def thread(thread_id):
    """
    Thread function
    
    """
    query = text("""
        SELECT id,title,user_id FROM threads WHERE id = :thread_id
    """)
    thread = db.session.execute(query,{"thread_id":thread_id}).fetchone()
    if thread:
        messages_query = text("""
            SELECT 
                m.content, 
                m.created_at, 
                u.username
            FROM messages m
            LEFT JOIN users u ON m.user_id = u.id
            WHERE m.thread_id = :thread_id
            ORDER BY m.created_at ASC
        """)
        messages = db.session.execute(messages_query,{"thread_id":thread_id}).fetchall()

        area_query = text("""
            SELECT
                da.id
            FROM
                discussion_areas da
            JOIN
                threads t
            ON 
                da.id = t.discussion_area_id
            WHERE
                t.id = :thread_id
        """)
        area = db.session.execute(area_query,{"thread_id":thread_id}).fetchone()
        print(area)

        return render_template("thread.html", messages=messages, thread=thread,area=area)
    else:
        return "Thread not found", 404
    

from flask import request, session, redirect, render_template
from sqlalchemy import text

@app.route("/post_reply", methods=["POST"])
def post_reply():
    thread_id = request.form.get("thread_id")
    reply_content = request.form.get("reply_content")
    user_id = session.get("user_id")

    
    if not thread_id or not reply_content:
        return "Bad Request: Missing thread ID or reply content", 400

    insert_message_query = text("""
        INSERT INTO messages (content, thread_id, user_id, created_at, updated_at)
        VALUES (:content, :thread_id, :user_id, NOW(), NOW())
    """)
    
    db.session.execute(insert_message_query, {
        "content": reply_content,
        "thread_id": thread_id,
        "user_id": user_id
    })
    db.session.commit()

    return redirect(f"/thread/{thread_id}")


@app.route("/delete_area/<int:area_id>",methods=["POST"])
def delete_area(area_id):
    """
    Function to hide a discussion area by flipping is_hidden to true
    """
    hide_area_query = text("UPDATE discussion_areas SET is_hidden = TRUE WHERE id = :area_id")
    db.session.execute(hide_area_query, {"area_id": area_id})
    db.session.commit()

    return redirect("/")