"""
生成情感趋势数据
从已有的新闻数据聚合生成每日情感趋势
"""

from django.core.management.base import BaseCommand
from django.db.models import Avg, Count, Q
from django.db.models.functions import TruncDate
from apps.news.models import NewsData
from apps.analysis.models import SentimentTrend
from apps.stocks.models import StockInfo


class Command(BaseCommand):
    help = '从新闻数据生成情感趋势统计'

    def handle(self, *args, **options):
        stocks = StockInfo.objects.filter(is_active=True)
        total = 0

        for stock in stocks:
            self.stdout.write(f'处理 {stock.stock_code} {stock.stock_name}...')

            # 按日期聚合情感数据
            daily_stats = (
                NewsData.objects.filter(
                    stock=stock,
                    sentiment_score__isnull=False
                )
                .annotate(date=TruncDate('publish_time'))
                .values('date')
                .annotate(
                    avg_score=Avg('sentiment_score'),
                    count=Count('id'),
                    positive=Count('id', filter=Q(sentiment_label='positive')),
                    negative=Count('id', filter=Q(sentiment_label='negative')),
                )
                .order_by('date')
            )

            count = 0
            for stat in daily_stats:
                SentimentTrend.objects.update_or_create(
                    stock=stock,
                    date=stat['date'],
                    defaults={
                        'sentiment_score': round(stat['avg_score'], 4),
                        'news_count': stat['count'],
                        'positive_count': stat['positive'],
                        'negative_count': stat['negative'],
                    }
                )
                count += 1

            self.stdout.write(self.style.SUCCESS(f'  生成 {count} 条趋势数据'))
            total += count

        self.stdout.write(self.style.SUCCESS(f'\n完成！共生成 {total} 条情感趋势数据'))
