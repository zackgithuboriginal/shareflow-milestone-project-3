#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from flask import Flask, flash, render_template, redirect, request, \
    session, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, \
    check_password_hash
if os.path.exists('env.py'):
    import env
from datetime import datetime
from flask_paginate import Pagination, get_page_args

app = Flask(__name__)

app.config['MONGO_DBNAME'] = os.environ.get('MONGO_DBNAME')
app.config['MONGO_URI'] = os.environ.get('MONGO_URI')
app.secret_key = os.environ.get('SECRET_KEY')

db = PyMongo(app).db


# Function used to develop pagination lists

def get_posts(posts, offset=0, per_page=10):
    return posts[offset:offset + per_page]


# Route responsible for handling 404 errors and directing user to 404 page

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


# View Responsible for routing of home page and default post display page

@app.route('/')
@app.route('/posts')
def posts():

    # Takes the filter and sort arguments from the input form, if no arguments, uses default values

    filter_sort = request.args.get('sort-by') or 'post_date'
    filter_topic = request.args.get('topic')

    # Uses given arguments to get relevant list of posts

    if filter_topic:
        if filter_topic == 'all':
            posts = list(db.posts.find().sort(filter_sort, -1))
        else:
            posts = \
                list(db.posts.find({'topic_name': filter_topic}).sort(filter_sort,
                     -1))
    else:
        posts = list(db.posts.find().sort(filter_sort, -1))

    # Parameters used for paginating the list of posts
    # page represents the current page of pagination, default value is 1
    # per_page represents the number of posts to be displayed per page
    # offset represents the posts needed to be displayed on each page
    # i.e page 2 will be 10 - 19 page 4 will be 30 - 39 ...

    (page, per_page, offset) = get_page_args(page_parameter='page',
            per_page_parameter='per_page')

    # Total length of posts used to determine the total number of pages

    total = len(posts)

    # Pagination_posts is the total list of posts

    pagination_posts = get_posts(posts=posts, offset=offset,
                                 per_page=per_page)

    # Pagination contains the pagination details, and data for navigation

    pagination = Pagination(page=page, page_parameter='page',
                            per_page=per_page, total=total,
                            css_framework='bootstrap4')

    topics = list(db.topics.find())
    users = list(db.users.find())

    # If user is signed in, will pass their plussed posts to the render to
    # inform whether a post should display a plus or tick

    if 'user' in session:
        plusses = db.users.find_one({'username': session['user'
                                    ]})['voted']
        user_plusses = []
        for post in plusses:
            user_plusses.append(ObjectId(post))
        return render_template(
            'posts.html',
            users=users,
            topics=topics,
            posts=pagination_posts,
            page=page,
            per_page=per_page,
            pagination=pagination,
            user_plusses=user_plusses,
            )
    return render_template(
        'posts.html',
        users=users,
        topics=topics,
        posts=pagination_posts,
        page=page,
        per_page=per_page,
        pagination=pagination,
        )


# View responsible for rendering the user register page and creating the user object record

@app.route('/register', methods=['GET', 'POST'])
def register():

    # If user submits registration form from register.html
    # this section will handle creating the register object and posting it to the collection

    if request.method == 'POST':
        existing_user = \
            db.users.find_one({'username': request.form.get('username'
                              ).lower()})

        if existing_user:
            flash('Username unavailable.')
            return redirect(url_for('register'))

        # The username and password are taken from the user's submitted form
        # the registration date will be generated automatically
        # all other fields will be generated with their default values

        register = {
            'username': request.form.get('username').lower(),
            'password': generate_password_hash(request.form.get('password'
                    )),
            'voted': [],
            'account_image': '/static/images/avatar_images/avatar_1.png',
            'directly_input_url': False,
            'registration_date': datetime.now().strftime('%m/%d/%Y'),
            'posts_made': 0,
            'comments_made': 0,
            'plusses': 0,
            }

        # Here the new user object is added to the collection

        db.users.insert_one(register)

        session['user'] = request.form.get('username').lower()

        # User is provided feedback with a flash message

        flash('Registration Complete')
        return redirect(url_for('posts'))

    # If the user has not submitted the form,
    # this is the default routing and will render the register.html template for the user

    return render_template('register.html')


# This view handles users updating their avatar or adding a direct url to their user record

@app.route('/edit_avatar/<active_tab>/<userPlusPage>/<userPostPage>',
           methods=['GET', 'POST'])
