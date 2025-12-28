"""
用户认证路由
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def index():
    """首页路由"""
    if current_user.is_authenticated:
        return redirect(url_for('task.task_list'))
    return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    if current_user.is_authenticated:
        return redirect(url_for('task.task_list'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # 输入验证
        errors = []
        
        if not username:
            errors.append('用户名不能为空')
        elif len(username) < 3 or len(username) > 50:
            errors.append('用户名长度应为3-50个字符')
        elif User.query.filter_by(username=username).first():
            errors.append('用户名已被注册')
        
        if not email:
            errors.append('邮箱不能为空')
        elif User.query.filter_by(email=email).first():
            errors.append('邮箱已被注册')
        
        if not password:
            errors.append('密码不能为空')
        elif len(password) < 6:
            errors.append('密码长度至少6个字符')
        
        if password != confirm_password:
            errors.append('两次输入的密码不一致')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('register.html', username=username, email=email)
        
        # 创建用户
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('注册成功，请登录', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if current_user.is_authenticated:
        return redirect(url_for('task.task_list'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        # 验证用户
        user = User.query.filter_by(username=username).first()
        
        if user is None or not user.check_password(password):
            flash('用户名或密码错误', 'danger')
            return render_template('login.html', username=username)
        
        # 登录用户
        login_user(user, remember=bool(remember))
        
        # 跳转到之前请求的页面或任务列表
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('task.task_list')
        
        flash(f'欢迎回来，{user.username}！', 'success')
        return redirect(next_page)
    
    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """用户登出"""
    logout_user()
    flash('已成功退出登录', 'info')
    return redirect(url_for('auth.login'))


# ==================== API接口 ====================

@auth_bp.route('/api/users/register', methods=['POST'])
def api_register():
    """用户注册API"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '无效的请求数据'}), 400
    
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    # 验证
    if not username or len(username) < 3 or len(username) > 50:
        return jsonify({'error': '用户名长度应为3-50个字符'}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({'error': '用户名已被注册'}), 400
    
    if not email:
        return jsonify({'error': '邮箱不能为空'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'error': '邮箱已被注册'}), 400
    
    if not password or len(password) < 6:
        return jsonify({'error': '密码长度至少6个字符'}), 400
    
    # 创建用户
    user = User(username=username, email=email)
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': '注册成功',
        'data': user.to_dict()
    }), 201


@auth_bp.route('/api/users/login', methods=['POST'])
def api_login():
    """用户登录API"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '无效的请求数据'}), 400
    
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    user = User.query.filter_by(username=username).first()
    
    if user is None or not user.check_password(password):
        return jsonify({'error': '用户名或密码错误'}), 401
    
    login_user(user)
    
    return jsonify({
        'message': '登录成功',
        'data': user.to_dict()
    }), 200


@auth_bp.route('/api/users/logout', methods=['POST'])
@login_required
def api_logout():
    """用户登出API"""
    logout_user()
    return jsonify({'message': '已成功退出登录'}), 200