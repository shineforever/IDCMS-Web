#coding=utf-8

import os
import copy

from flask import render_template, redirect, request, url_for, flash, jsonify
from flask.ext.login import login_required, current_user

from . import task
from .forms import TicketForm, ActionForm
from .sidebar import start_sidebar

from .. import db
from app.models import Task
from app.utils.permission import Permission, permission_validation
from app.utils.utils import init_sidebar, init_checkbox
from app.utils.curd import edit, search

now = 'task'
thead = [(0, u'发布者'), (1, u'标题'), (2, u'任务'), (3, u'机房'), (4, u'创建时间'), 
         (5, u'技术支持'), (6, u'状态')]
check_field = ['title', 'body']
endpoint= '.task'

@task.route('/task/ticket',  methods=['GET', 'POST'])
@login_required
def ticket():
    ticket_form = TicketForm()
    sidebar = copy.deepcopy(start_sidebar)
    sidebar = init_sidebar(sidebar, now, 'put_task')
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
                    'task/ticket.html', sidebar=sidebar, ticket_form=ticket_form, 
                    search_value=search_value, thead=thead, pagination=pagination,
                    endpoint=endpoint, items=items
                )

    if request.method == "POST":
        if request.form['action'] == 'put_task':
            idebar = init_sidebar(sidebar, now,'put_task')
            if ticket_form.validate_on_submit():
                task = Task(
                    author=current_user.username,
                    title=ticket_form.title.data,
                    task=ticket_form.task.data,
                    site=ticket_form.site.data,
                    body=ticket_form.body.data,
                    status=u"审核"
                )
                add_sql = edit(current_user.username, task, "title", record=False )
                add_sql.run('add')
                flash(u'任务添加成功 可以继续添加新的任务')
            else:
                for key in check_field :
                    if ticket_form.errors.get(key, None):
                        flash(ticket_form.errors[key][0])
                        break

    return render_template(
        'task/ticket.html', sidebar=sidebar, thead=thead, ticket_form=ticket_form
    )

@task.route('/task/action/<int:id>',  methods=['GET', 'POST'])
@login_required
def action(id):
    task = Task.query.get_or_404(id)
    action_form = ActionForm()
    if request.method == "POST":
        if action_form.validate_on_submit():
            reply = Reply(
                task_id = task.id,
                user = current_user.alias,
                body = action_form.body.data
            )
            add_sql = edit(current_user.username, reply, "task_id", record=False)
            add_sql.run('add')
            # 回复成功后重定向回改网页
            return redirect(url_for('.action', id=post.id))
        else:
            flash(action_form.errors['body'][0])
    return render_template('task/action.html', sidebar=start_sidebar)

@task.route('/task')
@login_required
def index():
    return render_template('index.html')

@task.route('/task/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
  if request.method == 'POST':
    f = request.files['files[]']
    filename = f.filename
    minetype = f.content_type
    print os.path.join('uploads', filename)
    f.save(os.path.join('uploads', filename))
  return jsonify({"files": [{"name": filename, "minetype": minetype}]})
