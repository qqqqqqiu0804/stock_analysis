"""
股票数据模块 - 序列化器
"""

from rest_framework import serializers
from .models import StockInfo, DailyQuotes


class StockInfoSerializer(serializers.ModelSerializer):
    """股票基本信息序列化器"""
    class Meta:
        model = StockInfo
        fields = '__all__'


class StockListSerializer(serializers.ModelSerializer):
    """股票列表序列化器（简化版）"""
    class Meta:
        model = StockInfo
        fields = ['id', 'stock_code', 'stock_name', 'industry', 'market', 'is_active']


class DailyQuotesSerializer(serializers.ModelSerializer):
    """日行情数据序列化器"""
    stock_name = serializers.CharField(source='stock_code.stock_name', read_only=True)

    class Meta:
        model = DailyQuotes
        fields = ['id', 'stock_code', 'stock_name', 'trade_date', 'open_price', 'close_price',
                  'high_price', 'low_price', 'volume', 'amount', 'change_pct', 'turnover_rate']


class StockQuoteQuerySerializer(serializers.Serializer):
    """股票行情查询序列化器"""
    stock_code = serializers.CharField(required=True)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    days = serializers.IntegerField(required=False, default=30)


class StockSearchSerializer(serializers.Serializer):
    """股票搜索序列化器"""
    keyword = serializers.CharField(required=True)
