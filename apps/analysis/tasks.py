"""
分析模块 - 异步任务
"""

from celery import shared_task
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)


@shared_task
def daily_sentiment_analysis():
    """每日情感分析任务"""
    from apps.stocks.models import StockInfo
    from apps.news.models import NewsData
    from utils.sentiment_analyzer import SentimentAnalyzer

    stocks = StockInfo.objects.filter(is_active=True)
    analyzer = SentimentAnalyzer()
    total_processed = 0

    for stock in stocks:
        news_list = NewsData.objects.filter(
            stock=stock,
            is_processed=False
        )[:100]  # 每次处理100条

        for news in news_list:
            text = news.title
            if news.content:
                text += ' ' + news.content[:200]

            result = analyzer.analyze(text)
            news.sentiment_score = result['score']
            news.sentiment_label = result['label']
            news.is_processed = True
            news.save()
            total_processed += 1

    logger.info(f"每日情感分析完成，处理了 {total_processed} 条新闻")
    return {'processed': total_processed}


@shared_task
def daily_correlation_analysis():
    """每日相关性分析任务"""
    from apps.stocks.models import StockInfo
    from apps.analysis.models import AnalysisResult, SentimentTrend
    from apps.news.models import NewsData
    from apps.stocks.models import DailyQuotes
    from scipy import stats
    import numpy as np

    stocks = StockInfo.objects.filter(is_active=True)

    for stock in stocks:
        # 获取最近30天数据
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)

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
                    'sentiment_score': sentiment_dict[quote.trade_date],
                    'price_change': float(quote.change_pct) if quote.change_pct else 0
                })

        if len(correlation_data) >= 3:
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

            AnalysisResult.objects.create(
                stock=stock,
                analysis_type='correlation',
                analysis_date=end_date,
                start_date=start_date,
                end_date=end_date,
                correlation=round(correlation, 4),
                p_value=round(p_value, 8),
                correlation_strength=strength,
                is_significant=p_value < 0.05,
                analysis_summary=f"相关系数: {correlation:.4f}, P值: {p_value:.4f}",
                result_data=json.dumps({
                    'correlation': round(correlation, 4),
                    'p_value': round(p_value, 8),
                    'strength': strength,
                    'data_points': len(correlation_data)
                })
            )

    logger.info("每日相关性分析完成")
