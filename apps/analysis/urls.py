"""
分析模块 - URL配置
"""

from django.urls import path
from . import views

urlpatterns = [
    # 分析结果
    path('results/', views.AnalysisResultListView.as_view(), name='analysis-results'),
    path('results/<int:pk>/', views.AnalysisResultDetailView.as_view(), name='analysis-detail'),
    path('query/', views.AnalysisQueryView.as_view(), name='analysis-query'),

    # 相关性分析
    path('correlation/', views.CorrelationAnalysisView.as_view(), name='correlation-analysis'),

    # 情感趋势
    path('sentiment/<str:stock_code>/', views.sentiment_trend, name='sentiment-trend'),

    # 分析摘要
    path('summary/<str:stock_code>/', views.analysis_summary, name='analysis-summary'),

    # 执行分析
    path('run/sentiment/<str:stock_code>/', views.run_sentiment_analysis, name='run-sentiment'),
    path('run/topic/<str:stock_code>/', views.run_topic_analysis, name='run-topic'),
]
