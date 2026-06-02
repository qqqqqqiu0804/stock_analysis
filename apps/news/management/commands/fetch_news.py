"""
从东方财富获取真实新闻（公告）
"""

import time
import requests
from datetime import datetime
from django.core.management.base import BaseCommand
from apps.stocks.models import StockInfo
from apps.news.models import NewsData, NewsSource


class Command(BaseCommand):
    help = '从东方财富获取真实新闻数据（公告）'

    def add_arguments(self, parser):
        parser.add_argument('--code', type=str, help='指定股票代码')
        parser.add_argument('--pages', type=int, default=3, help='获取页数')

    def handle(self, *args, **options):
        target_code = options.get('code')
        pages = options.get('pages', 3)

        if target_code:
            stocks = StockInfo.objects.filter(stock_code=target_code)
        else:
            stocks = StockInfo.objects.filter(is_active=True)

        if not stocks.exists():
            self.stdout.write(self.style.ERROR('没有找到股票记录'))
            return

        # 确保新闻来源存在
        source, _ = NewsSource.objects.get_or_create(name='东方财富')

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }

        total_saved = 0

        for stock in stocks:
            self.stdout.write(f'正在获取 {stock.stock_code} {stock.stock_name} 的公告...')
            saved = 0

            for page in range(1, pages + 1):
                time.sleep(2)

                # 东方财富公告API
                url = (
                    f'https://np-anotice-stock.eastmoney.com/api/security/ann'
                    f'?sr=-1&page_size=20&page_index={page}'
                    f'&ann_type=SHA&client_source=web&f_node=0&s_node=0'
                    f'&stock_list={stock.stock_code}'
                )

                try:
                    resp = requests.get(url, headers=headers, timeout=10)
                    data = resp.json()

                    if 'data' not in data or 'list' not in data['data']:
                        break

                    news_list = data['data']['list']
                    if not news_list:
                        break

                    for item in news_list:
                        title = item.get('title', '')
                        notice_date = item.get('notice_date', '')
                        art_code = item.get('art_code', '')

                        if not title or not notice_date:
                            continue

                        # 解析日期
                        try:
                            pub_datetime = datetime.strptime(notice_date[:10], '%Y-%m-%d')
                        except ValueError:
                            continue

                        # 构建URL
                        article_url = f'https://data.eastmoney.com/notices/detail/{stock.stock_code}/{art_code}.html'

                        # 检查是否已存在
                        if NewsData.objects.filter(stock=stock, title=title).exists():
                            continue

                        NewsData.objects.create(
                            stock=stock,
                            title=title,
                            content='',
                            publish_time=pub_datetime,
                            source=source,
                            source_name='东方财富',
                            url=article_url,
                            is_processed=False,
                        )
                        saved += 1

                    self.stdout.write(f'  第{page}页: 获取 {len(news_list)} 条')

                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'  第{page}页获取失败: {e}'))
                    break

            self.stdout.write(self.style.SUCCESS(f'  {stock.stock_code} 完成，新增 {saved} 条'))
            total_saved += saved

        self.stdout.write(self.style.SUCCESS(f'\n采集完成！共新增 {total_saved} 条新闻'))

        if total_saved > 0:
            self.stdout.write('\n下一步：运行情感分析')
            self.stdout.write('  python manage.py run_sentiment_analysis')
