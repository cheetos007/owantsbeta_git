from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.core.files.uploadedfile import UploadedFile 

from emailconfirmation.models import EmailAddress
from sorl.thumbnail.admin.current import AdminImageWidget



def get_profile_form_class(user):
	class ProfileForm(forms.Form):
		email = forms.EmailField(label=_('Email'), initial=user.email)
		first_name = forms.CharField(label=_('First name'), required=False, initial=user.first_name)
		last_name = forms.CharField(label=_('Last name'), required=False, initial=user.last_name)
		username = forms.CharField(label=_('Username'), initial=user.username)
		about = forms.CharField(widget=forms.widgets.Textarea, label=_('About'), required=False, initial=user.get_profile().about)
		location = forms.CharField(label=_('Location'), required=False, initial=user.get_profile().location)
		website = forms.URLField(label=_('Website'), required=False, verify_exists=False, initial=user.get_profile().website)

		link_facebook = forms.BooleanField(label=_('Link Facebook account'), required=False, initial=True)
		link_twitter = forms.BooleanField(label=_('Link Twitter account'), required=False, initial=True)


		def clean_username(self):
			data = self.cleaned_data['username']
			if user.username!=data:
				if User.objects.filter(username__iexact=data).count()>0:
					raise forms.ValidationError(_("This username is already in use. Please choose another username."))
			return data

		def clean_email(self):
			data = self.cleaned_data['email']
			if User.objects.filter(email__iexact=data).exclude(pk=user.pk).count()>0 or EmailAddress.objects.filter(email__iexact=data, verified=True).exclude(user=user.pk).count()>0:
				raise forms.ValidationError(_("This e-mail address is already in use. Please use another e-mail address."))
			return data

		def save(self, commit=True):
			user.first_name = self.cleaned_data['first_name']
			user.last_name = self.cleaned_data['last_name']
			user.username = self.cleaned_data['username']
			new_email = self.cleaned_data['email']
			if user.email!=new_email and EmailAddress.objects.filter(email__iexact=new_email).count()==0:
				EmailAddress.objects.add_email(email=new_email, user=user)
			profile = user.get_profile()
			profile.about = self.cleaned_data['about']
			profile.location = self.cleaned_data['location']
			profile.website = self.cleaned_data['website']
			profile.save()

			if commit:
				user.save()
			return user


	return ProfileForm

class ProfileImageForm(forms.Form):
	image = forms.ImageField(label=_('Image'))

	def save(self, profile):
		new_img = self.cleaned_data['image']
		profile.image.save(new_img.name, new_img)
		return profile.image


def get_password_form(user):
	class PasswordForm(forms.Form):
		password = forms.CharField(label=_('Password'), widget=forms.PasswordInput)
		def clean_password(self):
			data = self.cleaned_data['password']
			if not user.check_password(data):
				raise forms.ValidationError(_("Password you entered is incorrect!"))
			return data
	return PasswordForm



