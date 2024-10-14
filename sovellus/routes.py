from app import app
from flask import redirect, render_template, request, session

from dotenv import load_dotenv
from os import getenv


import authentication
import discussion_areas
import threads
import search

load_dotenv()

app.secret_key = getenv("SECRET_KEY")

@app.route("/")
def index():
    """
    Index page to display all discussion areas the user has privileges to along with metadata.

    This function handles the "/" route and queries the database for all 
    discussion discussion_areas. For each discussion area, it retrieves:
      - The name and description of the area
      - The number of threads in the area
      - The number of messages across all threads in the area
      - The date of the latest message
      - The variable is_hidden
    The results are passed to the 'index.html' template for rendering.

    Returns:
        A rendered HTML template showing the list of discussion discussion_areas, 
        along with their thread and message counts and the latest message date.
    """
    user_id = session.get("user_id")
    user_role = session.get("role")

    all_areas = discussion_areas.get_areas(user_id,user_role)
    return render_template("index.html", areas=all_areas)

@app.route("/login",methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]


    if authentication.login(username,password):


        return redirect("/")
    else:
        return render_template("index.html", error="Invalid username or password")
        

@app.route("/register", methods=["GET", "POST"])
def register():

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

        return redirect("/")
    

    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/new_area")
def new_area():
    return render_template("new_area.html")


@app.route("/create_area", methods=["POST"])
def create_area():
    name = request.form["name"]
    description = request.form["description"]
    is_secret = bool(request.form.get("is_secret"))
    users = request.form.get("users").strip()
    if users:
        users = users.split(",")
    else:
        users = []
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
        return "Discussion area not found", 404
    

@app.route("/delete_area/<int:area_id>",methods=["POST"])
def delete_area(area_id):
    """
    Function to hide a discussion area by flipping is_hidden to true
    """
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

    print(user_id)
    if not thread_id or not reply_content:
        return "Bad Request: Missing thread ID or reply content", 400

    threads.add_message(reply_content,thread_id,user_id)


    return redirect(f"/thread/{thread_id}")





@app.route("/search_result",methods=["GET"])
def result():
    query = request.args["query"]
    results = search.search(query)

    return render_template("search_result.html",messages = results)
