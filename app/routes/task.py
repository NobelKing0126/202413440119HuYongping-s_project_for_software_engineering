"""
任务管理路由
"""
from datetime import datetime, date
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Task, Category

task_bp = Blueprint('task', __name__)


# ==================== 页面路由 ====================

@task_bp.route('/tasks')
@login_required
def task_list():
    """任务列表页面"""
    # 获取筛选参数
    filter_type = request.args.get('filter', 'all')
    category_id = request.args.get('category', type=int)
    sort_by = request.args.get('sort', 'created_at')
    search_keyword = request.args.get('search', '').strip()
    
    # 构建查询
    query = Task.query.filter_by(user_id=current_user.id)
    
    # 应用筛选
    if filter_type == 'today':
        today = date.today()
        query = query.filter(
            db.func.date(Task.deadline) == today,
            Task.is_completed == False
        )
    elif filter_type == 'overdue':
        query = query.filter(
            Task.deadline < datetime.utcnow(),
            Task.is_completed == False
        )
    elif filter_type == 'completed':
        query = query.filter(Task.is_completed == True)
    elif filter_type == 'pending':
        query = query.filter(Task.is_completed == False)
    
    # 按分类筛选
    if category_id:
        query = query.filter(Task.category_id == category_id)
    
    # 搜索
    if search_keyword:
        query = query.filter(
            db.or_(
                Task.title.contains(search_keyword),
                Task.description.contains(search_keyword)
            )
        )
    
    # 排序
    if sort_by == 'deadline':
        query = query.order_by(Task.deadline.asc().nullslast())
    elif sort_by == 'priority':
        # 自定义优先级排序
        priority_order = db.case(
            (Task.priority == 'urgent_important', 1),
            (Task.priority == 'important_not_urgent', 2),
            (Task.priority == 'urgent_not_important', 3),
            (Task.priority == 'not_urgent_not_important', 4),
            else_=5
        )
        query = query.order_by(priority_order)
    else:
        query = query.order_by(Task.created_at.desc())
    
    tasks = query.all()
    
    # 获取分类列表
    preset_categories = Category.query.filter_by(is_preset=True).all()
    user_categories = Category.query.filter_by(user_id=current_user.id).all()
    categories = preset_categories + user_categories
    
    # 统计数据
    stats = {
        'total': Task.query.filter_by(user_id=current_user.id).count(),
        'completed': Task.query.filter_by(user_id=current_user.id, is_completed=True).count(),
        'pending': Task.query.filter_by(user_id=current_user.id, is_completed=False).count(),
        'overdue': Task.query.filter(
            Task.user_id == current_user.id,
            Task.deadline < datetime.utcnow(),
            Task.is_completed == False
        ).count()
    }
    
    return render_template(
        'index.html',
        tasks=tasks,
        categories=categories,
        filter_type=filter_type,
        category_id=category_id,
        sort_by=sort_by,
        search_keyword=search_keyword,
        stats=stats,
        priority_choices=Task.PRIORITY_CHOICES
    )


