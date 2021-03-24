import os
from flask import (
    Flask, flash, render_template, redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env
from datetime import datetime


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/posts")
def posts(): 
    filter_sort = (request.args.get("sort-by") or "post_date")
    filter_topic = request.args.get("topic")
    if filter_topic:
        posts = list(mongo.db.posts.find(
            {"topic_name": filter_topic}).sort(filter_sort, -1))
        if filter_topic == "all":
            posts = list(mongo.db.posts.find().sort(filter_sort, -1))
    else:
        posts = list(mongo.db.posts.find().sort(filter_sort, -1))

    topics = list(mongo.db.topics.find())

    if "user" in session:
        pluses = mongo.db.users.find_one(
            {"username": session["user"]})["voted"]
        user_pluses = []
        for post in pluses:
            user_pluses.append(ObjectId(post))
        return render_template(
            "posts.html", posts=posts, topics=topics,
            user_pluses=user_pluses)
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
            "password": generate_password_hash(request.form.get("password")),
            "voted": []
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
                return redirect(url_for("posts"))
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
    if "user" in session:
        if request.method == "POST":
            post = {
                "post_title": request.form.get("post_title"),
                "post_content": request.form.get("post_content"),
                "topic_name": request.form.get("post_topic"),
                "author": session["user"],
                "post_date": datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                "pluses": 0,
                "comments": [],
                "total_comments": 0
            }
            mongo.db.posts.insert_one(post)
            flash("Post Successfully Added")
            return redirect(url_for("posts"))
    else:
        flash("You must be signed in to create posts")
        return redirect(url_for("register"))


@app.route("/edit_post/<post_id>/<user_location>", methods=["GET", "POST"])
def edit_post(post_id, user_location):
    if request.method == "POST":
        post = mongo.db.posts.find_one({"_id": ObjectId(post_id)})
        updated_post = {
            "post_title": request.form.get("post_title"),
            "post_content": request.form.get("post_content"),
            "topic_name": request.form.get("post_topic"),
            "author": session["user"],
            "post_date": post["post_date"],
            "pluses": post["pluses"],
            "comments": post["comments"]
        }

        mongo.db.posts.update({"_id": ObjectId(post_id)}, updated_post)
        flash("Post Successfully Edited")
        return redirect(url_for(user_location, post_id=post_id, _anchor=post_id))

    post = mongo.db.posts.find_one({"_id": ObjectId(post_id)})
    topics = mongo.db.topics.find()
    return render_template("edit_post.html", post=post, topics=topics, user_location=user_location)


@app.route("/sign_out")
def sign_out():
    flash("Successfully signed out.")
    session.pop("user")

    return redirect(url_for("log_in"))


@app.route("/vote/<post_id>/<user_location>", methods=["GET", "POST"])
def vote(post_id, user_location):
    print(post_id)
    print(user_location)
    current_post = mongo.db.posts.find_one({"_id": ObjectId(post_id)})
    current_vote = current_post["pluses"]

    if "user" in session:
        already_voted = mongo.db.users.find_one(
            {"username": session["user"]})["voted"]
        if post_id in already_voted:
            update_vote = {
                "$set": {
                     "pluses": current_vote - 1
                     }
                     }
            update_user = {
                '$pull': {
                     "voted": post_id
                     }
                     }
            mongo.db.users.update_one(
                {"username": session["user"]}, update_user)
            mongo.db.posts.update_one({"_id": ObjectId(post_id)}, update_vote)
            if user_location == 'account':
                return redirect(url_for(user_location, username=session["user"], _anchor=post_id))
            else:
                return redirect(url_for(user_location, post_id=post_id, _anchor=post_id))
        else:
            update_vote = {
                "$set": {
                     "pluses": current_vote + 1
                     }
                     }
            update_user = {
                '$push': {
                     "voted": post_id
                     }
                     }
            mongo.db.users.update_one(
                {"username": session["user"]}, update_user)
            mongo.db.posts.update_one({"_id": ObjectId(post_id)}, update_vote)
            if user_location == 'account':
                return redirect(url_for(user_location, username=session["user"], _anchor=post_id))
            else:
                return redirect(url_for(user_location, post_id=post_id, _anchor=post_id))
    else:
        alertUser("session")
        return redirect(url_for("posts"))


@app.route("/post_details/<post_id>/<user_location>")
def post_details(post_id, user_location):
    post = mongo.db.posts.find_one({"_id": ObjectId(post_id)})
    if "user" in session:
        plusses = mongo.db.users.find_one(
            {"username": session["user"]})["voted"]
        user_plusses = []
        for plussed_post in plusses:
            user_plusses.append(ObjectId(plussed_post))
        return render_template(
            "post_detail.html", post=post, user_plusses=user_plusses, user_location=user_location)
    return render_template(
        "post_detail.html", post=post, user_location=user_location)


@app.route("/add_comment/<post_id>/<user_location>", methods=["GET", "POST"])
def add_comment(post_id, user_location):
    if "user" in session:
        if request.method == "POST":
            post = mongo.db.posts.find_one({"_id": ObjectId(post_id)})
            comment_id = (str(post_id) + "/" + str(post["total_comments"]+1))
            comment = {
                "comment_id": comment_id,
                "comment_content": request.form.get("comment_content"),
                "author": session["user"],
                "post_date": datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                "attached_post": post_id
            }
            update_post = {
                "$push": {
                        "comments": comment
                        },
                "$set": {
                        "total_comments": post["total_comments"]+1
                        }
                        }
            update_user = {
                "$push": {
                        "comments": comment
                        }
                        }
            mongo.db.users.update_one(
                {"username": session["user"]}, update_user)
            mongo.db.posts.update_one({"_id": ObjectId(post_id)}, update_post)
            flash("Comment Successfully Added")
            if user_location == 'account':
                return redirect(url_for(user_location, username=session["user"], _anchor=post_id))
            else:
                return redirect(url_for(user_location, post_id=post_id, _anchor=post_id))

    else:
        alertUser("session")
        return redirect(url_for("posts"))


@app.route("/delete_post/<post_id>")
def delete_post(post_id):
    mongo.db.posts.remove({"_id": ObjectId(post_id)})
    mongo.db.users.update({},{"$pull": { "voted": { "$in": [ post_id ] }}},
    True)
    mongo.db.users.update(
    {}, 
    { "$pull": { "comments": { "attached_post": post_id } } },
    True)
    flash("Post Deleted")
    return redirect(url_for("posts"))


@app.route("/account", methods=["GET", "POST"])
def account():
    if session["user"]:
        user = mongo.db.users.find_one(
            {"username": session["user"]})
        username = user["username"]
        plusses = mongo.db.users.find_one(
            {"username": session["user"]})["voted"]
        plussed_posts = []
        for post in plusses:
            plussed_posts.append(ObjectId(post))
        plussedPostIds = user["voted"]
        userPlusses = []
        for post in plussedPostIds:
            userPlusses.append(
                mongo.db.posts.find_one({"_id": ObjectId(post)}))
                
        userPosts = list(
            mongo.db.posts.find({"author": session["user"]}))
        print(session["user"])
        return render_template(
            "account.html", username=username,
            userPosts=userPosts,
            userPlusses=userPlusses,
            plussed_posts=plussed_posts)

    return redirect(url_for("login"))


@app.route("/close_post_details/<post_id>/<previous_location>")
def close_post_details(post_id, previous_location):
    return redirect(url_for(previous_location, post_id=post_id, _anchor=post_id))

def alertUser(key):
    if key == "session":
        flash("You must be signed in to vote")
    return "Ok"


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
