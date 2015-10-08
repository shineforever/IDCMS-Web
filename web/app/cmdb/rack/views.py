#coding=utf-8
# 机柜管理 

from app.models import Rack, Cabinet

from ..same import *
from .forms import RackForm
from .custom import CustomValidator

now = "rack"
start_thead = [
    [0, u'机柜','rack', False, False], [1,u'机房', 'site', False, False], 
    [2,u'机架U数', 'count', False, True],[3, u'机架电流','power', False, True], 
    [4, u'销售代表', 'sales', False, True], [5, u'机架用户', 'client', False, True], 
    [6, u'开通时间' ,'start_date', False, True],[7, u'到期时间' ,'expire_date', False, True],
    [8, u'备注' ,'remark', False, True], [9, u'操作', 'setting', True],
    [10, u'批量处理', 'batch', True]
]
endpoint = '.rack'

@cmdb.route('/cmdb/rack',  methods=['GET', 'POST'])
@login_required
def rack():
    role_permission = getattr(Permission, current_user.role)
    rack_form = RackForm()
    sidebar = copy.deepcopy(start_sidebar)
    thead = copy.deepcopy(start_thead)
    sidebar = init_sidebar(sidebar, now,'edititem')
    search_value = ''

    if request.method == "GET":
        search_value = request.args.get('search', '') 
        checkbox = request.args.getlist('hidden') or request.args.get('hiddens', '')    
        if search_value:
            sidebar = init_sidebar(sidebar, now, "edititem")
            thead = init_checkbox(thead, checkbox)
            page = int(request.args.get('page', 1)) 
            result = search(Rack, 'rack', search_value)
            result = result.search_return()
            if result:
                pagination = result.paginate(page, 100, False)
                items = pagination.items
                return render_template(
                    'cmdb/item.html',  sidebar=sidebar, item_form=rack_form,
                    search_value=search_value, checkbox=str(checkbox), thead=thead,  
                    pagination=pagination, endpoint=endpoint, items=items 
                ) 

    if request.method == "POST" and role_permission >= Permission.ALTER:
        sidebar = init_sidebar(sidebar, now, "additem")
        if rack_form.validate_on_submit():
            rack = Rack(
                rack=rack_form.rack.data,
                site=rack_form.site.data,
                count=rack_form.count.data,
                power=rack_form.power.data,
                sales=rack_form.sales.data,
                client=rack_form.client.data,
                start_date=rack_form.start_date.data,
                expire_date=rack_form.expire_date.data,
                remark=rack_form.remark.data
            )
            add_sql = edit(current_user.username, rack, "rack" )
            add_sql.run('add')
            flash(u'机柜添加成功')
        else:
            for thead in start_thead:
                key = thead[2]
                if rack_form.errors.get(key, None):
                    flash(rack_form.errors[key][0])
                    break
    
    return render_template(
        'cmdb/item.html', sidebar=sidebar, item_form=rack_form,
        search_value=search_value, thead=thead
    )

@cmdb.route('/cmdb/rack/delete',  methods=['POST'])
@login_required
@permission_validation(Permission.ALTER)
def rack_delete():
    del_id = int(request.form["id"])
    rack = Rack.query.filter_by(id=del_id).first()
    if rack:
        # 这里要检查两个，因为不同机房，可能有相同名称机架名
        if Cabinet.query.filter_by(rack=rack.rack, site=rack.site).first():
            return u'删除失败 有设备使用这个 *** %s *** 机架' %  rack.rack
        delete_sql = edit(current_user.username, rack, "rack", rack.rack)
        delete_sql.run('delete') 
        return "OK"
    return u"删除失败 没有找到这个机架"

@cmdb.route('/cmdb/rack/change',  methods=['POST'])
@login_required
@permission_validation(Permission.ALTER)
def reak_change():
    change_id = int(request.form["id"])
    item = request.form["item"]
    value = request.form['value']
    rack = Rack.query.filter_by(id=change_id).first()
    if rack:
        verify = CustomValidator(item, change_id, value)
        result = verify.validate_return()
        if result == "OK":
            change_sql = edit(current_user.username, rack, item, value)
            change_sql.run('change')
            return "OK"
        return result 
    return u"更改失败 没有找到该机架"

@cmdb.route('/cmdb/rack/batchdelete',  methods=['POST'])
@login_required
@permission_validation(Permission.ALTER)
def rack_batch_delete():
    list_id = eval(request.form["list_id"])
    
    for id in list_id:
        rack = Rack.query.filter_by(id=id).first()
        if rack:
            if Cabinet.query.filter_by(rack=rack.rack, site=rack.site).first():
                return u"删除失败 *** %s *** 机架有设备在使用" % rack.rack
        else:
            return u"删除失败没有这些机架"

    for id in list_id:
        rack = Rack.query.filter_by(id=id).first()
        delete_sql = edit(current_user.username, rack, "rack", rack.rack)
        delete_sql.run('delete')
    return "OK"

@cmdb.route('/cmdb/rack/batchchange',  methods=['POST'])
@login_required
@permission_validation(Permission.ALTER)
def rack_batch_change():
    list_id = eval(request.form["list_id"])
    item = request.form["item"]
    value = request.form["value"]

    for id in list_id:
        rack = Rack.query.filter_by(id=id).first()
        if rack:
            verify = CustomValidator(item, id, value)
            result = verify.validate_return()
            if not result == "OK":
                return result
        else:
            return u"更改失败没有找到这些机架"

    for id in list_id:
        rack = Rack.query.filter_by(id=id).first()
        change_sql = edit(current_user.username, rack, item, value)
        change_sql.run('change')
    return "OK"
