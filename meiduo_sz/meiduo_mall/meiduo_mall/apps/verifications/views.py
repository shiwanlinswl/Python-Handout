from django.shortcuts import render
from rest_framework.views import APIView
from random import randint
from django_redis import get_redis_connection
from meiduo_mall.libs.yuntongxun.sms import CCP
from rest_framework.response import Response
import logging
from rest_framework import status
from . import constants
from celery_tasks.sms.tasks import send_sms_code


# Create your views here.

logger = logging.getLogger('django')  # 创建日志输出器


class SMSCodeView(APIView):
    """发送短息验证码"""

    def get(self, request, mobile):

        # 0.连接redis数据库
        redis_conn = get_redis_connection('verify_codes')

        # 1.获取此手机号是否有发送过标记
        flag = redis_conn.get('send_flag_%s' % mobile)

        # 2.如果有发送就提前响应，不执行后续代码
        if flag:  # 如果if成立说明此手机号60秒内发过短信
            return Response({'message': '频繁发送短信'}, status=status.HTTP_400_BAD_REQUEST)

        # 3.后端生成短信验证码
        sms_code = "%06d" % randint(0, 999999)
        logger.info(sms_code)
        # 创建redis管道对象
        pl = redis_conn.pipeline()

        # 4.保存验证码到redis数据库
        # redis_conn.setex("sms_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex("sms_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # 4.1存储此手机号已发送短信标记
        # redis_conn.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        pl.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)

        # 执行管道
        pl.execute()

        # 5.通过容联云通讯发送短信
        # CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60], 1)
        # 触发异步任务(让发短信不要阻塞主线程)
        # send_sms_code(mobile, sms_code)  # 这种写法并不能触发异步
        send_sms_code.delay(mobile, sms_code)
        # 6.响应
        return Response({"message": "ok"})



