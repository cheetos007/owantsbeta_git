{# This Javascript is included in target site when the bookmarklet is executed. It is rendered as template because it needs access to translations and server\'s URL, which can change #}
    {% load compress setting_tags i18n cache %}
    {% get_current_language as LANGUAGE_CODE %}
    {% include "pins/bookmarklet/video_sources/base.html.js" %}
    {% include "pins/bookmarklet/video_sources/youtube.html.js" %}
    {% include "pins/bookmarklet/video_sources/vimeo.html.js" %}
    var owants = {
        static_url:'http://{{request.get_host}}{{STATIC_URL}}',
        /* Helper functions
         */
        addEvent: function (html_element, event_name, event_function)
        {
            if(html_element.attachEvent) //Internet Explorer
                html_element.attachEvent("on" + event_name, function() {event_function.call(html_element);});
            else if(html_element.addEventListener) //Firefox & company
                html_element.addEventListener(event_name, event_function, false); //don't need the 'call' trick because in FF everything already works in the right way
        },

        browser: {
            ie: /MSIE/i.test(navigator.userAgent),
            ie6: /MSIE 6/i.test(navigator.userAgent),
            ie7: /MSIE 7/i.test(navigator.userAgent),
            ie8: /MSIE 8/i.test(navigator.userAgent),
            firefox: /Firefox/i.test(navigator.userAgent),
            opera: /Opera/i.test(navigator.userAgent),
            webkit: /Webkit/i.test(navigator.userAgent)
        },

        setClassName: function (element, classname) {
            if (this.browser.ie) {
                element.className=classname;
            }
            else {
                element.setAttribute('class', classname);
            }
        },
        closeOverlay: function () {
            var overlay = document.getElementById('pbmOverlay');
            document.body.removeChild(overlay);
            document.body.removeChild(document.getElementById('owants_shim'));
            return false;
        },

        returnOwnFunction: function (pin_src) {
            return function () {
                var urlBase = 'http://{{request.get_host}}{% url own_bookmarklet %}?';
                if (typeof(pin_src.src)!='undefined')
                    urlBase = urlBase + 'media_type=image&media='+encodeURIComponent(pin_src.src);
                else
                    urlBase = urlBase + 'media='+encodeURIComponent(pin_src.thumbnail)+'&media_type=video&parser='+encodeURIComponent(pin_src.parser)+'&video_id='+encodeURIComponent(pin_src.video_id);
                newwindow=window.open(urlBase+'&src='+encodeURIComponent(window.location.href),'name','height=650,width=700');
                closeOverlay();
                if (window.focus) {newwindow.focus()}
                return false;
            };
        },

        returnWantFunction: function (pin_src) {
            return function () {
                var urlBase = 'http://{{request.get_host}}{% url want_bookmarklet %}?';
                if (typeof(pin_src.src)!='undefined')
                    urlBase = urlBase + 'media_type=image&media='+encodeURIComponent(pin_src.src);
                else
                    urlBase = urlBase + 'media='+encodeURIComponent(pin_src.thumbnail)+'&media_type=video&parser='+encodeURIComponent(pin_src.parser)+'&video_id='+encodeURIComponent(pin_src.video_id);

                newwindow=window.open(urlBase+'&src='+encodeURIComponent(window.location.href),'name','height=650,width=700');
                closeOverlay();
                if (window.focus) {newwindow.focus()}
                return false;
            };
        },

        onImageLoad : function () {
            if (isNaN(this.clientHeight) || this.clientHeight==1) {
                //probably falsely detected video id
                return;
            }
            if (this.clientHeight>200 || this.clientWidth>200) {
                //calculate new size of image so it fits inside and aspect ratio is not lost
                if (this.clientHeight > this.clientWidth) {
                    //we need to compress it vertically
                    var new_height = 200;
                    var new_width = (new_height*this.clientWidth) / this.clientHeight;

                } else if (this.clientHeight <= this.clientWidth) {
                    //we need to compress it horizontally
                    var new_width = 200;
                    var new_height = (new_width*this.clientHeight) / this.clientWidth;

                }
                else {
                    //no need to compress
                    var new_width = this.clientWidth;
                    var new_height = this.clientHeight;
                }
            } else {
                var new_width = this.clientWidth;
                var new_height = this.clientHeight;
            }
            var leftOffset = parseInt((200 - new_width) / 2);
            var topOffset = parseInt((200-new_height)/2);

            if (new_height)
                this.setAttribute('height', parseInt(new_height));
            if (new_width)
                this.setAttribute('width', parseInt(new_width));
            else if (!new_height) {
                this.setAttribute('width', 200);
                this.style.maxHeight='200px';
            }

            this.setAttribute('style', "top: "+topOffset+"px; left:"+leftOffset+"px;");
        },
        addMediaThumb: function (media_item) {
            if (typeof(media_item.complete_data)!='undefined' && media_item.complete_data==false)
                return;
            var imgContainer = document.createElement('div');
            this.setClassName(imgContainer, 'btn-container');

            var pinBtnContainer = document.createElement('a');
            this.setClassName(pinBtnContainer, 'pin-button-container');

            var img = document.createElement('img');
            if (typeof(media_item.src)!='undefined')
                img.setAttribute('src', media_item.src);
            else
                img.setAttribute('src', media_item.thumbnail);
            img.onload = this.onImageLoad;
            pinBtnContainer.appendChild(img);

            var ownBtnContainer = document.createElement('a');
            var ownBtn = document.createElement('div');
            this.setClassName(ownBtn,'own-button');
            ownBtn.innerHTML = "{% trans "Own it" %}";
            this.addEvent(ownBtnContainer, 'click', this.returnOwnFunction(media_item));
            ownBtnContainer.appendChild(ownBtn);
            pinBtnContainer.appendChild(ownBtnContainer);

            var wantBtnContainer = document.createElement('a');
            var wantBtn = document.createElement('div');
            this.setClassName(wantBtn,'want-button');
            wantBtn.innerHTML = "{% trans "Want it" %}";
            this.addEvent(wantBtnContainer, 'click', this.returnWantFunction(media_item));
            wantBtnContainer.appendChild(wantBtn);
            pinBtnContainer.appendChild(wantBtnContainer);

            imgContainer.appendChild(pinBtnContainer);
            this.overlayBase.appendChild(imgContainer);

        },


        /**
         * Creates overlay with contents.
         * @param sorted_images Array of dict's which contain image's src attribute, total area (sorted by this), width & height
         */
        createOverlay: function (media_list) {
            var cssUrl = this.static_url + "css/pins/bookmarklet.css?r="+Math.random(0,100000);
            var cssElem = document.createElement('link');
            cssElem.setAttribute('rel', 'stylesheet');
            cssElem.setAttribute('type', 'text/css');
            cssElem.setAttribute('href', cssUrl);
            document.getElementsByTagName('head')[0].appendChild(cssElem);
            if (this.browser.ie) {
                var cssUrl = this.static_url + "css/pins/bookmarklet_ie.css?r="+Math.random(0,100000);
                var cssElem = document.createElement('link');
                cssElem.setAttribute('rel', 'stylesheet');
                cssElem.setAttribute('type', 'text/css');
                cssElem.setAttribute('href', cssUrl);
                document.getElementsByTagName('head')[0].appendChild(cssElem);
            }


            this.overlayBase = document.createElement('div');
            this.overlayBase.setAttribute('id', 'pbmOverlay');

            closeButton = document.createElement('a');
            this.setClassName(closeButton, 'close-button');
            closeButton.innerHTML = "{% trans "Cancel" %}";
            this.addEvent(closeButton, 'click', this.closeOverlay);
            this.overlayBase.appendChild(closeButton);

            for (var i=0;i<media_list.length;i++) {
                var media = media_list[i];
                this.addMediaThumb(media);
            }
            document.body.appendChild(this.overlayBase);
            ifr = document.createElement('iframe');
            ifr.setAttribute('id', 'owants_shim');
            ifr.setAttribute('height', '100%');
            ifr.setAttribute('width', '100%');
            ifr.setAttribute('allowTransparency', true);
            document.body.appendChild(ifr);
        },

        fetchImages: function () {
            var images = document.getElementsByTagName('img');
            var sorted_images = [];
            for(var i=0;i<images.length;i++) {
                var img = images[i];
                var found = false;
                for (var j=0;j<sorted_images.length;j++) {
                    if (sorted_images[j].src==img.src) {
                        found=true;
                        break;
                    }
                }
                if (!found && img.clientWidth>100 && img.clientHeight > 100)
                    sorted_images.push({'src': img.src,'area': parseInt(img.clientWidth * img.clientHeight),
                        'height': parseInt(img.clientHeight), 'width': parseInt(img.clientWidth)
                    });
            }

            sorted_images.sort(function (a, b) {return b.area - a.area});
            return sorted_images;
        },


        fetchMedia: function () {
            var images = this.fetchImages();
            var results = images.concat(video_source_pool.parseDocument(document));
            if (results.length==0) {
                alert('{% trans "Sorry, no products found!" %}');
                return;
            }
            this.createOverlay(results);
        },
    };
    if (!document.getElementById('pbmOverlay'))
        owants.fetchMedia();


