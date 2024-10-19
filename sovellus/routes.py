from app import app
from flask import redirect, render_template, request, session, abort

from dotenv import load_dotenv
from os import getenv


import authentication
import discussion_areas
import threads
import search
import messages

import secrets

load_dotenv()

app.secret_key = getenv("SECRET_KEY")

@app.route("/")
def index():
    """
    Index page to display all discussion areas the user has privileges to along with metadata.

    This function handles the "/" route and queries the database for all 
    discussion_areas. The results are passed to the 'index.html' template for rendering.

    Returns:
        A rendered HTML template showing the list of discussion discussion_areas, 
        along with their thread and message counts and the latest message date.
    """
    user_id = session.get("user_id")
    user_role = session.get("role")
    if user_id:
        all_areas = discussion_areas.get_areas(user_id,user_role)
        return render_template("index.html", areas=all_areas)
    else:
        return render_template("login.html")
        
@app.route("/login",methods=["POST"])
def login():
    """
    Login page for authenticating users

    This function handles the "/login" route and verifies the user information.
    The function also creates a csrf_token on succesful login


    Returns:
        Redirects to index on succesful login.
        On failure to login returns template with username pre-loaded
    """
        
    username = request.form["username"]
    password = request.form["password"]


    if authentication.login(username,password):

        session["csrf_token"] = secrets.token_hex(16)
        return redirect("/")
    else:
        return render_template("login.html", error="Invalid username or password",username=username)
        

@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Registration page for registering new users

    This function handles the "/register" route.
    The function also creates a csrf_token on succesful login


    Returns:
        Redirects to index on succesful registration.
        On failure to renders the registration page again with the relevant error
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if not username or not password or not confirm_password:
            return render_template("register.html", error="Please fill in all fields")
        
        if password != confirm_password:
            return render_template("register.html", error="Passwords do not match")
        
        if not authentication.register(username,password):
            return render_template("register.html", error="username already taken")
        session["csrf_token"] = secrets.token_hex(16)
        return redirect("/")
    

    return render_template("register.html")

@app.route("/logout")
def logout():
    """
    Logout page for logging out

    This function handles the "/logout" route and clears the session.


    Returns:
        returns a redirection to index
    """
    session.clear()
    return redirect("/")


@app.route("/new_area")
def new_area():
    """
    Logout page for logging out

    This function handles the "/logout" route and clears the session.


    Returns:
        returns a html template for creating the new area
    """
    return render_template("new_area.html")


@app.route("/create_area", methods=["POST"])
def create_area():
    
    if session["role"] == "admin":
        name = request.form["name"]
        description = request.form["description"]
        is_secret = bool(request.form.get("is_secret"))
        users = request.form.get("users").strip()
        if users:
            users = users.split(",")
        else:
            users = []
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        discussion_areas.create_area(name,description,is_secret,users)

    return redirect("/")


@app.route("/discussion/<int:area_id>")
def get_discussion_area(area_id):
    """
    Discussion area function
    
    """
    area_found, area, threads = discussion_areas.get_area_by_id(area_id)
    if area_found:
        return render_template("discussion_area.html", threads=threads, area=area)
    else:
        return "Discussion area not found or user unauthorized"
    

@app.route("/delete_area/<int:area_id>",methods=["POST"])
def delete_area(area_id):
    """
    Function to hide a discussion area by flipping is_hidden to true
    """
    if session["role"] == "admin":
        discussion_areas.hide_area(area_id)

    return redirect("/")

@app.route("/new_thread", methods=["GET", "POST"])
def create_thread():
    area_id = request.args.get("area_id")
    if request.method == "POST":
        title = request.form["title"]
        first_message = request.form["First_message"]
        user_id = session.get("user_id")

        area_id = request.form.get("area_id")
        thread_id = threads.create_thread(title,user_id,area_id,first_message)
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        return redirect(f"/thread/{thread_id}")
    
    # If GET request, render the thread creation form
    return render_template("new_thread.html", area_id=area_id)

@app.route("/thread/<int:thread_id>")
def get_thread(thread_id):
    area,thread,messages = threads.get_thread(thread_id)
    if not area == False:

        return render_template("thread.html", messages=messages, thread=thread,area=area)
    else:
        return "Thread not found", 404
    
@app.route("/post_reply", methods=["POST"])
def post_reply():
    thread_id = request.form.get("thread_id")
    reply_content = request.form.get("reply_content")
    user_id = session.get("user_id")

    if not thread_id or not reply_content:
        return "Bad Request: Missing thread ID or reply content", 400

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)
    threads.add_message(reply_content,thread_id,user_id)


    return redirect(f"/thread/{thread_id}")





@app.route("/search_result",methods=["GET"])
def result():
    query = request.args["query"]
    results = search.search(query)

    return render_template("search_result.html",messages = results)


@app.route("/edit_message/<int:message_id>", methods=["GET", "POST"])
def edit_message(message_id):
    # Fetch the message by ID
    message = messages.get_message(message_id=message_id)

    if not message:
        return "Message not found"

    # Check if the logged-in user is the author of the message or an admin
    if message.user_id != session["user_id"] and session.get("role") != "admin":
        return "Not authorized"

    if request.method == "POST":
        # Handle the message update
        new_content = request.form["content"]
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        messages.edit_message(message_id=message_id,content=new_content)
        return redirect(f"/thread/{message.thread_id}")  # Redirect to the thread where the message is

    return render_template("edit_message.html", message=message)


@app.route("/delete_message/<int:message_id>")
def delete_message(message_id):
    message = messages.get_message(message_id=message_id)
    if message.user_id != session["user_id"] and session.get("role") != "admin":
        return "Not authorized"
    else:
        messages.delete_message(message_id)
        return redirect(f"/thread/{message.thread_id}")
    


@app.route("/edit_thread/<int:thread_id>", methods=["GET", "POST"])
def edit_thread(thread_id):
    # Fetch the thread and area by thread_ID
    area,thread,_ = threads.get_thread(thread_id=thread_id)

    if not thread:
        return "Thread not found"

    # Check if the logged-in user is the author of the thread or an admin
    if thread.user_id != session["user_id"] and session.get("role") != "admin":
        return "Not authorized"

    if request.method == "POST":
        # Handle the thread update
        new_title = request.form["title"]
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        threads.edit_thread(thread_id=thread_id, title=new_title)
        return redirect(f"/discussion/{area.id}")  # Redirect to the area after editing

    return render_template("edit_thread.html", thread=thread,area=area)


@app.route("/delete_thread/<int:thread_id>", methods=["GET","POST"])
def delete_thread(thread_id):
    # Fetch the thread and area by thread_ID
    area,thread,_ = threads.get_thread(thread_id=thread_id)

    if not thread:
        return "Thread not found"

    # Check if the logged-in user is the author of the thread or an admin
    if thread.user_id != session["user_id"] and session.get("role") != "admin":
        return "Not authorized"

    # Soft delete the thread
    threads.delete_thread(thread_id)
    return redirect(f"/discussion/{area.id}")  # Redirect to the discussion area after deleting
