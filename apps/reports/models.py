"""
报告生成模块 - 模型定义
"""

from django.db import models
from apps.stocks.models import StockInfo
from django.conf import settings


class Report(models.Model):
    """分析报告"""
    REPORT_TYPE_CHOICES = (
        ('pdf', 'PDF报告'),
        ('excel', 'Excel报告'),
    )
    STATUS_CHOICES = (
        ('pending', '生成中'),
        ('completed', '已完成'),
        ('failed', '生成失败'),
    )

    title = models.CharField(max_length=200, verbose_name='报告标题')
    stock = models.ForeignKey(StockInfo, on_delete=models.CASCADE,
                              related_name='reports', verbose_name='关联股票')
    report_type = models.CharField(max_length=10, choices=REPORT_TYPE_CHOICES, verbose_name='报告类型')
    start_date = models.DateField(verbose_name='分析起始日期')
    end_date = models.DateField(verbose_name='分析结束日期')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    file = models.FileField(upload_to='reports/', blank=True, null=True, verbose_name='报告文件')
    file_size = models.IntegerField(blank=True, null=True, verbose_name='文件大小(字节)')
    description = models.TextField(blank=True, null=True, verbose_name='报告描述')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                    null=True, blank=True, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name='完成时间')

    class Meta:
        verbose_name = '分析报告'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.get_report_type_display()}"
