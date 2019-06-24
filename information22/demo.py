import random
import datetime
from manage import app
from info import db
from info.models import User


def add_test_users():
    # 用户列表
    users = []
    # 当前时间
    now = datetime.datetime.now()
    # 生成10000个用户
    for num in range(0, 10000):
        try:
            user = User()
            user.nick_name = "%011d" % num
            user.mobile = "%011d" % num
            user.password_hash = "pbkdf2:sha256:50000$SgZPAbEj$a253b9220b7a916e03bf27119d401c48ff4a1c81d7e00644e0aaf6f3a8c55829"
            # 用户活跃量   =    当前时间   -    (0~31天中间的随机秒数)   ：2018-12-5 ～ 2019-1-5 任意一个时间点登录
            user.last_login = now - datetime.timedelta(seconds=random.randint(0, 2678400))
            users.append(user)
            print(user.mobile)
        except Exception as e:
            print(e)
    # 手动开启应用上下文
    with app.app_context():
        # 往数据库添加用户对象
        db.session.add_all(users)
        db.session.commit()
    print('OK')

if __name__ == '__main__':
    add_test_users()