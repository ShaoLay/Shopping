import random

from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from meiduo_mall.libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from rest_framework.generics import GenericAPIView
from rest_framework import status
import logging

from . import constants
from .serializers import ImageCodeCheckSerializer
from meiduo_mall.utils.yuntongxun.sms import CCP
from celery_tasks.sms.tasks import send_sms_code

# Create your views here.

logger = logging.getLogger('django')


class ImageCodeView(APIView):
    """图片验证码"""
    def get(self, request, image_code_id):

        # 生成验证码图片
        text, image = captcha.generate_captcha()

        # 保存真实值到Redis数据库
        redis_conn = get_redis_connection('verify_codes')
        redis_conn.setex("img_%s" % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)

        return HttpResponse(image, content_type='image/jpg')


class SMSCodeView(GenericAPIView):
    """
    短信验证码
    传入参数：
        mobile,     image_code_id, text
    """
    serializer_class = ImageCodeCheckSerializer

    def get(self, request, mobile):
        # 校验参数  由序列化器完成
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        # 生成短信验证码
        sms_code = '%06d' % random.randint(0, 999999)

        # 保存短信验证码  保存发送记录
        redis_conn = get_redis_connection('verify_codes')

        # redis管道
        pl = redis_conn.pipeline()
        pl.setex("sms_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex("send_flag_%s" % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)

        # 让管道通知redis执行命令
        pl.execute()

        # 使用celery发送短信验证码
        expires = constants.SMS_CODE_REDIS_EXPIRES // 60
        send_sms_code.delay(mobile, sms_code, expires, constants.SMS_CODE_TEMP_ID)
        print(sms_code)

        return Response({'message': 'OK'})













