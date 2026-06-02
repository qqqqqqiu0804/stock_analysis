"""
用户管理模块 - 模型定义
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """自定义用户模型"""
    ROLE_CHOICES = (
        ('admin', '管理员'),
        ('user', '普通用户'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user', verbose_name='角色')
    phone = models.CharField(max_length=11, blank=True, null=True, verbose_name='手机号')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='头像')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == 'admin'
