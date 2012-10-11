from django import forms
from django.utils.translation import ugettext_lazy as _

from pins.models import Board, Category


class BoardForm(forms.ModelForm):
	category = forms.ModelChoiceField(label=_("Category"),
			queryset=Category.objects.filter(is_active=True),
			empty_label=None)
	class Meta:
		model = Board
		fields = ("name", "category",)

class OptionalBoardForm(forms.ModelForm):
	category = forms.ModelChoiceField(label=_("Category"),
			queryset=Category.objects.filter(is_active=True),
			empty_label=None)
	name = forms.CharField(label=_("Name"), required=False)
	class Meta:
		model = Board
		fields = ("name", "category",)