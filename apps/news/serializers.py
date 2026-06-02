"""
舆情数据模块 - 序列化器
"""

from rest_framework import serializers
from .models import NewsData, NewsSource, HotTopic


class NewsSourceSerializer(serializers.ModelSerializer):
    """新闻来源序列化器"""
    class Meta:
        model = NewsSource
        fields = '__all__'


class NewsDataSerializer(serializers.ModelSerializer):
    """舆情数据序列化器"""
    stock_name = serializers.CharField(source='stock.stock_name', read_only=True)
    stock_code = serializers.CharField(source='stock.stock_code', read_only=True)
    source_display = serializers.CharField(source='source_name', read_only=True)
    sentiment_display = serializers.CharField(source='get_sentiment_label_display', read_only=True)

    class Meta:
        model = NewsData
        fields = ['id', 'stock', 'stock_code', 'stock_name', 'title', 'summary',
                  'publish_time', 'source_name', 'source_display', 'url',
                  'sentiment_score', 'sentiment_label', 'sentiment_display',
                  'keywords', 'is_processed', 'created_at']


class NewsListSerializer(serializers.ModelSerializer):
    """舆情列表序列化器（简化版）"""
    stock_code = serializers.CharField(source='stock.stock_code', read_only=True)
    stock_name = serializers.CharField(source='stock.stock_name', read_only=True)

    class Meta:
        model = NewsData
        fields = ['id', 'stock_code', 'stock_name', 'title', 'publish_time',
                  'source_name', 'sentiment_score', 'sentiment_label']


class NewsQuerySerializer(serializers.Serializer):
    """舆情查询序列化器"""
    stock_code = serializers.CharField(required=False)
    sentiment = serializers.ChoiceField(
        choices=['positive', 'negative', 'neutral'],
        required=False
    )
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    keyword = serializers.CharField(required=False)
    days = serializers.IntegerField(required=False, default=30)


class HotTopicSerializer(serializers.ModelSerializer):
    """热门话题序列化器"""
    stock_code = serializers.CharField(source='stock.stock_code', read_only=True, default=None)

    class Meta:
        model = HotTopic
        fields = ['id', 'stock', 'stock_code', 'topic_name', 'keywords',
                  'weight', 'news_count', 'date']
