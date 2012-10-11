"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from site_settings.models import Setting
from site_settings.helpers import get_setting
from django.utils.translation import get_language
from django.utils.translation import trans_real
from django.template import Template, Context

class SettingTest(TestCase):

    def test_setting_addition(self):
    	s = Setting()
    	s.site_name = "Example name"
    	s.save()
    	self.assertEquals(get_setting('site_name',''), "Example name")

    def test_setting_translation(self):
    	s = Setting.objects.create()
    	s.site_name = "Example name"
    	s.save()
    	
    	trans_real.activate('es')
    	
    	s.site_name = "Example in Spanish"
    	s.save()
    	self.assertEquals(get_setting('site_name', ''), s.site_name)

    def test_templatetag(self):
    	s = Setting()
    	s.site_name = "Example name"
    	s.save()
    	template = Template('{% load setting_tags %}{% site_setting "site_name" %}')
    	self.assertEquals(template.render(Context({})), "Example name")



