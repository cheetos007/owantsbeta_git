from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
from django.template import Context
from django.template.loader import get_template
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse

from site_settings.helpers import get_setting

from audit_fields.models import BaseAuditModel



class AbuseReport(BaseAuditModel):
    status = models.CharField(verbose_name = _('status'), max_length=50, 
        choices=(('new', _('New')), ('processing', _('Processing')), ('rejected',_('Rejected')), ('fulfilled', _('Fulfilled'))),
        default='new')

    description = models.TextField(verbose_name = _('description'), blank=True)

    reason = models.ForeignKey('AbuseReportReason', verbose_name=_('reason'))

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = _('abuse report')
        verbose_name_plural = _('abuse reports')
        ordering = ['-id']

    def __unicode__(self):
        return self.description

    
    def get_absolute_url(self):
        return reverse('admin:abuse_reports_abusereport_change', args=(self.pk, ))




class AbuseReportReason(BaseAuditModel):
    name = models.CharField(verbose_name = _('name'), max_length = 100)

    class Meta:
        verbose_name =_('abuse report reason')
        verbose_name_plural = _('abuse report reasons')

    def __unicode__(self):
        return self.name



def email_send(sender, instance, created, raw, **kwargs):
    if not raw and created:
        if hasattr(instance.content_object, 'is_flagged'):
            instance.content_object.is_flagged = True
            instance.content_object.save()

        context = Context({'report': instance})
        subject = get_template('abuse_reports/new_report_subject.txt').render(context)
        context = Context({'subject': subject,'report':instance, 'SITE': Site.objects.get_current()})
        text = get_template('abuse_reports/new_report.html').render(context)
        
        to = get_setting("administrator_email")
        from_addr = settings.DEFAULT_FROM_EMAIL
        send_mail(subject, text, from_addr, [to], fail_silently=False)

if settings.SEND_EMAIL_FOR_ABUSE_REPORTS:
    models.signals.post_save.connect(email_send, sender=AbuseReport, dispatch_uid="abuse_reports.models")

        








