from django.shortcuts import render

# Create your views here.
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView

from goods.models import SKU
from goods.serializers import SKUSerializer


class SKUListView(ListAPIView):
    """
    商品列表视图
    """
    serializer_class = SKUSerializer
    # queryset = SKU.objects.filter(category=???)

    # 排序
    filter_backends = [OrderingFilter]
    ordering_fields = ('create_time', 'price', 'sales')

    # 分页, 全局设置

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return SKU.objects.filter(category_id=category_id, is_launched=True)
