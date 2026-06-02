"""
分析模块 - 模型定义
"""

from django.db import models
from apps.stocks.models import StockInfo


class AnalysisResult(models.Model):
    """分析结果"""
    ANALYSIS_TYPE_CHOICES = (
        ('correlation', '相关性分析'),
        ('sentiment', '情感分析'),
        ('topic', '主题分析'),
        ('prediction', '预测分析'),
    )

    stock = models.ForeignKey(StockInfo, on_delete=models.CASCADE,
                              related_name='analyses', verbose_name='关联股票')
    analysis_type = models.CharField(max_length=20, choices=ANALYSIS_TYPE_CHOICES, verbose_name='分析类型')
    analysis_date = models.DateField(verbose_name='分析日期')
    start_date = models.DateField(verbose_name='分析起始日期')
    end_date = models.DateField(verbose_name='分析结束日期')

    # 相关性分析结果
    correlation = models.DecimalField(max_digits=6, decimal_places=4,
                                      blank=True, null=True, verbose_name='相关系数')
    p_value = models.DecimalField(max_digits=10, decimal_places=8,
                                   blank=True, null=True, verbose_name='P值')
    correlation_strength = models.CharField(max_length=20, blank=True, null=True, verbose_name='相关性强度')
    is_significant = models.BooleanField(default=False, verbose_name='是否显著')

    # 情感分析结果
    avg_sentiment_score = models.DecimalField(max_digits=5, decimal_places=4,
                                               blank=True, null=True, verbose_name='平均情感得分')
    positive_ratio = models.DecimalField(max_digits=5, decimal_places=2,
                                          blank=True, null=True, verbose_name='正面比例')
    negative_ratio = models.DecimalField(max_digits=5, decimal_places=2,
                                          blank=True, null=True, verbose_name='负面比例')

    # 主题分析结果
    main_topics = models.TextField(blank=True, null=True, verbose_name='主要主题(JSON)')

    # 综合分析结果
    analysis_summary = models.TextField(blank=True, null=True, verbose_name='分析摘要')
    result_data = models.TextField(blank=True, null=True, verbose_name='详细结果(JSON)')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '分析结果'
        verbose_name_plural = verbose_name
        ordering = ['-analysis_date']

    def __str__(self):
        return f"{self.stock.stock_code} - {self.get_analysis_type_display()} - {self.analysis_date}"


class SentimentTrend(models.Model):
    """情感趋势数据"""
    stock = models.ForeignKey(StockInfo, on_delete=models.CASCADE,
                              related_name='sentiment_trends', verbose_name='关联股票')
    date = models.DateField(verbose_name='日期')
    sentiment_score = models.DecimalField(max_digits=5, decimal_places=4, verbose_name='情感得分')
    news_count = models.IntegerField(default=0, verbose_name='新闻数量')
    positive_count = models.IntegerField(default=0, verbose_name='正面新闻数')
    negative_count = models.IntegerField(default=0, verbose_name='负面新闻数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '情感趋势'
        verbose_name_plural = verbose_name
        unique_together = ('stock', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.stock.stock_code} - {self.date} - {self.sentiment_score}"


class PriceCorrelation(models.Model):
    """舆情-股价相关性数据"""
    stock = models.ForeignKey(StockInfo, on_delete=models.CASCADE,
                              related_name='correlations', verbose_name='关联股票')
    date = models.DateField(verbose_name='日期')
    sentiment_score = models.DecimalField(max_digits=5, decimal_places=4, verbose_name='情感得分')
    price_change = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='股价涨跌幅(%)')
    volume_change = models.DecimalField(max_digits=10, decimal_places=2,
                                         blank=True, null=True, verbose_name='成交量变化(%)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '舆情-股价相关性数据'
        verbose_name_plural = verbose_name
        unique_together = ('stock', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.stock.stock_code} - {self.date}"
