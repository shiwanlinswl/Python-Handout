from flask import current_app, jsonify
from flask_script import Manager
from flask_migrate import MigrateCommand, Migrate
from info import create_app, db
from info import models
from info.models import User
from info.response_code import RET

app = create_app("development")

# 此时导入是为了加载到的redis对象数据不为None,现在的redis在函数内部已经获取了数据,None没有set属性
from info import redis_store

# 6.创建数据库管理对象,将app交给管理对象管理
manager = Manager(app)

# 7.数据库迁移初始化
migrate = Migrate(app, db)

# 8.添加迁移命令和数据类型
manager.add_command("db", MigrateCommand)


# 9.自定义创建管理员用户的方法
@manager.option("-n", "-name", dest="name")
@manager.option("-p", "-password", dest="password")
def createsuperuser(name, password):
    # 1.获取参数
    # 2.参数检验
    if not all([name, password]):
        print("参数不足")
        return
    # 3.创建管理员用户对象
    admin_user = User()
    admin_user.mobile = name
    admin_user.password = password
    admin_user.nick_name = name
    # 代表创建一个管理员用户
    admin_user.is_admin = True

    try:
       db.session.add(admin_user)
       db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        print("保存数据库异常")

    print("创建管理员用户成功")


if __name__ == '__main__':
    # 使用manager对象启动程序代替app.run(debug=True)
    manager.run()
