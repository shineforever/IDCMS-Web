#coding=utf-8

import re
import time

from flask.ext.login import current_user

from app import db
from app.models import Rack, Site, IpPool, Cabinet, Sales, Client
from app.utils.utils import re_date, re_ip, record_sql

class CustomValidator():
    def __init__(self, item, item_id, value):
        self.item = item
        self.value = value
        self.change_cabinet = Cabinet.query.filter_by(id=int(item_id)).first()
        self.sm =  {
            "rack": self.validate_an,
            "wan_ip": self.validate_wan_ip,
            "lan_ip": self.validate_lan_ip,
            "site": self.validate_site,
            "rack": self.validate_rack,
            "bandwidth": self.validate_bandwidth,
            "height": self.validate_height,
            "sales": self.validate_sales,
            "client": self.validate_client,
            "start_time": self.validate_start_time,
            "expire_time": self.validate_expire_time
        }

    def validate_return(self):
        if self.sm.get(self.item, None):
            return self.sm[self.item](self.value)
        else:
            if self.item in ("model", "sn") and len(self.value) > 32: 
                return u"更改失败 最大32个字符"
            if len(self.value) > 64:
                return u"更改事变最大 64个字符"
            if self.item in ("remark") or self.value:
                return "OK"
            return u"这个项目不能为空"

    def validate_an(self,value):
        if Cabinet.query.filter_by(an=value).first():
            return u'更改失败 这个资产编号 *** %s *** 已经使用' % value

    def validate_wan_ip(self,value):
        if not re.match(re_ip, value):
            return u'更改失败 外网IP应该是一个IP格式'
        if Cabinet.query.filter_by(wan_ip=value).first():
            return u'更改失败 这个外网IP *** %s *** 已经使用' % value
        ip = IpPool.query.filter_by(ip=value).first()
        if ip: 
            if ip.sales or ip.client:
                return u'更改失败 外网IP *** %s *** 已经使用' % value
            return "OK"
        else:
            return u'更改失败 这个外网IP *** %s *** 还没有添加' % value
 
    def validate_lan_ip(self,value):
        if not re.match(re_ip, value):
            return  u'更改失败 内网IP应该是一个IP格式'
        return "OK"

    def validate_site(self,value):
        return u"不能更改机房更改机房要先执行下架(删除) 然后从新添加"

    def validate_rack(self,value):
        if not Rack.query.filter_by(rack=value ,site=self.change_cabinet.site).first():
            return u'更改失败 没有在该机房找到这个 *** %s *** 机柜' % value
        return "OK"

    def validate_bandwidth(self,value):
        re_count = '^\d+M$|^上联设备$|^百兆共享$'
        if re.match(re_count, value):
            return "OK"
        return u"更改失败 格式为 数字+M、上联设备、百兆共享"
    
    def validate_height(self,value):
        re_power = '^\d+U$'
        if re.match(re_power, value):
            return "OK"
        return u"更改失败 格式为 数字+U"

    def validate_sales(self,value):
        if not Sales.query.filter_by(username=value).first():
            return u'更改失败 这个销售 *** %s *** 不存在' % value
        return "OK"

    def validate_client(self,value):
        if not Client.query.filter_by(username=value).first():
            return u'更改失败 这个客户 *** %s *** 不存在' % value
        return "OK"

    def validate_start_time(self, value):
        if re.match(re_date, value):
            start_time = time.mktime(time.strptime(value,'%Y-%m-%d'))
            expire_time = time.mktime(time.strptime(str(self.change_cabinet.expire_time),'%Y-%m-%d'))
            if start_time > expire_time:
                return u"添加失败，开通时间小于到期时间"
            return "OK"
        return u"更改失败，时间格式不正确"

    def validate_expire_time(self, value):
        if re.match(re_date, value):
            start_time = time.mktime(time.strptime(str(self.change_cabinet.start_time),'%Y-%m-%d'))
            expire_time = time.mktime(time.strptime(value,'%Y-%m-%d'))
            if expire_time < start_time:
                return u"添加失败，到期时间小于开通时间"
            return "OK"
        return u'更改失败，时间格式不正确'


class ChangeCheck():
    """根据不同的字段进行修改
    主要是检查了ip是不是更改，如果更改了同时更改ip信息
    """
    def __init__(self,item, value, cabinet):
        self.item = item
        self.value = value
        self.cabinet = cabinet
        self.sm = {
            "sales": self.sales_and_clinet,
            "client": self.sales_and_clinet,
            "wan_ip": self.wan_ip,
        }
    
    def change_run(self):
        if self.sm.get(self.item, None):
            self.sm[self.item]()
        ange_sql = edit(current_user.username, self.cabinet, self.item,
                        self.value)
        change_sql.change()

    def sales_and_clinet(self):
        if self.cabinet.wan_ip:
            ip = IpPool.query.filter_by(ip=self.cabinet.wan_ip).first()
            change_sql = edit(current_user.username, ip,self.item,
                            self.value)
            change_sql.change()

    def wan_ip(self):
        # 如果有旧IP 要先清空就IP主机信息
        if self.cabinet.wan_ip:
            old_ip = IpPool.query.filter_by(ip=self.cabinet.wan_ip).first()
            change_sql = edit(current_user.username, old_ip, 'sales', '')
            change_sql.change()
            change_sql = edit(current_user.username, old_ip, 'client', '')
            change_sql.change()
        # 给新IP 添加主机信息
        add_ip = IpPool.query.filter_by(ip=self.value).first()
        change_sql = edit(current_user.username, ip, 'sales', self.cabinet.sales)
        change_sql.change()
        change_sql = edit(current_user.username, ip, 'client', self.cabinet.client)
        change_sql.change()
