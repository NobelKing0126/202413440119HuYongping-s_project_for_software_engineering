/**
 * 校园待办清单系统 - 前端脚本
 * 作者：软件工程课程项目
 * 日期：2025年1月
 */

// ==================== 文档加载完成后执行 ====================
document.addEventListener('DOMContentLoaded', function() {
    // 初始化工具提示
    initTooltips();
    
    // 初始化字符计数器
    initCharacterCounters();
    
    // 初始化日期时间选择器默认值
    initDatetimePicker();
    
    // 初始化自动关闭提示框
    initAutoCloseAlerts();
    
    // 绑定键盘快捷键
    initKeyboardShortcuts();
});

// ==================== 工具提示初始化 ====================
function initTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// ==================== 字符计数器 ====================
function initCharacterCounters() {
    // 标题字符计数
    var titleInput = document.getElementById('title');
    var titleCount = document.getElementById('titleCount');
    
    if (titleInput && titleCount) {
        titleCount.textContent = titleInput.value.length;
        
        titleInput.addEventListener('input', function() {
            titleCount.textContent = this.value.length;
            
            // 超出限制时显示警告
            if (this.value.length > 45) {
                titleCount.classList.add('text-warning');
            } else {
                titleCount.classList.remove('text-warning');
            }
            
            if (this.value.length >= 50) {
                titleCount.classList.remove('text-warning');
                titleCount.classList.add('text-danger');
            } else {
                titleCount.classList.remove('text-danger');
            }
        });
    }
    
    // 描述字符计数
    var descInput = document.getElementById('description');
    var descCount = document.getElementById('descCount');
    
    if (descInput && descCount) {
        descCount.textContent = descInput.value.length;
        
        descInput.addEventListener('input', function() {
            descCount.textContent = this.value.length;
            
            if (this.value.length > 450) {
                descCount.classList.add('text-warning');
            } else {
                descCount.classList.remove('text-warning');
            }
            
            if (this.value.length >= 500) {
                descCount.classList.remove('text-warning');
                descCount.classList.add('text-danger');
            } else {
                descCount.classList.remove('text-danger');
            }
        });
    }
}

// ==================== 日期时间选择器 ====================
function initDatetimePicker() {
    var deadlineInput = document.getElementById('deadline');
    
    if (deadlineInput && !deadlineInput.value) {
        // 设置最小日期为当前时间
        var now = new Date();
        var year = now.getFullYear();
        var month = String(now.getMonth() + 1).padStart(2, '0');
        var day = String(now.getDate()).padStart(2, '0');
        var hours = String(now.getHours()).padStart(2, '0');
        var minutes = String(now.getMinutes()).padStart(2, '0');
        
        deadlineInput.min = `${year}-${month}-${day}T${hours}:${minutes}`;
    }
    
    // 日期选择验证
    if (deadlineInput) {
        deadlineInput.addEventListener('change', function() {
            var selectedDate = new Date(this.value);
            var now = new Date();
            
            if (selectedDate < now) {
                // 显示警告但允许选择（用于补录历史任务）
                showToast('提示：您选择的是过去的日期', 'warning');
            }
        });
    }
}

// ==================== 自动关闭提示框 ====================
function initAutoCloseAlerts() {
    var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    
    alerts.forEach(function(alert) {
        setTimeout(function() {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000); // 5秒后自动关闭
    });
}

// ==================== 键盘快捷键 ====================
function initKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + N: 新建任务
        if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
            e.preventDefault();
            var createBtn = document.querySelector('a[href*="create"]');
            if (createBtn) {
                window.location.href = createBtn.href;
            }
        }
        
        // Ctrl/Cmd + F: 聚焦搜索框
        if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
            var searchInput = document.querySelector('input[name="search"]');
            if (searchInput) {
                e.preventDefault();
                searchInput.focus();
            }
        }
        
        // Escape: 关闭模态框
        if (e.key === 'Escape') {
            var modals = document.querySelectorAll('.modal.show');
            modals.forEach(function(modal) {
                var bsModal = bootstrap.Modal.getInstance(modal);
                if (bsModal) {
                    bsModal.hide();
                }
            });
        }
    });
}

