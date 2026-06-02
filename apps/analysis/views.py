"""
分析模块 - 视图
"""

from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Avg, Count
from django.db.models.functions import TruncDate
from datetime import datetime, timedelta
import json

from .models import AnalysisResult, SentimentTrend, PriceCorrelation
from .serializers import (
    AnalysisResultSerializer, AnalysisQuerySerializer,
    SentimentTrendSerializer, PriceCorrelationSerializer,
    CorrelationAnalysisSerializer
)
from apps.stocks.models import StockInfo, DailyQuotes
from apps.news.models import NewsData
from utils.sentiment_analyzer import SentimentAnalyzer
from utils.topic_extractor import TopicExtractor


class AnalysisResultListView(generics.ListAPIView):
    """分析结果列表"""
    queryset = AnalysisResult.objects.select_related('stock').all()
    serializer_class = AnalysisResultSerializer
    filterset_fields = ['stock__stock_code', 'analysis_type']


class AnalysisResultDetailView(generics.RetrieveAPIView):
    """分析结果详情"""
    queryset = AnalysisResult.objects.select_related('stock').all()
    serializer_class = AnalysisResultSerializer


class AnalysisQueryView(APIView):
    """分析查询"""

    def get(self, request):
        serializer = AnalysisQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        stock_code = serializer.validated_data['stock_code']
        analysis_type = serializer.validated_data.get('analysis_type')
        days = serializer.validated_data.get('days', 90)
        start_date = serializer.validated_data.get('start_date')
        end_date = serializer.validated_data.get('end_date')

        try:
            stock = StockInfo.objects.get(stock_code=stock_code)
        except StockInfo.DoesNotExist:
            return Response({'error': '股票不存在'}, status=status.HTTP_404_NOT_FOUND)

        if not start_date:
            start_date = datetime.now().date() - timedelta(days=days)
        if not end_date:
            end_date = datetime.now().date()

        queryset = AnalysisResult.objects.filter(
            stock=stock,
            analysis_date__gte=start_date,
            analysis_date__lte=end_date
        )

        if analysis_type:
            queryset = queryset.filter(analysis_type=analysis_type)

        results = queryset.order_by('-analysis_date')

        return Response({
            'stock_code': stock_code,
            'stock_name': stock.stock_name,
            'results': AnalysisResultSerializer(results, many=True).data
        })


