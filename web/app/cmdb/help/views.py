#coding=utf-8

from ..same import *

now = 'help'

@cmdb.route('/cmdb/help',  methods=['GET'])
@login_required
def help():
    '''帮助'''
    sidebar = copy.deepcopy(start_sidebar)
    sidebar = init_sidebar(sidebar, now,'usage')
    return render_template('cmdb/help.html', sidebar=sidebar)