// ==================== 任务排序 ====================
function sortTasks(sortBy) {
    var url = new URL(window.location.href);
    url.searchParams.set('sort', sortBy);
    window.location.href = url.toString();
}

// ==================== 删除确认 ====================
function confirmDelete(taskId, taskTitle) {
    document.getElementById('deleteTaskTitle').textContent = taskTitle;
    document.getElementById('deleteForm').action = '/tasks/' + taskId + '/delete';
    
    var deleteModal = new bootstrap.Modal(document.getElementById('deleteModal'));
    deleteModal.show();
}

// ==================== 删除分类确认 ====================
function confirmDeleteCategory(categoryId, categoryName) {
    if (confirm('确定要删除分类 "' + categoryName + '" 吗？\n该分类下的任务将变为"未分类"。')) {
        var form = document.createElement('form');
        form.method = 'POST';
        form.action = '/categories/' + categoryId + '/delete';
        document.body.appendChild(form);
        form.submit();
    }
}

// ==================== AJAX完成任务 ====================
function toggleTaskComplete(taskId, button) {
    // 添加加载状态
    var originalContent = button.innerHTML;
    button.innerHTML = '<span class="loading"></span>';
    button.disabled = true;
    
    fetch('/tasks/' + taskId + '/complete', {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
        }
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(data) {
        if (data.success) {
            // 更新按钮状态
            if (data.is_completed) {
                button.classList.remove('btn-outline-secondary');
                button.classList.add('btn-success');
                button.innerHTML = '<i class="bi bi-check-lg"></i>';
            } else {
                button.classList.remove('btn-success');
                button.classList.add('btn-outline-secondary');
                button.innerHTML = '<i class="bi bi-circle"></i>';
            }
            
            // 更新任务项样式
            var taskItem = button.closest('.task-item');
            var taskTitle = taskItem.querySelector('.task-title');
            
            if (data.is_completed) {
                taskItem.classList.add('completed');
                taskTitle.classList.add('text-decoration-line-through', 'text-muted');
            } else {
                taskItem.classList.remove('completed');
                taskTitle.classList.remove('text-decoration-line-through', 'text-muted');
            }
            
            // 显示提示
            showToast(data.is_completed ? '任务已完成' : '任务已恢复', 'success');
        } else {
            button.innerHTML = originalContent;
            showToast('操作失败，请重试', 'danger');
        }
    })
    .catch(function(error) {
        console.error('Error:', error);
        button.innerHTML = originalContent;
        showToast('网络错误，请重试', 'danger');
    })
    .finally(function() {
        button.disabled = false;
    });
}

