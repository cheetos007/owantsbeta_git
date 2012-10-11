from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404, redirect
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site

from abuse_reports.forms import get_abuse_form_class
from abuse_reports.models import AbuseReport


def report_abuse(request, content_type, object_id):
	content_type = get_object_or_404(ContentType, pk=content_type)
	model = content_type.model_class()

	obj = get_object_or_404(model, pk=object_id)

	form = get_abuse_form_class(obj)(request.POST or None)


	if form.is_valid():
		report = form.save()
		messages.success(request, _('Thank you for submitting abuse report. Administrator has been notified and will review your report!'))
		return redirect(obj.get_absolute_url())

	return direct_to_template(request, "abuse_reports/form.html", locals())


def preview_email(request):

    report=AbuseReport.objects.all()[0]
    SITE= Site.objects.get_current()
    
    return direct_to_template(request, 'abuse_reports/new_report.html', locals())