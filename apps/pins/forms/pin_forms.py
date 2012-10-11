from urlparse import urlparse
import urllib2
import os
import random

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.files import File
from django.core.files.base import ContentFile

from pins.models import Pin, Board
from pins.video_source_pool import parser_pool

class AddPinForm(forms.ModelForm):
	image = forms.ImageField(label=_("Image"))
	class Meta:
		model = Pin
		fields = ("image", "board", "description")

class UploadPinForm(forms.ModelForm):
	image = forms.ImageField(label=_("Image"))
	class Meta:
		model = Pin
		fields = ("image", )

def get_pin_description_form(user):
	class PinDescriptionForm(forms.ModelForm):
		board = forms.ModelChoiceField(label=_("Room"), queryset=Board.objects.get_user_boards(user),
			empty_label=None)
		class Meta:
			model = Pin
			fields = ("board", "description")
	return PinDescriptionForm


class WebsiteURLForm(forms.Form):
	url = forms.URLField(max_length=255, verify_exists=False)

def get_pin_url_form(user):
	superform = get_pin_description_form(user)
	class PinFromURLForm(superform):
		image_url = forms.URLField(max_length=255, verify_exists=False, required=False)
		parser = forms.CharField(required=False)
		video_id = forms.CharField(required=False)

		class Meta:
			model = Pin
			fields = ("url", "board", "description")

		def clean(self, *args, **kwargs):
			super(PinFromURLForm, self).clean(*args, **kwargs)
			if 'image_url' in self.cleaned_data and self.cleaned_data['image_url']:
				img_url = self.cleaned_data['image_url']
				image_name = urlparse(img_url).path.split('/')[-1]

				#shorten long image strings
				name, ext = os.path.splitext(image_name)
				image_name = "%s_%f%s" % (name[:40], random.random(), ext)
				
				self.instance.image.save(image_name, ContentFile(urllib2.urlopen(img_url).read()))
			return self.cleaned_data

		def save(self, *args, **kwargs):
			if 'parser' in self.cleaned_data and self.cleaned_data['parser']:
				video_descriptor = parser_pool.get_video_descriptor(self.cleaned_data['parser'],
					self.cleaned_data['video_id'])
				self.instance.video_parser = self.cleaned_data['parser']
				self.instance.video_id = self.cleaned_data['video_id']
				local_image = video_descriptor.get_image_file()
				self.instance.image.save(local_image[0], local_image[1])

			return super(PinFromURLForm, self).save(*args, **kwargs)


	return PinFromURLForm

def get_repin_form(user):
	superform = get_pin_description_form(user)
	class RepinForm(superform):
		class Meta:
			model = Pin
			fields = ("repinned_pin", "board", "description")
		def save(self, *args, **kwargs):
			if 'repinned_pin' in self.cleaned_data:
				if self.cleaned_data['repinned_pin'].source_pin:
					self.instance.source_pin = self.cleaned_data['repinned_pin'].source_pin
				else:
					self.instance.source_pin = self.cleaned_data['repinned_pin']
				self.instance.url = self.instance.source_pin.url
				self.instance.domain = self.instance.source_pin.domain
			self.instance.is_repin = True
			return super(RepinForm, self).save(*args, **kwargs)
	return RepinForm


class PinLikeForm(forms.Form):
	pin = forms.ModelChoiceField(label=_("Pin"), 
		queryset=Pin.objects.filter(is_active=True, 
			board__is_active=True, board__category__is_active=True))
