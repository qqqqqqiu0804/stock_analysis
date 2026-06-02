"""
舆情数据模块 - 模型定义
"""

from django.db import models
from apps.stocks.models import StockInfo


class NewsSource(models.Model):
    """新闻来源"""
    name = models.CharField(max_length=50, unique=True, verbose_name='来源名称')
    url = models.URLField(blank=True, null=True, verbose_name='来源网址')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '新闻来源'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class NewsData(models.Model):
    """舆情数据"""
    SENTIMENT_CHOICES = (
        ('positive', '正面'),
        ('negative', '负面'),
        ('neutral', '中性'),
    )

    stock = models.ForeignKey(StockInfo, on_delete=models.CASCADE,
                              related_name='news', verbose_name='关联股票')
    title = models.CharField(max_length=200, verbose_name='新闻标题')
    content = models.TextField(blank=True, null=True, verbose_name='新闻内容')
    summary = models.TextField(blank=True, null=True, verbose_name='摘要')
    publish_time = models.DateTimeField(verbose_name='发布时间')
    source = models.ForeignKey(NewsSource, on_delete=models.SET_NULL,
                               null=True, blank=True, verbose_name='来源')
    source_name = models.CharField(max_length=50, blank=True, null=True, verbose_name='来源名称')
    url = models.URLField(blank=True, null=True, verbose_name='原文链接')
    sentiment_score = models.DecimalField(max_digits=5, decimal_places=4,
                                          blank=True, null=True, verbose_name='情感得分')
    sentiment_label = models.CharField(max_length=10, choices=SENTIMENT_CHOICES,
                                        blank=True, null=True, verbose_name='情感标签')
    keywords = models.TextField(blank=True, null=True, verbose_name='关键词(JSON)')
    is_processed = models.BooleanField(default=False, verbose_name='是否已分析')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '舆情数据'
        verbose_name_plural = verbose_name
        ordering = ['-publish_time']

    def __str__(self):
        return f"{self.stock.stock_code} - {self.title[:30]}"

    def save(self, *args, **kwargs):
        # 自动设置情感标签
        if self.sentiment_score is not None and not self.sentiment_label:
            if self.sentiment_score > 0.6:
                self.sentiment_label = 'positive'
            elif self.sentiment_score < 0.4:
                self.sentiment_label = 'negative'
            else:
                self.sentiment_label = 'neutral'
        super().save(*args, **kwargs)


class HotTopic(models.Model):
    """热门话题"""
    stock = models.ForeignKey(StockInfo, on_delete=models.CASCADE,
                              related_name='topics', verbose_name='关联股票', null=True, blank=True)
    topic_name = models.CharField(max_length=100, verbose_name='话题名称')
    keywords = models.TextField(verbose_name='关键词列表')
    weight = models.FloatField(default=0, verbose_name='权重')
    news_count = models.IntegerField(default=0, verbose_name='相关新闻数')
    date = models.DateField(verbose_name='日期')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '热门话题'
        verbose_name_plural = verbose_name
        ordering = ['-date', '-weight']

    def __str__(self):
        return f"{self.date} - {self.topic_name}"
