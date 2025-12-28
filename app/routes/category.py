"""
分类管理路由
"""
from flask import Blueprint, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Category, Task

category_bp = Blueprint('category', __name__)


@category_bp.route('/categories/create', methods=['POST'])
@login_required
def create_category():
    """创建分类"""
    name = request.form.get('name', '').strip()
    
    if not name:
        flash('分类名称不能为空', 'danger')
        return redirect(url_for('task.task_list'))
    
    if len(name) > 30:
        flash('分类名称不能超过30个字符', 'danger')
        return redirect(url_for('task.task_list'))
    
    # 检查是否已存在同名分类
    existing = Category.query.filter(
        db.or_(
            db.and_(Category.user_id == current_user.id, Category.name == name),
            db.and_(Category.is_preset == True, Category.name == name)
        )
    ).first()
    
    if existing:
        flash('该分类名称已存在', 'warning')
        return redirect(url_for('task.task_list'))
    
    category = Category(name=name, user_id=current_user.id, is_preset=False)
    db.session.add(category)
    db.session.commit()
    
    flash(f'分类 "{name}" 创建成功', 'success')
    return redirect(url_for('task.task_list'))


@category_bp.route('/categories/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
    """删除分类"""
    category = Category.query.get_or_404(category_id)
    
    # 检查权限
    if category.is_preset:
        flash('系统预设分类不能删除', 'danger')
        return redirect(url_for('task.task_list'))
    
    if category.user_id != current_user.id:
        flash('无权删除该分类', 'danger')
        return redirect(url_for('task.task_list'))
    
    # 将该分类下的任务设为未分类
    Task.query.filter_by(category_id=category_id).update({'category_id': None})
    
    name = category.name
    db.session.delete(category)
    db.session.commit()
    
    flash(f'分类 "{name}" 已删除', 'info')
    return redirect(url_for('task.task_list'))


# ==================== API接口 ====================

@category_bp.route('/api/categories', methods=['GET'])
@login_required
def api_get_categories():
    """获取分类列表API"""
    preset_categories = Category.query.filter_by(is_preset=True).all()
    user_categories = Category.query.filter_by(user_id=current_user.id).all()
    
    all_categories = preset_categories + user_categories
    
    return jsonify({
        'data': [category.to_dict() for category in all_categories],
        'count': len(all_categories)
    }), 200


@category_bp.route('/api/categories', methods=['POST'])
@login_required
def api_create_category():
    """创建分类API"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': '无效的请求数据'}), 400
    
    name = data.get('name', '').strip()
    
    if not name:
        return jsonify({'error': '分类名称不能为空'}), 400
    
    if len(name) > 30:
        return jsonify({'error': '分类名称不能超过30个字符'}), 400
    
    # 检查是否已存在同名分类
    existing = Category.query.filter(
        db.or_(
            db.and_(Category.user_id == current_user.id, Category.name == name),
            db.and_(Category.is_preset == True, Category.name == name)
        )
    ).first()
    
    if existing:
        return jsonify({'error': '该分类名称已存在'}), 400
    
    category = Category(name=name, user_id=current_user.id, is_preset=False)
    db.session.add(category)
    db.session.commit()
    
    return jsonify({
        'message': '分类创建成功',
        'data': category.to_dict()
    }), 201


@category_bp.route('/api/categories/<int:category_id>', methods=['DELETE'])
@login_required
def api_delete_category(category_id):
    """删除分类API"""
    category = Category.query.get(category_id)
    
    if not category:
        return jsonify({'error': '分类不存在'}), 404
    
    if category.is_preset:
        return jsonify({'error': '系统预设分类不能删除'}), 403
    
    if category.user_id != current_user.id:
        return jsonify({'error': '无权删除该分类'}), 403
    
    # 将该分类下的任务设为未分类
    Task.query.filter_by(category_id=category_id).update({'category_id': None})
    
    db.session.delete(category)
    db.session.commit()
    
    return jsonify({'message': '分类已删除'}), 200