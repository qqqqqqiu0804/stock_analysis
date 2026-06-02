"""
股票数据模块 - URL配置
"""

from django.urls import path
from . import views

urlpatterns = [
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
