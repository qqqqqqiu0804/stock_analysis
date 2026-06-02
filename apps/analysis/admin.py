"""
分析模块 - Admin配置
"""

from django.contrib import admin
from .models import AnalysisResult, SentimentTrend, PriceCorrelation


@admin.register(AnalysisResult)
class AnalysisResultAdmin(admin.ModelAdmin):
    list_display = ['stock', 'analysis_type', 'analysis_date', 'correlation',
                    'correlation_strength', 'is_significant']
    list_filter = ['analysis_type', 'is_significant', 'analysis_date']
    search_fields = ['stock__stock_code', 'stock__stock_name']
    ordering = ['-analysis_date']


@admin.register(SentimentTrend)
class SentimentTrendAdmin(admin.ModelAdmin):
    list_display = ['stock', 'date', 'sentiment_score', 'news_count',
                    'positive_count', 'negative_count']
    list_filter = ['date']
    search_fields = ['stock__stock_code']
    ordering = ['-date']


@admin.register(PriceCorrelation)
class PriceCorrelationAdmin(admin.ModelAdmin):
    list_display = ['stock', 'date', 'sentiment_score', 'price_change', 'volume_change']
    list_filter = ['date']
    search_fields = ['stock__stock_code']
    ordering = ['-date']