def edit_avatar(active_tab, userPlusPage, userPostPage):
    if request.method == 'POST':
        user = db.users.find_one({'username': session['user']})

        # If the user inputs an image url as their avatar
        # it will update their record with the url and with
        # 'directly_input_url' = True so that jinja can render
        # the url string in the form if they go to update it again

        if request.form.get('avatar_select') == 'direct_input':
            updated_avatar = \
                {'$set': {'account_image': request.form.get('avatar_direct_input'
                 ), 'directly_input_url': True}}
        else:

            selected_avatar = request.form.get('avatar_select')

            # If the user chooses the avatar that they already have selected
            # nothing is posted to the database and the page is reloaded

            if selected_avatar == user['account_image']:
                return redirect(url_for('account', post_id='None',
                                active_tab=active_tab,
                                userPlusPage=userPlusPage,
                                userPostPage=userPostPage))
            else:

            # If the user chooses a new avatar the href relating to the image
            # is set as the value of their account_image field

                updated_avatar = \
                    {'$set': {'account_image': selected_avatar,
                     'directly_input_url': False}}

        # Updates the user's record with the values in the update object

        db.users.update({'username': session['user']}, updated_avatar)

        # A flash message is displayed to the user to inform them that the update has been made
        # and then the page is reloaded to display the updated image

        flash('Image Successfully Updated')
        return redirect(url_for('account', post_id='None',
                        active_tab=active_tab,
                        userPlusPage=userPlusPage,
                        userPostPage=userPostPage))
    else:
        return redirect(url_for('account', post_id='None',
                        active_tab=active_tab,
                        userPlusPage=userPlusPage,
                        userPostPage=userPostPage))


# This view handles the rendering of the sign in page as well as
# the actual sign in functionality

@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'POST':

    # If the user submits the form will check if their is a user record with the provided username

        existing_user = \
            db.users.find_one({'username': request.form.get('username'
                              ).lower()})

    # If there is an existing record

        if existing_user:

            # It will check whether the provided password hash matches the stored hashed password value

            if check_password_hash(existing_user['password'],
                                   request.form.get('password')):

                # If the values match then the user will be added to the session cookie and the user will be presented feedback with a flash message

                session['user'] = request.form.get('username').lower()
                flash('Successfully Signed In')
                return redirect(url_for('posts'))
            else:

            # If there is no password match the page is reloaded and the user is informed

                flash('Incorrect Account Details')
                return redirect(url_for('sign_in'))
        else:

        # If there is no existing user the page is reloaded and the user is informed

            flash('Incorrect Account Details')
            return redirect(url_for('sign_in'))

    # If the user is not submitting the form the default behaviour of rendering the page will occur

    return render_template('sign_in.html')


# This view will handle rendering the create post page

@app.route('/create_post')
def create_post():
    topics = list(db.topics.find())
    return render_template('create_post.html', topics=topics)


# This view will handle adding a post to the database from the create_post page

@app.route('/add_post', methods=['GET', 'POST'])
def add_post():

    # if the user is in session and the

    if 'user' in session:
        if request.method == 'POST':
            user = db.users.find_one({'username': session['user']})
            user_posts_made = user['posts_made']

            # This object will be used to update the posts made tally of the author's record

            update_user = {'$set': {'posts_made': user_posts_made + 1}}

            # This object will be added to the posts collection,
            # the post title, psot content and post topic will be taken from the submitted form
            # the author and post date will be read automatically
            # and the other properties will be set with their default values

            post = {
                'post_title': request.form.get('post_title'),
                'post_content': request.form.get('post_content'),
                'topic_name': request.form.get('post_topic'),
                'author': session['user'],
                'post_date': datetime.now().strftime('%m/%d/%Y, %H:%M:%S'
                        ),
                'plusses': 0,
                'comments': [],
                'total_comments': 0,
                'users_voted': [],
                }
            db.posts.insert_one(post)
            db.users.update_one({'username': session['user']},
                                update_user)
            flash('Post Successfully Added')
            return redirect(url_for('posts'))
    else:

    # If the user is not signed in, they will be redirected to the registration page

        flash('You must be signed in to create posts')
        return redirect(url_for('register'))


# This view handles the rendering of the edit post page as well as submitted an updated
# post to the database
# It accepts post_id pagination_arguments, these are used to store the pagination status of
# both the posts and account templates
# they will be passed back into the redirect statements to render the user's previous page

