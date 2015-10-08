#coding=utf-8

import re
import time

from flask.ext.wtf import Form
from wtforms import StringField, SelectField
from wtforms import ValidationError
from wtforms.validators import Required, Length, Regexp

from app.models import Site, Rack, IpPool, Cabinet, Sales, Client
from app.utils.utils import re_date, re_ip


class CabinetForm(Form):
    an = StringField(u'资产编号', validators=[Required(message=u'资产编号不能为空'), 
                     Length(1, 64, message=u'资产编号为1-64个字符')])
    wan_ip = StringField(u'外网IP', validators=[Length(0, 64, message=u'机房名为0-64个字符')])
    lan_ip = StringField(u'内网IP', validators=[Length(0, 64, message=u'机房名为0-64个字符')])
    site = StringField(u'所在机房', validators=[Required(message=u'机房名不能为空'), 
                       Length(1, 64, message=u'机房名为1-64个字符')])
    rack = StringField(u'所在机架', validators=[Required(message=u'机架名不能为空'), 
                       Length(1, 32, message=u'机架名为1-32个字符')])
    seat = StringField(u'机架位置', validators=[Length(0, 32, message=u'机架位置最大为32个字符')])
    bandwidth = SelectField(u'设备带宽', choices=[('2M', '2M'),('5M', '5M'), ('10M', '10M' ),
                            ('20M', '20M'), ('50M', '50M'),('100M','100M'),
                            (u'百兆共享', u'百兆共享'), (u'上联设备', u'上联设备')])
    up_link = StringField(u'上联端口', validators=[Required(message=u'上联端口不能为空'),
                           Length(1, 32, message=u'上连为1-32个字符')])
    height = SelectField(u'设备高度', choices=[('1U', '1U'),('2U', '2U'), ('3U','3U' ), ('4U','4U')])
    brand = SelectField(u'设备品牌', choices=[(u'戴尔', u'戴尔'), (u'惠普', u'惠普'), ('IBM', 'IBM'), 
                        (u'浪潮', u'浪潮' ), (u'联想', u'联想'), (u'金品', u'金品'), (u'思科', u'思科'),
                        (u'华为', u'华为'), ('H3C', 'H3C'), ('TP-Link', 'TP-Link'),('D-Link', 'D-Link'),
                        (u'兼容机', u'兼容机')])
    model = StringField(u'设备型号', validators=[Length(0, 32, message=u'设备型号最大为32个字符')])
    sn = StringField(u'设备SN', validators=[Length(0, 32, message=u'设备SN最大为32个字符')])
    sales = StringField(u'销售代表', validators=[Required(message=u'销售代表不能为空'),
                            Length(1, 32, message=u'销售代表最大为32个字符')])
    client = StringField(u'使用用户', validators=[Required(message=u'使用用户不能为空'),
                         Length(1, 64, message=u'使用用户为最大为64个字符')])
    start_date = StringField(u'开通日期', validators=[Regexp(re_date, message=u'开通时间格式为yyyy-mm-dd')])
    expire_date = StringField(u'到期日期',validators=[Regexp(re_date, message=u'到期时间格式为yyyy-mm-dd')])
    remark = StringField(u'备注', validators=[Length(0, 64, message=u'备注最大64个字符')])

    def validate_an(self, field):
        if Cabinet.query.filter_by(an=field.data).first():
            raise ValidationError(u'添加失败 资产编号 *** %s *** 已经存在' % field.data)

    def validate_wan_ip(self, field):
        if field.data:
            if not  re.match(re_ip, field.data):
                raise ValidationError(u'添加失败 外网IP应该是一个IP格式')
            if Cabinet.query.filter_by(wan_ip=field.data).first():
                raise ValidationError(u'添加失败 这个外网IP *** %s *** 已经添加' % field.data)
            ip = IpPool.query.filter_by(ip=field.data).first()
            if ip:
                if ip.sales or ip.client:
                    raise ValidationError(u'添加失败 这个外网IP *** %s *** 已经使用' % field.data)
            else:
                raise ValidationError(u'添加失败 这个外网IP *** %s *** 还没有添加' % field.data)
    
    def validate_lan_ip(self, field):
        if field.data:
            if not re.match(re_ip, field.data):
                raise ValidationError(u'添加失败 内网IP应该是一个IP格式')

    def validate_site(self, field):
        if not Site.query.filter_by(site=field.data).first():
            raise ValidationError(u'添加失败 机房 *** %s *** 不存在' % field.data)

    def validate_rack(self, field):
        if not Rack.query.filter_by(rack=field.data, site=self.site.data).first():
            raise ValidationError(u'添加失败 机架 *** %s *** 不存在' % field.data)

    def validate_sales(self, field):
        if not Sales.query.filter_by(username=field.data).first():
            raise ValidationError(u'添加失败 销售 *** %s *** 不存在' % field.data)

    def validate_client(self, field):
        if not Client.query.filter_by(username=field.data).first():
            raise ValidationError(u'添加失败 客户 *** %s *** 不存在' % field.data)

    def validate_expire_date(self, field):
        start_date = time.mktime(time.strptime(self.start_date.data,'%Y-%m-%d'))
        expire_date = time.mktime(time.strptime(self.expire_date.data,'%Y-%m-%d'))
        if expire_date < start_date:
            raise ValidationError(u'添加失败 到期时间小于开通时间')
