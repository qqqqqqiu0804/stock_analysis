"""
舆情数据模块 - Admin配置
"""

from django.contrib import admin
from .models import NewsData, NewsSource, HotTopic


@admin.register(NewsSource)
class NewsSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'is_active', 'created_at']
    list_filter = ['is_active']


@admin.register(NewsData)
class NewsDataAdmin(admin.ModelAdmin):
    list_display = ['title', 'stock', 'publish_time', 'source_name',
                    'sentiment_score', 'sentiment_label', 'is_processed']
    list_filter = ['sentiment_label', 'is_processed', 'publish_time']
    search_fields = ['title', 'content', 'stock__stock_code']
    ordering = ['-publish_time']


@admin.register(HotTopic)
class HotTopicAdmin(admin.ModelAdmin):
    list_display = ['topic_name', 'stock', 'date', 'weight', 'news_count']
    list_filter = ['date']
    search_fields = ['topic_name']
    ordering = ['-date', '-weight']
