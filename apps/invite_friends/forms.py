from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms.models import BaseModelFormSet


from invite_friends.models import EmailInvite


def email_invite_form_factory(user):
	class EmailInviteForm(forms.ModelForm):

		class Meta:
			model = EmailInvite
			fields = ('email', )

		def save(self, *args, **kwargs):
			self.instance.user = user
			return super(EmailInviteForm, self).save(*args, **kwargs)
	return EmailInviteForm

class PersonalNoteForm(forms.Form):
	personal_note = forms.CharField(widget=forms.widgets.Textarea, label=_('Personal note'), required=False)


class BaseEmailInviteFormSet(BaseModelFormSet):
	def clean(self):
		"""Validates that at least one email address is entered"""
		if any(self.errors):
			# Don't bother validating the formset unless each form is valid on its own
			return
		non_blank_found = False
		for i in range(0, self.total_form_count()):
			form = self.forms[i]
			if form.is_valid() and 'email' in form.cleaned_data and form.cleaned_data['email']:
				non_blank_found = True
				break
		if not non_blank_found:
			raise forms.ValidationError(_("You must enter at least one e-mail address."))

