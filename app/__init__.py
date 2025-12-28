"""
校园待办清单系统 - 应用工厂
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

# 初始化扩展
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录后再访问该页面'
login_manager.login_message_category = 'warning'

def create_app(config_class=Config):
    """应用工厂函数"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    
    # 注册蓝图
    from app.routes.auth import auth_bp
    from app.routes.task import task_bp
    from app.routes.category import category_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(task_bp)
    app.register_blueprint(category_bp)
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    return app