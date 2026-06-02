"""
股票模块测试
"""

from django.test import TestCase
from rest_framework.test import APIClient
from datetime import date, timedelta
from apps.stocks.models import StockInfo, DailyQuotes


class StockInfoModelTest(TestCase):
    """股票信息模型测试"""

    def setUp(self):
        self.stock = StockInfo.objects.create(
            stock_code='601012',
            stock_name='隆基绿能',
            industry='光伏',
            list_date=date(2012, 4, 11)
        )

    def test_stock_creation(self):
        """测试股票创建"""
        self.assertEqual(self.stock.stock_code, '601012')
        self.assertEqual(self.stock.stock_name, '隆基绿能')

    def test_stock_str(self):
        """测试股票字符串表示"""
        self.assertEqual(str(self.stock), '601012 - 隆基绿能')


class DailyQuotesModelTest(TestCase):
    """日行情数据模型测试"""

    def setUp(self):
        self.stock = StockInfo.objects.create(
            stock_code='601012',
            stock_name='隆基绿能'
        )
        self.quote = DailyQuotes.objects.create(
            stock_code=self.stock,
            trade_date=date.today(),
            open_price=25.00,
            close_price=26.50,
            high_price=27.00,
            low_price=24.50,
            volume=10000000,
            amount=250000000.00
        )

    def test_quote_creation(self):
        """测试行情数据创建"""
        self.assertEqual(self.quote.stock_code, self.stock)
        self.assertEqual(float(self.quote.close_price), 26.50)

    def test_quote_str(self):
        """测试行情数据字符串表示"""
        expected = f"601012 - {date.today()}"
        self.assertEqual(str(self.quote), expected)


class StockAPITest(TestCase):
    """股票API测试"""

    def setUp(self):
        self.client = APIClient()
        self.stock = StockInfo.objects.create(
            stock_code='601012',
            stock_name='隆基绿能',
            industry='光伏'
        )

    def test_stock_list(self):
        """测试股票列表"""
        response = self.client.get('/api/stocks/list/')
        self.assertEqual(response.status_code, 200)

    def test_stock_detail(self):
        """测试股票详情"""
        response = self.client.get('/api/stocks/601012/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['stock_name'], '隆基绿能')

    def test_stock_search(self):
        """测试股票搜索"""
        response = self.client.get('/api/stocks/search/?keyword=隆基')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data) > 0)
