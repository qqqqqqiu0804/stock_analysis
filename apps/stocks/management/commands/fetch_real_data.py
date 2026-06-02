"""
实时数据采集命令（东方财富API版）
"""

import time
import requests
from datetime import datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from apps.stocks.models import StockInfo, DailyQuotes


class Command(BaseCommand):
    help = '从东方财富获取真实股票行情数据'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=90, help='获取最近多少天的数据')
        parser.add_argument('--code', type=str, help='指定股票代码')

    def fetch_kline(self, code, days, headers):
        """获取K线数据，带重试"""
        if code.startswith('6'):
            secid = f'1.{code}'
        elif code.startswith('5'):
            secid = f'1.{code}'
        else:
            secid = f'0.{code}'

        url = (
            f'https://push2his.eastmoney.com/api/qt/stock/kline/get'
            f'?secid={secid}'
            f'&fields1=f1,f2,f3,f4,f5,f6'
            f'&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61'
            f'&klt=101&fqt=1&end=20500101&lmt={days}'
        )

        for attempt in range(3):
            try:
                resp = requests.get(url, headers=headers, timeout=15)
                data = resp.json()
                if data.get('data') and data['data'].get('klines'):
                    return data
                return None
            except Exception:
                if attempt < 2:
                    time.sleep((attempt + 1) * 8)
        return None

    def handle(self, *args, **options):
        days = options['days']
        target_code = options.get('code')

        if target_code:
            stocks = StockInfo.objects.filter(stock_code=target_code)
        else:
            stocks = StockInfo.objects.filter(is_active=True)

        if not stocks.exists():
            self.stdout.write(self.style.ERROR('没有找到股票记录，请先运行 seed_data'))
            return

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://quote.eastmoney.com/',
        }

        success = 0
        fail = 0

        for i, stock in enumerate(stocks):
            if i > 0:
                time.sleep(12)

            self.stdout.write(f'正在获取 {stock.stock_code} {stock.stock_name}...')

            data = self.fetch_kline(stock.stock_code, days, headers)

            if not data or not data.get('data') or not data['data'].get('klines'):
                self.stdout.write(self.style.WARNING(f'  {stock.stock_code} 无数据'))
                fail += 1
                continue

            count = 0
            for line in data['data']['klines']:
                parts = line.split(',')
                trade_date = datetime.strptime(parts[0], '%Y-%m-%d').date()

                DailyQuotes.objects.update_or_create(
                    stock_code=stock,
                    trade_date=trade_date,
                    defaults={
                        'open_price': Decimal(str(round(float(parts[1]), 2))),
                        'close_price': Decimal(str(round(float(parts[2]), 2))),
                        'high_price': Decimal(str(round(float(parts[3]), 2))),
                        'low_price': Decimal(str(round(float(parts[4]), 2))),
                        'volume': int(float(parts[5])),
                        'amount': Decimal(str(round(float(parts[6]), 2))),
                        'change_pct': Decimal(str(round(float(parts[8]), 2))),
                        'turnover_rate': Decimal(str(round(float(parts[10]), 2))),
                    }
                )
                count += 1

            self.stdout.write(self.style.SUCCESS(f'  {stock.stock_code} 完成，更新 {count} 条'))
            success += 1

        self.stdout.write(self.style.SUCCESS(
            f'数据采集完成！成功 {success} 只，失败 {fail} 只'
        ))
