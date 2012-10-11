REQUEST_IN_PROGRESS = false;

function updatePins(data) {
	if (data.status=='ok') {
		for (var i=0;i<data.pins.length;i++) {
			pin = data.pins[i];
			li = document.createElement('li');
			if (pin.content) {
				li.innerHTML = pin.content;
			} else {
				var html = $('#blank-pin-template').html();
				html = html.replace(/__pin.get_popup_url__/g, pin.popup_url);
				html = html.replace(/__pin.get_absolute_url__/g, pin.absolute_url);
				html = html.replace(/__pin.pk__/g, pin.pk);
				html = html.replace(/__pin.get_number_of_repins__/, pin.number_of_repins);
				html = html.replace(/__pin.get_number_of_likes__/, pin.number_of_likes);
				html = html.replace(/__pin.description__/, pin.description);
				html = html.replace(/__im.url__/, pin.thumbnail.url);
				html = html.replace(/__im.height__/, pin.thumbnail.height);
				html = html.replace(/__im.width__/, pin.thumbnail.width);
				li.innerHTML = html;
				$(li).find('.option-button').addClass('round-corners');
				var comment_html = $(li).find('.pin-comments').html();
				var resulting_comment_html = '';
				for (var j=0;j<pin.comments.length;j++) {
					var c = pin.comments[j];
					var c_html = comment_html;
					var color = 'color' + ((j % 2) + 1);
					c_html = c_html.replace(/__comment.color__/, color);
					c_html = c_html.replace(/__comment.comment__/, c.comment);
					c_html = c_html.replace(/__comment.im.url__/, c.im.url);
					c_html = c_html.replace(/__comment.im.height__/, c.im.height);
					c_html = c_html.replace(/__comment.im.width__/, c.im.width);
					resulting_comment_html = resulting_comment_html + c_html;
				}
				$(li).find('.pin-comments').html(resulting_comment_html);
			}
			$('#pin-grid').append(li);
		}
		// Clear our previous layout handler.
        if(window.wkhandler) window.wkhandler.wookmarkClear();
        
		// Get a reference to your grid items.
      	window.wkhandler = $('#pin-grid li');
      
      	// Call the layout function.
      	window.wkhandler.wookmark(window.wkoptions);
	}
	REQUEST_IN_PROGRESS = false;
}

$(function () {
	if (typeof(window.MORE_PINS_URL)!='undefined') {
		$(window).scroll(function (e){
		    if (document.body.offsetHeight - document.body.scrollTop - window.innerHeight<=150) {
		    	if (!REQUEST_IN_PROGRESS) {
		    		REQUEST_IN_PROGRESS = true;
		        	window.PINS_START = window.PINS_START + window.PINS_PER_REQUEST;
		        	$.get(window.MORE_PINS_URL+window.PINS_START, updatePins);
				}
		    }

		});
	}
});