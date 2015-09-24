#coding=utf-8

from app.models import Cabinet, IpPool

from ..same import *
from .forms import CabinetForm
from .custom import CustomValidator

now = "cabinet"
start_thead = [
    [0, u'资产编号','an', False, False], [1,u'外网IP', 'wan_ip', False, False], 
    [2,u'内网IP', 'lan_ip', False, False], [3,u'所在机房', 'site', False, False], 
    [4, u'所在机架','rack', False, True], [5,u'机架位置', 'seat', False, False],
    [6, u'设备带宽', 'bandwidth', False, True], [7, u'上联端口', 'up_link', False, True],
    [8, u'设备高度','height', False, False], [9, u'设备品牌', 'brand', False, True], 
    [10, u'设备型号', 'model', False, True], [11, u'设备SN','sn', True, False], 
    [12, u'销售代表', 'sales', False, True], [13,u'使用用户', 'client', False, True],
    [14, u'开通时间', 'start_time', True, True], [15, u'到期时间' ,'expire_time', True, True], 
    [16, u'备注' ,'remark', False, True], [17, u'操作', 'setting', True],
    [18, u'批量处理', 'batch', True] 
]
endpoint = '.cabinet'

@cmdb.route('/cmdb/cabinet',  methods=['GET', 'POST'])
@login_required
def cabinet():
    '''机柜表'''
    role_permission = getattr(Permission, current_user.role)
    cabinet_form = CabinetForm()
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
            result = search(Cabinet, 'an', search_value)
            result = result.search_return()
            if result:
                pagination = result.paginate(page, 100, False)
                items = pagination.items
                return render_template(
                    'cmdb/item.html',  sidebar=sidebar, item_form=cabinet_form,
                    search_value=search_value, checkbox=str(checkbox), thead=thead,  
                    pagination=pagination, endpoint=endpoint, items=items 
                )

    if request.method == "POST" and role_permission >= Permission.ALTER:
        sidebar = init_sidebar(sidebar, now, "additem")
        if cabinet_form.validate_on_submit():
            cabinet = Cabinet(
                 an = cabinet_form.an.data,
                 wan_ip = cabinet_form.wan_ip.data,
                 lan_ip = cabinet_form.lan_ip.data,
                 site=cabinet_form.site.data,
                 rack=cabinet_form.rack.data,
                 seat=cabinet_form.seat.data,
                 bandwidth=cabinet_form.bandwidth.data,
                 up_link=cabinet_form.up_link.data,
                 height=cabinet_form.height.data,
                 brand=cabinet_form.brand.data,
                 model=cabinet_form.model.data,
                 sn=cabinet_form.sn.data,
                 sales=cabinet_form.sales.data,
                 client=cabinet_form.client.data,
                 start_time=cabinet_form.start_time.data,
                 expire_time=cabinet_form.expire_time.data,
                 remark=cabinet_form.remark.data
            )
            if cabinet_form.wan_ip.data:
                ip = IpPool.query.filter_by(ip=cabinet_form.wan_ip.data).first()
                change_sql = edit(current_user.username, ip, 'sales', cabinet_form.sales.data)
                change_sql.run('change')
                change_sql = edit(current_user.username, ip, 'client', cabinet_form.client.data)
                change_sql.run('change') 
            add_sql = edit(current_user.username, cabinet, "an" )
            add_sql.run('add')
            flash(u'设备添加成功')
        else:
            for thead in start_thead:
                key = thead[2]
                if cabinet_form.errors.get(key, None):
                    flash(cabinet_form.errors[key][0])
                    break
    
    return render_template(
        'cmdb/item.html', sidebar=sidebar, item_form=cabinet_form,
        search_value=search_value, thead=thead
    )

@cmdb.route('/cmdb/cabinet/delete',  methods=['POST'])
@login_required
@permission_validation(Permission.ALTER)
def cabinet_delete():
    del_id = int(request.form["id"])
    cabinet = Cabinet.query.filter_by(id=del_id).first()
    if cabinet:
        if cabinet.wan_ip:
            change_ip = IpPool.query.filter_by(ip=cabinet.wan_ip).first()
            change_sql = edit(current_user.username, ip, 'sales', '')
            change_sql.run('change')
            change_sql = edit(current_user.username, ip, 'client', '')
            change_sql.run('change')
        delete_sql = edit(current_user.username, cabinet, "an", cabinet.an)
        delete_sql.run('delete')
        return "OK"
    return u"删除失败没有找到这个设备"


@cmdb.route('/cmdb/cabinet/change',  methods=['POST'])
@login_required
@permission_validation(Permission.ALTER)
def cabinet_change():
    change_id = int(request.form["id"])
    item = request.form["item"]
    value = request.form['value']
    cabinet = Cabinet.query.filter_by(id=change_id).first()
    if cabinet:
        verify = CustomValidator(item, change_id, value)
        result = verify.validate_return()
        if result == "OK":
           change = ChangeCheck(item, value, cabinet)
           change.change_run()
           return "OK"
        return result
    return u"更改失败没有找到该设备"

@cmdb.route('/cmdb/cabinet/batchdelete',  methods=['POST'])
@login_required
@permission_validation(Permission.ALTER)
def cabinet_batch_delete():
    list_id = eval(request.form["list_id"])

    for id in list_id:
        cabinet = Cabinet.query.filter_by(id=id).first()
        if not cabinet:
            return u"删除失败没有这些设备"

    for id in list_id:
        cabinet = Cabinet.query.filter_by(id=id).first()
        if cabinet.wan_ip:
            change_ip = IpPool.query.filter_by(ip=cabinet.wan_ip).first()
            change_sql = edit(current_user.username, ip, 'sales', '') 
            change_sql.run('change')
            change_sql = edit(current_user.username, ip, 'client', '') 
            change_sql.run('change')
        delete_sql = edit(current_user.username, cabinet, "an", cabinet.an)
        delete_sql.run('delete')
    return "OK"

@cmdb.route('/cmdb/cabinet/batchchange',  methods=['POST'])
@login_required
@permission_validation(Permission.ALTER)
def cabinet_batch_change():
    list_id = eval(request.form["list_id"])
    item = request.form["item"]
    value = request.form["value"]

    for id in list_id:
        cabinet = Cabinet.query.filter_by(id=id).first()
        if cabinet:
            verify = CustomValidator(item, id, value)
            result = verify.validate_return()
            if not result == "OK":
                return result
        else:
            return u"更改失败没有找到这些设备"

    for id in list_id:
        cabinet = Cabinet.query.filter_by(id=id).first()
        change = ChangeCheck(item, value, cabinet)
        change.change_run()
    return "OK"
