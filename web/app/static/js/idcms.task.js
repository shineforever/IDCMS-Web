$(function(){
    // 导航切换，批量处理
    $('ul.sub-menu li').click(function(){
        $(this).addClass('active').siblings('li').removeClass('active')
        var id = $(this).attr('id')
        //变量组合使用＋号
        $('div#'+id).removeClass('hidden')
        $('div.content').not('#'+id).addClass('hidden')
    });
    // 表格点击跳转
    // 这里使用each遍历的意思是为所有css=tabletr的元素添加click动作
    $(".tabletr").each(function(){
        $(this).click(function(event){
            event.stopPropagation();
            location.href = $(this).attr("data-href");
        });
    });
});


$(document).ready(function() {
    // DataTable
    var table_dict = {
        //分页
        paging: false,
        // 排序
        //ordering: false,
        //页面信息
        info: false,
        //分页
        //bLengthChange: false,
        //aLengthMenu:[50, 100],
        //表格太长，添加滚动
        dom: "<'row' <'col-md-12'T>><'row'<'col-md-6 col-sm-12'l><'col-md-6 col-sm-12'f>r><'table-scrollable't><'row'<'col-md-5 col-sm-12'i><'col-md-7     col-sm-12'p>>",
        language: {
            "sLengthMenu": "显示 _MENU_ 项结果",
            "sZeroRecords": "没有匹配结果",
            "sEmptyTable": "表中数据为空",
            "sInfoEmpty": "显示第 0 至 0 项结果，共 0 项",
            "sInfo": "显示第 _START_ 至 _END_ 项结果，共 _TOTAL_ 项",
            "sSearch": "搜索:",
            "oPaginate": {
                "sFirst": "首页",
                "sPrevious": "上页",
                "sNext": "下页",
                "sLast": "末页"
            }        
        },
    };
    
    var table = $('#search').DataTable( 
        table_dict
    );
});
