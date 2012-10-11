import random
import hashlib
from urllib import urlencode

from django.core import mail
from django.core.urlresolvers import reverse
from django.dispatch import receiver
from django.db import models
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.template.loader import get_template
from django.template import Context
from django.conf import settings
from invite_friends.settings import EMAIL_INVITE_BODY_TEMPLATE, EMAIL_INVITE_SUBJECT_TEMPLATE

class Invite(models.Model):
	"""
	Abstract base class which handles invite code generation and common fields for all types of invites.
	Other classes should inherit from this class
	"""
	user = models.ForeignKey(User, verbose_name = _('user'), related_name="%(class)s_created_set", help_text=_('User who has sent this invitation.'))
	code = models.CharField(max_length=32, verbose_name = _('code'), unique=True, help_text=_('Unique invitation code'))
	created_datetime = models.DateTimeField(verbose_name = _('created datetime'), auto_now_add=True)
	accepted_user = models.ForeignKey(User, verbose_name=_('accepted user'), related_name="%(class)s_accepted_set", null=True, blank=True, 
		help_text=_('This field is populated with user who accepted invitation on acceptance.'))
	personal_note = models.TextField(blank=True, verbose_name=_('personal note'), help_text=_('Optional personal note to receiver(s) of invitation.'))


	class Meta:
		abstract = True

	def save(self, *args, **kwargs):
		if not self.pk and not self.code:
			self.code = self._generate_code()

		return super(Invite, self).save(*args, **kwargs)

	def _generate_code(self):
		"""
		Generates unique invitation code.
		"""
		while True:
			code = hashlib.md5(str(random.random())).hexdigest()
			if self.__class__.objects.filter(code=code).count()==0:
				return code

	
	def get_absolute_url(self):
		return '%s?%s' % (reverse('acct_signup'), urlencode({'inv_type': self.__class__.__name__, 'code': self.code}))

	def accept_invitation(self, request, new_user):
		raise NotImplemented("Subclasses must implement this method!")


class EmailInvite(Invite):
	"""
	Email invite is classical invitation by e-mail- user enters e-mail address and
	an e-mail is sent which contains invitation link.
	"""
	email = models.EmailField(max_length=255, verbose_name=_('email'))

	def accept_invitation(self, request, new_user):
		self.accepted_user = new_user
		self.save()

	class Meta:
		verbose_name = _('email invite')
		verbose_name_plural = _('email invites')


@receiver(models.signals.post_save, sender=EmailInvite, dispatch_uid="invite_friends.models")
def send_email(sender, instance, created, raw, **kwargs):
	"""
	Sends e-mail about invitation to user who has been invited
	"""
	if not raw and created:
		context = Context({'invite': instance, 'site': Site.objects.get_current()})
		subject = get_template(EMAIL_INVITE_SUBJECT_TEMPLATE).render(context)
		context.update({'subject': subject})
		message = get_template(EMAIL_INVITE_BODY_TEMPLATE).render(context)
		msg = mail.EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [instance.email])
		msg.content_subtype = "html"
		msg.send()

class FacebookInvite(Invite):
	"""Since we can't get a list of users who have been sent Facebook invitations, 
	we can only use this model to track invites which are already accepted.
	For every user who has invited friends from Facebook we store one FacebookInvite with sent=True.
	Accepted Facebook invites have sent=False.
	"""
	sent = models.BooleanField(verbose_name=_('sent'), default=False, help_text=_('Determines if this invitation has been sent or accepted.'))
	facebook_user_id = models.CharField(max_length=255, verbose_name=_('Facebook user id'), blank=True)

	def accept_invitation(self, request, new_user):
		"""Facebook invitations create a new invitation object with sent=False, because invite can be accepted by multiple users"""
		
		inv = FacebookInvite.objects.create(user=self.user, sent=False, facebook_user_id=self.facebook_user_id, accepted_user=new_user, personal_note=self.personal_note)

	class Meta:
		verbose_name = _('Facebook invite')
		verbose_name_plural = _('Facebook invites')



