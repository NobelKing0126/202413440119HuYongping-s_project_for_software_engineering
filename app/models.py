"""
校园待办清单系统 - 数据模型
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

class User(UserMixin, db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    tasks = db.relationship('Task', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    categories = db.relationship('Category', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """设置密码（加密存储）"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>'


class Category(db.Model):
    """分类模型"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    is_preset = db.Column(db.Boolean, default=False)  # 是否为系统预设分类
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    tasks = db.relationship('Task', backref='category', lazy='dynamic')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'is_preset': self.is_preset,
            'user_id': self.user_id,
            'task_count': self.tasks.count()
        }
    
    def __repr__(self):
        return f'<Category {self.name}>'


class Task(db.Model):
    """任务模型"""
    __tablename__ = 'tasks'
    
    # 优先级常量
    PRIORITY_URGENT_IMPORTANT = 'urgent_important'          # 紧急重要
    PRIORITY_IMPORTANT_NOT_URGENT = 'important_not_urgent'  # 重要不紧急
    PRIORITY_URGENT_NOT_IMPORTANT = 'urgent_not_important'  # 紧急不重要
    PRIORITY_NOT_URGENT_NOT_IMPORTANT = 'not_urgent_not_important'  # 不紧急不重要
    
    PRIORITY_CHOICES = [
        (PRIORITY_URGENT_IMPORTANT, '紧急重要'),
        (PRIORITY_IMPORTANT_NOT_URGENT, '重要不紧急'),
        (PRIORITY_URGENT_NOT_IMPORTANT, '紧急不重要'),
        (PRIORITY_NOT_URGENT_NOT_IMPORTANT, '不紧急不重要')
    ]
    
    PRIORITY_LABELS = dict(PRIORITY_CHOICES)
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    deadline = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.String(30), default=PRIORITY_IMPORTANT_NOT_URGENT)
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 外键
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    
    @property
    def priority_label(self):
        """获取优先级中文标签"""
        return self.PRIORITY_LABELS.get(self.priority, '未知')
    
    @property
    def is_overdue(self):
        """判断是否逾期"""
        if self.deadline and not self.is_completed:
            return datetime.utcnow() > self.deadline
        return False
    
    @property
    def is_today(self):
        """判断是否为今日任务"""
        if self.deadline:
            today = datetime.utcnow().date()
            return self.deadline.date() == today
        return False
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'priority': self.priority,
            'priority_label': self.priority_label,
            'is_completed': self.is_completed,
            'is_overdue': self.is_overdue,
            'is_today': self.is_today,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Task {self.title}>'


@login_manager.user_loader
def load_user(user_id):
    """Flask-Login 用户加载回调"""
    return User.query.get(int(user_id))