from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.sql import text
from flask import session

from db import db

def login(username,password):
    """
    This function handles login.

    Fetches all the information relevant to the username.
    If username exists checks the password.
    If password and username is correct, assigns session
    variables username, role, user_id, permissions.

    Returns:
        False if the user doesn't exist or the password is incorrect
        True if the login is succesful
    """

    user_check_query = text("SELECT * FROM users WHERE username = :username")
    user_row = db.session.execute(user_check_query,{"username":username})
    user_row = user_row.fetchone()

    if user_row:
        stored_password_hash = user_row[2]

        if check_password_hash(stored_password_hash, password):
            user_permissions_query = text("""
                SELECT up.discussion_area_id 
                FROM user_permissions up 
                JOIN users u ON up.user_id = u.id 
                WHERE u.username = :username
            """)


            permissions = db.session.execute(user_permissions_query,{"username":username})
            permissions = permissions.fetchall()

            session["username"] = username
            session["role"] = user_row[3]
            session["user_id"] = user_row[0]
            try:
                #This try-excepts is because permissions can type None
                session["permissions"] = [i[0] for i in permissions]
            except:
                session["permissions"] = []
            return True

        else:
            return False

    else:
        return False


def register(username,password):
    """
    This function handles registration.

    Checks whether the username already exists in the database and if it does returns False.
    If the username doesn't exist inserts into the database the relevant information.
    Users named admin get automatically admin privileges

    Returns:
        False if the user already exists
        True if the user succefully gets inserted into the database
    """
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
    result = db.session.execute(insert_user_query,
                                {"username":username, "password_hash":hashed_password})

    session["username"] = username
    session["user_id"] = result.fetchone()[0]


    db.session.commit()
    return True
