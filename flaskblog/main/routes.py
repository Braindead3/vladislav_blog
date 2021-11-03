from flask import Blueprint, request, render_template
from playhouse.flask_utils import object_list
from flaskblog.models import Post

main = Blueprint('main', __name__)


@main.route('/')
@main.route('/home')
def home():
    posts = Post.select().order_by(Post.date_posted.desc())
    return object_list('home.html', query=posts, context_variable='posts', paginate_by=5, title='Home')


@main.route('/about')
def about():
    return render_template('about.html', title='About')
