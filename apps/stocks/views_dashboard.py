"""
数据大盘API
"""

from datetime import date, timedelta
from django.db.models import Avg, Count, Q, Sum
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.stocks.models import StockInfo, DailyQuotes
from apps.news.models import NewsData
from apps.analysis.models import SentimentTrend


@api_view(['GET'])
def dashboard_summary(request):
    """数据大盘摘要"""
    today = date.today()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    # 股票统计
    stocks = StockInfo.objects.filter(is_active=True)
    stock_count = stocks.count()

    # 今日行情统计
    today_quotes = DailyQuotes.objects.filter(trade_date=today)
    if not today_quotes.exists():
        # 如果今天没有数据，取最近一天
        latest_date = DailyQuotes.objects.order_by('-trade_date').values_list('trade_date', flat=True).first()
        if latest_date:
            today_quotes = DailyQuotes.objects.filter(trade_date=latest_date)
            today = latest_date

    up_count = today_quotes.filter(change_pct__gt=0).count()
    down_count = today_quotes.filter(change_pct__lt=0).count()
    flat_count = today_quotes.filter(change_pct=0).count()

    avg_change = today_quotes.aggregate(avg=Avg('change_pct'))['avg']
    total_amount = today_quotes.aggregate(total=Sum('amount'))['total']

    # 涨跌幅最大
    top_gainer = today_quotes.order_by('-change_pct').first()
    top_loser = today_quotes.order_by('change_pct').first()

    # 舆情统计
    week_news = NewsData.objects.filter(publish_time__date__gte=week_ago)
    total_news_week = week_news.count()
    positive_week = week_news.filter(sentiment_label='positive').count()
    negative_week = week_news.filter(sentiment_label='negative').count()

    # 行业情感指数（近7天平均情感得分）
    sentiment_index = week_news.filter(
        sentiment_score__isnull=False
    ).aggregate(avg=Avg('sentiment_score'))['avg']

    return Response({
        'stock_count': stock_count,
        'today': str(today),
        'market': {
            'up_count': up_count,
            'down_count': down_count,
            'flat_count': flat_count,
            'avg_change': round(float(avg_change), 2) if avg_change else 0,
            'total_amount': float(total_amount) if total_amount else 0,
        },
        'top_gainer': {
            'code': top_gainer.stock_code.stock_code if top_gainer else None,
            'name': top_gainer.stock_code.stock_name if top_gainer else None,
            'change': float(top_gainer.change_pct) if top_gainer else 0,
        },
        'top_loser': {
            'code': top_loser.stock_code.stock_code if top_loser else None,
            'name': top_loser.stock_code.stock_name if top_loser else None,
            'change': float(top_loser.change_pct) if top_loser else 0,
        },
        'sentiment': {
            'index': round(float(sentiment_index), 4) if sentiment_index else 0.5,
            'news_week': total_news_week,
            'positive_week': positive_week,
            'negative_week': negative_week,
        }
    })


@api_view(['GET'])
def dashboard_stock_ranking(request):
    """股票涨跌排行"""
    # 取最近交易日
    latest_date = DailyQuotes.objects.order_by('-trade_date').values_list('trade_date', flat=True).first()
    if not latest_date:
        return Response([])

    quotes = DailyQuotes.objects.filter(
        trade_date=latest_date
    ).select_related('stock_code').order_by('-change_pct')

    data = []
    for q in quotes:
        data.append({
            'code': q.stock_code.stock_code,
            'name': q.stock_code.stock_name,
            'price': float(q.close_price),
            'change_pct': float(q.change_pct) if q.change_pct else 0,
            'volume': q.volume,
            'amount': float(q.amount),
        })

    return Response(data)


@api_view(['GET'])
def dashboard_sentiment_compare(request):
    """各股票情感对比"""
    days = int(request.query_params.get('days', 7))
    start_date = date.today() - timedelta(days=days)

    stocks = StockInfo.objects.filter(is_active=True)
    data = []

    for stock in stocks:
        avg_score = NewsData.objects.filter(
            stock=stock,
            publish_time__date__gte=start_date,
            sentiment_score__isnull=False
        ).aggregate(avg=Avg('sentiment_score'))['avg']

        news_count = NewsData.objects.filter(
            stock=stock,
            publish_time__date__gte=start_date
        ).count()

        data.append({
            'code': stock.stock_code,
            'name': stock.stock_name,
            'sentiment_score': round(float(avg_score), 4) if avg_score else 0.5,
            'news_count': news_count,
        })

    # 按情感得分排序
    data.sort(key=lambda x: x['sentiment_score'], reverse=True)
    return Response(data)


@api_view(['GET'])
def dashboard_latest_news(request):
    """最新热点新闻"""
    limit = int(request.query_params.get('limit', 10))

    news = NewsData.objects.select_related('stock').filter(
        sentiment_score__isnull=False
    ).order_by('-publish_time')[:limit]

    data = []
    for n in news:
        data.append({
            'id': n.id,
            'title': n.title,
            'stock_code': n.stock.stock_code,
            'stock_name': n.stock.stock_name,
            'publish_time': n.publish_time.strftime('%Y-%m-%d'),
            'sentiment_label': n.sentiment_label,
            'sentiment_score': float(n.sentiment_score) if n.sentiment_score else None,
            'source_name': n.source_name,
        })

    return Response(data)


@api_view(['GET'])
def dashboard_price_trend(request):
    """股价走势对比（近30天）"""
    days = int(request.query_params.get('days', 30))
    start_date = date.today() - timedelta(days=days)

    stocks = StockInfo.objects.filter(is_active=True)[:5]  # 只取前5只

    result = {}
    dates_set = set()

    for stock in stocks:
        quotes = DailyQuotes.objects.filter(
            stock_code=stock,
            trade_date__gte=start_date
        ).order_by('trade_date')

        # 计算相对于第一天的涨跌幅
        prices = []
        dates = []
        base_price = None

        for q in quotes:
            if base_price is None:
                base_price = float(q.close_price)
            change = (float(q.close_price) - base_price) / base_price * 100
            prices.append(round(change, 2))
            dates.append(q.trade_date.strftime('%Y-%m-%d'))
            dates_set.add(q.trade_date.strftime('%Y-%m-%d'))

        result[stock.stock_code] = {
            'name': stock.stock_name,
            'data': prices,
            'dates': dates,
        }

    return Response({
        'dates': sorted(list(dates_set)),
        'stocks': result,
    })
