 

$(document).ready(
function(){
    var urlParams = new URLSearchParams(window.location.search);
    if (urlParams == "") {
        localStorage.clear();
        $("#filter_state").css("display","none");
    }else{
          $("#filter_state").css("display","inline-block");
    }


$('input:checkbox').on('click',function(){
    var fav, favs = [];
    $('input:checkbox').each(function(){
fav={ id : $(this).attr('id'), value:$(this).prop('checked')

};
favs.push(fav);})
 localStorage.setItem('favorites', JSON.stringify(favs));
})

  var favorites = JSON.parse(localStorage.getItem('favorites')) || [];

  for (var i = 0; i< favorites.length; i++){
    $('#' + favorites[i].id).prop('checked',favorites[i].value);

  }});
       

// =========================

function showVal(x){
 x = x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
 document.getElementById('sel_price').innerText = x;

}


function removeURLParameter(url, parameter) {
    // آدرس را به دو بخش اصلی و Query تقسیم می‌کنیم
    var urlparts = url.split('?');

    // اگر اصلاً پارامتری نبود، همان URL را برگردان
    if (urlparts.length >= 2) {

        // بخش Query String را جدا کن (مثل page=2&sort=asc)
        var prefix = encodeURIComponent(parameter) + "=";
        var params = urlparts[1].split(/[&;]/g);

        // حذف پارامتر خواسته‌شده
        for (var i = params.length ; i-- >= 0; ) {
            if (params[i].lastIndexOf(prefix, 0) !== -1) {
                params.splice(i, 1);
            }
        }

        // ساختن دوباره URL بدون پارامتر
        url = urlparts[0] + (params.length > 0 ? '?' + params.join('&') : "");
    }

    return url;
}


// =========================







function select_sort(){
    var url = new URL(window.location.href);
    url.searchParams.set("sort_type", $("#select_sort").val());
    url.searchParams.delete("page");  // برگشت به صفحهٔ اول بعد از تغییر ترتیب
    window.location = url.toString();
}

function select_per_page(){
    var url = new URL(window.location.href);
    url.searchParams.set("per_page", $("#select_per_page").val());
    url.searchParams.delete("page");  // برگشت به صفحهٔ اول بعد از تغییر تعداد
    window.location = url.toString();
}



status_of_shop_cart();

// =========================

function status_of_shop_cart(){

  $.ajax({
      type: "GET",
      url: "/orders/status_of_shop_cart/",
    

    success: function(res){
       
        $("#indicator__value").text(res);
    }

    });

}





// =========================


function add_to_shop_cart(product_id, qty){
    if (qty === 0){

    qty = $("#product-qty").val();
 

    }

    $.ajax({
      type: "GET",
      url: "/orders/add_to_shop_cart/",
      data:{
         product_id :product_id ,
         qty: qty

      },

    success: function(res){
        alert("کالای مورد نظر به سبد خرید اضافه شد");
        status_of_shop_cart();
    },
    error: function(){
        alert("افزودن به سبد خرید با خطا مواجه شد");
    }

    });
  
}


// =========================


function delete_from_shop_cart(product_id){
    $.ajax({
      type: "GET",
      url: "/orders/delete_from_shop_cart/",
      data:{
         product_id :product_id ,

      },

    success: function(res){
        alert("کالای مورد نظر حذف شد");
        $("#shop_cart_list").html(res);
        status_of_shop_cart();
    }

    });
      
}




// =========================



function update_shop_cart(){
   var product_id_list = []
   var qty_list = []
   $("input[id^='qty_']").each(function(index) {

    product_id_list.push($(this).attr('id').slice(4));
    qty_list.push($(this).val())

   });
 $.ajax({
      type: "GET",
      url: "/orders/update_shop_cart/",
      data:{
        product_id_list :product_id_list ,
qty_list:qty_list
      },

    success: function(res){
        // alert("کالای د");
   $("#shop_cart_list").html(res);
   status_of_shop_cart();
    }

    });
}

// =========================


function showCreateCommentForm(productId,commentId,slug){
    $.ajax({
        type:"GET",
        url:"/csf/create_comment/"+slug,
        data:{
            productId:productId,
            commentId:commentId,
        },
        success:function(res){
            $("#btn_"+ commentId).hide();
            $("#comment_form_"+commentId).html(res);
        }
    });

}


// =========================




function addScore(score,productId){
    $.ajax({
        type: "GET",
        url: "/csf/add_score/",
        data:{
            productId:productId,
            score:score,
        },
        success:function(res){
            // colour the stars only after the server accepted the score
            $(".fa-star").removeClass("checked");
            for (let i = 1; i <= score; i++){
                $("#star_" + i).addClass("checked");
            }
            alert(res);
            window.location.reload();   // refresh the average score
        },
        error:function(xhr){
            alert(xhr.status === 401 ? xhr.responseText : "ثبت امتیاز با خطا مواجه شد");
        }
    });
}



function status_of_compare_list(){
    $.ajax({
        type:"GET",
        url:"/products/status_of_compare_list/",
        success:function(res){
            if (Number(res) === 0){
                $("#compare_count_icon").hide();
            }else{
                $("#compare_count_icon").show();
                $("#compare_count").text(res);
            }
        }
    });
}





function addToCompareList(productId,productGroupId){
       $.ajax({
        type:"GET",
        url:"/products/add_to_compare_list/",
        data:{
            productId:productId,
            productGroupId:productGroupId

        },
        success:function(res){
            alert(res);
            status_of_compare_list();
        }

});
}





function deleteFromCompareList(productId){
       $.ajax({
        type:"GET",
        url:"/products/delete_from_compare_list/",
        data:{
            productId:productId,

        },
        success:function(res){
            alert('حذف با موفقیت انجام شد');
            $("#compare_list").html(res);
            status_of_compare_list();
        }

});
}




