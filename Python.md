## Python 知识点

#### 字符串编码

##### 编码概念

将计算机的数据按照人类可以理解的方式展现的规则

二进制转十进制：int()

十进制转ASCll字符：chr()

##### 编码发展史

**ASCII码 0~127**（初期美国发明，只考虑了字母）===>**Latin-1码 0~256**（欧洲普及，新增西方文字）===>各国编码如：日本：Shift-JIS、简体中文：gb2312>>>gbk>>>gb18030、繁体中文：Big5(计算机普及全球，各国有各国的编码，乱码：二进制和编码表不匹配)===>**Unicode**(国际标准组织制定统一编码)===>**Utf-8**(可变长的Unicode,对Unicode升级)

一般情况下网页代码和Linux终端编码都是Utf-8

注意:unicode常作为中间转码;Unicode包含Utf-8,包含其他所有编码

任何编程语言、任何操作系统、任何编码都可以和Unicode转换

编码：encode()===>将Unicode编码成想要成为的编码

解码：decode()===>将你的编码解码成Unicode

##### Python中字符串和编码

byte类型：表示所有非Unicode类型数据（gbk、utf-8、jpg、avi、mp3）

str类型：指表示Unicode类型数据

##### python2和python3编码区别

python2:ASCII(当时还没有Unicode)

python3:Utf-8

查看步骤

import sys

sys.getdefaultencording()

##### Windows和Linux系统编码区别

Windows：GBK

##### Linux：UTF-8

### 安装虚拟环境

安装到默认.virtualenv路径

```
sudo pip install virtualenv  # 使电脑具有安装虚拟环境的能力
sudo pip install virtualenvwrapper
-p 指定python版本，默认是python2
mkvirtualenv -p python3 虚拟环境名称
```

安装到指定路径

```
sudo pip install virtualenv
virtualenv -p python3 虚拟环境名称  # 安装虚拟环境
source 虚拟环境名/bin/activate  # 进入虚拟环境
```

 **logging 模块的使用方式介绍**

- loggers 提供应用程序代码直接使用的接口
- handlers 用于将日志记录发送到指定的目的位置
- filters 提供更细粒度的日志过滤功能，用于决定哪些日志记录将会被输出（其它的日志记录将会被忽略）
- formatters 用于控制日志信息的最终输出格式
- 再次git status就不会显示.idea文件要添加

```python
# 设置日志的记录等级
logging.basicConfig(level=logging.DEBUG) # 调试debug级
# 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
# 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（flask app使用的）添加日志记录器
logging.getLogger().addHandler(file_log_handler)
```

```python
LOGGING = {  # Django中settings文件配置日志
    'version': 1,
    'disable_existing_loggers': False,  # 是否禁用已经存在的日志器
    'formatters': {  # 日志信息显示的格式
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(lineno)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(module)s %(lineno)d %(message)s'
        },
    },
    'filters': {  # 对日志进行过滤
        'require_debug_true': {  # django在debug模式下才输出日志
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {  # 日志处理方法
        'console': {  # 向终端中输出日志
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {  # 向文件中输出日志
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(os.path.dirname(BASE_DIR), "logs/meiduo.log"),  # 日志文件的位置
            'maxBytes': 300 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose'
        },
    },
    'loggers': {  # 日志器
        'django': {  # 定义了一个名为django的日志器
            'handlers': ['console', 'file'],  # 可以同时向终端与文件中输出日志
            'propagate': True,  # 是否继续传递日志信息
            'level': 'INFO',  # 日志器接收的最低日志级别
        },
    }
}
```

## Django框架

安装工程

django-admin startproject 工程名

安装子应用

python manage startapp 应用名

路由匹配范围

ip:端口  之后 查询参数？之前 

### Djnago静态文件

##### 所在位置

静态文件可以放在项目**根目录**下，也可以放在**应用的目录**下，由于有些静态文件在项目中是通用的，所以推荐放在项目的根目录下，方便管理。

##### 静态文件参数

- **STATICFILES_DIRS：** 存放查找静态文件的目录
- **STATIC_URL：** 访问静态文件的URL前缀

