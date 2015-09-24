#coding=utf-8
# 机房管理

from app.models import Site, Rack, IpSubnet

from ..same import *
from .forms import SiteForm
from .custom import CustomValidator

now = "site"
start_thead = [
    [0, u'机房','site', False, False], [1,u'ISP', 'isp', False, True], 
    [2,u'地理位置', 'location', False, False], [3, u'地址','addresults', False, False], 
    [4, u'联系方式', 'contact', False, True], [5, u'机房DNS', 'dns', False, True], 
    [6, u'备注' ,'remark', False, True], [7, u'操作', 'setting', True],
    [8, u'批量处理', 'batch', True]
]
endpoint = '.site'

@cmdb.route('/cmdb/site',  methods=['GET', 'POST'])
@login_required
def site():
    '''机房设置'''
    role_permission = getattr(Permission, current_user.role)
    site_form = SiteForm()
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
            result = search(Site, 'site' , search_value)
            result = result.search_return()
            if result:
                pagination = result.paginate(page, 100, False)
                items = pagination.items
                return render_template(
                    'cmdb/item.html', sidebar=sidebar, item_form=client_form,
                    search_value=search_value, checkbox=str(checkbox), thead=thead,  
                    pagination=pagination, endpoint=endpoint, items=items 
                )

    if request.method == "POST" and \
            role_permission >= Permission.ALTER:
        sidebar = init_sidebar(sidebar, now, "additem")
        if site_form.validate_on_submit():
            site = Site(
                site=site_form.site.data,
                isp=site_form.isp.data,
                location=site_form.location.data,
                address=site_form.address.data,
                contact=site_form.contact.data,
                dns=site_form.dns.data,
                remark=site_form.remark.data
            )
            add_sql = edit(current_user.username, site, "site" )
            add_sql.run('add')
            flash(u'机房添加成功')
        else:
            for thead in start_thead:
                key = thead[2]
                if site_form.errors.get(key, None):
                    flash(site_form.errors[key][0])
                    break 

    return render_template(
        'cmdb/item.html', sidebar=sidebar, item_form=site_form,
        search_value=search_value, thead=thead
    )

@cmdb.route('/cmdb/site/delete',  methods=['POST'])
@login_required
@permission_validation(Permission.ALTER)
def site_delete():
    del_id = int(request.form["id"])
    site = Site.query.filter_by(id=del_id).first()
    if site:
        # 删除机房只需要检查机架和IP子网就好，机架会检查机柜表
        # 子网会检查IP 所有只要这两个没有使用就可以删除
        if Rack.query.filter_by(site=site.site).first():
            return u"删除失败 *** %s *** 机房有机架在使用" % site.site
        if IpSubnet.query.filter_by(site=site.site).first():
            return u"删除失败 *** %s *** 机房有IP子网在使用" % site.site
        delete_sql = edit(current_user.username, site, "site", site.site)
        delete_sql.run('delete')
        return "OK"
    return u"删除失败 没有找到这个机房"

@cmdb.route('/cmdb/site/change',  methods=['POST'])
@login_required
@permission_validation(Permission.ALTER)
def site_change():
    change_id = int(request.form["id"])
    item = request.form["item"]
    value = request.form["value"]
    site = Site.query.filter_by(id=change_id).first()
    if site:
        verify = CustomValidator(item, change_id, value)
        result = verify.validate_return()
        if result == "OK":
            change_sql = edit(current_user.username, site, item, value)
            change_sql.run('change')
            return "OK"
        return result 
    return u"更改失败没有找到该机房"

@cmdb.route('/cmdb/site/batchdelete',  methods=['POST'])
@login_required
@permission_validation(Permission.ALTER)
def site_batch_delete():
    list_id = eval(request.form["list_id"])

    for id in list_id:
        site = Site.query.filter_by(id=id).first()
        if site:
            if Rack.query.filter_by(site=site.site).first():
                return u"删除失败 *** %s *** 有机架在使用" % site.site
            if IpSubnet.query.filter_by(site=site.site).first():
                return u"删除失败 *** %s *** 有IP子网在使用" % site.site
        else:
            return u"删除失败没有这些机房"

    for id in list_id:
        site = Site.query.filter_by(id=id).first()
        delete_sql = edit(current_user.username, site, "site", site.site)
        delete_sql.run('delete')
    db.session.commit()
    return "OK"

@cmdb.route('/cmdb/site/batchchange',  methods=['POST'])
@login_required
@permission_validation(Permission.ALTER)
def site_batch_change():
    list_id = eval(request.form["list_id"])
    item = request.form["item"]
    value = request.form["value"]

    for id in list_id:
        site = Site.query.filter_by(id=id).first()
        if site:
            verify = CustomValidator(item, id, value)
            result = verify.validate_return()
            if not result == "OK":
                return result
        else:
            return u"更改失败没有找到这些机房"

    for id in list_id:
        site = Site.query.filter_by(id=id).first()
        change_sql = edit(current_user.username, site, item, value)
        change_sql.run('change')
    return "OK"
