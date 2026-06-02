"""
用户管理模块 - URL配置
"""

from django.urls import path
from . import views

urlpatterns = [
    # 认证相关
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    # 用户信息
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('current/', views.current_user, name='current-user'),

    # 管理员接口
    path('list/', views.UserListView.as_view(), name='user-list'),
    path('<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
]
