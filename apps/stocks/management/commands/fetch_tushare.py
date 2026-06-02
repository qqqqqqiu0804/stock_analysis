"""
Tushare Pro 数据采集命令

使用前需要：
1. 注册 https://tushare.pro/register
2. 获取Token: https://tushare.pro/main/auth
3. 在 settings.py 中配置 TUSHARE_TOKEN，或通过 --token 参数传入
"""

import time
from datetime import datetime, timedelta
from decimal import Decimal
from django.conf import settings
from django.core.management.base import BaseCommand
from apps.stocks.models import StockInfo, DailyQuotes


class Command(BaseCommand):
    help = '从Tushare Pro获取真实股票行情数据'

    def add_arguments(self, parser):
        parser.add_argument('--token', type=str, help='Tushare Pro Token')
        parser.add_argument('--days', type=int, default=90, help='获取最近多少天的数据')
        parser.add_argument('--code', type=str, help='指定股票代码')

    def handle(self, *args, **options):
        import tushare as ts

        token = options.get('token') or getattr(settings, 'TUSHARE_TOKEN', None)
        if not token:
            self.stdout.write(self.style.ERROR(
                '请提供Tushare Token！\n'
                '方式1: python manage.py fetch_tushare --token 你的token\n'
                '方式2: 在 settings.py 中添加 TUSHARE_TOKEN = "你的token"'
            ))
            return

        ts.set_token(token)
        pro = ts.pro_api()

        days = options['days']
        target_code = options.get('code')

        if target_code:
            stocks = StockInfo.objects.filter(stock_code=target_code)
        else:
            stocks = StockInfo.objects.filter(is_active=True)

        if not stocks.exists():
            self.stdout.write(self.style.ERROR('没有找到股票记录，请先运行 seed_data'))
            return

        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')

        success = 0
        fail = 0

        for i, stock in enumerate(stocks):
            # Tushare限流：每分钟最多500次
            if i > 0:
                time.sleep(0.5)

            self.stdout.write(f'正在获取 {stock.stock_code} {stock.stock_name}...')

            try:
                # ts_code格式：600000.SH / 000001.SZ
                code = stock.stock_code
                if code.startswith('6'):
                    ts_code = f'{code}.SH'
                else:
                    ts_code = f'{code}.SZ'

                df = pro.daily(
                    ts_code=ts_code,
                    start_date=start_date,
                    end_date=end_date
                )

                if df is None or df.empty:
                    self.stdout.write(self.style.WARNING(f'  {code} 无数据'))
                    fail += 1
                    continue

                count = 0
                for _, row in df.iterrows():
                    trade_date = datetime.strptime(str(row['trade_date']), '%Y%m%d').date()

                    # 计算涨跌幅（Tushare的pct_chg已经是百分比）
                    change_pct = float(row.get('pct_chg', 0) or 0)

                    DailyQuotes.objects.update_or_create(
                        stock_code=stock,
                        trade_date=trade_date,
                        defaults={
                            'open_price': Decimal(str(round(row['open'], 2))),
                            'close_price': Decimal(str(round(row['close'], 2))),
                            'high_price': Decimal(str(round(row['high'], 2))),
                            'low_price': Decimal(str(round(row['low'], 2))),
                            'volume': int(row.get('vol', 0) or 0),
                            'amount': Decimal(str(round(row.get('amount', 0) or 0, 2))),
                            'change_pct': Decimal(str(round(change_pct, 2))),
                            'turnover_rate': Decimal(str(round(float(row.get('turnover_rate', 0) or 0), 2))),
                        }
                    )
                    count += 1

                self.stdout.write(self.style.SUCCESS(f'  {code} 完成，更新 {count} 条'))
                success += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  {stock.stock_code} 失败: {e}'))
                fail += 1

        self.stdout.write(self.style.SUCCESS(
            f'\n数据采集完成！成功 {success} 只，失败 {fail} 只'
        ))
