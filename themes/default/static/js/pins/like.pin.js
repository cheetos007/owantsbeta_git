$(function () {
	$('.like-pin').live('click',function () {
		var pin_pk = $(this).data('pin-pk');
		if (!USER_LOGGED_IN) {
			window.location.href=LOGIN_URL;
			return false;
		}
		$.post(LIKE_PIN_URL, {'pin': pin_pk}, function (data) {
			if (data.status=="ok") {
				$(this).find('.number').html(data.number_of_likes);
			}
		}.bind(this));

		return false;
		});
});

