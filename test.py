import os


if __name__ == '__main__':
    # username='Vladislave'
    # user = get_object_or_404(User.select(), User.username == username)
    # print(user.username)
    # posts = Post.select().where(Post.user_id == user)
    # for post in posts:
    #     print(post.title)
    print('test running')
    print(os.environ.get('USER_EMAIL'))
    print(os.environ.get('USER_PASSWORD'))

