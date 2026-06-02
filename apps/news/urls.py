"""
舆情数据模块 - URL配置
"""

from django.urls import path
from . import views

urlpatterns = [
    # 舆情数据
    path('list/', views.NewsListView.as_view(), name='news-list'),
    path('query/', views.NewsQueryView.as_view(), name='news-query'),
    path('sources/', views.NewsSourceListView.as_view(), name='news-sources'),

    # 统计分析
    path('sentiment/<str:stock_code>/', views.news_sentiment_summary, name='news-sentiment'),
    path('topics/', views.hot_topics, name='hot-topics'),
    path('topics/<str:stock_code>/', views.hot_topics, name='stock-topics'),
    path('wordcloud/<str:stock_code>/', views.word_cloud_data, name='word-cloud'),

    # 详情
    path('<int:pk>/', views.NewsDetailView.as_view(), name='news-detail'),
]
