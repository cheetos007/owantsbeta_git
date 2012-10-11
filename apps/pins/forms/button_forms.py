from django import forms
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

validator = URLValidator(verify_exists=False)

class IframeParamsForm(forms.Form):
	image_url = forms.URLField(label=_('URL of the image to pin'), verify_exists=False, max_length=255)
	url = forms.CharField(label=_('URL of the page where pin is on'), max_length=255, required=False)
	description = forms.CharField(required=False, widget=forms.Textarea)
	button_type = forms.ChoiceField(label=_('Number of pins placement'), choices=(('vertical',_('Vertical')), ('horizontal', _('Horizontal')), ('none', _('None'))), 
		initial='horizontal', required=False)


	def clean_url(self):
		"""If URL is invalid, return '' instead of triggering validation error"""
		data = self.cleaned_data['url']
		try:
			validator(data)
		except ValidationError:
			data = ''
		return data

