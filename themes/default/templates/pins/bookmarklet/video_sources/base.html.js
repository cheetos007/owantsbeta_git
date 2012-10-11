/*
* JS video source parsers act pretty much like python one's- there is a parser pool which holds registered parser classes, and each parser
* class is responsible for it's own type of videos.
* Parser classes must have parseDocument function, which accepts document instance and 
* returns an array of found videos. Each video is a dictionary containing the following attributes:
* 
* {	parser: "<parser_name>", 
* 	thumbnail: 'http://example.org/image.jpg', 
*	video_id: '<video_id>'
* }
* Parser name must match existing, python video parser name!
*/

var video_source_pool = {
	parsers: [],
	parseDocument: function (d) {
		var results = [];
		for (var i=0;i<this.parsers.length;i++) {
			results = results.concat(this.parsers[i].parseDocument(d));
		}
		return results;
	},
	registerParser: function (p) {
		this.parsers.push(p);
	}
};
function getJSON(URL,success){
    var ud = 'json'+(Math.random()*100).toString().replace(/\./g,'');
    window[ud]= function(o){
        success&&success(o);
    };
    document.getElementsByTagName('body')[0].appendChild((function(){
        var s = document.createElement('script');
        s.type = 'text/javascript';
        s.src = URL.replace('callback=?','callback='+ud);
        return s;
    })());
}