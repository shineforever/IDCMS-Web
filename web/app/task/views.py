#coding=utf-8

import copy
import datetime

from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_required, current_user

from . import task
from .forms import TaskForm
from .sidebar import start_sidebar

from .. import db
from app.models import Task
from app.utils.permission import Permission, permission_validation
from app.utils.utils import init_sidebar, init_checkbox
from app.utils.curd import edit, search

# 初始化参数
sidebar_name = 'task'

thead = [(0, u'标题'), (1, u'任务'), (2, u'机房'), (3, u'创建时间'), (4, u'状态')]

@task.route('/task',  methods=['GET', 'POST'])
@login_required
def task():
    task_form = TaskForm()
    sidebar = copy.deepcopy(start_sidebar)
    sidebar = init_sidebar(sidebar, sidebar_name,'put_task')
    if request.method == "GET":
        search_value = request.args.get('search', '')
        if search_value:
            sidebar = init_sidebar(sidebar, sidebar_name, "my_task")
            page = int(request.args.get('page', 1))
            # search 方法处理搜索
            result = search(Sales, 'username' , search_value)
            result = result.search_return()
            if result:
                # 100 是默认页面显示数量
                pagination = result.paginate(page, 100, False)
                items = pagination.items
                return render_template(
                    'cmdb/item.html', thead=thead, endpoint=endpoint, set_page=set_page,
                    item_form=sales_form, sidebar=sidebar, sidebar_name=sidebar_name,
                    pagination=pagination, search_value=search_value, items=items, checkbox=str(checkbox)
                )
    if request.method == "POST":
        if request.form['action'] == 'put_task':
            idebar = init_sidebar(sidebar, sidebar_name,'put_task')
            date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            task = Task(
                author=current_user.username,
                title=task_form.title.data,
                task=task_form.task.data,
                site=task_form.site.data,
                body=task_form.body.data,
                date=date,
                status=u"审核"
            )
            add_sql = edit(current_user.username, task, "title", record=False )
            add_sql.run('add')
            flash(u'任务添加成功 可以继续添加新的任务')

    return render_template(
        'task/task.html', thead=thead, task_form=task_form, sidebar=sidebar, 
        sidebar_name=sidebar_name
    )
