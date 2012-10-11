var vimeo_parser = {
	video_id_regex: new RegExp('(?:[\w]+\.)*vimeo\.com(?:[\/\w]*\/videos?)?\/([0-9]+)'),
	vimeo_embed_regex: new RegExp('.*vimeo\.com.*clip_id=([0-9]+).*'),
	createResult: function (video_id) {
		getJSON('http://www.vimeo.com/api/v2/video/' + video_id + '.json?callback=?',function(data){
			if (data.length==1)
    		owants.addMediaThumb({thumbnail:data[0].thumbnail_medium, video_id: data[0].id, parser: 'VimeoParser'});
		});

		return {complete_data: false, video_id: video_id, parser: 'VimeoParser'};
	},

	parseDocument: function (d) {
		var objects = d.getElementsByTagName('embed');
		var results = [];
		for (var i=0;i<objects.length;i++) {
			var matches = this.vimeo_embed_regex.exec(objects[i].src);
			if (matches==null || matches.length!=2) {
				matches = this.video_id_regex.exec(window.location.href);
			}
			if (matches!=null && matches.length==2) {
				var found=false;
				var video_id = matches[1];
				for (var j=0;j<results.length;j++) {
					if (results[j].video_id==video_id) {
						found=true;
						break;
					}
				}
				if (!found)
					results.push(this.createResult(matches[1]));
			}
		}
		return results;
	}
}
video_source_pool.registerParser(vimeo_parser);
