import pymysql

"""
pymysql：是一种客户端，用于在python中连接mysql,进行数据库编程
python语言的3.x完全不向前兼容,导致我们在python2.x中可以正常使用的库,到了python3就用不了了.比如说mysqldb
目前MySQLdb并不支持python3.x ， Python3.x连接MySQL的方案有：oursql, PyMySQL, myconnpy 等
"""
# 目的：将Pymysql当成是mysqldb一样使用,django中数据库操作支持的是mysqldb
pymysql.install_as_MySQLdb()