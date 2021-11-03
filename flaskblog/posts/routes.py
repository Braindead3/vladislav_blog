from flask import (Blueprint, flash, render_template, redirect, url_for, abort, request)
from flask_login import login_required, current_user
from playhouse.flask_utils import get_object_or_404
from flaskblog.models import Post
from flaskblog.posts.forms import PostForm

posts = Blueprint('posts', __name__)


@posts.route('/posts/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, user_id=current_user)
        post.save()
        flash('Your posts has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='New posts', form=form, legend='New Post')


@posts.route('/posts/<int:post_id>', methods=['GET', 'POST'])
@login_required
def selected_post(post_id):
    post = get_object_or_404(Post.select(), Post.id == post_id)
    return render_template('post.html', title=post.title, post=post)


@posts.route('/posts/<int:post_id>/update', methods=['GET', 'POST'])
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
        flash('Your posts has been updated!', 'success')
        return redirect(url_for('posts.selected_post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update posts', form=form, legend='Update')


@posts.route('/posts/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = get_object_or_404(Post.select(), Post.id == post_id)
    if post.user_id != current_user:
        abort(403)
    post.delete_instance()
    flash('Your posts has been deleted!', 'success')
    return redirect(url_for('main.home'))
