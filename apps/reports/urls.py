"""
报告生成模块 - URL配置
"""

from django.urls import path
from . import views

urlpatterns = [
    # 报告管理
    path('list/', views.ReportListView.as_view(), name='report-list'),
    path('create/', views.ReportCreateView.as_view(), name='report-create'),
    path('<int:pk>/', views.ReportDetailView.as_view(), name='report-detail'),

    # 报告操作
    path('download/<int:report_id>/', views.download_report, name='report-download'),
    path('delete/<int:report_id>/', views.delete_report, name='report-delete'),
]
