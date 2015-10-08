#coding=utf-8
# IP子网管理

from app.models import IpSubnet, IpPool

from ..same import *
from .forms import IpSubnetForm
from .custom import CustomValidator

now = "ipsubnet"
start_thead = [
    [0, u'IP子网','subnet', False, False], [1, u'子网掩码','netmask', False, False],
    [2,u'起始IP', 'start_ip', False, False], [4,u'结束IP', 'end_ip', False, False],
    [4, u'所属机房', 'site', False, True], [5, u'销售代表', 'sales', False, True], 
    [6, u'使用用户', 'client', False, True], [7, u'开通时间' ,'start_date', False, True], 
    [8, u'到期时间' ,'expire_date', False, True], [9, u'备注' ,'remark', False],
    [10, u'操作', "setting", True], [11, u'批量处理', 'batch', True]
]
endpoint = '.ipsubnet'

@cmdb.route('/cmdb/ipsubnet',  methods=['GET', 'POST'])
@login_required
def ipsubnet():
    role_permission = getattr(Permission, current_user.role)
    ipsubnet_form = IpSubnetForm()
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
            result = search(IpSubnet, 'subnet', search_value)
            result = result.search_return()
            if result:
                pagination = result.paginate(page, 100, False)
                items = pagination.items
                return render_template(
                    'cmdb/item.html',  sidebar=sidebar, item_form=ipsubnet_form,
                    search_value=search_value, checkbox=str(checkbox), thead=thead,  
                    pagination=pagination, endpoint=endpoint, items=items 
                )

    if request.method == "POST" and \
            role_permission >= Permission.ALTER:
        sidebar = init_sidebar(sidebar, now,'additem')
        if ipsubnet_form.validate_on_submit():
            ipsubnet=IpSubnet(
                 subnet=ipsubnet_form.subnet.data,
                 netmask=ipsubnet_form.netmask.data,
                 start_ip=ipsubnet_form.start_ip.data,
                 end_ip=ipsubnet_form.end_ip.data,
                 site=ipsubnet_form.site.data,
                 sales=ipsubnet_form.sales.data,
                 client=ipsubnet_form.client.data,
                 start_date=ipsubnet_form.start_date.data,
                 expire_date=ipsubnet_form.expire_date.data,
                 remark=ipsubnet_form.remark.data
            )
            add_sql = edit(current_user.username, ipsubnet, "subnet" )
            add_sql.run('add')
            flash(u'IP子网添加成功')
        else:
            for key in start_thead:
                key = key[2]
                if ipsubnet_form.errors.get(key, None):
                    flash(ipsubnet_form.errors[key][0])
                    break

    return render_template(
        'cmdb/item.html', sidebar=sidebar, item_form=ipsubnet_form,
        search_value=search_value, thead=thead
    )

@cmdb.route('/cmdb/ipsubnet/delete',  methods=['POST'])
@login_required
@permission_validation(Permission.ALTER)
def ipsubnet_delete():
    del_id = int(request.form["id"])
    ipsubnet = IpSubnet.query.filter_by(id=del_id).first()
    if ipsubnet:
        if IpPool.query.filter_by(subnet=ipsubnet.subnet).first():
            return u"删除失败 有IP使用这个子网"
        delete_sql = edit(current_user.username, ipsubnet, "subnet", ipsubnet.subnet)
        delete_sql.run('delete')
        return "OK"
    return u"删除失败 没有找到这个IP子网"

@cmdb.route('/cmdb/ipsubnet/change',  methods=['POST'])
@login_required
@permission_validation(Permission.ALTER)
def ipsubnet_change():
    change_id = int(request.form["id"])
    item = request.form["item"]
    value = request.form['value']
    ipsubnet = IpSubnet.query.filter_by(id=change_id).first()
    if ipsubnet:
        verify = CustomValidator(item, change_id, value)
        result = verify.validate_return()
        print result
        if result == "OK":
            change_sql = edit(current_user.username, ipsubnet, item, value)
            print 123
            change_sql.run('change')
            return "OK"
        return result 
    return u"更改失败没有找到该IP子网"

@cmdb.route('/cmdb/ipsubnet/batchdelete',  methods=['POST'])
@login_required
@permission_validation(Permission.ALTER)
def ipsubnet_batch_delete():
    list_id = eval(request.form["list_id"])

    for id in list_id:
        ipsubnet = IpSubnet.query.filter_by(id=id).first()
        if ipsubnet:
            if IpPool.query.filter_by(subnet=ipsubnet.subnet).first():
                return u"删除失败 *** <b>%s</b> *** 有IP在使用" % ipsubnet.subnet
        else:
            return u"删除失败没有这些IP子网"

    for id in list_id:
        ipsubnet = IpSubnet.query.filter_by(id=id).first()
        delete_sql = edit(current_user.username, ipsubnet, "subnet", ipsubnet.subnet)
        delete_sql.run('delete')
    return "OK"

@cmdb.route('/cmdb/ipsubnet/batchchange',  methods=['POST'])
@login_required
@permission_validation(Permission.ALTER)
def ipsubnet_batch_change():
    list_id = eval(request.form["list_id"])
    item = request.form["item"]
    value = request.form["value"]

    for id in list_id:
        ipsubnet = IpSubnet.query.filter_by(id=id).first()
        if ipsubnet:
            verify = CustomValidator(item, id, value)
            result = verify.validate_return()
            if not result == "OK":
                return result
        else:
            return u"更改失败没有找到这些IP子网"

    for id in list_id:
        ipsubnet = IpSubnet.query.filter_by(id=id).first()
        change_sql = edit(current_user.username, ipsubnet, item, value)
        change_sql.run('change')
    return "OK"