// ==================== Toast提示 ====================
function showToast(message, type) {
    type = type || 'info';
    
    // 创建toast容器（如果不存在）
    var toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toastContainer';
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        toastContainer.style.zIndex = '1100';
        document.body.appendChild(toastContainer);
    }
    
    // 创建toast元素
    var toastId = 'toast_' + Date.now();
    var iconMap = {
        'success': 'bi-check-circle-fill text-success',
        'danger': 'bi-exclamation-triangle-fill text-danger',
        'warning': 'bi-exclamation-circle-fill text-warning',
        'info': 'bi-info-circle-fill text-info'
    };
    
    var toastHtml = `
        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <i class="bi ${iconMap[type]} me-2"></i>
                <strong class="me-auto">提示</strong>
                <small>刚刚</small>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    var toastElement = document.getElementById(toastId);
    var toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: 3000
    });
    
    toast.show();
    
    // 移除已关闭的toast
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}

// ==================== 表单验证 ====================
function validateTaskForm(form) {
    var title = form.querySelector('#title');
    var isValid = true;
    
    // 验证标题
    if (!title.value.trim()) {
        showFieldError(title, '任务标题不能为空');
        isValid = false;
    } else if (title.value.length > 50) {
        showFieldError(title, '任务标题不能超过50个字符');
        isValid = false;
    } else {
        clearFieldError(title);
    }
    
    return isValid;
}

function showFieldError(field, message) {
    field.classList.add('is-invalid');
    
    var feedback = field.parentElement.querySelector('.invalid-feedback');
    if (!feedback) {
        feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        field.parentElement.appendChild(feedback);
    }
    feedback.textContent = message;
}

function clearFieldError(field) {
    field.classList.remove('is-invalid');
    
    var feedback = field.parentElement.querySelector('.invalid-feedback');
    if (feedback) {
        feedback.remove();
    }
}

// ==================== 搜索功能增强 ====================
function initSearchAutocomplete() {
    var searchInput = document.querySelector('input[name="search"]');
    
    if (searchInput) {
        var debounceTimer;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            
            var query = this.value.trim();
            
            if (query.length >= 2) {
                debounceTimer = setTimeout(function() {
                    // 可以在这里添加搜索建议功能
                    console.log('Searching for:', query);
                }, 300);
            }
        });
    }
}

// ==================== 本地存储工具 ====================
var Storage = {
    set: function(key, value) {
        try {
            localStorage.setItem('campus_todo_' + key, JSON.stringify(value));
        } catch (e) {
            console.error('Storage set error:', e);
        }
    },
    
    get: function(key, defaultValue) {
        try {
            var value = localStorage.getItem('campus_todo_' + key);
            return value ? JSON.parse(value) : defaultValue;
        } catch (e) {
            console.error('Storage get error:', e);
            return defaultValue;
        }
    },
    
    remove: function(key) {
        try {
            localStorage.removeItem('campus_todo_' + key);
        } catch (e) {
            console.error('Storage remove error:', e);
        }
    }
};

// ==================== 主题切换（可选功能） ====================
function toggleDarkMode() {
    var body = document.body;
    var isDark = body.classList.toggle('dark-mode');
    Storage.set('darkMode', isDark);
}

// 初始化主题
function initTheme() {
    var isDark = Storage.get('darkMode', false);
    if (isDark) {
        document.body.classList.add('dark-mode');
    }
}

// ==================== 导出功能（可选） ====================
function exportTasks(format) {
    format = format || 'json';
    
    fetch('/api/tasks')
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            var content;
            var filename;
            var type;
            
            if (format === 'json') {
                content = JSON.stringify(data.data, null, 2);
                filename = 'tasks_' + new Date().toISOString().slice(0, 10) + '.json';
                type = 'application/json';
            } else if (format === 'csv') {
                content = convertToCSV(data.data);
                filename = 'tasks_' + new Date().toISOString().slice(0, 10) + '.csv';
                type = 'text/csv';
            }
            
            downloadFile(content, filename, type);
        })
        .catch(function(error) {
            console.error('Export error:', error);
            showToast('导出失败', 'danger');
        });
}

function convertToCSV(tasks) {
    var headers = ['ID', '标题', '描述', '截止日期', '优先级', '分类', '是否完成', '创建时间'];
    var rows = [headers.join(',')];
    
    tasks.forEach(function(task) {
        var row = [
            task.id,
            '"' + (task.title || '').replace(/"/g, '""') + '"',
            '"' + (task.description || '').replace(/"/g, '""') + '"',
            task.deadline || '',
            task.priority_label || '',
            task.category_name || '',
            task.is_completed ? '是' : '否',
            task.created_at || ''
        ];
        rows.push(row.join(','));
    });
    
    return rows.join('\n');
}

function downloadFile(content, filename, type) {
    var blob = new Blob([content], { type: type + ';charset=utf-8;' });
    var link = document.createElement('a');
    
    if (navigator.msSaveBlob) {
        navigator.msSaveBlob(blob, filename);
    } else {
        link.href = URL.createObjectURL(blob);
        link.download = filename;
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

// ==================== 页面可见性处理 ====================
document.addEventListener('visibilitychange', function() {
    if (document.visibilityState === 'visible') {
        // 页面重新可见时可以刷新数据
        console.log('Page is visible, consider refreshing data');
    }
});

// ==================== 网络状态检测 ====================
window.addEventListener('online', function() {
    showToast('网络已连接', 'success');
});

window.addEventListener('offline', function() {
    showToast('网络已断开，部分功能可能不可用', 'warning');
});

// ==================== 控制台欢迎信息 ====================
console.log('%c校园待办清单系统', 'color: #0d6efd; font-size: 24px; font-weight: bold;');
console.log('%c软件工程课程项目 © 2025', 'color: #6c757d; font-size: 12px;');