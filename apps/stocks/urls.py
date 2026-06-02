"""
股票数据模块 - URL配置
"""

from django.urls import path
from . import views, views_dashboard

urlpatterns = [
    # 数据大盘
    path('dashboard/summary/', views_dashboard.dashboard_summary, name='dashboard-summary'),
    path('dashboard/ranking/', views_dashboard.dashboard_stock_ranking, name='dashboard-ranking'),
    path('dashboard/sentiment/', views_dashboard.dashboard_sentiment_compare, name='dashboard-sentiment'),
    path('dashboard/news/', views_dashboard.dashboard_latest_news, name='dashboard-news'),
    path('dashboard/trend/', views_dashboard.dashboard_price_trend, name='dashboard-trend'),

    # 股票基本信息
    path('list/', views.StockListView.as_view(), name='stock-list'),
    path('search/', views.StockSearchView.as_view(), name='stock-search'),
    path('summary/', views.stock_list_summary, name='stock-summary'),

    # 股票行情
    path('quotes/', views.StockQuotesView.as_view(), name='stock-quotes'),
    path('kline/<str:stock_code>/', views.kline_data, name='kline-data'),

    # 股票详情
    path('<str:stock_code>/', views.StockDetailView.as_view(), name='stock-detail'),
]
