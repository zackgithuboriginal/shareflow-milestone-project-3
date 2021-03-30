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

    users = list(mongo.db.users.find())
    if "user" in session:
        pluses = mongo.db.users.find_one(
            {"username": session["user"]})["voted"]
        user_pluses = []
        for post in pluses:
            user_pluses.append(ObjectId(post))
        return render_template(
            "posts.html", posts=posts, users=users,  topics=topics,
            user_pluses=user_pluses)
    return render_template("posts.html", posts=posts, users=users, topics=topics)


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
            "voted": [],
            "account_image": "/static/images/avatar_images/avatar_1.png",
            "directly_input_url": False,
            "registration_date": datetime.now().strftime("%m/%d/%Y"),
            "posts_made": 0,
            "comments_made": 0,
            "plusses": 0,
        }

        mongo.db.users.insert_one(register)

        session["user"] = request.form.get("username").lower()
        flash("Registration Complete")

    return render_template("register.html")


@app.route("/edit_avatar", methods=["GET", "POST"])
def edit_avatar():
    if request.method == "POST":
        user = mongo.db.users.find_one(
            {"username": session["user"]})
        if request.form.get("avatar_select") == "direct_input":
            updated_avatar = {
                    "$set": {
                        "account_image": request.form.get("avatar_direct_input"),
                        "directly_input_url": True
                        }
            }
        else:
            selected_avatar = request.form.get("avatar_select")
            if selected_avatar == user["account_image"]:
                return redirect(url_for('account', post_id="None"))
            else:
                updated_avatar = {
                        "$set": {
                            "account_image": selected_avatar,
                            "directly_input_url": False
                            }
                }

        mongo.db.users.update({"username": session["user"]}, updated_avatar)
        flash("Image Successfully Updated")
        return redirect(url_for('account', post_id="None"))
    else:
        return redirect(url_for('account', post_id="None"))

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
            user = mongo.db.users.find_one({"username": session["user"]})
            user_posts_made = user["posts_made"]
            update_user = {
                "$set": {
                    "posts_made":user_posts_made + 1
                    }
                }
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
            mongo.db.users.update_one(
                {"username": session["user"]}, update_user)
            flash("Post Successfully Added")
            return redirect(url_for("posts"))
    else:
        flash("You must be signed in to create posts")
        return redirect(url_for("register"))


@app.route("/edit_post/<post_id>/<prev_location>", methods=["GET", "POST"])
def edit_post(post_id, prev_location):
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
        return redirect(url_for('post_details', post_id=post_id, user_location=prev_location, _anchor=post_id))

    post = mongo.db.posts.find_one({"_id": ObjectId(post_id)})
    topics = mongo.db.topics.find()
    return render_template("edit_post.html", post=post, topics=topics, prev_location=prev_location)


@app.route("/sign_out")
def sign_out():
    flash("Successfully signed out.")
    session.pop("user")

    return redirect(url_for("log_in"))


@app.route("/vote/<post_id>/<user_location>/<author>", methods=["GET", "POST"])
def vote(post_id, user_location, author):
    print(post_id)
    print(author)
    print(user_location)
    current_post = mongo.db.posts.find_one({"_id": ObjectId(post_id)})
    current_vote = current_post["pluses"]
    post_creator = mongo.db.users.find_one({"username": author})
    post_creator_plusses = post_creator["plusses"]
    print(post_creator_plusses)
    if "user" in session:
        already_voted = mongo.db.users.find_one(
            {"username": session["user"]})["voted"]
        if post_id in already_voted:
            update_vote = {
                "$set": {
                     "pluses": current_vote - 1
                     }
                     }
            update_author = {
                "$set": {
                     "plusses": post_creator_plusses - 1
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
            mongo.db.users.update_one({"username" :author}, update_author)
            if user_location == 'account':
                return redirect(url_for(user_location, post_id=post_id, _anchor=post_id))
            else:
                return redirect(url_for(user_location, post_id=post_id, user_location=user_location, _anchor=post_id))
        else:
            update_vote = {
                "$set": {
                     "pluses": current_vote + 1
                     }
                     }
            update_author = {
                "$set": {
                     "plusses": post_creator_plusses + 1
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
            mongo.db.users.update_one({"username" :author}, update_author)
            if user_location == 'account':
                return redirect(url_for(user_location, post_id=post_id, _anchor=post_id))
            else:
                return redirect(url_for(user_location, post_id=post_id, user_location=user_location, _anchor=post_id))
    else:
        alertUser("session")
        return redirect(url_for("posts"))


@app.route("/post_details/<post_id>/<user_location>")
def post_details(post_id, user_location):
    post = mongo.db.posts.find_one({"_id": ObjectId(post_id)})
    if "user" in session:
        user = mongo.db.users.find_one(
            {"username": session["user"]})
        plusses = user["voted"]
        user_plusses = []
        for plussed_post in plusses:
            user_plusses.append(ObjectId(plussed_post))
        return render_template(
            "post_detail.html", post=post, user=user, user_plusses=user_plusses, user_location=user_location)
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
            user = mongo.db.users.find_one({"username": session["user"]})
            user_comments_made = user["comments_made"]
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
                        },
                "$set": {
                        "comments_made":user_comments_made + 1
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


@app.route("/account/<post_id>", methods=["GET", "POST"])
def account(post_id):
    if session["user"]:
        user = mongo.db.users.find_one(
            {"username": session["user"]})
        username = user["username"]

        users = list(mongo.db.users.find())
        # Finds the list of posts that a user has liked for the check
        plussed_posts = []
        plusses = mongo.db.users.find_one(
            {"username": session["user"]})["voted"]
        for post in plusses:
            plussed_posts.append(ObjectId(post))

        # Finds the list of posts that a user has liked to display on profile
        userPlusses = []
        plussedPostIds = user["voted"]
        for post in plussedPostIds:
            if mongo.db.posts.find_one({"_id": ObjectId(post)})["author"] != username:
                userPlusses.append(
                    mongo.db.posts.find_one({"_id": ObjectId(post)}))
        
        userPosts = list(
            mongo.db.posts.find({"author": session["user"]}))
        if post_id=="None":
            return render_template(
                "account.html", username=username,
                users=users,
                userPosts=userPosts,
                userPlusses=userPlusses,
                plussed_posts=plussed_posts,
                active_tab="posts",
                user=user )
        else: 
            post = mongo.db.posts.find_one({"_id": ObjectId(post_id)})
            if post['author'] == session['user']:
                return render_template(
                    "account.html", username=username,
                    users=users,
                    userPosts=userPosts,
                    userPlusses=userPlusses,
                    plussed_posts=plussed_posts, active_tab="posts",
                    user=user)
            else:
                return render_template(
                    "account.html", username=username,
                    users=users,
                    userPosts=userPosts,
                    userPlusses=userPlusses,
                    plussed_posts=plussed_posts,
                    active_tab="plusses",
                    user=user)


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
