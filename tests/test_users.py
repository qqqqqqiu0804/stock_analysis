"""
用户模块测试
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


class UserModelTest(TestCase):
    """用户模型测试"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            phone='13800138000'
        )

    def test_user_creation(self):
        """测试用户创建"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.role, 'user')
        self.assertTrue(self.user.check_password('testpass123'))

    def test_user_str(self):
        """测试用户字符串表示"""
        self.assertEqual(str(self.user), 'testuser (普通用户)')

    def test_is_admin(self):
        """测试管理员判断"""
        self.assertFalse(self.user.is_admin)
        self.user.role = 'admin'
        self.user.save()
        self.assertTrue(self.user.is_admin)


class UserAPITest(TestCase):
    """用户API测试"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_register(self):
        """测试用户注册"""
        data = {
            'username': 'newuser',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'email': 'new@example.com'
        }
        response = self.client.post('/api/users/register/', data)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login(self):
        """测试用户登录"""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post('/api/users/login/', data)
        self.assertEqual(response.status_code, 200)

    def test_login_wrong_password(self):
        """测试错误密码登录"""
        data = {
            'username': 'testuser',
            'password': 'wrongpass'
        }
        response = self.client.post('/api/users/login/', data)
        self.assertEqual(response.status_code, 401)

    def test_profile(self):
        """测试获取个人资料"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/users/profile/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], 'testuser')