@app.route('/edit_post/<post_id>/<pagination_arguments>', methods=['GET'
           , 'POST'])
def edit_post(post_id, pagination_arguments):

    # pagination_arguments is split from a string to an array of values

    split_pagination_arguments = pagination_arguments.replace('[', ''
            ).replace(']', '').replace("'", '').split(',')

    # If the user has submitted the edit post form a function will be called to process the form's values

    if request.method == 'POST':
        if process_post_edit(post_id) == 'success':

            # If the number of values in the array is 3, the account page will be rendered using the relevant parameters

            if len(split_pagination_arguments) == 3:
                return redirect(url_for(
                    'account',
                    post_id=post_id,
                    active_tab=split_pagination_arguments[2],
                    userPlusPage=split_pagination_arguments[1],
                    userPostPage=split_pagination_arguments[0],
                    _anchor=post_id,
                    ))
            else:

            # Otherwise the posts template will be rendered

                return redirect(url_for('posts', post_id=post_id,
                                page=split_pagination_arguments[0],
                                _anchor=post_id))

    post = db.posts.find_one({'_id': ObjectId(post_id)})
    topics = db.topics.find()
    return render_template('edit_post.html', post=post, topics=topics,
                           pagination_arguments=pagination_arguments)


# This view handles the functionality of redirecting the user to their previous location
# when they try to close the edit post page

@app.route('/close_post_edit/<post_id>/<pagination_arguments>')
def close_post_edit(post_id, pagination_arguments):

    # It splits the pagination argument into an array of values which will then inform the parameters provided to the redirect statement

    split_pagination_arguments = pagination_arguments.replace('[', ''
            ).replace(']', '').replace("'", '').split(',')
    if len(split_pagination_arguments) == 3:
        return redirect(url_for(
            'account',
            post_id=post_id,
            active_tab=split_pagination_arguments[2],
            userPlusPage=split_pagination_arguments[1],
            userPostPage=split_pagination_arguments[0],
            _anchor=post_id,
            ))
    else:
        return redirect(url_for('post_details', post_id=post_id,
                        post_page=int(split_pagination_arguments[0])))


# This function takes the provided post_id parameter
# it uses it to find the relevant post and then updated it using the
# values provided in the form by the user

def process_post_edit(post_id):
    post = db.posts.find_one({'_id': ObjectId(post_id)})
    updated_post = {'$set': {'post_title': request.form.get('post_title'
                    ), 'post_content': request.form.get('post_content'
                    ), 'topic_name': request.form.get('post_topic')}}

    db.posts.update({'_id': ObjectId(post_id)}, updated_post)
    flash('Post Successfully Edited')
    return 'success'


# This view handles the removal of the user from the cookie session

@app.route('/sign_out')
def sign_out():
    flash('Successfully signed out.')
    session.pop('user')

    return redirect(url_for('sign_in'))


# This view handles the processing of the post voting
# it accepts only the post_id as a parameter

def process_vote(post_id):
    current_post = db.posts.find_one({'_id': ObjectId(post_id)})
    current_vote = current_post['plusses']
    post_creator = current_post['author']
    author = db.users.find_one({'username': post_creator})
    post_creator_plusses = author['plusses']
    if 'user' in session:

        # The function checks whether the post is already present in the user's array of plussed posts

        already_voted = db.users.find_one({'username': session['user'
                ]})['voted']

        # If the user has already plussed the post,
        # the post will be updated by removing one from the plus count and removing the user from the array of voters
        # the author of the post will be updated by removing 1 from their total plus tally
        # the active user will be updated by removing the post id from their voted posts array

        if post_id in already_voted:
            update_vote = {'$set': {'plusses': current_vote - 1},
                           '$pull': {'users_voted': session['user']}}

            update_author = {'$set': {'plusses': post_creator_plusses \
                             - 1}}

            update_user = {'$pull': {'voted': post_id}}

            # The three records will then be updated and the function will return to the view

            db.users.update_one({'username': session['user']},
                                update_user)
            db.posts.update_one({'_id': ObjectId(post_id)}, update_vote)
            db.users.update_one({'username': author}, update_author)
            return (post_id, 'success')
        else:

        # If the user has not already plussed the post
        # the post will be updated by adding one from the plus count and adding the user to the array of voters
        # the author of the post will be updated by adding 1 to their total plus tally
        # the active user will be updated by adding the post id to their voted posts array

            update_vote = {'$set': {'plusses': current_vote + 1},
                           '$push': {'users_voted': session['user']}}

            update_author = {'$set': {'plusses': post_creator_plusses \
                             + 1}}

            update_user = {'$push': {'voted': post_id}}

            # The three records will then be updated and the function will return to the view

            db.users.update_one({'username': session['user']},
                                update_user)
            db.posts.update_one({'_id': ObjectId(post_id)}, update_vote)
            db.users.update_one({'username': author}, update_author)
            return (post_id, 'success')
    else:

    # If the users is not signed in they will be presented with a flash message and no update will occur

        alertUser('session')
        return (post_id, 'error')


