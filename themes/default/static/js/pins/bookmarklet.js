(function () {
	var static_url = 'http://localhost:8000/site_media/static/';
	/* Helper functions
	*/
	var addEvent = function (html_element, event_name, event_function) 
	{       
	   if(html_element.attachEvent) //Internet Explorer
	      html_element.attachEvent("on" + event_name, function() {event_function.call(html_element);}); 
	   else if(html_element.addEventListener) //Firefox & company
	      html_element.addEventListener(event_name, event_function, false); //don't need the 'call' trick because in FF everything already works in the right way          
	};

	var closeOverlay = function () {
		var overlay = document.getElementById('pbmOverlay');
		document.body.removeChild(overlay);
		return false;
	};

	var returnPinFunction = function (pin_src) {
		return function () {
			alert("Pinning pin: "+ pin_src +', ' + window.location.href);
		};
	}

	/**
	* Creates overlay with contents.
	* @param sorted_images Array of dict's which contain image's src attribute, total area (sorted by this), width & height
	*/
	var createOverlay = function (sorted_images) {
		var cssUrl = static_url + "css/pins/bookmarklet.css?r="+Math.random(0,100000);
		console.log(sorted_images);
		var cssElem = document.createElement('link');
		cssElem.setAttribute('rel', 'stylesheet');
		cssElem.setAttribute('type', 'text/csss');
		cssElem.setAttribute('href', cssUrl);
		document.getElementsByTagName('head')[0].appendChild(cssElem);
		var overlayBase = document.createElement('div');
		overlayBase.setAttribute('id', 'pbmOverlay');
		
		closeButton = document.createElement('a');
		closeButton.setAttribute('class', 'close-button');
		closeButton.innerHTML = "Cancel pin";
		addEvent(closeButton, 'click', closeOverlay);
		overlayBase.appendChild(closeButton);
		
		for (var i=0;i<sorted_images.length;i++) {
			var image = sorted_images[i];
			var imgContainer = document.createElement('div');
			imgContainer.setAttribute('class','btn-container');
			var pinBtnContainer = document.createElement('a');
			pinBtnContainer.setAttribute('class', 'pin-button-container');
			addEvent(pinBtnContainer, 'click', returnPinFunction(image.src));
			var pinBtn = document.createElement('div');
			pinBtn.setAttribute('class','pin-button');
			pinBtn.innerHTML = "Pin it";
			pinBtnContainer.appendChild(pinBtn);



			var img = document.createElement('img');
			img.setAttribute('src', image.src);

			if (img.height>200 || img.width>200) {
				//calculate new size of image so it fits inside and aspect ratio is not lost
				if (img.height > img.width) {
					//we need to compress it vertically
					var new_height = 200;
					var new_width = (new_height*img.width) / img.height;
					
				} else if (img.height <= img.width) {
					//we need to compress it horizontally
					var new_width = 200;
					var new_height = (new_width*img.height) / img.width;
					
				}
				else {
					//no need to compress
					var new_width = img.width;
					var new_height = img.height;
				}

				var leftOffset = parseInt((200 - new_width) / 2);
				var topOffset = parseInt((200-new_height)/2);

				img.setAttribute('height', parseInt(new_height));
				img.setAttribute('width', parseInt(new_width));
				img.setAttribute('style', "top: "+topOffset+"px; left:"+leftOffset+"px;");
				pinBtnContainer.appendChild(img);
			}

			imgContainer.appendChild(pinBtnContainer);

			overlayBase.appendChild(imgContainer);
		}
		document.body.appendChild(overlayBase);
	};

	var fetchImages = function () {
		var images = document.getElementsByTagName('img');
		var sorted_images = [];
		for(var i=0;i<images.length;i++) {
			var img = images[i];
			if (img.clientWidth>100 && img.clientHeight > 100)
				sorted_images.push({'src': img.src,'area': parseInt(img.clientWidth * img.clientHeight), 
						'height': parseInt(img.clientHeight), 'width': parseInt(img.clientWidth)
					});
		}
		if (sorted_images.length==0) {
			alert('Sorry, no products found!');
			return;
		}
		sorted_images.sort(function (a, b) {return b.area - a.area});
		
		createOverlay(sorted_images);
	};

	if (!document.getElementById('pbmOverlay'))
		fetchImages();
})();