@task_bp.route('/tasks/create', methods=['GET', 'POST'])
@login_required
def create_task():
    """创建任务页面"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        deadline_str = request.form.get('deadline', '').strip()
        priority = request.form.get('priority', Task.PRIORITY_IMPORTANT_NOT_URGENT)
        category_id = request.form.get('category_id', type=int)
        
        # 验证
        errors = []
        
        if not title:
            errors.append('任务标题不能为空')
        elif len(title) > 50:
            errors.append('任务标题不能超过50个字符')
        
        if len(description) > 500:
            errors.append('任务描述不能超过500个字符')
        
        # 解析截止日期
        deadline = None
        if deadline_str:
            try:
                deadline = datetime.fromisoformat(deadline_str)
            except ValueError:
                errors.append('截止日期格式不正确')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template(
                'task_form.html',
                action='create',
                title=title,
                description=description,
                deadline=deadline_str,
                priority=priority,
                category_id=category_id,
                categories=get_user_categories(),
                priority_choices=Task.PRIORITY_CHOICES
            )
        
        # 创建任务
        task = Task(
            title=title,
            description=description,
            deadline=deadline,
            priority=priority,
            category_id=category_id if category_id else None,
            user_id=current_user.id
        )
        
        db.session.add(task)
        db.session.commit()
        
        flash('任务创建成功', 'success')
        return redirect(url_for('task.task_list'))
    
    return render_template(
        'task_form.html',
        action='create',
        categories=get_user_categories(),
        priority_choices=Task.PRIORITY_CHOICES
    )


@task_bp.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    """编辑任务页面"""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        deadline_str = request.form.get('deadline', '').strip()
        priority = request.form.get('priority', Task.PRIORITY_IMPORTANT_NOT_URGENT)
        category_id = request.form.get('category_id', type=int)
        
        # 验证
        errors = []
        
        if not title:
            errors.append('任务标题不能为空')
        elif len(title) > 50:
            errors.append('任务标题不能超过50个字符')
        
        if len(description) > 500:
            errors.append('任务描述不能超过500个字符')
        
        # 解析截止日期
        deadline = None
        if deadline_str:
            try:
                deadline = datetime.fromisoformat(deadline_str)
            except ValueError:
                errors.append('截止日期格式不正确')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template(
                'task_form.html',
                action='edit',
                task=task,
                categories=get_user_categories(),
                priority_choices=Task.PRIORITY_CHOICES
            )
        
        # 更新任务
        task.title = title
        task.description = description
        task.deadline = deadline
        task.priority = priority
        task.category_id = category_id if category_id else None
        
        db.session.commit()
        
        flash('任务更新成功', 'success')
        return redirect(url_for('task.task_list'))
    
    return render_template(
        'task_form.html',
        action='edit',
        task=task,
        categories=get_user_categories(),
        priority_choices=Task.PRIORITY_CHOICES
    )


@task_bp.route('/tasks/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    """删除任务"""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    
    db.session.delete(task)
    db.session.commit()
    
    flash('任务已删除', 'info')
    return redirect(url_for('task.task_list'))


@task_bp.route('/tasks/<int:task_id>/complete', methods=['POST'])
@login_required
def complete_task(task_id):
    """完成/取消完成任务"""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    
    task.is_completed = not task.is_completed
    db.session.commit()
    
    status = '已完成' if task.is_completed else '已恢复为未完成'
    flash(f'任务{status}', 'success')
    
    # 判断是否为AJAX请求
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'is_completed': task.is_completed})
    
    return redirect(url_for('task.task_list'))


# ==================== API接口 ====================

@task_bp.route('/api/tasks', methods=['GET'])
@login_required
def api_get_tasks():
    """获取任务列表API"""
    filter_type = request.args.get('filter', 'all')
    category_id = request.args.get('category', type=int)
    sort_by = request.args.get('sort', 'created_at')
    search_keyword = request.args.get('search', '').strip()
    
    query = Task.query.filter_by(user_id=current_user.id)
    
    # 应用筛选
    if filter_type == 'today':
        today = date.today()
        query = query.filter(
            db.func.date(Task.deadline) == today,
            Task.is_completed == False
        )
    elif filter_type == 'overdue':
        query = query.filter(
            Task.deadline < datetime.utcnow(),
            Task.is_completed == False
        )
    elif filter_type == 'completed':
        query = query.filter(Task.is_completed == True)
    elif filter_type == 'pending':
        query = query.filter(Task.is_completed == False)
    
    if category_id:
        query = query.filter(Task.category_id == category_id)
    
    if search_keyword:
        query = query.filter(
            db.or_(
                Task.title.contains(search_keyword),
                Task.description.contains(search_keyword)
            )
        )
    
    # 排序
    if sort_by == 'deadline':
        query = query.order_by(Task.deadline.asc().nullslast())
    elif sort_by == 'priority':
        priority_order = db.case(
            (Task.priority == 'urgent_important', 1),
            (Task.priority == 'important_not_urgent', 2),
            (Task.priority == 'urgent_not_important', 3),
            (Task.priority == 'not_urgent_not_important', 4),
            else_=5
        )
        query = query.order_by(priority_order)
    else:
        query = query.order_by(Task.created_at.desc())
    
    tasks = query.all()
    
    return jsonify({
        'data': [task.to_dict() for task in tasks],
        'count': len(tasks)
    }), 200


@task_bp.route('/api/tasks/<int:task_id>', methods=['GET'])
@login_required
def api_get_task(task_id):
    """获取单个任务API"""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    
    if not task:
        return jsonify({'error': '任务不存在'}), 404
    
    return jsonify({'data': task.to_dict()}), 200


@task_bp.route('/api/tasks', methods=['POST'])
@login_required
def api_create_task():
    """创建任务API"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '无效的请求数据'}), 400
    
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    deadline_str = data.get('deadline')
    priority = data.get('priority', Task.PRIORITY_IMPORTANT_NOT_URGENT)
    category_id = data.get('category_id')
    
    # 验证
    if not title:
        return jsonify({'error': '任务标题不能为空'}), 400
    
    if len(title) > 50:
        return jsonify({'error': '任务标题不能超过50个字符'}), 400
    
    if description and len(description) > 500:
        return jsonify({'error': '任务描述不能超过500个字符'}), 400
    
    # 解析截止日期
    deadline = None
    if deadline_str:
        try:
            deadline = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': '截止日期格式不正确'}), 400
    
    # 验证分类
    if category_id:
        category = Category.query.get(category_id)
        if not category:
            return jsonify({'error': '分类不存在'}), 400
        if not category.is_preset and category.user_id != current_user.id:
            return jsonify({'error': '无权使用该分类'}), 403
    
    # 创建任务
    task = Task(
        title=title,
        description=description,
        deadline=deadline,
        priority=priority,
        category_id=category_id,
        user_id=current_user.id
    )
    
    db.session.add(task)
    db.session.commit()
    
    return jsonify({
        'message': '任务创建成功',
        'data': task.to_dict()
    }), 201


