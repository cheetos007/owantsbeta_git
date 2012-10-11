var facebookInvite = {
	init: function (params) {
		this.params = params;
		
		$('#invite-all').click(function (){
			if (!$('#invite-all').hasClass('disabled')) {
			var fb_ids = this.params['all_friends'];
			if (fb_ids.length>0) {
				this.sendInvites(fb_ids, $('#personal-note').val());
				$('#invite-all').addClass('disabled');
				$('#invite-selected').addClass('disabled');
			}
			}
			return false;
		}.bind(this));

		$('#invite-selected').click(function (){
			if (!$('#invite-selected').hasClass('disabled')) {
				
				var fb_ids = [];
				$('.invite-each input[type="checkbox"]').each(function (ind, elem) {
					if (elem.checked) {
						fb_ids.push(elem.name);
					}
				});
				if (fb_ids.length>0) {
					$('#invite-selected').addClass('disabled')
					this.sendInvites(fb_ids, $('#personal-note').val());

				}
			
			}
			return false;
		}.bind(this));

	},
	sendInvites: function (fb_ids, personal_note) {
		this.successfulInvites = [];
		this.invitesPendingResponse = fb_ids.length;
		this.personalNote = personal_note;
		for (var i=0;i<fb_ids.length;i++) {
			var fb_id = fb_ids[i];
			FB.api('/'+fb_id+'/feed', 'post', {message: personal_note, type: this.params['type'], name: this.params['name'],
				description: this.params['description'], link: this.params['link']}, this.responseCallback.bind(this))

		}

	},

	responseCallback: function(response) {
			//var fb_id;
			if (response.error) {
				alert("Unable to invite friends. Facebook API error: " + response.error.message);
				return;
			}

			this.successfulInvites.push(response.id.split('_')[0]);
			this.invitesPendingResponse=this.invitesPendingResponse-1;
			if (this.invitesPendingResponse==0)
				this.responsesFinished();
	},
	responsesFinished: function () {
		$('#invite-selected').removeClass('disabled');
		$.post(this.params['invites_sent_url'], {'fb_ids': this.successfulInvites.join(','), 'note': this.personalNote}, function (data) {
			if (data.status=='ok') {
				for (var i=0;i<this.successfulInvites.length;i++) {
					var fb_id = this.successfulInvites[i];
					$('li#invite-friend-'+fb_id+' .invite-actions').html('Invited!').addClass('green');
				}
			}
		}.bind(this));

	}
}