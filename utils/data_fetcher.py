"""
数据采集工具模块
用于获取股票行情数据和新闻舆情数据
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class StockDataFetcher:
    """股票数据采集器"""

    def __init__(self):
        self._akshare = None

    @property
    def akshare(self):
        if self._akshare is None:
            try:
                import akshare as ak
                self._akshare = ak
            except ImportError:
                logger.warning("akshare未安装，股票数据采集功能不可用")
        return self._akshare

    def fetch_stock_list(self, industry: str = '光伏') -> List[Dict]:
        """获取光伏行业股票列表"""
        if not self.akshare:
            return self._get_mock_stock_list()

        try:
            # 获取股票列表
            df = self.akshare.stock_info_a_code_name()
            # 筛选光伏相关股票
            solar_keywords = ['光伏', '太阳能', '新能源', '晶硅', '电池']
            solar_stocks = df[df['name'].str.contains('|'.join(solar_keywords), na=False)]

            stocks = []
            for _, row in solar_stocks.iterrows():
                stocks.append({
                    'stock_code': row['code'],
                    'stock_name': row['name'],
                    'industry': industry
                })
            return stocks
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            return self._get_mock_stock_list()

    def fetch_daily_quotes(self, stock_code: str, start_date: str = None,
                           end_date: str = None) -> List[Dict]:
        """获取日行情数据"""
        if not self.akshare:
            return self._get_mock_quotes(stock_code, start_date, end_date)

        try:
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')
            if not start_date:
                start_date = (datetime.now() - timedelta(days=90)).strftime('%Y%m%d')

            df = self.akshare.stock_zh_a_hist(
                symbol=stock_code,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust="qfq"
            )

            quotes = []
            for _, row in df.iterrows():
                quotes.append({
                    'trade_date': row['日期'],
                    'open_price': float(row['开盘']),
                    'close_price': float(row['收盘']),
                    'high_price': float(row['最高']),
                    'low_price': float(row['最低']),
                    'volume': int(row['成交量']),
                    'amount': float(row['成交额']),
                    'change_pct': float(row['涨跌幅']),
                    'turnover_rate': float(row['换手率'])
                })
            return quotes
        except Exception as e:
            logger.error(f"获取{stock_code}行情数据失败: {e}")
            return self._get_mock_quotes(stock_code, start_date, end_date)

    def _get_mock_stock_list(self) -> List[Dict]:
        """模拟股票列表数据"""
        return [
            {'stock_code': '601012', 'stock_name': '隆基绿能', 'industry': '光伏'},
            {'stock_code': '002459', 'stock_name': '天业通联', 'industry': '光伏'},
            {'stock_code': '600438', 'stock_name': '通威股份', 'industry': '光伏'},
            {'stock_code': '002129', 'stock_name': '中环股份', 'industry': '光伏'},
            {'stock_code': '688599', 'stock_name': '天合光能', 'industry': '光伏'},
            {'stock_code': '688223', 'stock_name': '晶科能源', 'industry': '光伏'},
            {'stock_code': '300274', 'stock_name': '阳光电源', 'industry': '光伏'},
            {'stock_code': '002050', 'stock_name': '三花智控', 'industry': '光伏'},
        ]

    def _get_mock_quotes(self, stock_code: str, start_date: str = None,
                         end_date: str = None) -> List[Dict]:
        """模拟行情数据"""
        import random
        from decimal import Decimal

        quotes = []
        if not start_date:
            start = datetime.now() - timedelta(days=30)
        else:
            start = datetime.strptime(start_date, '%Y%m%d')

        if not end_date:
            end = datetime.now()
        else:
            end = datetime.strptime(end_date, '%Y%m%d')

        base_price = random.uniform(10, 100)
        current = start

        while current <= end:
            if current.weekday() < 5:  # 工作日
                change = random.uniform(-3, 3)
                open_price = round(base_price, 2)
                close_price = round(base_price * (1 + change / 100), 2)
                high_price = round(max(open_price, close_price) * (1 + random.uniform(0, 0.02)), 2)
                low_price = round(min(open_price, close_price) * (1 - random.uniform(0, 0.02)), 2)

                quotes.append({
                    'trade_date': current.strftime('%Y-%m-%d'),
                    'open_price': open_price,
                    'close_price': close_price,
                    'high_price': high_price,
                    'low_price': low_price,
                    'volume': random.randint(1000000, 50000000),
                    'amount': round(random.uniform(10000000, 500000000), 2),
                    'change_pct': round(change, 2),
                    'turnover_rate': round(random.uniform(0.5, 5), 2)
                })
                base_price = close_price

            current += timedelta(days=1)

        return quotes


class NewsDataFetcher:
    """新闻数据采集器"""

    def fetch_stock_news(self, stock_code: str, stock_name: str,
                         days: int = 30) -> List[Dict]:
        """获取股票相关新闻（使用模拟数据）"""
        # 实际项目中可接入新闻API
        return self._get_mock_news(stock_code, stock_name, days)

    def _get_mock_news(self, stock_code: str, stock_name: str, days: int) -> List[Dict]:
        """模拟新闻数据"""
        import random

        news_templates = [
            {"title": f"{stock_name}发布2025年度业绩预告，净利润同比增长", "sentiment": "positive"},
            {"title": f"{stock_name}签订重大光伏组件供货合同", "sentiment": "positive"},
            {"title": f"光伏行业政策利好，{stock_name}有望受益", "sentiment": "positive"},
            {"title": f"{stock_name}宣布大规模扩产计划", "sentiment": "positive"},
            {"title": f"机构调研{stock_name}，看好公司发展前景", "sentiment": "positive"},
            {"title": f"{stock_name}股东减持公告", "sentiment": "negative"},
            {"title": f"光伏行业产能过剩担忧加剧", "sentiment": "negative"},
            {"title": f"{stock_name}产品价格下调，市场竞争加剧", "sentiment": "negative"},
            {"title": f"光伏行业补贴政策调整，影响{stock_name}盈利", "sentiment": "negative"},
            {"title": f"{stock_name}高管离职，市场关注公司治理", "sentiment": "negative"},
            {"title": f"光伏行业技术路线之争：TOPCon vs HJT", "sentiment": "neutral"},
            {"title": f"{stock_name}参加行业展会，展示最新产品", "sentiment": "neutral"},
            {"title": f"光伏行业协会发布月度报告", "sentiment": "neutral"},
            {"title": f"{stock_name}召开股东大会", "sentiment": "neutral"},
        ]

        sources = ['东方财富', '新浪财经', '同花顺', '证券时报', '中国证券报', '上海证券报']

        news_list = []
        for i in range(min(days * 2, 60)):
            template = random.choice(news_templates)
            date = datetime.now() - timedelta(days=random.randint(0, days))

            news_list.append({
                'title': template['title'],
                'content': f"{template['title']}。详细内容请查阅相关公告和报告。",
                'publish_time': date.strftime('%Y-%m-%d %H:%M:%S'),
                'source_name': random.choice(sources),
                'url': f"https://finance.example.com/news/{stock_code}/{i}",
            })

        return sorted(news_list, key=lambda x: x['publish_time'], reverse=True)
