"""
初始化示例数据命令
"""

import random
from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from apps.stocks.models import StockInfo, DailyQuotes
from apps.news.models import NewsData, NewsSource


class Command(BaseCommand):
    help = '初始化光伏行业示例数据'

    def handle(self, *args, **options):
        self.stdout.write('开始初始化数据...')

        # 创建股票
        stocks_data = [
            ('601012', '隆基绿能', '光伏', '2012-04-11', '上交所'),
            ('002459', '天业通联', '光伏', '2010-08-10', '深交所'),
            ('600438', '通威股份', '光伏', '2004-03-02', '上交所'),
            ('002129', '中环股份', '光伏', '2007-04-20', '深交所'),
            ('688599', '天合光能', '光伏', '2020-06-10', '科创板'),
            ('688223', '晶科能源', '光伏', '2022-01-26', '科创板'),
            ('300274', '阳光电源', '光伏', '2011-11-02', '创业板'),
            ('002050', '三花智控', '光伏', '2005-06-03', '深交所'),
            ('601865', '福莱特', '光伏', '2019-02-15', '上交所'),
            ('300118', '东方日升', '光伏', '2010-09-02', '创业板'),
        ]

        stocks = []
        for code, name, industry, list_date, market in stocks_data:
            stock, created = StockInfo.objects.get_or_create(
                stock_code=code,
                defaults={
                    'stock_name': name,
                    'industry': industry,
                    'list_date': list_date,
                    'market': market,
                }
            )
            stocks.append(stock)
            if created:
                self.stdout.write(f'  创建股票: {code} - {name}')

        # 创建新闻来源
        sources = ['东方财富', '新浪财经', '同花顺', '证券时报', '中国证券报', '上海证券报']
        news_sources = []
        for name in sources:
            src, _ = NewsSource.objects.get_or_create(name=name)
            news_sources.append(src)

        # 为每只股票生成行情和新闻
        today = date.today()
        news_templates = [
            ("{name}发布年度业绩预告，净利润同比增长{pct}%", "positive"),
            ("{name}签订重大光伏组件供货合同，金额达{amount}亿元", "positive"),
            ("光伏行业政策利好，{name}有望持续受益", "positive"),
            ("{name}宣布{amount}亿元扩产计划，产能将大幅提升", "positive"),
            ("机构密集调研{name}，多家券商给予买入评级", "positive"),
            ("{name}技术创新突破，电池转换效率再创新高", "positive"),
            ("{name}海外订单大增，全球化布局加速", "positive"),
            ("{name}股东减持{amount}万股，市场关注后续走势", "negative"),
            ("光伏行业产能过剩担忧加剧，{name}股价承压", "negative"),
            ("{name}产品价格下调{pct}%，行业竞争白热化", "negative"),
            ("光伏补贴政策调整，{name}盈利预期下调", "negative"),
            ("{name}高管集体离职，公司治理引发市场担忧", "negative"),
            ("原材料价格大幅上涨，{name}成本压力增大", "negative"),
            ("光伏行业技术路线之争：TOPCon vs HJT谁主沉浮", "neutral"),
            ("{name}参加SNEC光伏展会，展示最新N型组件产品", "neutral"),
            ("中国光伏行业协会发布月度运行报告", "neutral"),
            ("{name}召开2025年度股东大会", "neutral"),
            ("光伏行业2025年装机量数据出炉，同比增{pct}%", "neutral"),
        ]

        for stock in stocks:
            self.stdout.write(f'  生成 {stock.stock_name} 的数据...')

            # 生成90天行情数据
            base_price = random.uniform(15, 80)
            for i in range(90):
                trade_date = today - timedelta(days=89 - i)
                if trade_date.weekday() >= 5:
                    continue

                change = random.uniform(-4, 4)
                open_price = round(base_price, 2)
                close_price = round(base_price * (1 + change / 100), 2)
                high_price = round(max(open_price, close_price) * (1 + random.uniform(0, 0.03)), 2)
                low_price = round(min(open_price, close_price) * (1 - random.uniform(0, 0.03)), 2)
                volume = random.randint(5000000, 80000000)
                amount = round(volume * (open_price + close_price) / 2, 2)

                DailyQuotes.objects.get_or_create(
                    stock_code=stock,
                    trade_date=trade_date,
                    defaults={
                        'open_price': Decimal(str(open_price)),
                        'close_price': Decimal(str(close_price)),
                        'high_price': Decimal(str(high_price)),
                        'low_price': Decimal(str(low_price)),
                        'volume': volume,
                        'amount': Decimal(str(amount)),
                        'change_pct': Decimal(str(round(change, 2))),
                        'turnover_rate': Decimal(str(round(random.uniform(0.5, 8), 2))),
                    }
                )
                base_price = close_price

            # 生成30条新闻
            for i in range(30):
                template, sentiment = random.choice(news_templates)
                title = template.format(
                    name=stock.stock_name,
                    pct=random.randint(10, 60),
                    amount=random.randint(5, 100)
                )
                pub_date = today - timedelta(days=random.randint(0, 60))

                score = None
                if sentiment == 'positive':
                    score = round(random.uniform(0.65, 0.95), 4)
                elif sentiment == 'negative':
                    score = round(random.uniform(0.05, 0.35), 4)
                else:
                    score = round(random.uniform(0.4, 0.6), 4)

                NewsData.objects.create(
                    stock=stock,
                    title=title,
                    content=f"{title}。详细内容请查阅相关公告和报告。",
                    publish_time=f"{pub_date} 09:30:00",
                    source=random.choice(news_sources),
                    source_name=random.choice(sources),
                    sentiment_score=Decimal(str(score)),
                    sentiment_label=sentiment,
                    is_processed=True,
                )

        self.stdout.write(self.style.SUCCESS(f'数据初始化完成！创建了 {len(stocks)} 只股票的数据'))