示例：当在项目**根目录**下创建static_file静态文件目录时，需要在项目settings文件中配置如下

```
STATIC_URL = "static"  # 添加静态文件前缀
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static_files'),  # 拼接静态文件路径，可配置多个路径，请求时依次匹配
]
```

此时static_file中静态文件的访问url为：网址/static/文件路径

如: 127.0.0.1:8000/**static**/index.html

### django请求传参

|  传参方式  |         示例          |  Django获取  |       DRF获取        | 请求方式 |
| :--------: | :-------------------: | :----------: | :------------------: | -------- |
|  url路径   | /weather/beijing/2018 |    正则组    |        正则组        | GET      |
| 查询字符串 |   /qs/?a=1&b=2&a=3    | request.GET  | request.query_params | GET/POST |
|            |         表单          | request.POST |     request.data     | GET/POST |
|   请求体   |        非标单         | request.body |     request.data     | GET      |
|   请求头   |                       | request.META |                      |          |

```python
url(r'^weather/(?P<city>[a-z]+)/(?P<year>\d{4})/$', views.weather),
```

?P<city>:给路径参数指定别名

路径匹配范围：ip端口之后，？（查询参数）之前

静态文件：配置文件中配置静态文件访问路径STATIC_URL

请求体给表单：json格式

提取：request.body   返回的是json二进制字符串类型

解码：reques.body.decode()  为字符串

转换json字典：json.loads(reques.body.decode()) 

类视图和函数视图的区别

视图写法：

```python
from django.views.generic import View

class RegisterView(View):
    """类视图：处理注册"""

    def get(self, request):
        """处理GET请求，返回注册页面"""
        return render(request, 'register.html')

    def post(self, request):
        """处理POST请求，实现注册逻辑"""
        return HttpResponse('这里实现注册逻辑')
```

路由定义：

```python
urlpatterns = [
    # 视图函数：注册
    # url(r'^register/$', views.register, name='register'),
    # 类视图：注册
    url(r'^register/$', views.RegisterView.as_view(), name='register'),
]
```

### 日志用法

1. settings.py文件中配置LOGGING = {}
2. 定义日志输出器名称为django
   'loggers': {  # 日志器
   ​        'django': {  # 定义了一个名为django的日志器
   ​            'handlers': ['console', 'file'],  # 可以同时向终端与文件中输出日志
   ​            'propagate': True,  # 是否继续传递日志信息
   ​            'level': 'INFO',  # 日志器接收的最低日志级别
   ​        },
   ​    }
3. 导入日志模块：import logging
4. 获取在配置文件中定义的logger，用来记录日志:    logger = logging.getLogger('django')
5. 输出日志：logger.info(输出内容)

### 设计接口的思路

- 分析要实现的业务逻辑，将每一个子业务当做一个接口来设计；
- 分析接口的功能任务，明确接口的访问方式和返回数据；

1. 接口的请求方式，如get、post、put
2. 接口的url路径定义
3. 需要前端发送的数据及数据格式（路径参数、查询字符串、请求体表单、json）
4. 返回给前端的数据及格式

- 前后端分离的模式下，后端开发人员只需要考虑如何保存哪些数据和返回哪些数据；

### 序列化器

1. 进行数据的校验
2. 对数据对象进行转换
   - 将请求的数据（如：json)转化为模型类对象
   - 操作数据库
   - 将模型对象转换为响应的数据（如：json）

  序列化：模型对象——python字典数据——对应输出

  反序列化：前端后端的数据——校验——validated_data字典——save——模型对象——对应输入

**关联对象嵌套序列化**

1. PrimaryKeyRealatedField:此**字段**将被序列化为关联对象的**主键**
2. StringRelatedFileld:此字段将被序列化为关联对象的**字符串表示方法**，即models.py中__str__方法的返回值
3. 使用关联对象的序列化器：hbook = BookInfoSerializer()

**反序列化额外校验**

1. validate_字段：对某个字段校验

   ```
   def validate_btitle(self, value):  # value指校验的字段
   ```

