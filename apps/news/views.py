"""
舆情数据模块 - 视图
"""

from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q, Count, Avg
from django.db.models.functions import TruncDate
from datetime import datetime, timedelta

from .models import NewsData, NewsSource, HotTopic
from .serializers import (
    NewsDataSerializer, NewsListSerializer, NewsQuerySerializer,
    NewsSourceSerializer, HotTopicSerializer
)
from apps.stocks.models import StockInfo


class NewsListView(generics.ListAPIView):
    """舆情列表"""
    queryset = NewsData.objects.select_related('stock', 'source').all()
    serializer_class = NewsListSerializer
    search_fields = ['title', 'content']
    ordering_fields = ['publish_time', 'sentiment_score']


class NewsDetailView(generics.RetrieveAPIView):
    """舆情详情"""
    queryset = NewsData.objects.select_related('stock', 'source').all()
    serializer_class = NewsDataSerializer


class NewsQueryView(APIView):
    """舆情查询"""

    def get(self, request):
        serializer = NewsQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        queryset = NewsData.objects.select_related('stock', 'source').all()

        # 按股票代码筛选
        stock_code = serializer.validated_data.get('stock_code')
        if stock_code:
            queryset = queryset.filter(stock__stock_code=stock_code)

        # 按情感筛选
        sentiment = serializer.validated_data.get('sentiment')
        if sentiment:
            queryset = queryset.filter(sentiment_label=sentiment)

        # 按日期范围筛选
        start_date = serializer.validated_data.get('start_date')
        end_date = serializer.validated_data.get('end_date')
        days = serializer.validated_data.get('days', 30)

        if not start_date:
            start_date = datetime.now().date() - timedelta(days=days)
        if not end_date:
            end_date = datetime.now().date()

        queryset = queryset.filter(publish_time__date__gte=start_date,
                                   publish_time__date__lte=end_date)

        # 按关键词筛选
        keyword = serializer.validated_data.get('keyword')
        if keyword:
            queryset = queryset.filter(Q(title__icontains=keyword) | Q(content__icontains=keyword))

        # 分页
        page_size = int(request.query_params.get('page_size', 20))
        page = int(request.query_params.get('page', 1))
        start = (page - 1) * page_size
        end = start + page_size

        total = queryset.count()
        news = queryset[start:end]

        return Response({
            'total': total,
            'page': page,
            'page_size': page_size,
            'results': NewsDataSerializer(news, many=True).data
        })


class NewsSourceListView(generics.ListCreateAPIView):
    """新闻来源列表"""
    queryset = NewsSource.objects.filter(is_active=True)
    serializer_class = NewsSourceSerializer


@api_view(['GET'])
def news_sentiment_summary(request, stock_code):
    """舆情情感统计摘要"""
    days = int(request.query_params.get('days', 30))
    start_date = datetime.now().date() - timedelta(days=days)

    try:
        stock = StockInfo.objects.get(stock_code=stock_code)
    except StockInfo.DoesNotExist:
        return Response({'error': '股票不存在'}, status=status.HTTP_404_NOT_FOUND)

    news = NewsData.objects.filter(
        stock=stock,
        publish_time__date__gte=start_date
    )

    total = news.count()
    positive = news.filter(sentiment_label='positive').count()
    negative = news.filter(sentiment_label='negative').count()
    neutral = news.filter(sentiment_label='neutral').count()

    avg_score = news.filter(sentiment_score__isnull=False).aggregate(
        avg=Avg('sentiment_score')
    )['avg']

    # 按日期统计情感趋势
    daily_sentiment = news.filter(sentiment_score__isnull=False).annotate(
        date=TruncDate('publish_time')
    ).values('date').annotate(
        avg_score=Avg('sentiment_score'),
        count=Count('id')
    ).order_by('date')

    return Response({
        'stock_code': stock_code,
        'stock_name': stock.stock_name,
        'period_days': days,
        'total_news': total,
        'positive_count': positive,
        'negative_count': negative,
        'neutral_count': neutral,
        'positive_ratio': round(positive / total * 100, 2) if total > 0 else 0,
        'negative_ratio': round(negative / total * 100, 2) if total > 0 else 0,
        'average_score': round(float(avg_score), 4) if avg_score else None,
        'daily_trend': list(daily_sentiment)
    })


@api_view(['GET'])
def hot_topics(request, stock_code=None):
    """获取热门话题"""
    days = int(request.query_params.get('days', 7))
    start_date = datetime.now().date() - timedelta(days=days)

    queryset = HotTopic.objects.filter(date__gte=start_date)

    if stock_code:
        try:
            stock = StockInfo.objects.get(stock_code=stock_code)
            queryset = queryset.filter(stock=stock)
        except StockInfo.DoesNotExist:
            pass

    topics = queryset.order_by('-weight')[:20]
    return Response(HotTopicSerializer(topics, many=True).data)


@api_view(['GET'])
def word_cloud_data(request, stock_code):
    """词云图数据"""
    days = int(request.query_params.get('days', 30))
    start_date = datetime.now().date() - timedelta(days=days)

    try:
        stock = StockInfo.objects.get(stock_code=stock_code)
    except StockInfo.DoesNotExist:
        return Response({'error': '股票不存在'}, status=status.HTTP_404_NOT_FOUND)

    # 获取关键词统计
    news = NewsData.objects.filter(
        stock=stock,
        publish_time__date__gte=start_date,
        keywords__isnull=False
    )

    word_count = {}
    for n in news:
        if n.keywords:
            try:
                import json
                keywords = json.loads(n.keywords) if isinstance(n.keywords, str) else n.keywords
                if isinstance(keywords, list):
                    for kw in keywords:
                        if isinstance(kw, str):
                            word_count[kw] = word_count.get(kw, 0) + 1
            except (json.JSONDecodeError, TypeError):
                pass

    # 按词频排序
    sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:100]

    return Response({
        'stock_code': stock_code,
        'words': [{'name': w, 'value': c} for w, c in sorted_words]
    })
