"""
报告生成模块 - Admin配置
"""

from django.contrib import admin
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'stock', 'report_type', 'status', 'created_by', 'created_at']
    list_filter = ['report_type', 'status', 'created_at']
    search_fields = ['title', 'stock__stock_code', 'stock__stock_name']
    ordering = ['-created_at']
