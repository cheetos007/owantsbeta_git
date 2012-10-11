import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from audit_fields.middleware import thread_namespace


#Model which adds audit fields- created datetime, updated/modified datetime, created by user and last modified user
#created by and modified by user is set to current user from request, if that info is available
#it uses threadlocals which is potentially unsafe: http://code.djangoproject.com/wiki/CookBookThreadlocalsAndUser

class BaseAuditModel(models.Model):
    created_datetime = models.DateTimeField(_('created datetime'), 
                                            default=datetime.datetime.now)
    modified_datetime = models.DateTimeField(_('modified datetime'), 
                                             default=datetime.datetime.now)
    created_user = models.ForeignKey(verbose_name = _('created user'), to = User, blank = True, 
                                     null = True, related_name = '%(app_label)s_%(class)s_created_set')
    
    modified_user = models.ForeignKey(verbose_name = _('modified user'), to = User, blank = True, 
                                      null = True, related_name = '%(app_label)s_%(class)s_modified_set')
    class Meta:
        abstract = True
    
    def save(self,**kwargs):
        #updates modified datetime if object already exists
        current_user = getattr(thread_namespace, 'user', None)

        if current_user and current_user.is_authenticated():
            if self.pk:
                self.modified_datetime = datetime.datetime.now()
                self.modified_user = getattr(thread_namespace,'user',None)
            else:
                self.created_user = current_user
        return super(BaseAuditModel, self).save(**kwargs)
