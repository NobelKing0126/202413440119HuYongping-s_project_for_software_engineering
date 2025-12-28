"""
单元测试 - 数据模型测试
"""
import unittest
from datetime import datetime, timedelta
from app import create_app, db
from app.models import User, Task, Category
from config import Config


class TestConfig(Config):
    """测试配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


class TestUserModel(unittest.TestCase):
    """用户模型测试"""
    
    def setUp(self):
        """测试前准备"""
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self):
        """测试后清理"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_password_hashing(self):
        """测试密码加密"""
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        
        self.assertFalse(user.check_password('wrongpassword'))
        self.assertTrue(user.check_password('password123'))
        self.assertNotEqual(user.password_hash, 'password123')
    
    def test_user_creation(self):
        """测试用户创建"""
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        
        db.session.add(user)
        db.session.commit()
        
        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
    
    def test_user_unique_username(self):
        """测试用户名唯一性"""
        user1 = User(username='testuser', email='test1@example.com')
        user1.set_password('password123')
        db.session.add(user1)
        db.session.commit()
        
        user2 = User(username='testuser', email='test2@example.com')
        user2.set_password('password456')
        db.session.add(user2)
        
        with self.assertRaises(Exception):
            db.session.commit()
    
    def test_user_to_dict(self):
        """测试用户转字典"""
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        user_dict = user.to_dict()
        
        self.assertEqual(user_dict['username'], 'testuser')
        self.assertEqual(user_dict['email'], 'test@example.com')
        self.assertNotIn('password_hash', user_dict)


class TestTaskModel(unittest.TestCase):
    """任务模型测试"""
    
    def setUp(self):
        """测试前准备"""
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # 创建测试用户
        self.user = User(username='testuser', email='test@example.com')
        self.user.set_password('password123')
        db.session.add(self.user)
        db.session.commit()
    
    def tearDown(self):
        """测试后清理"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_task_creation(self):
        """测试任务创建"""
        task = Task(
            title='测试任务',
            description='这是一个测试任务',
            user_id=self.user.id
        )
        db.session.add(task)
        db.session.commit()
        
        self.assertIsNotNone(task.id)
        self.assertEqual(task.title, '测试任务')
        self.assertFalse(task.is_completed)
    
    def test_task_priority_label(self):
        """测试优先级标签"""
        task = Task(
            title='测试任务',
            priority=Task.PRIORITY_URGENT_IMPORTANT,
            user_id=self.user.id
        )
        
        self.assertEqual(task.priority_label, '紧急重要')
    
    def test_task_is_overdue(self):
        """测试逾期判断"""
        # 已过期任务
        overdue_task = Task(
            title='逾期任务',
            deadline=datetime.utcnow() - timedelta(days=1),
            user_id=self.user.id
        )
        
        self.assertTrue(overdue_task.is_overdue)
        
        # 未过期任务
        future_task = Task(
            title='未来任务',
            deadline=datetime.utcnow() + timedelta(days=1),
            user_id=self.user.id
        )
        
        self.assertFalse(future_task.is_overdue)
        
        # 已完成的逾期任务不算逾期
        completed_task = Task(
            title='已完成任务',
            deadline=datetime.utcnow() - timedelta(days=1),
            is_completed=True,
            user_id=self.user.id
        )
        
        self.assertFalse(completed_task.is_overdue)
    
    def test_task_is_today(self):
        """测试今日任务判断"""
        today_task = Task(
            title='今日任务',
            deadline=datetime.utcnow(),
            user_id=self.user.id
        )
        
        self.assertTrue(today_task.is_today)
        
        tomorrow_task = Task(
            title='明日任务',
            deadline=datetime.utcnow() + timedelta(days=1),
            user_id=self.user.id
        )
        
        self.assertFalse(tomorrow_task.is_today)
    
    def test_task_to_dict(self):
        """测试任务转字典"""
        task = Task(
            title='测试任务',
            description='描述',
            priority=Task.PRIORITY_IMPORTANT_NOT_URGENT,
            user_id=self.user.id
        )
        db.session.add(task)
        db.session.commit()
        
        task_dict = task.to_dict()
        
        self.assertEqual(task_dict['title'], '测试任务')
        self.assertEqual(task_dict['priority'], 'important_not_urgent')
        self.assertEqual(task_dict['priority_label'], '重要不紧急')
        self.assertFalse(task_dict['is_completed'])


class TestCategoryModel(unittest.TestCase):
    """分类模型测试"""
    
    def setUp(self):
        """测试前准备"""
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # 创建测试用户
        self.user = User(username='testuser', email='test@example.com')
        self.user.set_password('password123')
        db.session.add(self.user)
        db.session.commit()
    
    def tearDown(self):
        """测试后清理"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_category_creation(self):
        """测试分类创建"""
        category = Category(
            name='作业',
            is_preset=True
        )
        db.session.add(category)
        db.session.commit()
        
        self.assertIsNotNone(category.id)
        self.assertEqual(category.name, '作业')
        self.assertTrue(category.is_preset)
    
    def test_category_task_count(self):
        """测试分类任务计数"""
        category = Category(name='测试分类', user_id=self.user.id)
        db.session.add(category)
        db.session.commit()
        
        # 添加任务
        task1 = Task(title='任务1', category_id=category.id, user_id=self.user.id)
        task2 = Task(title='任务2', category_id=category.id, user_id=self.user.id)
        db.session.add_all([task1, task2])
        db.session.commit()
        
        category_dict = category.to_dict()
        self.assertEqual(category_dict['task_count'], 2)


if __name__ == '__main__':
    unittest.main()