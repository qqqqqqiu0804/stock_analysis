"""
用户管理模块 - Admin配置
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'phone', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['username', 'email', 'phone']
    ordering = ['-created_at']

    fieldsets = UserAdmin.fieldsets + (
        ('扩展信息', {'fields': ('role', 'phone', 'avatar')}),
    )
