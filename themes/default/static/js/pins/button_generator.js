$(function (){
	var updateButtonCode = function () {
		var template = '<a href="'+window.IFRAME_SRC+'?__params__" class="pinit-button">'+window.PIN_IT_TITLE+'</a>';
		var params = {};
		var fields = ['image_url', 'description','url', 'button_type'];
		for (var f in fields) {
			var fname = fields[f];
			var fval = $('#id_'+fname).val();
			if (fval)
				params[fname] = encodeURIComponent(fval);
		}
		var paramsStr = '';
		for (var p in params) {
			paramsStr = paramsStr +p+'='+params[p]+'&';
		}
		var buttonCode = template.replace(/__params__/, paramsStr);
		$('#id_button_code').val(buttonCode);
		$('.example-button .button-container').html('<div class="button-'+params['button_type']+' button"></div>');
		return false;
	};
	$('.pin-it-button-generator input, .pin-it-button-generator textarea').keyup(updateButtonCode).keyup();
	$(".pin-it-button-generator div.jqTransformSelectWrapper ul li a").click(updateButtonCode);


});