from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
import pickle
import base64

from carts import contants
from .serializers import CartSerializer
# Create your views here.


class CartView(GenericAPIView):
    """购物车"""
    serializer_class = CartSerializer

    def perform_authentication(self, request):
        """将执行具体请求方法前的身份认证关掉，由视图自己来进行身份认证"""
        pass

    def post(self, request):
        # sku_id  count  selected
        # 校验
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_excption=True)

        sku_id = serializer.validated_data['sku_id']
        count = serializer.validated_data['count']
        selected = serializer.validated_data['selected']

        # 判断用户登录状态
        try:
            user = request.user   # 匿名用户 AnonymoseUser
        except Exception:
            user = None

        # 保存
        if user and user.is_authenticated:
            # 如果用户已登录，保存到redis
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipeline()

            # 用户购物车数据  redis hash哈希
            pl.hincrby('cart_%s' % user.id, sku_id, count)

            # 用户购物车勾选数据  redis  set
            if selected:
                pl.sadd('cart_selected_%s' % user.id, sku_id)

            pl.execute()
            return Response(serializer.data)

        else:
            # 如果用户未登录，保存到cookie  reponse = Response() response.set_cookie
            # 取出cookie中的购物车数据
            cart_str = request.COOKIES.get('cart')

            if cart_str:
                # 解析
                cart_str = cart_str.encode()  # str -> bytes
                cart_bytes = base64.b64decode(cart_str)  # b64decode(byes类型）
                cart_dict = pickle.loads(cart_bytes)
            else:
                cart_dict = {}

            # cart_dict = {
            #     sku_id_1: {
            #         'count': 10
            #         'selected': True
            #     },
            #     sku_id_2: {
            #         'count': 10
            #         'selected': False
            #     },
            #     sku_id_3: {
            #         'count': 10
            #         'selected': True
            #     }
            # }

            if sku_id in cart_dict:
                # 如果商品存在购物车中，累加
                cart_dict[sku_id]['count'] += count
                cart_dict[sku_id]['selected'] = selected
            else:
                # 如果商品不在购物车中，设置
                cart_dict[sku_id] = {
                    'count': count,
                    'selected': selected
                }

            cart_cookie = base64.b64encode(pickle.dumps(cart_dict)).decode()

            # 设置cookie
            response = Response(serializer.data)
            response.set_cookie('cart', cart_cookie, max_age=contants.CART_COOKIE_EXPIRES)

            return response










