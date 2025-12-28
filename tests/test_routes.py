"""
单元测试 - 路由测试
"""
import unittest
import json
from app import create_app, db
from app.models import User, Task, Category
from config import Config


class TestConfig(Config):
    """测试配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


class TestAuthRoutes(unittest.TestCase):
    """认证路由测试"""
    
    def setUp(self):
        """测试前准备"""
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self):
        """测试后清理"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_register_page(self):
        """测试注册页面访问"""
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn('用户注册', response.data.decode('utf-8'))
    
    def test_login_page(self):
        """测试登录页面访问"""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn('用户登录', response.data.decode('utf-8'))
    
    def test_register_success(self):
        """测试注册成功"""
        response = self.client.post('/register', data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('注册成功', response.data.decode('utf-8'))
        
        # 验证用户已创建
        user = User.query.filter_by(username='newuser').first()
        self.assertIsNotNone(user)
    
    def test_register_duplicate_username(self):
        """测试重复用户名注册"""
        # 先创建一个用户
        user = User(username='existuser', email='exist@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # 尝试用相同用户名注册
        response = self.client.post('/register', data={
            'username': 'existuser',
            'email': 'new@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('已被注册', response.data.decode('utf-8'))
    
    def test_register_password_mismatch(self):
        """测试密码不匹配"""
        response = self.client.post('/register', data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'password123',
            'confirm_password': 'different'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('不一致', response.data.decode('utf-8'))
    
    def test_login_success(self):
        """测试登录成功"""
        # 创建用户
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('欢迎回来', response.data.decode('utf-8'))
    
    def test_login_wrong_password(self):
        """测试密码错误"""
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('错误', response.data.decode('utf-8'))


class TestTaskRoutes(unittest.TestCase):
    """任务路由测试"""
    
    def setUp(self):
        """测试前准备"""
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # 创建并登录测试用户
        self.user = User(username='testuser', email='test@example.com')
        self.user.set_password('password123')
        db.session.add(self.user)
        db.session.commit()
        
        self.client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        })
    
    def tearDown(self):
        """测试后清理"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_task_list_page(self):
        """测试任务列表页面"""
        response = self.client.get('/tasks')
        self.assertEqual(response.status_code, 200)
        self.assertIn('任务列表', response.data.decode('utf-8'))
    
    def test_create_task_page(self):
        """测试创建任务页面"""
        response = self.client.get('/tasks/create')
        self.assertEqual(response.status_code, 200)
        self.assertIn('新建任务', response.data.decode('utf-8'))
    
    def test_create_task_success(self):
        """测试创建任务成功"""
        response = self.client.post('/tasks/create', data={
            'title': '测试任务',
            'description': '这是一个测试任务',
            'priority': 'urgent_important'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('创建成功', response.data.decode('utf-8'))
        
        task = Task.query.filter_by(title='测试任务').first()
        self.assertIsNotNone(task)
    
    def test_create_task_empty_title(self):
        """测试空标题创建任务"""
        response = self.client.post('/tasks/create', data={
            'title': '',
            'description': '描述'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('不能为空', response.data.decode('utf-8'))
    
    def test_create_task_title_too_long(self):
        """测试标题过长"""
        response = self.client.post('/tasks/create', data={
            'title': 'a' * 51,
            'description': '描述'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('不能超过', response.data.decode('utf-8'))
    
    def test_complete_task(self):
        """测试完成任务"""
        task = Task(title='测试任务', user_id=self.user.id)
        db.session.add(task)
        db.session.commit()
        
        response = self.client.post(f'/tasks/{task.id}/complete', follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        updated_task = Task.query.get(task.id)
        self.assertTrue(updated_task.is_completed)
    
    def test_delete_task(self):
        """测试删除任务"""
        task = Task(title='测试任务', user_id=self.user.id)
        db.session.add(task)
        db.session.commit()
        task_id = task.id
        
        response = self.client.post(f'/tasks/{task_id}/delete', follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        deleted_task = Task.query.get(task_id)
        self.assertIsNone(deleted_task)


class TestTaskAPI(unittest.TestCase):
    """任务API测试"""
    
    def setUp(self):
        """测试前准备"""
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # 创建并登录测试用户
        self.user = User(username='testuser', email='test@example.com')
        self.user.set_password('password123')
        db.session.add(self.user)
        db.session.commit()
        
        self.client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        })
    
    def tearDown(self):
        """测试后清理"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_api_get_tasks(self):
        """测试获取任务列表API"""
        # 创建测试任务
        task = Task(title='测试任务', user_id=self.user.id)
        db.session.add(task)
        db.session.commit()
        
        response = self.client.get('/api/tasks')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['data'][0]['title'], '测试任务')
    
    def test_api_create_task(self):
        """测试创建任务API"""
        response = self.client.post('/api/tasks',
            data=json.dumps({
                'title': 'API测试任务',
                'description': '通过API创建',
                'priority': 'urgent_important'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['data']['title'], 'API测试任务')
    
    def test_api_create_task_empty_title(self):
        """测试API创建任务空标题"""
        response = self.client.post('/api/tasks',
            data=json.dumps({
                'title': '',
                'description': '描述'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_api_update_task(self):
        """测试更新任务API"""
        task = Task(title='原标题', user_id=self.user.id)
        db.session.add(task)
        db.session.commit()
        
        response = self.client.put(f'/api/tasks/{task.id}',
            data=json.dumps({
                'title': '新标题'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['data']['title'], '新标题')
    
    def test_api_delete_task(self):
        """测试删除任务API"""
        task = Task(title='测试任务', user_id=self.user.id)
        db.session.add(task)
        db.session.commit()
        task_id = task.id
        
        response = self.client.delete(f'/api/tasks/{task_id}')
        
        self.assertEqual(response.status_code, 200)
        
        deleted_task = Task.query.get(task_id)
        self.assertIsNone(deleted_task)
    
    def test_api_complete_task(self):
        """测试完成任务API"""
        task = Task(title='测试任务', user_id=self.user.id)
        db.session.add(task)
        db.session.commit()
        
        response = self.client.patch(f'/api/tasks/{task.id}/complete')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['data']['is_completed'])
    
    def test_api_search_tasks(self):
        """测试搜索任务API"""
        task1 = Task(title='Python学习', user_id=self.user.id)
        task2 = Task(title='Java学习', user_id=self.user.id)
        task3 = Task(title='其他任务', user_id=self.user.id)
        db.session.add_all([task1, task2, task3])
        db.session.commit()
        
        response = self.client.get('/api/tasks/search?keyword=学习')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['count'], 2)


if __name__ == '__main__':
    unittest.main()