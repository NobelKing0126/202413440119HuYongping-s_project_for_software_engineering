第一步：打开命令行并进入项目目录

1.1 打开命令提示符

按 Win + R，输入 cmd，回车

1.2 进入项目文件夹

假设你的项目在桌面，输入：

cd C:\Users\你的用户名\Desktop\campus_todo

注意： 把"你的用户名"替换成你电脑的实际用户名

验证是否进入成功：

dir

应该能看到 app、requirements.txt、run.py 等文件

第二步：创建虚拟环境

2.1 什么是虚拟环境？

虚拟环境是一个独立的Python环境，可以避免不同项目之间的依赖冲突。

2.2 创建虚拟环境

在命令行中输入：

python -m venv venv

执行后会发生什么：

项目文件夹中会出现一个 venv 文件夹

这个文件夹包含了独立的Python环境

2.3 激活虚拟环境

Windows系统：

venv\Scripts\activate

Mac/Linux系统：


source venv/bin/activate

激活成功的标志：

命令行前面会出现 (venv) 字样，像这样：


(venv) C:\Users\你的用户名\Desktop\campus_todo>

第三步：安装项目依赖

3.1 安装依赖包

确保虚拟环境已激活（命令行前有 (venv)），然后输入：

pip install -r requirements.txt

3.2 等待安装完成

你会看到类似这样的输出：


Collecting Flask==2.3.3
  Downloading Flask-2.3.3-py3-none-any.whl
Collecting Flask-SQLAlchemy==3.0.5
  ...
Successfully installed Flask-2.3.3 Flask-SQLAlchemy-3.0.5 ...

3.3 验证安装成功

pip list

应该能看到 Flask、Flask-SQLAlchemy 等包

第四步：运行项目
4.1 启动应用
确保你在项目根目录（campus_todo），输入：


python run.py

4.2 成功启动的标志
你会看到类似这样的输出：


预设分类初始化完成
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.x.x:5000
Press CTRL+C to quit

4.3 访问系统

打开浏览器（Chrome、Edge等），在地址栏输入：


http://localhost:5000

或者：

http://127.0.0.1:5000

第五步：使用系统

5.1 注册账号

首次访问会跳转到登录页

点击"立即注册"

填写用户名、邮箱、密码

点击注册按钮

5.2 登录系统

输入刚才注册的用户名和密码

点击登录

进入任务列表主页

5.3 创建任务

点击右上角"新建任务"按钮

填写任务标题（必填）

可选填写描述、截止日期、优先级、分类

点击"创建任务"

5.4 管理任务

完成任务：点击任务前的圆圈按钮

编辑任务：点击铅笔图标

删除任务：点击垃圾桶图标

常见问题解决

问题1：提示"python不是内部命令"

解决方法：

重新安装Python，安装时勾选"Add Python to PATH"

或者尝试使用 python3 代替 python

问题2：pip install报错

解决方法：

python -m pip install --upgrade pip

pip install -r requirements.txt

问题3：端口5000被占用

解决方法：

修改 run.py 最后一行，更换端口：

app.run(debug=True, host='0.0.0.0', port=5001)

然后访问 http://localhost:5001

问题4：页面显示乱码或样式丢失

解决方法：

确保所有文件使用 UTF-8 编码保存

检查 static/css/style.css 文件是否存在

问题5：数据库错误

解决方法：

删除项目目录下的 campus_todo.db 文件，重新运行：

python run.py

停止和重启项目

停止项目

在命令行中按 Ctrl + C

重启项目


# 如果虚拟环境未激活，先激活
venv\Scripts\activate

# 再次运行
python run.py
