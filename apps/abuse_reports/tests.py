"""
Tests for abuse report app.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from abuse_reports.models import AbuseReport, AbuseReportReason
from abuse_reports.forms import get_abuse_form_class


from django.test.client import Client

class ModelTest(TestCase):

    def test_model(self):
        u = User.objects.create(username="test user")
        reason = AbuseReportReason.objects.create(name="test reason")
        r = AbuseReport.objects.create(content_object = u, reason=reason)
        self.assertEqual(r.status, 'new')
        self.assertEqual(r.content_object, u)

    def test_form(self):
        r = AbuseReportReason.objects.create(name="test reason")
        u = User.objects.create(username="test user")
        description_text = 'Some test description'
        AbuseReportForm = get_abuse_form_class(u)
        form = AbuseReportForm(data={'description': description_text , 'content_object': u, 'reason' : r.pk})
        reason = form.save()
        self.assertIsInstance(reason, AbuseReport)
        self.assertEqual(reason.description, description_text)
        self.assertEqual(reason.content_object, u)

    def test_report_view(self):
        u = User.objects.create(username="test user")
        u_ct = ContentType.objects.get_for_model(User)
        r = AbuseReportReason.objects.create(name="test reason")
        c = Client()
        url = reverse('report_abuse', args = (u_ct.pk, u.pk))

        response = c.get(url)
        self.assertEqual(response.status_code, 200)

    def test_report_submission(self):
        u = User.objects.create(username="test user")
        u_ct = ContentType.objects.get_for_model(User)
        r = AbuseReportReason.objects.create(name="test reason")
        c = Client()
        description_text = 'Unique description text'
        url = reverse('report_abuse', args = (u_ct.pk, u.pk))

        response = c.post(url, {'description': description_text, 'reason': r.pk})
        
        self.assertEqual(AbuseReport.objects.filter(description=description_text).count(), 1)






