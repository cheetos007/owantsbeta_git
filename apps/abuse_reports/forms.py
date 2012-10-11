from django import forms

from abuse_reports.models import AbuseReport
from django.contrib.contenttypes.models import ContentType


def get_abuse_form_class(obj):
	"""
	Returns form class which will only contain fields neccessary from user- reason and description.
	When form is saved, it automatically creates required associations to obj.
	"""
	class AbuseReportForm(forms.ModelForm):
		class Meta:
			model = AbuseReport
			fields = ('reason','description')

		def save(self, *args, **kwargs):
			self.instance.content_type = ContentType.objects.get_for_model(obj.__class__)
			self.instance.object_id = obj.pk
			return super(AbuseReportForm, self).save(*args, **kwargs)
	return AbuseReportForm
