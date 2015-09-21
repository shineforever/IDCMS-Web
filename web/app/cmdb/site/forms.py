#coding=utf-8

from flask.ext.wtf import Form
from wtforms import StringField, ValidationError
from wtforms.validators import Required, Length

from app.models import Site

class SiteForm(Form):
    site = StringField(u'机房名称', validators=[Required(message=u'机房名不能为空'), 
                       Length(1, 64, message=u'机房名最大64个字符')])
    isp = StringField(u'ISP', validators=[Required(message=u'ISP不能为空'),
                      Length(1, 64, message=u'ISP最大-64个字符')])
    location = StringField(u'所在城市', validators=[Required(message=u'机房名不能为空'),
                           Length(1, 64, message=u'所在城市最大64个字符')])
    address = StringField(u'详细地址', validators=[Required(message=u'机房名不能为空'),
                           Length(1, 64, message=u'详细地址最大64个字符')])
    contact = StringField(u'联系方式', validators=[Required(message=u'机房名不能为空'),
                          Length(1, 64, message=u'联系方式最大64个字符')])
    dns = StringField(u'机房DNS', validators=[Length(0, 64, message=u'机房DNS最大64个字符')])
    remark = StringField(u'备注', validators=[Length(0, 64, message=u'备注最大64个字符')])

    def validate_site(self, field):
        '''如果这么写，wtf会自动监测这个问题'''
        if Site.query.filter_by(site=field.data).first():
            raise ValidationError(u'添加失败 *** %s *** 机房已添加' % field.data )

