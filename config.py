import os

class Config:
    """应用配置类"""
    # 密钥配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # 数据库配置
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASEDIR, 'campus_todo.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 会话配置
    PERMANENT_SESSION_LIFETIME = 1800  # 30分钟超时