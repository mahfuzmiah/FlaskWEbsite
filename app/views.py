from flask import render_template, flash, redirect, session, url_for, request, g

from app import app, db, admin
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from flask import jsonify
from .models import *
#admin.add_view(ModelView(Student, db.session))
from flask_login import login_user, logout_user, current_user, login_required
from .forms import *
from flask import g, session
import json

@app.route('/test_replies')
def test_replies():
    try:
        # Create a test user (if not already existing)
        user = User.query.first()  # Assuming there is at least one user in the database
        if not user:
            # Create a new user if none exists (adjust with valid data)
            user = User(username='testuser', email='test@example.com', password_hash='test')
            db.session.add(user)
            db.session.commit()

        # Create a test post
        post = Post(body='This is a test original post', author=user)
        db.session.add(post)
        db.session.commit()

        # Create a test reply
        reply = Post(body='This is a test reply', author=user, reply_id=post.id)
        db.session.add(reply)
        db.session.commit()

        return 'Test post and reply successfully created.'

    except Exception as e:
        return f'An error occurred: {str(e)}'

@app.route('/get_replies/<int:post_id>')
def get_replies(post_id):
    # Fetch replies based on the post_id
    replies = Post.query.filter_by(reply_id=post_id).all()
    return render_template('replies.html', replies=replies)

@app.route("/")
def show():

    if current_user.is_authenticated:
        # User is logged in, provide the home page functionality
        # For example, you can fetch user-specific data here
        return redirect('homepage')
    else:
        # User is not logged in, redirect to the login page
        return redirect('login')
    
@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    # Ensure the current user is the author of the post
    if post.author.id != current_user.id:
        flash("You don't have permission to edit this post.", "danger")
        return redirect(url_for('homepage'))

    form = PostForm(obj=post)  # Pre-fill form with post data
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.commit()
        flash("Post updated successfully", "success")
        return redirect(url_for('profile', username=current_user.username))

    return render_template('edit_post.html', form=form, post_id=post_id)

