$(document).ready(function () { 
     
    $('#menu li, #menu-top li').hover(
        function () {
            //show its submenu
            $('ul', this).slideDown(100);
 
        }, 
        function () {
            //hide its submenu
            $('ul', this).slideUp(100);         
        }
    );
     
});