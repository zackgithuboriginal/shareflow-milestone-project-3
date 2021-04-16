import os
from flask import Flask, flash, render_template, redirect, request, \
    session, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, \
    check_password_hash
from datetime import datetime
from flask_paginate import Pagination, get_page_args
if os.path.exists('env.py'):
    import env

app = Flask(__name__)

app.config['MONGO_DBNAME'] = os.environ.get('MONGO_DBNAME')
app.config['MONGO_URI'] = os.environ.get('MONGO_URI')
app.secret_key = os.environ.get('SECRET_KEY')

db = PyMongo(app).db


def get_posts(posts, offset=0, per_page=10):
    """
    Function used to develop paginated lists

    Arguments accepted:
            posts: this is the full list of posts
            offset: offset is the value used to determine the start integer
            per_page: this value is added to the offset to determine
            the end integer of the list slice

    i.e on the second page offset will be 10, per page wll be 10
    so the the returned list will be sliced from posts[10:20]
    """

    return posts[offset:offset + per_page]


@app.errorhandler(404)
def page_not_found(e):
    """
    Route responsible for handling 404 errors
    Renders 404.html page
    """

    return render_template('404.html')


@app.errorhandler(500)
def internal_server_error(e):
    """
    Route responsible for handling 500 errors
    Renders 500.html page
    """

    return render_template('500.html')