2. validate:多个字段联合校验

   ```
   def validate(self, attrs):  # attrs多个字段的的集合
   	bread = attrs['bread']
       bcomment = attrs['bcomment']
   ```

3. validators:在字段中添加validators选项，补充自定义验证行为

**保存：serializer.save()**

数据校验成功后，基于validated_data完成数据的创建，主要实现了create()和update()方法，通过serializer.save()方法完成保存操作，返回的是数据对象。

```python
serializer = BookInfoSerializer(instance, data)
serializer.is_valid()  # True
serializer.save()
#　save()：如果传了instance则调用update()进行更新，如果只传了data则调用create()进行新增
```

### Django项目部署一般流程

**静态文件收集**

先在配置文件中配置收集之后存放的目录

```python
STATIC_ROOT = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), 'front_end_pc/static')
```

执行收集命令

```
python manage.py  collectstatic
```

打开Nginx的配置文件

```shell
sudo vim /usr/local/nginx/conf/nginx.conf
```

在server部分中配置

```python
server {
         listen       80;
         server_name  www.meiduo.site;

        location / {
             root   /home/python/Desktop/front_end_pc;
             index  index.html index.htm;
         }

        # ...
}
```

重启Nginx服务器

```shell
sudo /usr/local/nginx/sbin/nginx -s reload  
或
sudo service nginx reload
```

**动态接口**
修改配置文件prod.py

```python
DEBUG = False

ALLOWED_HOSTS = [...,  'www.xxx.site']  # 添加项目前端域名

CORS_ORIGIN_WHITELIST = (  # 添加白名单
    '127.0.0.1:8080',
    'localhost:8080',
    '前端域名',
    '后端域名',
)
```

修改wsgi.py文件

```python
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings.prod")
```

使用uwsgi服务器来运行django程序

```python
pip install uwsgi  # 安装uwsgi
```

在项目工程目录下创建uwsgi配置文件 uwsgi.ini

```ini
[uwsgi]
#使用nginx连接时使用，Django程序所在服务器地址
socket=10.211.55.2:8001
#直接做web服务器使用，Django程序所在服务器地址
#http=10.211.55.2:8001
#项目目录
chdir=/Users/delron/Desktop/项目文件夹/工程目录
#项目中wsgi.py文件的目录，相对于项目目录
wsgi-file=内层工程目录/wsgi.py
# 进程数
processes=4
# 线程数
threads=2
# uwsgi服务器的角色
master=True
# 存放进程编号的文件
pidfile=uwsgi.pid
# 日志文件，因为uwsgi可以脱离终端在后台运行，日志看不见。我们以前的runserver是依赖终端的
daemonize=uwsgi.log
# 指定依赖的虚拟环境
virtualenv=/Users/delron/.virtualenv/虚拟环境名称
```

启动uwsgi服务器

```shell
uwsgi --ini uwsgi.ini
```

修改Nginx配置文件，让Nginx接收到请求后转发给uwsgi服务器

```python
     upstream meiduo {
         server 10.211.55.2:8001;  # 此处为uwsgi运行的ip地址和端口号
         # 如果有多台服务器，可以在此处继续添加服务器地址
     }

     #gzip  on;
     server {
         listen  8000;
         server_name 后端域名;

         location / {
             include uwsgi_params;
             uwsgi_pass 项目名;
         }

     }


     server {
         listen       80;
         server_name  前端域名;

         #charset koi8-r;

         #access_log  logs/host.access.log  main;
         location /xadmin {
             include uwsgi_params;
             uwsgi_pass 项目名;
         }

         location /ckeditor {
             include uwsgi_params;
             uwsgi_pass 项目名;
         }

         location / {
             root   /home/python/Desktop/front_end_pc;
             index  index.html index.htm;
         }


         error_page   500 502 503 504  /50x.html;
         location = /50x.html {
             root   html;
         }

     }
```

重启nginx

```shell
sudo /usr/local/nginx/sbin/nginx -s reload
或
sudo service nginx reload
```

## 工具使用

### Postman

