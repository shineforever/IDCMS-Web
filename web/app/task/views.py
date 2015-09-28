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

now = 'task'
thead = [(0, u'发布者'), (1, u'标题'), (2, u'任务'), (3, u'机房'), (4, u'创建时间'), 
         (5, u'技术支持'), (6, u'状态')]
endpoint= '.task'

@task.route('/task',  methods=['GET', 'POST'])
@login_required
def task():
    task_form = TaskForm()
    sidebar = copy.deepcopy(start_sidebar)
    sidebar = init_sidebar(sidebar, now,'put_task')
    if request.method == "GET":
        search_value = request.args.get('search', '')
        if search_value:
            sidebar = init_sidebar(sidebar, now, "my_task")
            page = int(request.args.get('page', 1))
            result = search(Task, 'title' , search_value)
            result = result.search_return()
            if result:
                pagination = result.paginate(page, 100, False)
                items = pagination.items
                return render_template(
                    'task/task.html', sidebar=sidebar, task_form=task_form, 
                    search_value=search_value, thead=thead, pagination=pagination,
                    endpoint=endpoint, items=items
                )
    if request.method == "POST":
        if request.form['action'] == 'put_task':
            idebar = init_sidebar(sidebar, now,'put_task')
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
        'task/task.html', thead=thead, task_form=task_form, sidebar=sidebar
    )
