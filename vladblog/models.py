from peewee import *
from datetime import datetime
from vladblog import db, login_manager, app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(int(user_id))


class BaseModel(Model):
    id = PrimaryKeyField(unique=True)

    class Meta:
        database = db
        order_by = 'id'


class User(BaseModel, UserMixin):
    username = CharField(max_length=20, unique=True, null=False)
    email = CharField(max_length=20, unique=True, null=False)
    image_file = CharField(max_length=20, null=False, default='default.jpg')
    password = CharField(max_length=60, null=False)

    def get_reset_token(self, expire_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expire_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        user_id = s.loads(token).get('user_id')
        if user_id is None:
            return None
        return User.get_by_id(user_id)

    def __repr__(self):
        return f'User("{self.username}","{self.email}","{self.image_file}")'

    class Meta:
        db_table = 'Users'


class Post(BaseModel):
    title = CharField(max_length=20, unique=True, null=False)
    date_posted = DateTimeField(null=False, default=datetime.utcnow())
    content = TextField(null=False)
    user_id = ForeignKeyField(User, backref='posts', null=False)

    def __repr__(self):
        return f'Post("{self.title}","{self.date_posted}")'

    class Meta:
        db_table = 'Posts'


def create_database():
    with db:
        db.create_tables([User, Post])
