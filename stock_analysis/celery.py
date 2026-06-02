"""
Celery配置模块
"""

import os
from celery import Celery

# 设置Django默认设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_analysis.settings')

# 创建Celery实例
app = Celery('stock_analysis')

# 从Django settings中加载配置
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现任务
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
