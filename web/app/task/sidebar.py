#coding=utf-8

start_sidebar = {
    "order":[
        "task"
    ],

    "now": "",
    
    "task":{
        "class":"",
        "href":"/task/ticket",
        "icon":"icon-note",
        "title":u"任务管理",
        "li_order":["my_task", "put_task"],
        "li":{
            "my_task": ["", "my_task", u"我的任务", 'content hidden'],
            "put_task": ["", "pu_task", u'发布任务', 'content hidden']
        }
    }
}