@app.route('/delete_post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    # Ensuring the current user is the author of the post
    if post.author.id != current_user.id:
        flash("You don't have permission to delete this post.", "danger")
        return redirect(url_for('homepage'))

    # Query and delete all replies to the post
    replies = Post.query.filter_by(reply_id=post.id).all()
    for reply in replies:
        db.session.delete(reply)

    # Now delete the original post
    db.session.delete(post)
    db.session.commit()
    flash("Post and its replies deleted successfully", "success")
    return redirect(url_for('profile', username=current_user.username))

@app.route('/reply/<int:post_id>', methods=['GET', 'POST'])
@login_required
def reply(post_id):
    original_post = Post.query.get_or_404(post_id)
    
    if request.method == 'POST':
        reply_body = request.form.get('reply_body')
        
        # Check if the reply body is not empty
        if not reply_body:
            flash('Reply cannot be empty.', 'error')
            return redirect(url_for('reply', post_id=post_id))

        # Create a new Post object for the reply
        reply = Post(body=reply_body, author=current_user, reply_id=original_post.id)

        # Add the reply to the database
        db.session.add(reply)
        db.session.commit()

        flash('Your reply has been posted.', 'success')
        return redirect(url_for('homepage'))  # or redirect to a different page as needed

    return render_template('reply.html', original_post=original_post)

@app.route('/homepage')
@login_required
def homepage():
    # Query only original posts (not replies)
    all_posts = Post.query.filter(Post.reply_id.is_(None)).order_by(Post.timestamp.desc()).all()


    # Query posts from friends
    subquery = db.session.query(followers.c.followed_id.label("friend_id")).filter(followers.c.follower_id == current_user.id).subquery()
    friend_ids = [f.friend_id for f in db.session.query(subquery).all()]
    for post in all_posts:
        post.is_liked_by_current_user = db.session.query(liked_by).filter(
            liked_by.c.user_id == current_user.id,
            liked_by.c.post_id == post.id
        ).first() is not None

    # Query only original posts from friends
    friend_posts = Post.query.filter(Post.user_id.in_(friend_ids), Post.reply_id.is_(None)).order_by(Post.timestamp.desc()).all()


    return render_template('home.html', title='homepage', all_posts=all_posts, friend_posts=friend_posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            return redirect('homepage')
        else:
            flash('Invalid username or password')
    return render_template('login.html', title='Login', form=form)

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    form = RegistrationForm()
    if form.validate_on_submit():
        password = form.password.data

        # Check if passwords match
        if password != form.confirm_password.data:
            flash('Passwords do not match. Please try again.', 'danger')
            return render_template('create_account.html', title='Register', form=form)

        # Check for password length
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return render_template('create_account.html', title='Register', form=form)

        # Check for presence of capital letters
        if not any(char.isupper() for char in password):
            flash('Password must contain at least one uppercase letter.', 'danger')
            return render_template('create_account.html', title='Register', form=form)

        # Check if username already exists
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user is not None:
            flash('Username already exists. Please choose a different one.', 'warning')
            return render_template('create_account.html', title='Register', form=form)

        # Password hashing and user creation
        hashed_password = generate_password_hash(password)
        user = User(username=form.username.data.lower(), email=form.email.data, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))

    return render_template('create_account.html', title='Register', form=form)

@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow_user(username):
    user_to_follow = User.query.filter_by(username=username).first_or_404()

    # Check if the user is trying to follow themselves
    if current_user.id == user_to_follow.id:
        flash("You cannot follow yourself.", "danger")
        return redirect(url_for('profile', username=username))

    # Check if the current user is already following the user_to_follow
    existing_follow = db.session.query(followers).filter(
        followers.c.follower_id == current_user.id,
        followers.c.followed_id == user_to_follow.id
    ).first()
    if existing_follow:
        # If relationship exists, remove it (unfollow)
        db.session.execute(
            followers.delete().where(
                followers.c.follower_id == current_user.id,
                followers.c.followed_id == user_to_follow.id
            )
        )
        db.session.commit()
        flash("You have unfollowed " + username, "success")
    else:
        # If relationship doesn't exist, create it (follow)
        new_follow = followers.insert().values(
            follower_id=current_user.id,
            followed_id=user_to_follow.id
        )
        db.session.execute(new_follow)
        db.session.commit()
        flash("You are now following " + username, "success")

    return redirect(url_for('homepage'))



@app.route('/profile/<username>', methods=['GET', 'POST'])
@login_required
def profile(username):
    if username==current_user.username:
        is_current_user=True
    else:
        is_current_user=False

    user = User.query.filter_by(username=username).first_or_404()
    
    form = ChangePasswordAndEmail()

    if form.validate_on_submit():
        # Update username and email only if they are changed
        if user.username != form.username.data:
            existing_user = User.query.filter_by(username=form.username.data).first()
            if existing_user:
                flash('Username already exists. Please choose a different one.', 'warning')
                return redirect(url_for('profile', username=user.username))
            user.username = form.username.data

        if user.email != form.email.data:
            existing_email = User.query.filter_by(email=form.email.data).first()
            if existing_email:
                flash('Email already in use. Please choose a different one.', 'warning')
                return redirect(url_for('profile', username=user.username))
            user.email = form.email.data

        # Update password only if provided
        if form.password.data:
            user.password = generate_password_hash(form.password.data)

        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('profile', username=user.username))

    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email

    posts = Post.query.filter_by(user_id=user.id, reply_id=None).all()
    for post in posts:
        post.is_liked_by_current_user = db.session.query(liked_by).filter(
            liked_by.c.user_id == current_user.id,
            liked_by.c.post_id == post.id
        ).first() is not None

    return render_template('profile.html', user=user, posts=posts, is_current_user=is_current_user, form=form)


@app.route('/search')
@login_required
def search():
    query = request.args.get('q')
    results = []
    if query:
        results = User.query.filter(User.username.ilike(f'%{query}%')).all()

    form = SearchForm() 
    return render_template('search.html', form=form, query=query, results=results, user=current_user)

@app.route("/logout")
@login_required
def logout():
    logout_user()  # Flask-Login logout
    return redirect(url_for('login'))

@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('homepage'))
    return render_template('create_post.html', title='Create Post', form=form)

@app.route('/like/<int:post_id>', methods=['POST'])
@login_required
def like(post_id):
    post = Post.query.get_or_404(post_id)
    if post is None:
        return jsonify({'message': 'Post not found'}), 404

    user_id = current_user.id
    existing_like = db.session.query(liked_by).filter(
        liked_by.c.user_id == user_id,
        liked_by.c.post_id == post_id
    ).first()

    if existing_like:
        # User has already liked this post, so unlike it
        db.session.execute(liked_by.delete().where(
            liked_by.c.user_id == user_id,
            liked_by.c.post_id == post_id
        ))
        post.likes_count -= 1
        db.session.commit()
        message = 'You have unliked the post.'
        is_liked = False  # Set is_liked to False as the post is unliked now
    else:
        # User has not liked this post yet, so like it
        new_like = liked_by.insert().values(
            user_id=user_id,
            post_id=post_id
        )
        post.likes_count += 1
        db.session.execute(new_like)
        db.session.commit()
        message = 'You have liked the post.'
        is_liked = True  # Set is_liked to True as the post is liked now
        


    return jsonify({'message': message, 'likes_count': post.likes_count, 'is_liked': is_liked})
