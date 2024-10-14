from werkzeug.security import check_password_hash, generate_password_hash
from db import db
from sqlalchemy.sql import text
from flask import session


def login(username,password):
    user_check_query = text("SELECT * FROM users WHERE username = :username")
    user_row = db.session.execute(user_check_query,{"username":username})
    user_row = user_row.fetchone()

    if user_row:
        stored_password_hash = user_row[2]

        if check_password_hash(stored_password_hash, password):
            
            session["username"] = username
            session["role"] = user_row[3]
            session["user_id"] = user_row[0]
            return True

        else:
            return False

    else:
        return False

    
def register(username,password):
    user_check_query = text("SELECT id FROM users WHERE username = :username")
    result = db.session.execute(user_check_query, {"username":username}).fetchone()
    if result:
        return False
    
    
    hashed_password = generate_password_hash(password)
    if username == "admin":
        insert_user_query = text("INSERT INTO users (username, password_hash, role, created_at)\
        VALUES (:username, :password_hash, 'admin', CURRENT_TIMESTAMP) RETURNING id")
        session["role"] = "admin"
    else:
        insert_user_query = text("INSERT INTO users (username, password_hash, role, created_at)\
            VALUES (:username, :password_hash, 'user', CURRENT_TIMESTAMP) RETURNING id")
    result = db.session.execute(insert_user_query,{"username":username, "password_hash":hashed_password})
    
    session["username"] = username
    session["user_id"] = result.fetchone()[0]

    db.session.commit()
    return True

