from django import forms
from site_settings.models import Setting

class SettingForm(forms.ModelForm):
	class Meta:
		model = Setting

	def clean_is_active(self):
		new_value = self.cleaned_data['is_active']
		if new_value == True:
			#check if there are no other sets of settings which are active
			if Setting.objects.filter(is_active=True).exclude(pk=self.instance.pk).count()>0:
				raise forms.ValidationError("""You tried to activate these settings, but there is already a group of settings which is active. 
					You need to de-activate the previous settings to activate this set of settings.""")
		return new_value
				
