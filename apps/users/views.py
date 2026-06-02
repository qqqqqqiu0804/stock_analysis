"""
用户管理模块 - 视图
"""

from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model

from .serializers import (
    UserSerializer, UserCreateSerializer, UserLoginSerializer,
    ChangePasswordSerializer, UserProfileSerializer
)

User = get_user_model()


class IsAdminUser(permissions.BasePermission):
    """管理员权限"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin


class RegisterView(generics.CreateAPIView):
    """用户注册"""
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'message': '注册成功',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """用户登录"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )

        if user:
            login(request, user)
            return Response({
                'message': '登录成功',
                'user': UserSerializer(user).data
            })
        return Response(
            {'error': '用户名或密码错误'},
            status=status.HTTP_401_UNAUTHORIZED
        )


class LogoutView(APIView):
    """用户登出"""
    def post(self, request):
        logout(request)
        return Response({'message': '登出成功'})


class UserProfileView(generics.RetrieveUpdateAPIView):
    """用户个人资料"""
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    """修改密码"""
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {'error': '原密码错误'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': '密码修改成功'})


class UserListView(generics.ListAPIView):
    """用户列表（管理员）"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """用户详情（管理员）"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def current_user(request):
    """获取当前登录用户信息"""
    return Response(UserSerializer(request.user).data)
