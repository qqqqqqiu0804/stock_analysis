"""
从新浪财经获取行情数据
"""

import time
import requests
import re
from datetime import datetime, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from apps.stocks.models import StockInfo, DailyQuotes


class Command(BaseCommand):
    help = '从新浪财经获取行情数据'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=90, help='获取最近多少天的数据')
        parser.add_argument('--code', type=str, help='指定股票代码')

    def fetch_sina_kline(self, code, days):
        """从新浪获取K线数据"""
        # 新浪代码格式：sh600000 / sz000001
        if code.startswith('6') or code.startswith('5'):
            sina_code = f'sh{code}'
        else:
            sina_code = f'sz{code}'

        # 新浪K线API
        url = f'https://quotes.sina.cn/cn/api/jsonp_v2.php/var%20_k=/CN_MarketDataService.getKLineData?symbol={sina_code}&scale=240&ma=no&datalen={days}'

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://finance.sina.com.cn/',
        }

        try:
            resp = requests.get(url, headers=headers, timeout=15)
            text = resp.text
            # 解析JSONP
            json_str = text[text.index('([') + 1:text.rindex(')')]
            import json
            data = json.loads(json_str)
            return data
        except Exception as e:
            return None

    def handle(self, *args, **options):
        days = options['days']
        target_code = options.get('code')

        if target_code:
            stocks = StockInfo.objects.filter(stock_code=target_code)
        else:
            stocks = StockInfo.objects.filter(is_active=True)

        if not stocks.exists():
            self.stdout.write(self.style.ERROR('没有找到股票记录'))
            return

        success = 0
        fail = 0

        for i, stock in enumerate(stocks):
            if i > 0:
                time.sleep(3)

            self.stdout.write(f'正在获取 {stock.stock_code} {stock.stock_name}...')

            data = self.fetch_sina_kline(stock.stock_code, days)

            if not data:
                self.stdout.write(self.style.WARNING(f'  {stock.stock_code} 无数据'))
                fail += 1
                continue

            count = 0
            for item in data:
                try:
                    trade_date = datetime.strptime(item['day'], '%Y-%m-%d').date()
                    open_price = float(item['open'])
                    close_price = float(item['close'])
                    high_price = float(item['high'])
                    low_price = float(item['low'])
                    volume = int(item['volume'])

                    if open_price == 0 and close_price == 0:
                        continue

                    change_pct = round((close_price - open_price) / open_price * 100, 2) if open_price > 0 else 0

                    DailyQuotes.objects.update_or_create(
                        stock_code=stock,
                        trade_date=trade_date,
                        defaults={
                            'open_price': Decimal(str(open_price)),
                            'close_price': Decimal(str(close_price)),
                            'high_price': Decimal(str(high_price)),
                            'low_price': Decimal(str(low_price)),
                            'volume': volume,
                            'amount': Decimal(str(round(volume * close_price, 2))),
                            'change_pct': Decimal(str(change_pct)),
                            'turnover_rate': Decimal('0'),
                        }
                    )
                    count += 1
                except Exception:
                    continue

            if count > 0:
                self.stdout.write(self.style.SUCCESS(f'  {stock.stock_code} 完成，更新 {count} 条'))
                success += 1
            else:
                self.stdout.write(self.style.WARNING(f'  {stock.stock_code} 无有效数据'))
                fail += 1

        self.stdout.write(self.style.SUCCESS(f'\n数据采集完成！成功 {success} 只，失败 {fail} 只'))