# This view receives and handles votes from the main post view page
# it accepts the posts id and a page parameter
# the post id is passed into the process vote function to update the relevant records
# the page parameter is passed back into the return statment to reload the posts page on the correct page

@app.route('/posts_vote/<post_id>/<page>', methods=['GET', 'POST'])
def posts_vote(post_id, page):
    vote_status = process_vote(post_id)
    return redirect(url_for('posts', post_id=post_id, page=page,
                    _anchor=post_id))


# This view receives and handles votes from the detailed post page
# it accepts the post id and an array called pagination arguments as parameters
# the post id is passed into the process vote function to update the relevant records
# the pagination_arguments are passed to allow the pagination arguments to be used once the page reloads so
# that if the details page is closed the user will be redirected to the correct postion

@app.route('/vote/<post_id>/<pagination_arguments>')
def vote(post_id, pagination_arguments):
    vote_status = process_vote(post_id)
    split_pagination_arguments = pagination_arguments.replace('[', ''
            ).replace(']', '').replace("'", '').replace(' ', ''
            ).split(',')
    if len(split_pagination_arguments) == 3:
        return redirect(url_for(
            'account_post_details',
            post_id=post_id,
            active_tab=split_pagination_arguments[2],
            userPlusPage=split_pagination_arguments[1],
            userPostPage=split_pagination_arguments[0],
            _anchor=post_id,
            ))
    else:
        return redirect(url_for('post_details', post_id=post_id,
                        post_page=int(split_pagination_arguments[0])))


# This view handles the creation of comments
# accepts post id and the pagination arguments of the user's postiion before opening the details view

@app.route('/comment/<post_id>/<pagination_arguments>', methods=['GET',
           'POST'])
def add_comment(post_id, pagination_arguments):
    split_pagination_arguments = pagination_arguments.replace('[', ''
            ).replace(']', '').replace("'", '').replace(' ', ''
            ).split(',')
    if 'user' in session:
        if request.method == 'POST':

            # Finds the relevant post and creates a unique comment id

            post = db.posts.find_one({'_id': ObjectId(post_id)})
            comment_id = str(post_id) + '/' + str(post['total_comments'
                    ] + 1)

            # Takes the comment content from the request form, automatically generates other values

            comment = {
                'comment_id': comment_id,
                'comment_content': request.form.get('comment_content'),
                'author': session['user'],
                'post_date': datetime.now().strftime('%m/%d/%Y, %H:%M:%S'
                        ),
                'attached_post': post_id,
                }

            # Updates user and post by adding the comment object to their comments array and increasing their comments count by 1

            user = db.users.find_one({'username': session['user']})
            user_comments_made = user['comments_made']
            update_post = {'$push': {'comments': comment},
                           '$set': {'total_comments': post['total_comments'
                           ] + 1}}

            update_user = {'$push': {'comments': comment},
                           '$set': {'comments_made': user_comments_made \
                           + 1}}

            db.users.update_one({'username': session['user']},
                                update_user)
            db.posts.update_one({'_id': ObjectId(post_id)}, update_post)
            flash('Comment Successfully Added')

            # The pagination arguments are used to determine which page the user was on previous to opening post details view
            # and then redirects the browser there using the relevant pagination parameters

            if len(split_pagination_arguments) == 3:
                return redirect(url_for(
                    'account_post_details',
                    post_id=post_id,
                    active_tab=split_pagination_arguments[2],
                    userPlusPage=split_pagination_arguments[1],
                    userPostPage=split_pagination_arguments[0],
                    _anchor=post_id,
                    ))
            else:
                return redirect(url_for('post_details',
                                post_id=post_id,
                                post_page=int(split_pagination_arguments[0])))
    else:

        alertUser('session')
        if len(split_pagination_arguments) == 3:
            return redirect(url_for(
                'account_post_details',
                post_id=post_id,
                active_tab=split_pagination_arguments[2],
                userPlusPage=split_pagination_arguments[1],
                userPostPage=split_pagination_arguments[0],
                _anchor=post_id,
                ))
        else:
            return redirect(url_for('post_details', post_id=post_id,
                            post_page=int(split_pagination_arguments[0])))