@task_bp.route('/api/tasks/<int:task_id>', methods=['PUT'])
@login_required
def api_update_task(task_id):
    """更新任务API"""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    
    if not task:
        return jsonify({'error': '任务不存在'}), 404
    
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '无效的请求数据'}), 400
    
    # 更新字段
    if 'title' in data:
        title = data['title'].strip()
        if not title:
            return jsonify({'error': '任务标题不能为空'}), 400
        if len(title) > 50:
            return jsonify({'error': '任务标题不能超过50个字符'}), 400
        task.title = title
    
    if 'description' in data:
        description = data['description'].strip() if data['description'] else ''
        if len(description) > 500:
            return jsonify({'error': '任务描述不能超过500个字符'}), 400
        task.description = description
    
    if 'deadline' in data:
        if data['deadline']:
            try:
                task.deadline = datetime.fromisoformat(data['deadline'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': '截止日期格式不正确'}), 400
        else:
            task.deadline = None
    
    if 'priority' in data:
        task.priority = data['priority']
    
    if 'category_id' in data:
        task.category_id = data['category_id']
    
    db.session.commit()
    
    return jsonify({
        'message': '任务更新成功',
        'data': task.to_dict()
    }), 200


@task_bp.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def api_delete_task(task_id):
    """删除任务API"""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    
    if not task:
        return jsonify({'error': '任务不存在'}), 404
    
    db.session.delete(task)
    db.session.commit()
    
    return jsonify({'message': '任务已删除'}), 200


@task_bp.route('/api/tasks/<int:task_id>/complete', methods=['PATCH'])
@login_required
def api_complete_task(task_id):
    """完成任务API"""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    
    if not task:
        return jsonify({'error': '任务不存在'}), 404
    
    task.is_completed = not task.is_completed
    db.session.commit()
    
    return jsonify({
        'message': '任务状态已更新',
        'data': task.to_dict()
    }), 200


@task_bp.route('/api/tasks/search', methods=['GET'])
@login_required
def api_search_tasks():
    """搜索任务API"""
    keyword = request.args.get('keyword', '').strip()
    
    if not keyword:
        return jsonify({'error': '请输入搜索关键词'}), 400
    
    tasks = Task.query.filter(
        Task.user_id == current_user.id,
        db.or_(
            Task.title.contains(keyword),
            Task.description.contains(keyword)
        )
    ).order_by(Task.created_at.desc()).all()
    
    return jsonify({
        'data': [task.to_dict() for task in tasks],
        'count': len(tasks),
        'keyword': keyword
    }), 200


# ==================== 辅助函数 ====================

def get_user_categories():
    """获取用户可用的分类列表"""
    preset_categories = Category.query.filter_by(is_preset=True).all()
    user_categories = Category.query.filter_by(user_id=current_user.id).all()
    return preset_categories + user_categories