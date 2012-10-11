$(function (){
	$('a#create-pin-popup').colorbox({
		scrolling: false,
		inline: true, 
		href: '#create-pin-popup-content',
		close: '',
	});

	$('a#popup-add-pin-button').colorbox({
		scrolling: false,
		inline: true,
		href:'#add-pin-popup-content',
		close: '',
	});
    $('a#popup-add-own-button').colorbox({
        scrolling: false,
        inline: true,
        href:'#add-own-popup-content',
        close: '',
    });
    $('a#popup-add-want-button').colorbox({
        scrolling: false,
        inline: true,
        href:'#add-want-popup-content',
        close: '',
    });
    $('a#popup-create-board-button').colorbox({
		scrolling: false,
		inline: true,
		href:'#create-board-popup',
		close: '',
	});	
	$('a#popup-add-video-button').colorbox({
		scrolling: false,
		inline: true,
		href:'#add-video-pin-popup-content',
		close: '',
	});
	$('a.pin-popup-link').live('click', function (){
		$(this).colorbox({open: true, scrolling: false, close:''});
		return false;
	});

	$('.popup-close-button').live('click',function () {
		$.colorbox.close();
		return false;
	});
});