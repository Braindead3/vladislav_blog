import os
import secrets
from PIL import Image
from flask import render_template, flash, redirect, url_for, request, abort
from playhouse.flask_utils import get_object_or_404, object_list
from vladblog import app, db, flask_bcrypt
from vladblog.models import User, Post
from vladblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from flask_login import login_user, current_user, logout_user, login_required


@app.route('/')
@app.route('/home')
def home():
    posts = Post.select()
    return object_list('home.html', query=posts, context_variable='posts', paginate_by=2, title='Home')


@app.route('/about')
def about():
    return render_template('about.html', title='About')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = flask_bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        user.save()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_or_none(User.email == form.email.data)
        if user and flask_bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Log In unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, file_ext = os.path.splitext(form_picture.filename)
    picture_file_name = random_hex + file_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_file_name)

    output_size = (125, 125)
    resized_image = Image.open(form_picture)
    resized_image.thumbnail(output_size)
    resized_image.save(picture_path)

    prev_picture = os.path.join(app.root_path, 'static/profile_pics', current_user.image_file)
    if os.path.exists(prev_picture):
        os.remove(prev_picture)

    return picture_file_name


@app.route('/account', methods=['GET', 'POST'])
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
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('Account.html', title='Account', image_file_src=image_file_src, form=form)


@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, user_id=current_user)
        post.save()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New post', form=form, legend='New Post')


@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def selected_post(post_id):
    post = get_object_or_404(Post.select(), Post.id == post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = get_object_or_404(Post.select(), Post.id == post_id)
    if post.user_id != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.save()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('selected_post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update post', form=form, legend='Update')


@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = get_object_or_404(Post.select(), Post.id == post_id)
    if post.user_id != current_user:
        abort(403)
    post.delete_instance()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))
