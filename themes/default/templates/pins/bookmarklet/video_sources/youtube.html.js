var youtube_parser = {
	video_id_regex: new RegExp('(?:youtube(?:-nocookie)?\.com/(?:[^/]+/.+/|(?:v|e(?:mbed)?)/|.*[?&]v=)|youtu\.be/)([^"&?/ ]{11})'),
	createResult: function (video_id) {
		return {thumbnail:'http://img.youtube.com/vi/'+video_id+'/hqdefault.jpg', video_id: video_id, parser: 'YoutubeParser'};
	},
	parseDocument: function (d) {
		var objects = d.getElementsByTagName('embed');
		var results = [];
		for (var i=0;i<objects.length;i++) {
			var matches = this.video_id_regex.exec(objects[i].src);
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
video_source_pool.registerParser(youtube_parser);