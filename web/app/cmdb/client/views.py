#coding=utf-8
# 客户管理

from app.models import Client, Rack, IpSubnet, IpPool, Cabinet

from ..same import *
from .forms import ClientForm
from .custom import CustomValidator

now = "client"
start_thead = [
    [0, u'客户','username', False, False], [1,u'联系方式', 'contact', False, False], 
    [2, u'备注' ,'remark', False, True], [3, u'操作', 'setting', True],
    [4, u'批量处理', 'batch', True]
]
endpoint = '.client'
check_item = [(Rack, u'机架'), (IpSubnet, u'IP子网'), (IpPool, u'IP池'),
              (Cabinet, u'机柜表')]

@cmdb.route('/cmdb/client',  methods=['GET', 'POST'])
@login_required
def client():
    role_Permission = getattr(Permission, current_user.role)
    client_form = ClientForm()
    sidebar = copy.deepcopy(start_sidebar)
    thead = copy.deepcopy(start_thead)
    sidebar = init_sidebar(sidebar, now,'edititem')
    search_value = ''

    if request.method == "GET":
        search_value = request.args.get('search', '') 
        checkbox = request.args.getlist('hidden') or request.args.get('hiddens', '') 
        if search_value:
            thead = init_checkbox(thead, checkbox)
            sidebar = init_sidebar(sidebar, now, "edititem")
            page = int(request.args.get('page', 1)) 
            result = search(Client, 'username' , search_value)
            result = result.search_return()
            if result:
                pagination = result.paginate(page, 100, False)
                items = pagination.items
                return render_template(
                    'cmdb/item.html', sidebar=sidebar, item_form=client_form,
                    search_value=search_value, checkbox=str(checkbox), thead=thead,  
                    pagination=pagination, endpoint=endpoint, items=items
                ) 

    if request.method == "POST" and role_Permission >= Permission.ALTER:
        sidebar = init_sidebar(sidebar, now, "additem")
        if client_form.validate_on_submit():
            client = Client(
                username=client_form.username.data,
                contact=client_form.contact.data,
                remark=client_form.remark.data
            )
            add_sql = edit(current_user.username, client, "client" )
            add_sql.run('add')
            flash(u'客户添加成功')
        else:
            for thead in start_thead:
                key = thead[2]
                if client_form.errors.get(key, None):
                    flash(client_form.errors[key][0])
                    break

    return render_template(
        'cmdb/item.html',sidebar=sidebar, item_form=client_form, 
        search_value=search_value, thead=thead
    )

@cmdb.route('/cmdb/client/delete',  methods=['POST'])
@login_required
@permission_validation(Permission.ALTER)
def client_delete():
    del_id = int(request.form["id"])
    client = Client.query.filter_by(id=del_id).first()
    if client:
        for item in check_item:
            if getattr(item[0],'query').filter_by(client=client.username).first():
                return u"删除失败 *** %s *** 有%s在使用" % (client.username, item[1])
        delete_sql = edit(current_user.username, client, "client", client.username)
        delete_sql.run('delete')
        return "OK"
    return u"删除失败 没有找到这个客户"

@cmdb.route('/cmdb/client/change',  methods=['POST'])
@login_required
@permission_validation(Permission.ALTER)
def client_change():
    change_id = int(request.form["id"])
    item = request.form["item"]
    value = request.form["value"]
    client = Client.query.filter_by(id=change_id).first()
    if client:
        verify = CustomValidator(item, change_id, value)
        result = verify.validate_return()
        if result == "OK":
            change_sql = edit(current_user.username, client, item, value)
            change_sql.run('change')
            return "OK"
        return result 
    return u"更改失败没有找到该客户"

# 批量删除
@cmdb.route('/cmdb/client/batchdelete',  methods=['POST'])
@login_required
@permission_validation(Permission.ALTER)
def client_batch_delete():
    list_id = eval(request.form["list_id"])

    for id in list_id:
        client = Client.query.filter_by(id=id).first()
        if client:
            for item in check_item:
                if getattr(item[0],'query').filter_by(client=client.username).first():
                    return u"删除失败 *** %s *** 有%s在使用" % (client.username, item[1])
        else:
            return u"删除失败没有这些客户"

    for id in list_id:
        client = Client.query.filter_by(id=id).first()
        delete_sql = edit(current_user.username, client, "client", client.username)
        delete_sql.run('delete')
    return "OK"

# 批量修改
@cmdb.route('/cmdb/client/batchchange',  methods=['POST'])
@login_required
@permission_validation(Permission.ALTER)
def client_batch_change():
    list_id = eval(request.form["list_id"])
    item = request.form["item"]
    value = request.form["value"]

    for id in list_id:
        client = Client.query.filter_by(id=id).first()
        if client:
            verify = CustomValidator(item, id, value)
            result = verify.validate_return()
            if not result == "OK":
                return result
        else:
            return u"更改失败没有找到这些客户"

    for id in list_id:
        client = Client.query.filter_by(id=id).first()
        change_sql = edit(current_user.username, client, item, value)
        change_sql.run('change')
    return "OK"
