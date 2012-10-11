var selected_categories = [];
$(function (){
	$('.categories a').click(function () {
		if ($(this).hasClass('selected')) {
			removeItem = $(this).data('category-id');
			selected_categories = y = jQuery.grep(selected_categories, function(value) {
			  return value != removeItem;
			});
			$(this).removeClass('selected');
		} else {
			selected_categories.push($(this).data('category-id'));
			$(this).addClass('selected');
		}
		return false;
	});



	$('#categories-form').submit(function () {
		$('#id_selected_categories').val(selected_categories.join(","));
		return true;
	});

	$('#users-form').submit(function (){
		var selected_users = [];
		$('.category .avatar').each(function (ind, elem) {
			if ($(elem).hasClass('selected'))
				selected_users.push($(elem).data('user-pk'));
		});
		$('#id_selected_users').val(selected_users.join(","));
		return true;
	});

	$('.category .avatar').click(function () {
		$(this).toggleClass('selected');
	});


	$('#add-field').click(function () {
		//increase the number of total forms
		var next_form_id = parseInt($('#id_form-TOTAL_FORMS').val());
		$('#id_form-TOTAL_FORMS').val(next_form_id+1);
		var new_html = $('#empty-board-form').html().replace(/__prefix__/g, next_form_id);
		$('#fieldset-container').append(new_html);
		$('#add-field').detach().appendTo('#fieldset-container fieldset:last div.row');
		//$('form.jqtransform').removeClass('jqtransformdone');
		//$('.jqtransform').jqTransform();
		$('.page-info-box').addClass('curvyRedraw');
		$('.page-info-box').removeClass('curvyIgnore');
		curvyCorners.redraw()
		return false;
	});
});