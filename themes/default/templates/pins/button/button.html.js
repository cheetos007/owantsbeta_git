(function (doc) {
	var links = doc.getElementsByTagName('A');

	for (var i=0;i<links.length;i++) {
		var link = links[i];

		var iframe = doc.createElement('iframe');

		var parts = link.href.split('?');
		var vars = parts[1].split('&');
		var params = {};
		for (var i=0;i<vars.length;i++) {
			var pair = vars[i].split('=');
			params[pair[0]]=decodeURIComponent(pair[1]);
		}
		if (typeof(params['button_type'])=='undefined' || params['button_type']=='horizontal') {
			var size = [71, 25];
		} else if (params['button_type']=='vertical') {
			var size = [49, 58];
		} else {
			var size = [49, 25];
		}
		if (typeof(params['url'])=='undefined')
			params['url'] = window.location.href;

		var src = parts[0] + '?';
		for (var key in params) {
			src = src + key +'=' +encodeURIComponent(params[key])+'&';
		}


	    iframe.setAttribute("src", src);
        iframe.setAttribute("scrolling", "no");
        iframe.allowTransparency = true;
        iframe.frameBorder = 0;
        iframe.style.border = "none";
        iframe.style.width = size[0]+"px";
        iframe.style.height = size[1]+"px";
        link.parentNode.replaceChild(iframe, link)
	}
})(document);