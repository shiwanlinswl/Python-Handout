import qiniu

access_key = "KP1RLxS4sxzg9x2MGUeqTYX3jcOeYCQGtxgg7x20"
secret_key = "VfwsLS0-A-9W9iNFNotuef5OmPyW1dhnxr6PwKf4"
# bucket_name：上传图像的空间存储名称
bucket_name = "shiwanlin"


# data:上传的图片二进制数据
def pic_storage(data):
    """上传图片到七牛云平台"""
    if not data:
        raise AttributeError("图片数据为空")

    # 权限认证
    q = qiniu.Auth(access_key, secret_key)

    # 上传图像的名称
    # 不设置key，七牛云会自动给图片分配一个图片名称，而且是唯一
    # key = 'hello'
    # data = 'hello qiniu!'

    token = q.upload_token(bucket_name)

    # 上传图片二进制数据到七牛云
    ret, info = qiniu.put_data(token, None, data)

    print(ret)
    print("----------------")
    print(info)

    # 封装的工具类，给别人调用，一单产生异常一定要抛出，不能私自解决，否则别人就不知道错误发生在什么地方
    if ret is not None:
        print('All is OK')
    else:
        raise AttributeError("上传图片到七牛云失败")
        # print(info) # error message in info

    if info.status_code == 200:
        print("上传图片成功")
    else:
        # 抛出异常
        raise AttributeError("上传图片到七牛云失败")

    # 返回图片名称
    return ret["key"]

if __name__ == '__main__':
    file_name = input("输入上传的文件")
    with open(file_name, "rb") as f:
        pic_storage(f.read())