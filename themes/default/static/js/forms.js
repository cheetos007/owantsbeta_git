$(function () {
	$('.pre-filled-login-form input[type="text"], .login-form input[type="text"]').focus(function (){
		if (!this.hadGainedFocus) {
			this.hadGainedFocus=true;
			this.value="";
		}
	});
	$("form.jqtransform").jqTransform();
});