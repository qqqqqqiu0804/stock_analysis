"""
分析模块 - 序列化器
"""

from rest_framework import serializers
from .models import AnalysisResult, SentimentTrend, PriceCorrelation


class AnalysisResultSerializer(serializers.ModelSerializer):
    """分析结果序列化器"""
    stock_code = serializers.CharField(source='stock.stock_code', read_only=True)
    stock_name = serializers.CharField(source='stock.stock_name', read_only=True)
    analysis_type_display = serializers.CharField(source='get_analysis_type_display', read_only=True)

    class Meta:
        model = AnalysisResult
        fields = '__all__'


class AnalysisQuerySerializer(serializers.Serializer):
    """分析查询序列化器"""
    stock_code = serializers.CharField(required=True)
    analysis_type = serializers.ChoiceField(
        choices=['correlation', 'sentiment', 'topic', 'prediction'],
        required=False
    )
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    days = serializers.IntegerField(required=False, default=90)


class SentimentTrendSerializer(serializers.ModelSerializer):
    """情感趋势序列化器"""
    stock_code = serializers.CharField(source='stock.stock_code', read_only=True)

    class Meta:
        model = SentimentTrend
        fields = ['id', 'stock', 'stock_code', 'date', 'sentiment_score',
                  'news_count', 'positive_count', 'negative_count']


class PriceCorrelationSerializer(serializers.ModelSerializer):
    """舆情-股价相关性序列化器"""
    stock_code = serializers.CharField(source='stock.stock_code', read_only=True)

    class Meta:
        model = PriceCorrelation
        fields = ['id', 'stock', 'stock_code', 'date', 'sentiment_score',
                  'price_change', 'volume_change']


class CorrelationAnalysisSerializer(serializers.Serializer):
    """相关性分析请求序列化器"""
    stock_code = serializers.CharField(required=True)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    days = serializers.IntegerField(required=False, default=90)
