from flask import Flask
from playhouse.sqliteq import SqliteQueueDatabase
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flaskblog.config import Config
import atexit

db = SqliteQueueDatabase('flaskblog/Flask_blog.db', use_gevent=False, autostart=True, queue_max_size=64,
                         results_timeout=5.0, pragmas={'foreign_keys': 1})
flask_bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    flask_bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from flaskblog.users.routes import users
    from flaskblog.posts.routes import posts
    from flaskblog.main.routes import main
    from flaskblog.errors.handlers import errors
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    return app


@atexit.register
def _stop_worker_threads():
    db.stop()
