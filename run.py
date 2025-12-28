"""
校园待办清单系统 - 启动脚本
"""
from app import create_app, db
from app.models import User, Task, Category

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """Flask shell 上下文"""
    return {
        'db': db,
        'User': User,
        'Task': Task,
        'Category': Category
    }

def init_database():
    """初始化数据库和预设分类"""
    with app.app_context():
        db.create_all()
        
        # 检查是否已有预设分类
        if Category.query.filter_by(is_preset=True).count() == 0:
            preset_categories = [
                Category(name='作业', is_preset=True, user_id=None),
                Category(name='考试', is_preset=True, user_id=None),
                Category(name='社团', is_preset=True, user_id=None),
                Category(name='生活', is_preset=True, user_id=None)
            ]
            for category in preset_categories:
                db.session.add(category)
            db.session.commit()
            print('预设分类初始化完成')

if __name__ == '__main__':
    init_database()
    app.run(debug=True, host='0.0.0.0', port=5000)