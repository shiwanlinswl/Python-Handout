from django.core.files.storage import Storage
from django.conf import settings
from fdfs_client.client import Fdfs_client


class FastDFSStorage(Storage):
    """自定义文件存储系统"""
    def __init__(self, base_url=None, client_conf=None):
        """
        初始化
        :param base_url: 用于构造图片完整路径使用，图片服务器的域名
        :param client_conf: FastDFS客户端配置文件的路径
        """
        # 写法1：
        # if base_url is None:
        #     base_url = settings.FDFS_BASE_URL
        # self.base_url = base_url

        # 写法2：
        # if base_url:
        #     self.base_url = base_url
        # else:
        #     self.base_url = settings.FDFS_BASE_URL

        # 写法3：
        # self.base_url = base_url if base_url else settings.FDFS_BASE_URL

        self.base_url = base_url or settings.FDFS_BASE_URL

        self.client_conf = client_conf or settings.FDFS_CLIENT_CONF

    def _open(self, name, mode='rb'):
        """
        打开文件，但是自定义文件存储系统是为了上传和下载文件，不是需要打开，所以这个方法什么也不需要做，可以直接pass
        """
        pass

    def _save(self, name, content):
        """
        在FastDFS中保存文件
        :param name: 传入的文件名
        :param content: 文件内容
        :return: 保存到数据库中的FastDFS的文件名
        """
        # 1.创建fdfs客户端
        # client = Fdfs_client('meiduo/utils/fastdfs/client.conf')
        # client = Fdfs_client(settings.FDFS_CLIENT_CONF)
        client = Fdfs_client(self.client_conf)

        # 2.上传文件
        # client.upload_by_filename()  # 如果用此方法，指定文件路径和文件名来上传上传，filename上传的文件在storage中有后缀
        ret = client.upload_by_buffer(content.read())  # 如果是通过文件的二进制上传buffer，上传文件在storage中没有后缀
        # 3.安全判断
        if ret.get('Status') != 'Upload successed.':
            raise Exception("上传文件失败")

        # 4.返回file_id
        return ret.get('Remote file_id')

    def url(self, name):
        """
        返回文件的完整URL路径
        :param name: 数据库中保存的文件名，即返回的Remote file_id
        :return: 完整的URL
        """
        # 访问文件时的完整url路径
        # return 'http://192.168.192.137:8888/' + name
        # return settings.FDFS_BASE_URL + name
        return self.base_url + name

    def exists(self, name):
        """
        判断文件是否存在，FastDFS可以自行解决文件的重名问题
        所以此处返回False，告诉Django上传的都是新文件
        :param name:  文件名
        :return: False
        """
        return False