class CorrelationAnalysisView(APIView):
    """相关性分析"""

    def get(self, request):
        serializer = CorrelationAnalysisSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        stock_code = serializer.validated_data['stock_code']
        days = serializer.validated_data.get('days', 90)
        start_date = serializer.validated_data.get('start_date')
        end_date = serializer.validated_data.get('end_date')

        try:
            stock = StockInfo.objects.get(stock_code=stock_code)
        except StockInfo.DoesNotExist:
            return Response({'error': '股票不存在'}, status=status.HTTP_404_NOT_FOUND)

        if not start_date:
            start_date = datetime.now().date() - timedelta(days=days)
        if not end_date:
            end_date = datetime.now().date()

        # 获取情感趋势数据
        sentiment_data = SentimentTrend.objects.filter(
            stock=stock,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')

        # 获取股价数据
        price_data = DailyQuotes.objects.filter(
            stock_code=stock,
            trade_date__gte=start_date,
            trade_date__lte=end_date
        ).order_by('trade_date')

        # 构建相关性数据
        correlation_data = []
        sentiment_dict = {s.date: float(s.sentiment_score) for s in sentiment_data}

        for quote in price_data:
            if quote.trade_date in sentiment_dict:
                correlation_data.append({
                    'date': quote.trade_date.strftime('%Y-%m-%d'),
                    'sentiment_score': sentiment_dict[quote.trade_date],
                    'price_change': float(quote.change_pct) if quote.change_pct else 0,
                    'volume': quote.volume
                })

        # 计算相关系数
        if len(correlation_data) >= 3:
            import numpy as np
            from scipy import stats

            sentiment_scores = [d['sentiment_score'] for d in correlation_data]
            price_changes = [d['price_change'] for d in correlation_data]

            correlation, p_value = stats.pearsonr(sentiment_scores, price_changes)

            if abs(correlation) >= 0.8:
                strength = '强相关'
            elif abs(correlation) >= 0.6:
                strength = '中等相关'
            elif abs(correlation) >= 0.4:
                strength = '弱相关'
            else:
                strength = '极弱相关'

            result = {
                'stock_code': stock_code,
                'stock_name': stock.stock_name,
                'period': f"{start_date} 至 {end_date}",
                'data_points': len(correlation_data),
                'correlation': round(correlation, 4),
                'p_value': round(p_value, 8),
                'strength': strength,
                'is_significant': p_value < 0.05,
                'data': correlation_data
            }
        else:
            result = {
                'stock_code': stock_code,
                'stock_name': stock.stock_name,
                'period': f"{start_date} 至 {end_date}",
                'data_points': len(correlation_data),
                'correlation': None,
                'p_value': None,
                'strength': '数据不足',
                'is_significant': False,
                'data': correlation_data,
                'message': '数据点不足，无法进行相关性分析'
            }

        return Response(result)

    def post(self, request):
        """执行并保存相关性分析"""
        serializer = CorrelationAnalysisSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        stock_code = serializer.validated_data['stock_code']
        days = serializer.validated_data.get('days', 90)

        try:
            stock = StockInfo.objects.get(stock_code=stock_code)
        except StockInfo.DoesNotExist:
            return Response({'error': '股票不存在'}, status=status.HTTP_404_NOT_FOUND)

        start_date = datetime.now().date() - timedelta(days=days)
        end_date = datetime.now().date()

        # 获取数据并计算
        sentiment_data = SentimentTrend.objects.filter(
            stock=stock, date__gte=start_date, date__lte=end_date
        ).order_by('date')

        price_data = DailyQuotes.objects.filter(
            stock_code=stock, trade_date__gte=start_date, trade_date__lte=end_date
        ).order_by('trade_date')

        correlation_data = []
        sentiment_dict = {s.date: float(s.sentiment_score) for s in sentiment_data}

        for quote in price_data:
            if quote.trade_date in sentiment_dict:
                correlation_data.append({
                    'date': quote.trade_date,
                    'sentiment_score': sentiment_dict[quote.trade_date],
                    'price_change': float(quote.change_pct) if quote.change_pct else 0
                })

        if len(correlation_data) < 3:
            return Response({'error': '数据不足，无法进行分析'}, status=status.HTTP_400_BAD_REQUEST)

        import numpy as np
        from scipy import stats

        sentiment_scores = [d['sentiment_score'] for d in correlation_data]
        price_changes = [d['price_change'] for d in correlation_data]
        correlation, p_value = stats.pearsonr(sentiment_scores, price_changes)

        if abs(correlation) >= 0.8:
            strength = '强相关'
        elif abs(correlation) >= 0.6:
            strength = '中等相关'
        elif abs(correlation) >= 0.4:
            strength = '弱相关'
        else:
            strength = '极弱相关'

        # 保存分析结果
        analysis = AnalysisResult.objects.create(
            stock=stock,
            analysis_type='correlation',
            analysis_date=end_date,
            start_date=start_date,
            end_date=end_date,
            correlation=round(correlation, 4),
            p_value=round(p_value, 8),
            correlation_strength=strength,
            is_significant=p_value < 0.05,
            analysis_summary=f"相关系数: {correlation:.4f}, P值: {p_value:.4f}, 相关性强度: {strength}",
            result_data=json.dumps({
                'correlation': round(correlation, 4),
                'p_value': round(p_value, 8),
                'strength': strength,
                'data_points': len(correlation_data)
            })
        )

        return Response({
            'message': '分析完成',
            'result': AnalysisResultSerializer(analysis).data
        })


@api_view(['GET'])
def sentiment_trend(request, stock_code):
    """情感趋势数据"""
    days = int(request.query_params.get('days', 30))

    try:
        stock = StockInfo.objects.get(stock_code=stock_code)
    except StockInfo.DoesNotExist:
        return Response({'error': '股票不存在'}, status=status.HTTP_404_NOT_FOUND)

    start_date = datetime.now().date() - timedelta(days=days)

    trends = SentimentTrend.objects.filter(
        stock=stock,
        date__gte=start_date
    ).order_by('date')

    return Response({
        'stock_code': stock_code,
        'stock_name': stock.stock_name,
        'trends': SentimentTrendSerializer(trends, many=True).data
    })


@api_view(['GET'])
def analysis_summary(request, stock_code):
    """分析摘要"""
    try:
        stock = StockInfo.objects.get(stock_code=stock_code)
    except StockInfo.DoesNotExist:
        return Response({'error': '股票不存在'}, status=status.HTTP_404_NOT_FOUND)

    # 获取最新的分析结果
    latest_correlation = AnalysisResult.objects.filter(
        stock=stock, analysis_type='correlation'
    ).order_by('-analysis_date').first()

    latest_sentiment = AnalysisResult.objects.filter(
        stock=stock, analysis_type='sentiment'
    ).order_by('-analysis_date').first()

    # 获取情感统计
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    sentiment_stats = NewsData.objects.filter(
        stock=stock,
        publish_time__date__gte=thirty_days_ago
    ).aggregate(
        total=Count('id'),
        positive=Count('id', filter=models.Q(sentiment_label='positive')),
        negative=Count('id', filter=models.Q(sentiment_label='negative')),
        avg_score=Avg('sentiment_score')
    )

    return Response({
        'stock_code': stock_code,
        'stock_name': stock.stock_name,
        'latest_correlation': AnalysisResultSerializer(latest_correlation).data if latest_correlation else None,
        'latest_sentiment': AnalysisResultSerializer(latest_sentiment).data if latest_sentiment else None,
        'sentiment_stats': {
            'total_news': sentiment_stats['total'] or 0,
            'positive_count': sentiment_stats['positive'] or 0,
            'negative_count': sentiment_stats['negative'] or 0,
            'average_score': round(float(sentiment_stats['avg_score']), 4) if sentiment_stats['avg_score'] else None
        }
    })


@api_view(['POST'])
def run_sentiment_analysis(request, stock_code):
    """执行情感分析"""
    days = int(request.data.get('days', 30))

    try:
        stock = StockInfo.objects.get(stock_code=stock_code)
    except StockInfo.DoesNotExist:
        return Response({'error': '股票不存在'}, status=status.HTTP_404_NOT_FOUND)

    start_date = datetime.now().date() - timedelta(days=days)

    # 获取未分析的新闻
    news_list = NewsData.objects.filter(
        stock=stock,
        publish_time__date__gte=start_date,
        is_processed=False
    )

    if not news_list.exists():
        return Response({'message': '没有需要分析的新闻'})

    analyzer = SentimentAnalyzer()
    processed_count = 0

    for news in news_list:
        text = news.title
        if news.content:
            text += ' ' + news.content[:200]

        result = analyzer.analyze(text)
        news.sentiment_score = result['score']
        news.sentiment_label = result['label']
        news.is_processed = True
        news.save()
        processed_count += 1

    return Response({
        'message': f'情感分析完成，处理了 {processed_count} 条新闻',
        'processed_count': processed_count
    })


@api_view(['POST'])
def run_topic_analysis(request, stock_code):
    """执行主题分析"""
    days = int(request.data.get('days', 30))
    n_topics = int(request.data.get('n_topics', 5))

    try:
        stock = StockInfo.objects.get(stock_code=stock_code)
    except StockInfo.DoesNotExist:
        return Response({'error': '股票不存在'}, status=status.HTTP_404_NOT_FOUND)

    start_date = datetime.now().date() - timedelta(days=days)

    # 获取新闻文本
    news_list = NewsData.objects.filter(
        stock=stock,
        publish_time__date__gte=start_date
    )

    if news_list.count() < 5:
        return Response({'error': '新闻数量不足，无法进行主题分析'}, status=status.HTTP_400_BAD_REQUEST)

    texts = []
    for news in news_list:
        text = news.title
        if news.content:
            text += ' ' + news.content[:200]
        texts.append(text)

    extractor = TopicExtractor()
    topics = extractor.extract_topics(texts, n_topics=n_topics)

    # 保存分析结果
    analysis = AnalysisResult.objects.create(
        stock=stock,
        analysis_type='topic',
        analysis_date=datetime.now().date(),
        start_date=start_date,
        end_date=datetime.now().date(),
        main_topics=json.dumps(topics, ensure_ascii=False),
        analysis_summary=f"提取了 {len(topics)} 个主题"
    )

    return Response({
        'message': '主题分析完成',
        'topics': topics,
        'result': AnalysisResultSerializer(analysis).data
    })