# This view handles the deletion of a post
# it accepts pagination arguments which are used to inform the pagination

@app.route('/delete_post/<post_id>/<pagination_arguments>')
def delete_post(post_id, pagination_arguments):

    # The function removes the post record from the collection

    db.posts.remove({'_id': ObjectId(post_id)})

    # The funciton pulls the vote record from the user's voted post array

    db.users.update({}, {'$pull': {'voted': {'$in': [post_id]}}}, True)

    # It removes the comments attached to the deleted post from the user's comments array

    db.users.update({},
                    {'$pull': {'comments': {'attached_post': post_id}}},
                    True)
    flash('Post Deleted')
    split_pagination_arguments = pagination_arguments.replace('[', ''
            ).replace(']', '').replace("'", '').replace(' ', ''
            ).split(',')
    if len(split_pagination_arguments) == 3:
        return redirect(url_for('account', post_id='None',
                        active_tab=split_pagination_arguments[2],
                        userPlusPage=split_pagination_arguments[1],
                        userPostPage=split_pagination_arguments[0]))
    else:
        return redirect(url_for('posts',
                        page=split_pagination_arguments[0]))


# This function handles the gathering of a posts details to populate the post details page
# It returns the post record and the list of users to create the authors avatar

def process_post_details(post_id):
    post = db.posts.find_one({'_id': ObjectId(post_id)})
    users = list(db.users.find())
    if 'user' in session:
        user = db.users.find_one({'username': session['user']})
        plusses = user['voted']
        user_plusses = []
        for plussed_post in plusses:
            user_plusses.append(ObjectId(plussed_post))
        return (post, user_plusses, users, user)
    return (post, users)


# View handles the rendering of the account details page
# accepts post id and post page as parameters

@app.route('/post_details/<post_id>/<post_page>')
def post_details(post_id, post_page):
    if db.posts.find_one({'_id': ObjectId(post_id)}):
        routing_parameters = process_post_details(post_id)
        if 'user' in session:
            return render_template(
                'post_details.html',
                post=routing_parameters[0],
                user_plusses=routing_parameters[1],
                users=routing_parameters[2],
                user=routing_parameters[3],
                page=post_page,
                )
        return render_template('post_details.html',
                               post=routing_parameters[0],
                               users=routing_parameters[1],
                               page=post_page)
    else:
        return redirect(url_for('posts', post_page=post_page))


# This view handles the voting functionality from the account page

@app.route('/account_vote/<active_tab>/<post_id>/<userPlusPage>/<userPostPage>'
           , methods=['GET', 'POST'])
def account_vote(
    post_id,
    active_tab,
    userPlusPage,
    userPostPage,
    ):
    vote_status = process_vote(post_id)
    return redirect(url_for(
        'account',
        post_id=post_id,
        active_tab=active_tab,
        userPlusPage=userPlusPage,
        userPostPage=userPostPage,
        _anchor=post_id,
        ))


# This view handles the rendering of the account details page from the account page
# The parameters it accepts are passed through
# to allow for the user to be returned to the correct location if they close the details view

@app.route('/account_post_details/<active_tab>/<post_id>/<userPlusPage>/<userPostPage>'
           )
def account_post_details(
    post_id,
    active_tab,
    userPlusPage,
    userPostPage,
    ):
    if db.posts.find_one({'_id': ObjectId(post_id)}):
        routing_parameters = process_post_details(post_id)
        if 'user' in session:
            return render_template(
                'post_details.html',
                active_tab=active_tab,
                post=routing_parameters[0],
                user_plusses=routing_parameters[1],
                users=routing_parameters[2],
                user=routing_parameters[3],
                userPlusPage=userPlusPage,
                userPostPage=userPostPage,
                )
        return render_template(
            'post_details.html',
            active_tab=active_tab,
            post=routing_parameters[0],
            users=routing_parameters[1],
            userPlusPage=userPlusPage,
            userPostPage=userPostPage,
            )
    else:
        return redirect(url_for('account', post_id='None',
                        active_tab=active_tab,
                        userPlusPage=userPlusPage,
                        userPostPage=userPostPage))


# This view handles the rendering of the account page

