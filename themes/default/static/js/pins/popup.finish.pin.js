$(function () {
	$('form.popup-form').submit(function () {
		if ($(this).find('button').hasClass('disabled'))
			return false;
		if ($(this).find('textarea').val()=='') {
			$('#pin-from-web-empty-description').show();
			return false;
		}

	});

});