from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from oauth.utils import OAuthQQ


class QQAuthURLView(APIView):
    """
    获取QQ登录的url    ?next=xxx
    """
    def get(self, request):
        # 获取next参数
        next = request.query_params.get("next")

        # 拼接QQ登录的网址
        oauth_qq = OAuthQQ(state=next)
        login_url = oauth_qq.get_login_url()

        # 返回
        return Response({'login_url': login_url})