/**
* JavaScript code for interaction with Pin it->Pin from web functionality
*/
var loaded_media;
var selected_media;

$(function () {
	$('input#add-pin-website').focus(function (){
		if (!this.hadLostFocus) {
			this.value='';
			this.hadLostFocus = true;
		}
	});

	$('#pin-url-form').submit(function () {
		$.colorbox({
			inline: true,
			href: '#add-pin-popup-finish-content',
			open: true,
			scrolling: false,
			onClosed: function () {
				$('#pin-from-web-empty-description').hide();
				$('#add-pin-popup-finish-content button').removeClass('disabled');
				$('#pin-from-web-error').hide();
			},
			onComplete: function () {
				$('form.popup-jqtransform').jqTransform();
			},
		});
		$('#add-pin-popup-finish-content form.popup-form').submit(function () {
			if ($(this).find('button').hasClass('disabled'))
				return false;
			if ($(this).find('textarea').val()=='') {
				$('#pin-from-web-empty-description').show();
				return false;
			}

		});
		$('#web-image').html('<div class="ajax-loader"></div>');
		$.colorbox.resize({'innerHeight': $('#add-pin-popup-finish-content').innerHeight()+50});
		$.post(WEBSITE_IMAGES_URL, {url: $('#add-pin-website').val()}, function (data) {
			if ((typeof(data.images)!='undefined' && data.images.length>0) || (typeof(data.videos)!='undefined' && data.videos.length>0)) {
				loaded_media = new Array();
				//populate loaded media with information from both data.videos and data.images

				if (typeof(data.videos)!='undefined' && data.videos.length>0) {
					for (i=0;i<data.videos.length;i++) {
						loaded_media.push({'thumbnail': data.videos[i].thumbnail, 'parser': data.videos[i].parser, 
											'video_id': data.videos[i].video_id,'media_type':'video'});
					}
				}
				
				if (typeof(data.images)!='undefined' && data.images.length>0) {
					for (i=0;i<data.images.length;i++) {
						loaded_media.push({'thumbnail': data.images[i], 'media_type':'image'});
					}
				}
				function setFormValues(media) {
					var preview_html = '<img src="'+media.thumbnail+'" class="'+media.media_type+'_media_preview" width="120" alt=""/>';

					if (media.media_type=='video') {
						$('#add-pin-parser').val(media.parser);
						$('#add-pin-video-id').val(media.video_id);
						$('#web-image').html()
						$('#pin-from-web-image-url').val('');
						preview_html +='<div class="video-button-overlay"></div>';
					} else {
						$('#pin-from-web-image-url').val(media.thumbnail);
						$('#add-pin-parser').val('');
						$('#add-pin-video-id').val('');
					}
					
					$('#web-image').html(preview_html);
				}


				selected_media = 0;
				
				$('#pin-from-web-url').val($('#add-pin-website').val());
				$('#add-pin-popup-finish-content form.popup-form button').removeClass('disabled');
				setFormValues(loaded_media[selected_media]);
				if (loaded_media.length>1) {
					$('#web-image-controls').show();
					$('#web-image-controls .left').click(function () {
						if (!$(this).hasClass('disabled')) {
							selected_media = selected_media - 1;
							setFormValues(loaded_media[selected_media]);
							if (selected_media==0) {
								$(this).addClass('disabled');
							} else if (selected_media!=loaded_media.length-1) {
								$('#web-image-controls .right').removeClass('disabled');
							}
						}
						return false;
					});
					$('#web-image-controls .right').click(function () {
						if (!$(this).hasClass('disabled')) {
							selected_media = selected_media + 1;
							setFormValues(loaded_media[selected_media]);
							if (selected_media==(loaded_media.length-1)) {
								$(this).addClass('disabled');
							} else if (selected_media!=0) {
								$('#web-image-controls .left').removeClass('disabled');
							}
						}
						return false;
					});
				}
			} else {
				$('#pin-from-web-error').show();

			}

		});
	return false;
	});
});