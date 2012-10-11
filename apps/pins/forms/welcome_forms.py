from django import forms
from pins.models import Category

class CategorySelectForm(forms.Form):
	selected_categories = forms.ModelMultipleChoiceField(queryset=Category.objects.get_list_for_welcome_screen(), required=True)