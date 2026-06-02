"""
股票数据模块 - 模型定义
"""

from django.db import models


class StockInfo(models.Model):
    """股票基本信息"""
    stock_code = models.CharField(max_length=10, unique=True, verbose_name='股票代码')
    stock_name = models.CharField(max_length=50, verbose_name='股票名称')
    industry = models.CharField(max_length=50, blank=True, null=True, verbose_name='所属行业')
    list_date = models.DateField(blank=True, null=True, verbose_name='上市日期')
    market = models.CharField(max_length=10, blank=True, null=True, verbose_name='市场')
    is_active = models.BooleanField(default=True, verbose_name='是否活跃')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '股票基本信息'
        verbose_name_plural = verbose_name
        ordering = ['stock_code']

    def __str__(self):
        return f"{self.stock_code} - {self.stock_name}"


class DailyQuotes(models.Model):
    """日行情数据"""
    stock_code = models.ForeignKey(StockInfo, on_delete=models.CASCADE,
                                   related_name='quotes', verbose_name='股票')
    trade_date = models.DateField(verbose_name='交易日期')
    open_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='开盘价')
    close_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='收盘价')
    high_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='最高价')
    low_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='最低价')
    volume = models.BigIntegerField(verbose_name='成交量')
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='成交额')
    change_pct = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name='涨跌幅(%)')
    turnover_rate = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name='换手率(%)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '日行情数据'
        verbose_name_plural = verbose_name
        unique_together = ('stock_code', 'trade_date')
        ordering = ['-trade_date']

    def __str__(self):
        return f"{self.stock_code} - {self.trade_date}"

    def save(self, *args, **kwargs):
        # 自动计算涨跌幅
        if not self.change_pct and self.open_price and self.open_price > 0:
            self.change_pct = round((self.close_price - self.open_price) / self.open_price * 100, 2)
        super().save(*args, **kwargs)
