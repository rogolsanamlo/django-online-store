


$(document).ready(function(){
    var listOfElements = $('select[id^="id_product_features-"][id$="-feature"]');
    $(listOfElements).on('change', function(){
        // var f_id = $(this).val();
        // var dd1 = $(this).attr('id');
        // var dd2 = dd1.replace("-feature", "-filter_value");
         f_id = $(this).val();
         dd1 = $(this).attr('id');
         dd2 = dd1.replace("-feature", "-filter_value");

// تا اونجایی که یادمه استاد ور نذاشته بود 


        $.ajax({
            type: 'GET',
            url: '/products/ajax_admin/?feature_id='+ f_id,     // آدرس ویوی AJAX
            
            success: function(res){
                cols=document.getElementById(dd2);
                cols.option.length=0;
                for(var k in res){
                    cols.options.add(new Option(k, res[k]));
                

                }
            }
        });
    });
});










