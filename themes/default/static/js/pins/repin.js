function repin_pin(pin_pk) {
	if (!USER_LOGGED_IN) {
		window.location.href=LOGIN_URL;
		return false;
	}
	$.colorbox({
			scrolling: false,
			inline: true,
			href:'#repin-finish-content',
			close: '',
			open: true,
			onComplete: function () {
				$('form.popup-jqtransform').jqTransform();
			},
		});
	$('#repinned-image').html('<div class="ajax-loader"></div>');
	$('#repin-finish-content form').submit(function () {
		if ($(this).find('textarea').val()=='') {
			$('#repin-empty-description').show();
			return false;
		}
		if ($(this).find('button').hasClass('disabled')) {
			return false;
		}
	});
	$.get(PIN_INFORMATION_URL, {pin_pk: pin_pk}, function (data) {
		$('#repinned-image').html('<img src="'+data.thumbnail+'" alt="" width="100" height="100"/>');
		$('#repin-finish-content #id_description').val(data.description).select();
		$('#id_repinned_pin').val(pin_pk);
		$('#repin-finish-content button').removeClass('disabled');
	});
	return false;

}

$(function () {
	$('.repin-pin').live('click', function () {
		return repin_pin($(this).data('pin-pk'));
	});
});

