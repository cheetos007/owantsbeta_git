
from pins.forms import get_pin_description_form
from pins.forms.board_forms import BoardForm

def pin_form_processor(request):
	if not request.user.is_authenticated():
		return {}
	else:
		data = {}
		for k,v in request.GET.iteritems():
			data[k]=v

		return {'pin_form': get_pin_description_form(request.user)(initial=data), 'board_form': BoardForm()}