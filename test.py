import os
import secrets
from PIL import Image
from flask import render_template, flash, redirect, url_for, request, abort
from playhouse.flask_utils import get_object_or_404, object_list
from vladblog import app, db, flask_bcrypt
from vladblog.models import User, Post
from vladblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from flask_login import login_user, current_user, logout_user, login_required


if __name__ == '__main__':
    username='Vladislave'
    user = get_object_or_404(User.select(), User.username == username)
    print(user.username)
    posts = Post.select().where(Post.user_id == user)
    for post in posts:
        print(post.title)