@app.route('/')
@app.route('/posts')
def posts():
    """
    View responsible for routing of home page and default post display page

    This function determines the filter and sort argments and uses them to get
    the posts list from the database.

    it then takes the list and slices it in order to output a
    shorter list with paginated pages

    Parameters used for paginating the list of posts
        page: represents the current page of pagination, default value is 1
        per_page: represents the number of posts to be displayed per page
        offset: represents the posts needed to be displayed on each page

    Pagination_posts is the total list of posts
    Pagination contains the pagination details, and data for
    navigating between pages


    If user is signed in, the function will pass a list of the user's plussed
    posts to inform whether each post should display a plus or tick
    """

    filter_sort = request.args.get('sort-by') or 'post_date'
    filter_topic = request.args.get('topic')

    if filter_topic:
        if filter_topic == 'all':
            posts = list(db.posts.find().sort(filter_sort, -1))
        else:
            posts = \
                list(db.posts.find({'topic_name': filter_topic}).sort(
                    filter_sort, -1))
    else:
        posts = list(db.posts.find().sort(filter_sort, -1))

    (page, per_page, offset) = get_page_args(page_parameter='page',
                                             per_page_parameter='per_page')

    total = len(posts)

    pagination_posts = get_posts(posts=posts,
                                 offset=offset, per_page=per_page)

    pagination = Pagination(page=page, page_parameter='page',
                            per_page=per_page, total=total,
                            css_framework='bootstrap4')

    topics = list(db.topics.find())
    users = list(db.users.find())

    if 'user' in session:
        plusses = db.users.find_one({'username': session['user']
                                     })['voted']
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


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    View responsible for rendering the user register page and
    creating the user object record

    If the function receives a post request from register.html
    the function will handle the creation of the new user object
    and posting it to the database

    The username and password are taken from the user's submitted form
    the registration date will be generated automatically
    all other fields will be generated with their default values

    the user will then be signed in by adding their username to the
    session cookie
    they will be redirected and provided successful feedback with a
    flash message


    If the function does not receive a post request
    it will instead render the register.html page
    """
    if 'user' not in session:
        if request.method == 'POST':
            existing_user = \
                db.users.find_one({'username': request.form.get(
                                    'username').lower()
                                })

            if existing_user:
                flash('Username unavailable.')
                return redirect(url_for('register'))

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

            db.users.insert_one(register)

            session['user'] = request.form.get('username').lower()

            flash('Registration Complete')
            return redirect(url_for('posts'))

        return render_template('register.html')

    else: 
        flash('You are already signed in.')
        return redirect(url_for('posts'))



@app.route('/edit-avatar/<active_tab>/<user_plus_page>/<user_post_page>',
           methods=['GET', 'POST'])
def edit_avatar(active_tab, user_plus_page, user_post_page):
    """
    This view handles users updating their avatar or adding a direct
     url to use as their avatar

    If the user inputs an image url as their avatar it will update
    their record with the url and with
    'directly_input_url' = True so that jinja can render knows that
    it should display the url in the url input field if the user
    goes to update it again

    If the user selects one of the avatar options the local path of
    the image is set as the value of their account_image field
    so that value can simply be input as the src of an img element

    The page will then be reloaded and the user's account image will
    be updated
    """

    if request.method == 'POST':
        user = db.users.find_one({'username': session['user']})

        if request.form.get('avatar_select') == 'direct_input':
            updated_avatar = \
                {'$set':
                    {'account_image': request.form.get('avatar_direct_input'),
                     'directly_input_url': True}}
        else:

            selected_avatar = request.form.get('avatar_select')

            # If the user chooses the avatar that they already have selected
            # nothing is posted to the database and the page is reloaded

            if selected_avatar == user['account_image']:
                return redirect(url_for('account', post_id='None',
                                active_tab=active_tab,
                                user_plus_page=user_plus_page,
                                user_post_page=user_post_page))
            else:
                updated_avatar = \
                    {'$set': {'account_image': selected_avatar,
                     'directly_input_url': False}}

        db.users.update({'username': session['user']}, updated_avatar)

        # A flash message is displayed to the user to inform them that
        # the update has been made

        flash('Image Successfully Updated')
        return redirect(url_for('account', post_id='None',
                        active_tab=active_tab,
                        user_plus_page=user_plus_page,
                        user_post_page=user_post_page))
    else:
        return redirect(url_for('account', post_id='None',
                        active_tab=active_tab,
                        user_plus_page=user_plus_page,
                        user_post_page=user_post_page))


@app.route('/sign-in', methods=['GET', 'POST'])
def sign_in():
    """
    View handles the rendering of the sign in page and handles the
    sign in functonality

    If the function receives a post request it will take two arguments
    from the request form
    the username, which must match an existing record in the database
    the password, which must match the hashed password value of the user object

    if both match the user is added to the session and
    redirected to the home page
    """
    if 'user' not in session:

        if request.method == 'POST':

            existing_user = \
                db.users.find_one({'username': request.form.get(
                                'username').lower()})

            if existing_user:
                if check_password_hash(existing_user['password'],
                                    request.form.get('password')):
                    session['user'] = request.form.get('username').lower()
                    flash('Successfully Signed In')
                    return redirect(url_for('posts'))
                else:

                    # If there is no password match the page is reloaded
                    # and the user is informed

                    flash('Incorrect Account Details')
                    return redirect(url_for('sign_in'))
            else:

                # If there is no existing user the page is
                # reloaded and the user is informed

                flash('Incorrect Account Details')
                return redirect(url_for('sign_in'))

        # If the user is not submitting the form the
        # default behaviour of rendering the page will occur

        return render_template('sign-in.html')
    else: 
        flash('You are already signed in.')
        return redirect(url_for('posts'))


@app.route('/create-post')
def create_post():
    """
    This view handles rendering the create post page
    It gets the list of topics from the database to ouput as select options
    """
    if 'user' in session:
        topics = list(db.topics.find())
        return render_template('create-post.html', topics=topics)
    
    else: 
        flash('You ust be signed in to create a post')
        return redirect(url_for('posts'))


@app.route('/add-post', methods=['GET', 'POST'])
def add_post():
    """
    This view handles adding a post to the database

    The user must be signed in, else they will be redirected
    and informed that it is necessary to be signed in

    The function creates an object containing a new post
    record with data from the request form and another containing
    the changes to be made to the user's record
    The objects are then added to the database and the
    user is redirected to the home page
    """

    if 'user' in session:
        if request.method == 'POST':
            user = db.users.find_one({'username': session['user']})
            user_posts_made = user['posts_made']

            # This object will be used to update the posts made
            # tally of the author's record

            update_user = {'$set': {'posts_made': user_posts_made + 1}}

            # This object will be added to the posts collection,
            # the post title, psot content and post topic
            # will be taken from the submitted form
            # the author and post date will be read automatically
            # and the other properties will be set with their default values

            post = {
                'post_title': request.form.get('post_title'),
                'post_content': request.form.get('post_content'),
                'topic_name': request.form.get('post_topic'),
                'author': session['user'],
                'post_date': datetime.now().strftime('%m/%d/%Y, %H:%M:%S'),
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

        # If the user is not signed in, they will be redirected
        # to the registration page

        flash('You must be signed in to create posts')
        return redirect(url_for('register'))


@app.route('/edit-post/<post_id>/<pagination_arguments>', methods=['GET',
           'POST'])
def edit_post(post_id, pagination_arguments):
    """
    This view handles the rendering of the edit post page as well as
    adding updated posts to the database

    Arguments:
        post_id: contains the unique objectid of the post being edited
        pagination_arguments: contains the page specific pagination and
        tab arguments from the user's previous location

    The pagination arguments are passed to allow the page to
     be rendered with the correct active tab and correct pagination status
    """
    if 'user' in session:
        # pagination_arguments is split from a string to an array of values

        split_pagination_arguments = pagination_arguments.replace(
            '[', '').replace(']', '').replace("'", '').replace(
            ' ', '').split(',')

        # If the user has submitted the edit post form a function will
        # be called to process the form's values

        if request.method == 'POST':
            if process_post_edit(post_id) == 'success':

                # If the number of values in the array is 3, the account
                # page will be rendered using the relevant parameters

                if len(split_pagination_arguments) == 3:
                    return redirect(url_for(
                        'account',
                        post_id=post_id,
                        active_tab=split_pagination_arguments[2],
                        user_plus_page=split_pagination_arguments[1],
                        user_post_page=split_pagination_arguments[0],
                        _anchor=post_id,
                        ))
                else:

                    # Otherwise the posts page will be rendered

                    return redirect(url_for('posts', post_id=post_id,
                                    page=split_pagination_arguments[0],
                                    _anchor=post_id))

        post = db.posts.find_one({'_id': ObjectId(post_id)})
        topics = db.topics.find()
        return render_template('edit-post.html', post=post, topics=topics,
                            pagination_arguments=pagination_arguments)
    else: 
        flash('You must be signed in to edit posts')
        return redirect(url_for('posts'))


@app.route('/close-post-edit/<post_id>/<pagination_arguments>')
def close_post_edit(post_id, pagination_arguments):
    """
    This view handles the closing of the edit post page and the
     redirecting of the user to their previous location

    Arguments:
        post_id: contains the unique objectid of the post that was
        being edited
        pagination_arguments: contains the page specific pagination and
        tab arguments from the user's previous location

    The pagination arguments are passed to allow the page to be
    rendered with the correct active tab and correct pagination status
    """

    # The pagination arguments are split into an array of
    # values which will then inform the parameters provided
    # to the redirect statement

    split_pagination_arguments = pagination_arguments.replace(
        '[', '').replace(']', '').replace("'", '').replace(
        ' ', '').split(',')
    if len(split_pagination_arguments) == 3:
        return redirect(url_for(
            'account',
            post_id=post_id,
            active_tab=split_pagination_arguments[2],
            user_plus_page=split_pagination_arguments[1],
            user_post_page=split_pagination_arguments[0],
            _anchor=post_id,
            ))
    else:
        return redirect(url_for('post_details', post_id=post_id,
                        post_page=int(split_pagination_arguments[0])))


def process_post_edit(post_id):
    """
    This function processes the editing of a post

    It takes the post_id as an argument to find and update the relevant post

    An object is created with the post details taken from the user's
    request form and that is then used to change the post's record
    """

    post = db.posts.find_one({'_id': ObjectId(post_id)})
    updated_post = {'$set':
                    {'post_title': request.form.get('post_title'),
                     'post_content': request.form.get('post_content'),
                     'topic_name': request.form.get('post_topic')}}

    db.posts.update({'_id': ObjectId(post_id)}, updated_post)
    flash('Post Successfully Edited')
    return 'success'


@app.route('/sign-out')
def sign_out():
    """
    This view handles siging the user out of the website by
    removing the user from the session
    """

    flash('Successfully signed out.')
    session.pop('user')

    return redirect(url_for('sign_in'))


def process_vote(post_id):
    """
    This function processes a user's vote

    it accepts the post's unique id value as the only argument

    it will determine whether the user has already voted on the post or not
    if the user has already voted for the post it will remove the
     vote from the post's record and the post author's record
    and remove post the post id of the post from the user's record

    if the user has not already voted for the post it will add its
     vote to the post's record, and the post author's record
    and add the post id of the post to the user's record

    """

    current_post = db.posts.find_one({'_id': ObjectId(post_id)})
    current_vote = current_post['plusses']
    post_creator = current_post['author']
    author = db.users.find_one({'username': post_creator})
    post_creator_plusses = author['plusses']
    if 'user' in session:

        # The function checks whether the post is already
        # present in the user's array of plussed posts

        already_voted = db.users.find_one({'username': session['user']
                                           })['voted']

        # If the user has already plussed the post,
        # the post will be updated by removing one from the plus
        # count and removing the user from the array of voters
        # the author of the post will be updated by removing 1
        # from their total plus tally
        # the active user will be updated by removing the post id
        # from their voted posts array

        if post_id in already_voted:
            update_vote = {'$set': {'plusses': current_vote - 1},
                           '$pull': {'users_voted': session['user']}}

            update_author = {'$set': {'plusses': post_creator_plusses -
                                      1}}

            update_user = {'$pull': {'voted': post_id}}

            db.users.update_one({'username': session['user']},
                                update_user)
            db.posts.update_one({'_id': ObjectId(post_id)}, update_vote)
            db.users.update_one({'username': author}, update_author)
            return (post_id, 'success')
        else:

            # If the user has not already plussed the post
            # the post will be updated by adding one from the plus
            # count and adding the user to the array of voters
            # the author of the post will be updated by adding
            # 1 to their total plus tally
            # the active user will be updated by adding the post id
            # to their voted posts array

            update_vote = {'$set': {'plusses': current_vote + 1},
                           '$push': {'users_voted': session['user']}}

            update_author = {'$set': {'plusses': post_creator_plusses +
                                      1}}

            update_user = {'$push': {'voted': post_id}}

            db.users.update_one({'username': session['user']},
                                update_user)
            db.posts.update_one({'_id': ObjectId(post_id)}, update_vote)
            db.users.update_one({'username': author}, update_author)
            return (post_id, 'success')
    else:

        # If the users is not signed in they will be presented with
        # a flash message and no update will occur

        alertUser('session')
        return (post_id, 'error')


@app.route('/posts-vote/<post_id>/<page>', methods=['GET', 'POST'])
def posts_vote(post_id, page):
    """
    This view handles a user voting on a post from the
    home page it accepts the post_id of the post
    in order to pass it on to the process vote function

    it accepts the page argument which represents the current
    active paginated page of posts
    in order to reload the page with the correct page of posts open
    """

    vote_status = process_vote(post_id)
    return redirect(url_for('posts',
                            post_id=post_id,
                            page=page,
                            _anchor=post_id))


@app.route('/vote/<post_id>/<pagination_arguments>')
def vote(post_id, pagination_arguments):
    """
    This view handles a user voting on a post from the
    post details page it accepts the post_id of the
    post in order to pass it on to the process vote function

    it accepts the pagination_arguments argument which contains
    the pagination status of the user's location before they
    opened the post details view. These details are passed
    through so that when the user closes the post details page
    they will be redirected to
    their previous location with the correct page of posts open.
    """

    vote_status = process_vote(post_id)
    split_pagination_arguments = pagination_arguments.replace(
        '[', '').replace(']', '').replace("'", '').replace(
        ' ', '').split(',')
    if len(split_pagination_arguments) == 3:
        return redirect(url_for(
            'account_post_details',
            post_id=post_id,
            active_tab=split_pagination_arguments[2],
            user_plus_page=split_pagination_arguments[1],
            user_post_page=split_pagination_arguments[0],
            _anchor=post_id,
            ))
    else:
        return redirect(url_for('post_details', post_id=post_id,
                        post_page=int(split_pagination_arguments[0])))


@app.route('/comment/<post_id>/<pagination_arguments>', methods=['GET',
           'POST'])
def add_comment(post_id, pagination_arguments):
    """
    This view handles the creation of comments

    Accepted arguments:
        post_id: this contains the unique objectid value of the post
         that is being commented on
        pagination_arguments: this contains the pagination status
         of the user's location before they
        opened the post details view

    The comment's details are taken from the user's request form and
     added to a new comment object that is then added to
     the relevant record's comment array
    """

    split_pagination_arguments = pagination_arguments.replace(
        '[', '').replace(']', '').replace("'", '').replace(
        ' ', '').split(',')
    if 'user' in session:
        if request.method == 'POST':

            # Finds the relevant post and creates a unique comment id

            post = db.posts.find_one({'_id': ObjectId(post_id)})
            comment_id = str(post_id) + '/' + str(post['total_comments'] +
                                                  1)

            # Takes the comment content from the request form,
            # automatically generates other values

            comment = {
                'comment_id': comment_id,
                'comment_content': request.form.get('comment_content'),
                'author': session['user'],
                'post_date': datetime.now().strftime('%m/%d/%Y, %H:%M:%S'),
                'attached_post': post_id,
                }

            # Updates user and post by adding the comment
            # object to their comments array and increasing
            # their comments count by 1

            user = db.users.find_one({'username': session['user']})
            user_comments_made = user['comments_made']
            update_post = {'$push': {'comments': comment},
                           '$set': {'total_comments': post['total_comments'] +
                                    1}}

            update_user = {'$push': {'comments': comment},
                           '$set': {'comments_made': user_comments_made +
                                    1}}

            db.users.update_one({'username': session['user']},
                                update_user)
            db.posts.update_one({'_id': ObjectId(post_id)}, update_post)
            flash('Comment Successfully Added')

            # The pagination arguments are used to determine which
            # page the user was on previous to opening post details view
            # and then redirects the browser there using the
            # relevant pagination parameters

            if len(split_pagination_arguments) == 3:
                return redirect(url_for(
                    'account_post_details',
                    post_id=post_id,
                    active_tab=split_pagination_arguments[2],
                    user_plus_page=split_pagination_arguments[1],
                    user_post_page=split_pagination_arguments[0],
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
                user_plus_page=split_pagination_arguments[1],
                user_post_page=split_pagination_arguments[0],
                _anchor=post_id,
                ))
        else:
            return redirect(url_for('post_details', post_id=post_id,
                            post_page=int(split_pagination_arguments[0])))


@app.route('/delete-post/<post_id>/<pagination_arguments>')
def delete_post(post_id, pagination_arguments):
    """
    This view handles the deletion of posts and the
     updating of all relevant records

    It removes the comment object from it's parent post's
     comments array, the removes the voting and commenting
     record for that post from all users voted and comment arrays

    Accepted arguments:
        post_id: this contains the unique objectid value of the
         post that is being commented on
        pagination_arguments: this contains the pagination
         status of the user's location when they deleted the post and
        they are used to return the user to the correct location
         with the correct pagination conditions
    """

    db.posts.remove({'_id': ObjectId(post_id)})

    # The funciton pulls the vote record from the user's voted post array

    db.users.update({}, {'$pull': {'voted': {'$in': [post_id]}}}, True)

    # It removes the comments attached to the deleted post
    # from the user's comments array

    db.users.update({},
                    {'$pull': {'comments': {'attached_post': post_id}}},
                    True)
    flash('Post Deleted')
    split_pagination_arguments = pagination_arguments.replace(
        '[', '').replace(']', '').replace("'", '').replace(
        ' ', '').split(',')
    if len(split_pagination_arguments) == 3:
        return redirect(url_for('account', post_id='None',
                        active_tab=split_pagination_arguments[2],
                        user_plus_page=split_pagination_arguments[1],
                        user_post_page=split_pagination_arguments[0]))
    else:
        return redirect(url_for('posts',
                        page=split_pagination_arguments[0]))


def process_post_details(post_id):
    """
    This function finds a post using it's unique id an then
     returns the details along with the full list of user records in
     order to supply the avatars used by each post

    If the user is signed in it will also find their record
     to determine whether the user has voted for the
     post or not
    """

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


@app.route('/post-details/<post_id>/<post_page>')
def post_details(post_id, post_page):
    """
    This view handles the rendering of the post details
     page from the home page

    Accepted arguments:
        post_id: this contains the unique objectid value of
         the post that is being opened
        post_page: this contains the pagination status of
         the home page when the user opened the post details view

    The post id will be used to find the post's record
     in the posts collection and then access it's details

    Routing parameters is the array returned from the
     process_post_details function. It contains the data necessary
    to render the page depending on whether the user is signed in or not
    """

    if db.posts.find_one({'_id': ObjectId(post_id)}):
        routing_parameters = process_post_details(post_id)
        if 'user' in session:
            return render_template(
                'post-details.html',
                post=routing_parameters[0],
                user_plusses=routing_parameters[1],
                users=routing_parameters[2],
                user=routing_parameters[3],
                page=post_page,
                )
        return render_template('post-details.html',
                               post=routing_parameters[0],
                               users=routing_parameters[1],
                               page=post_page)
    else:
        return redirect(url_for('posts', post_page=post_page))


@app.route('/account-vote/<active_tab>/<post_id>'
           '/<user_plus_page>/<user_post_page>', methods=['GET', 'POST'])
def account_vote(
                 post_id,
                 active_tab,
                 user_plus_page,
                 user_post_page,
                 ):
    """
    This view handles the process of voting when the user is on
     the account page

    Accepted arguments:
        post_id: this contains the unique objectid value of the post
         that is being voted on, this value is passed into
        the process_vote_function
        active_tab: this contains the current value of which account
         tab is open, posts or plussed
        user_post_page: contains the current value of the paginated
         page of user posts
        user_plus_page: contains the current value of the paginated
         page of user plussed posts

    The pagination status arguments are used to reload the page
     with the correct pages open maintain positive user experience
    """

    vote_status = process_vote(post_id)
    return redirect(url_for(
        'account',
        post_id=post_id,
        active_tab=active_tab,
        user_plus_page=user_plus_page,
        user_post_page=user_post_page,
        _anchor=post_id,
        ))


@app.route('/account-post-details/<active_tab>'
           '/<post_id>/<user_plus_page>/<user_post_page>')
def account_post_details(
                         post_id,
                         active_tab,
                         user_plus_page,
                         user_post_page,
                         ):
    """
    This view handles the rendering of the post details page from
     the account page

    Accepted arguments:
        post_id: this contains the unique objectid value of the post that
         is being opened
        active_tab: this contains the current value of which account tab is
         open, posts or plussed
        user_post_page: contains the current value of the paginated page of
         user posts
        user_plus_page: contains the current value of the paginated page of
         user plussed posts

    The post id will be used to find the post's record in the posts
     collection and then access it's details

    Routing parameters is the array returned from the process_post_details
     function. It contains the data necessary
    to render the page depending on whether the user is signed in or not

    The three pagination arguments are passed through to enable
     the accout page to reload with the correct
    pagination and tab status when the post details are closed
    """

    if db.posts.find_one({'_id': ObjectId(post_id)}):
        routing_parameters = process_post_details(post_id)
        if 'user' in session:
            return render_template(
                'post-details.html',
                active_tab=active_tab,
                post=routing_parameters[0],
                user_plusses=routing_parameters[1],
                users=routing_parameters[2],
                user=routing_parameters[3],
                user_plus_page=user_plus_page,
                user_post_page=user_post_page,
                )
        return render_template(
            'post-details.html',
            active_tab=active_tab,
            post=routing_parameters[0],
            users=routing_parameters[1],
            user_plus_page=user_plus_page,
            user_post_page=user_post_page,
            )
    else:
        return redirect(url_for('account', post_id='None',
                        active_tab=active_tab,
                        user_plus_page=user_plus_page,
                        user_post_page=user_post_page))


@app.route('/account/<post_id>/<active_tab>', methods=['GET', 'POST'])
def account(post_id, active_tab):
    """
    This view handles the rendering of the account page

    It uses the session user's attribute to find the user record of the user
    It then finds all posts where the user is the author and all posts
    that the user has voted for

    It will generate paginated lists for those two arrays and an individual
    pagination instance for both

    The arguments passed to the render of the page are:
            active tab either posts or plusses specified,
            the users username,
            a list of all user records for finding the avatar needed to display
            on each post, an the respective pagination parameters for both
            the posts list and the plusses list
    """

    if 'user' in session:
        user = db.users.find_one({'username': session['user']})
        username = user['username']

        users = list(db.users.find())

        # Finds the list of posts that a user has liked
        # to be used to display a check or plus icon

        plussed_posts = []
        plusses = db.users.find_one({'username': session['user']
                                     })['voted']
        for post in plusses:
            plussed_posts.append(ObjectId(post))

        # Finds the list of posts that a user has liked to display on profile

        userPlusses = []
        posts_plussed = \
            list(db.posts.find({'users_voted': session['user']
                                }).sort('post_date', -1))
        for post in posts_plussed:
            if post['author'] != session['user']:
                userPlusses.append(post)
            else:
                pass

        # Finds the list of posts authored by user

        userPosts = list(db.posts.find({'author': session['user']
                                        }).sort('post_date', -1))

        # Defining pagination parameters for the plusses list
        # page parameter represents the active page
        # per page parameter represents the number of posts to display per apge
        # offset represents the posts needed to be displayed on each page
        # i.e page 2 will be 10 - 19 page 4 will be 30 - 39 ...

        (plussesPage, per_page, offset) = \
            get_page_args(page_parameter='user_plus_page',
                          per_page_parameter='per_page')

        # Total length of plussed posts used to determine
        # the total number of pages

        totalPlussedPosts = len(userPlusses)

        # pagination plussed list is the total paginated list of plussed posts

        pagination_plussed_list = get_posts(posts=userPlusses,
                                            offset=offset,
                                            per_page=per_page)

        # Pagination contains the pagination details, and data for navigation

        pagination_plussed = Pagination(page_parameter='user_plus_page',
                                        user_plus_page=plussesPage,
                                        per_page=per_page,
                                        total=totalPlussedPosts,
                                        css_framework='bootstrap4')

        # As above but for user authored posts

        (postsPage, per_page, offset) = \
            get_page_args(page_parameter='user_post_page',
                          per_page_parameter='per_page')

        totalUserPosts = len(userPosts)
        pagination_posts_list = get_posts(posts=userPosts,
                                          offset=offset,
                                          per_page=per_page)
        pagination_posts = Pagination(page_parameter='user_post_page',
                                      user_post_page=postsPage,
                                      per_page=per_page,
                                      total=totalUserPosts,
                                      css_framework='bootstrap4')

        # if the post id passed in is = None then the
        # page will render on the default tab

        if post_id == 'None':
            return render_template(
                'account.html',
                active_tab=active_tab,
                username=username,
                users=users,
                userPlusses=pagination_plussed_list,
                plussed_posts=plussed_posts,
                pagination_plussed=pagination_plussed,
                user_post_page=postsPage,
                user=user,
                userPosts=pagination_posts_list,
                user_plus_page=plussesPage,
                per_page=per_page,
                pagination_posts=pagination_posts,
                )
        else:

            # if the post id passed in is defined
            # if the post represented by the post id is
            # authored by the user the page will load with the posts tab active

            post = db.posts.find_one({'_id': ObjectId(post_id)})
            if post['author'] == session['user']:
                return render_template(
                    'account.html',
                    username=username,
                    users=users,
                    userPlusses=pagination_plussed_list,
                    plussed_posts=plussed_posts,
                    pagination_plussed=pagination_plussed,
                    user_post_page=postsPage,
                    active_tab='posts',
                    user=user,
                    userPosts=pagination_posts_list,
                    user_plus_page=plussesPage,
                    per_page=per_page,
                    pagination_posts=pagination_posts,
                    _anchor='#' + post_id,
                    )
            else:

                # if the post id passed in represents a post not authored by
                # the user then the active page will be plusses

                return render_template(
                    'account.html',
                    username=username,
                    users=users,
                    userPlusses=pagination_plussed_list,
                    plussed_posts=plussed_posts,
                    pagination_plussed=pagination_plussed,
                    user_post_page=postsPage,
                    active_tab='plusses',
                    user=user,
                    userPosts=pagination_posts_list,
                    user_plus_page=plussesPage,
                    per_page=per_page,
                    pagination_posts=pagination_posts,
                    _anchor='#' + post_id,
                    )
    else:
        return redirect(url_for('sign_in'))


def alertUser(key):
    """
    This function sends a flash message to the user if they try
    and take an action without being logged in
    """

    if key == 'session':
        flash('You must be signed in to vote')
    return 'Ok'


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=os.environ.get('DEBUG'))