```
GET请求：
	请求url—>查询参数；
POST请求：
	表单：body—>form_data添加数据；
	非表单：body—>raw中添加json数据；
```

### Git

本地仓库上传远程git仓库

1. 初始化本地仓库
2. 新建远程仓库
3. 关联本地和远程仓库 git remote add origin ssh地址 --> git branch --set-upstream-to=origin/master master
4. 拉取远程代码 git pull
5. 上传本地代码 git push

#### .gitignore使用

1. 从远程仓库中clone文件
2. git status查看状态.idea/ 第一次文件需要添加
3. git.add .之前不要添加idea文件，
4. 在.gitignore忽略文件中添加 .dea/
5. 再次git status就不会显示.idea文件要添加

### VSCode

#### 配置python 

#### 快捷命令

打开命令面板

```
Ctrl + Shift + P
```

调整屏幕比例

```
Ctrl +  # 调大
Ctrl -  # 调小
```

移动行

```
alt + up  # 上移
alt + down  # 下移
```

删除当前行

```
crtl + shift + k
```

新建一个窗口

```
crtl + shift + n
```

快速复制当前行

```
shift + alt + up/down 
```

向下多选

```
ctrl + d
```



## 网络爬虫

### 爬虫分类

通用爬虫、**聚焦爬虫**

请求头：

​	User-Agent

​	Reference

​	Cookie

响应头：

​	Content-Length

​	Set-Cookie

注意：

爬虫只会请求url地址，也只会获取url地址响应的内容；

爬虫出来的页面和浏览器返回的页面有时不一致，因为爬虫不具备浏览器的渲染能力，一般浏览器展示的页面是多

次响应最终渲染的

random模块

random.choice()方法，会从一个容器(列表)中随机的选择一个		

## 前端开发

### 环境搭建

```
Vscode  + openChrome
```

以Chrome浏览器打开html

```
快捷键：Ctrl + Alt + A
```

创建HTML文档

```
！ + Enter  
或
！ + Tab
```

自动换行

```
查看>自动换行 
或
Alt + Z
```

## linux操作

安装apache

```
sudo apt-get install apache2
apachectl -v  # 查看apache版本
```

apache模块操作

```
sudo a2enmod 模块名  # 开启模块

sudo a2dismod 模块名  # 关闭模块
```

安装php

```
sudo apt-get install php
sudo apt-get isntall libapache2-mod-php  # 安装php和apache连接的插件
php -v  # 查看php版本
```

### Mysql数据库

查看mysql用户

- 用户信息保存在mysql库下的user表

  ```
  select User from mysql.user
  ```

##  Windows&Linux相关

### pip相关操作

查看package相关信息

```
pip show package_name
```

更新package

```
pip install --upgrade package_name
```

手动安装pip压缩包

解压下载的包，放入Lib\site-packages路径下，进入setup.py文件目录下,执行命令安装

```
python setup.py install
```

手动安装.whl文件

进入到\Python\Scripts路径下，打开cmd终端

```
pip install .whl文件
```

### virtualenv 相关操作

安装virtualenv命令

```
pip install virtualenv
```

安装虚拟环境

```
virtualenv 虚拟环境名称
```

使用虚拟环境

```
1.进入虚拟环境目录
2. cd Script\
3. activate
```

##### linux平台

安装virtualenv命令

```
pip install virtualenv
```

安装虚拟环境

```
virtualenv -p python3 虚拟环境名称
```

使用虚拟环境

```
1.进入虚拟环境目录
2.source bin/activate
```

添加环境变量

```
# 在bashrc中添加PATH路径
echo 'export PATH=/python路径/bin:$PATH'>> ~/.bashrc  
```

```
重新加载~/.bashrc文件
source ~/.bashrc 
```

**centos查看ip地址**

查询命令

```
ip addr 或 ifconfig
```

查询不到原因:CentOS 7 默认是不启动网卡的（ONBOOT=no）

```
vi /etc/sysconfig/network-scripts/ifcfg-ens33
```

修改ONBOOT=yes > 保存 > 重启网络

```
sudo service network restart 
```

再次输入查询命令即可

