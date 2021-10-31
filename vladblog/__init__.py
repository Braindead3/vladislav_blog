from flask import Flask
from peewee import SqliteDatabase
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a37a33cf9d5e105081c05abb60760fd2'
db = SqliteDatabase('vladblog/Flask_blog.db', pragmas={'foreign_keys': 1})
flask_bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from vladblog import routes