@app.route('/account/<post_id>/<active_tab>', methods=['GET', 'POST'])
def account(post_id, active_tab):
    if session['user']:
        user = db.users.find_one({'username': session['user']})
        username = user['username']

        users = list(db.users.find())

        # Finds the list of posts that a user has liked to be used to display a check or plus icon

        plussed_posts = []
        plusses = db.users.find_one({'username': session['user'
                                    ]})['voted']
        for post in plusses:
            plussed_posts.append(ObjectId(post))

        # Finds the list of posts that a user has liked to display on profile

        userPlusses = []
        posts_plussed = \
            list(db.posts.find({'users_voted': session['user'
                 ]}).sort('post_date', -1))
        for post in posts_plussed:
            if post['author'] != session['user']:
                userPlusses.append(post)
            else:
                pass

        # Finds the list of posts authored by user

        userPosts = list(db.posts.find({'author': session['user'
                         ]}).sort('post_date', -1))

        # Defining pagination parameters for the plusses list
        # page parameter represents the active page
        # per page parameter represents the number of posts to display per apge
        # offset represents the posts needed to be displayed on each page
        # i.e page 2 will be 10 - 19 page 4 will be 30 - 39 ...

        (plussesPage, per_page, offset) = \
            get_page_args(page_parameter='userPlusPage',
                          per_page_parameter='per_page')

        # Total length of plussed posts used to determine the total number of pages

        totalPlussedPosts = len(userPlusses)

        # pagination plussed list is the total paginated list of plussed posts

        pagination_plussed_list = get_posts(posts=userPlusses,
                offset=offset, per_page=per_page)

        # Pagination contains the pagination details, and data for navigation

        pagination_plussed = Pagination(page_parameter='userPlusPage',
                userPlusPage=plussesPage, per_page=per_page,
                total=totalPlussedPosts, css_framework='bootstrap4')

        # As above but for user authored posts

        (postsPage, per_page, offset) = \
            get_page_args(page_parameter='userPostPage',
                          per_page_parameter='per_page')

        totalUserPosts = len(userPosts)
        pagination_posts_list = get_posts(posts=userPosts,
                offset=offset, per_page=per_page)
        pagination_posts = Pagination(page_parameter='userPostPage',
                userPostPage=postsPage, per_page=per_page,
                total=totalUserPosts, css_framework='bootstrap4')

        # if the post id passed in is = None then the page will render on the default tab

        if post_id == 'None':
            return render_template(
                'account.html',
                active_tab=active_tab,
                username=username,
                users=users,
                userPlusses=pagination_plussed_list,
                plussed_posts=plussed_posts,
                pagination_plussed=pagination_plussed,
                userPostPage=postsPage,
                user=user,
                userPosts=pagination_posts_list,
                userPlusPage=plussesPage,
                per_page=per_page,
                pagination_posts=pagination_posts,
                )
        else:

        # if the post id passed in is defined
        # if the post represented by the post id is authored by the user the page will load with the posts tab active

            post = db.posts.find_one({'_id': ObjectId(post_id)})
            if post['author'] == session['user']:
                return render_template(
                    'account.html',
                    username=username,
                    users=users,
                    userPlusses=pagination_plussed_list,
                    plussed_posts=plussed_posts,
                    pagination_plussed=pagination_plussed,
                    userPostPage=postsPage,
                    active_tab='posts',
                    user=user,
                    userPosts=pagination_posts_list,
                    userPlusPage=plussesPage,
                    per_page=per_page,
                    pagination_posts=pagination_posts,
                    _anchor='#' + post_id,
                    )
            else:

        # if the post id passed in represents a post not authored by the user then the active page will be plusses

                return render_template(
                    'account.html',
                    username=username,
                    users=users,
                    userPlusses=pagination_plussed_list,
                    plussed_posts=plussed_posts,
                    pagination_plussed=pagination_plussed,
                    userPostPage=postsPage,
                    active_tab='plusses',
                    user=user,
                    userPosts=pagination_posts_list,
                    userPlusPage=plussesPage,
                    per_page=per_page,
                    pagination_posts=pagination_posts,
                    _anchor='#' + post_id,
                    )

    return redirect(url_for('sign_in'))


# This function sends a flash message to the user if they try to take an action without being logged in

def alertUser(key):
    if key == 'session':
        flash('You must be signed in to vote')
    return 'Ok'


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'), port=int(os.environ.get('PORT'
            )), debug=True)
