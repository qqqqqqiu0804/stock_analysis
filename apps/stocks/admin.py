"""
股票数据模块 - Admin配置
"""

from django.contrib import admin
from .models import StockInfo, DailyQuotes


@admin.register(StockInfo)
class StockInfoAdmin(admin.ModelAdmin):
    list_display = ['stock_code', 'stock_name', 'industry', 'market', 'is_active', 'created_at']
    list_filter = ['industry', 'market', 'is_active']
    search_fields = ['stock_code', 'stock_name']
    ordering = ['stock_code']


@admin.register(DailyQuotes)
class DailyQuotesAdmin(admin.ModelAdmin):
    list_display = ['stock_code', 'trade_date', 'open_price', 'close_price',
                    'high_price', 'low_price', 'volume', 'change_pct']
    list_filter = ['trade_date']
    search_fields = ['stock_code__stock_code', 'stock_code__stock_name']
    ordering = ['-trade_date']
