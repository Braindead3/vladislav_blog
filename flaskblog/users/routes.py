from flask import (Blueprint, url_for, redirect, flash, render_template, request)
from flask_login import current_user, login_user, logout_user, login_required
from playhouse.flask_utils import get_object_or_404, object_list
from flaskblog import flask_bcrypt
from flaskblog.models import User, Post
from flaskblog.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from flaskblog.users.utils import save_picture, send_reset_email

users = Blueprint('users', __name__)


@users.route('register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = flask_bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        user.save()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@users.route('login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_or_none(User.email == form.email.data)
        if user and flask_bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Log In unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html', title='Login', form=form)


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    image_file_src = url_for('static', filename=f'profile_pics/{current_user.image_file}')
    form = UpdateAccountForm()
    if form.validate_on_submit():
        updated_user: User = User.get_by_id(current_user.id)
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            updated_user.image_file = picture_file
        updated_user.username = form.username.data
        updated_user.email = form.email.data
        updated_user.save()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('Account.html', title='Account', image_file_src=image_file_src, form=form)


@users.route('/user/<string:username>')
def user_posts(username):
    user = get_object_or_404(User.select(), User.username == username)
    posts = Post.select().where(Post.user_id == user).order_by(Post.date_posted.desc())
    return object_list('user_posts.html', query=posts, context_variable='posts', paginate_by=5, title='Home', user=user,
                       posts_count=posts.count())


@users.route('/reset_password', methods=['GET', 'POST'])
def send_reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.get(User.email == form.email.data)
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset password', form=form)


@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user: User = User.verify_reset_token(token)
    if user is None:
        flash('This is invalid token or expired token', 'warning')
        return redirect(url_for('users.send_reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = flask_bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        user.save()
        flash(f'Your password has been updated! You are now able to log in.', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset password', form=form)
