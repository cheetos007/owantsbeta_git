$(function () {

var button = $('#popup-upload-pin-button');
if (button[0]) {
	var show_after_hide = false;
	new AjaxUpload(button,{
		//action: 'upload-test.php', // I disabled uploads in this example for security reasons
		action: PIN_UPLOAD_URL, 
		name: 'image',
		onSubmit : function(file, ext){
			// change button text, when user selects file
				$.colorbox({
				scrolling: false,
				inline: true,
				href:'#upload-pin-finish-content',
				close: '',
				open: true,
				onClosed: function () {
					$('#pin-upload-error').hide();
					$('#upload-pin-finish-content button').removeClass('disabled');
					$('#pin-upload-empty-description').hide();
				},
				onComplete: function () {
				$('form.popup-jqtransform').jqTransform();
			},
			});
			$('#uploaded-image').html('<div class="ajax-loader"></div>');

		},
		onComplete: function(file, response){
			if (response.pin_pk) {
				//response is correct- pin PK is given
				$('input#pin_pk').val(response.pin_pk);
				$('#uploaded-image').html('<img src="'+response.thumbnail+'" alt="" width="100" height="100"/>');
				$('#upload-pin-finish-content form button').removeClass('disabled');
			} else {
				$('#pin-upload-error').show();
			}	
		},
		responseType: 'json',
	});
	}
$('#upload-pin-finish-content form').submit(function () {
	if ($(this).find('button').hasClass('disabled'))
		return false;
	if ($(this).find('textarea').val()=='') {
		$('#pin-upload-empty-description').show();
		return false;
	}

});
});
