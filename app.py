import os
from flask import (
    Flask, flash, render_template, redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env
from datetime import date


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/get_posts")
def get_posts():
    posts = list(mongo.db.posts.find())
    topics = list(mongo.db.topics.find())
    return render_template("posts.html", posts=posts, topics=topics)


@app.route("/topics")
def topics():
    topics = list(mongo.db.topics.find())
    return render_template("topics.html", topics=topics)


@app.route("/filter_topics/<topic>")
def filter_topics(topic):
    topics = list(mongo.db.topics.find())
    posts = list(mongo.db.posts.find({"topic_name": topic}))
    return render_template("posts.html", posts=posts, topics=topics)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username unavailable.")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }

        mongo.db.users.insert_one(register)

        session["user"] = request.form.get("username").lower()
        flash("Registration Complete")

    return render_template("register.html")


@app.route("/log_in", methods=["GET", "POST"])
def log_in():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Successfully Logged In")
                return redirect(url_for("get_posts"))
            else:
                flash("Incorrect Account Details")
                return redirect(url_for("log_in"))
        else:
            flash("Incorrect Account Details")
            return redirect(url_for("log_in"))

    return render_template("log_in.html")


@app.route("/create_post")
def create_post():
    topics = list(mongo.db.topics.find())
    return render_template("create_post.html", topics=topics)


@app.route("/add_post", methods=["GET", "POST"])
def add_post():
    if request.method == "POST":
        post = {
            "post_title": request.form.get("post_title"),
            "post_content": request.form.get("post_content"),
            "topic_name": request.form.get("post_topic"),
            "post_date": date.today().strftime("%d/%m/%Y"),
            "author": session["user"],
            "pluses": 0,
            "comments": {}
        }
        mongo.db.posts.insert_one(post)
        flash("Post Successfully Added")
        return redirect(url_for("get_posts"))


@app.route("/sign_out")
def sign_out():
    flash("Successfully signed out.")
    session.pop("user")

    return redirect(url_for("log_in"))


@app.route("/account/<username>", methods=["GET", "POST"])
def account(username):

    if session["user"]:
        username = mongo.db.users.find_one(
            {"username": session["user"]})["username"]
        posts = list(mongo.db.posts.find({"author": session["user"]}))
        return render_template("account.html", username=username, posts=posts)

    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
