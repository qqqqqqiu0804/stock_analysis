"""
光伏行业舆情与股价关联分析系统 - URL配置
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    # 管理后台
    path('admin/', admin.site.urls),

    # 页面路由
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('stocks/', TemplateView.as_view(template_name='stocks/index.html'), name='stocks'),
    path('news/', TemplateView.as_view(template_name='news/index.html'), name='news'),
    path('analysis/', TemplateView.as_view(template_name='analysis/index.html'), name='analysis'),
    path('reports/', TemplateView.as_view(template_name='reports/index.html'), name='reports'),
    path('login/', TemplateView.as_view(template_name='users/login.html'), name='login'),
    path('register/', TemplateView.as_view(template_name='users/register.html'), name='register'),

    # API路由
    path('api/users/', include('apps.users.urls')),
    path('api/stocks/', include('apps.stocks.urls')),
    path('api/news/', include('apps.news.urls')),
    path('api/analysis/', include('apps.analysis.urls')),
    path('api/reports/', include('apps.reports.urls')),
]

# 开发环境下提供媒体文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
