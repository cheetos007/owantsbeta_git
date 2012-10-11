from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from pins.models import Pin, PinDomain, Board
from pins.forms.board_forms import BoardForm
from pins.helpers import process_pin_list_request


@login_required
def boards(request):
	"""Shows all boards of current user"""
	boards = Board.objects.get_user_public_boards(request.user)

	return direct_to_template(request, "pins/rooms/boards.html", locals())

@login_required
def add_board(request):
	"""
	Allows user to add board
	"""
	form = BoardForm(request.POST or None)
	if form.is_valid():
		board = form.save(commit=False)
		board.user = request.user
		board.save()
		messages.success(request, _('Board created successfully. You can now pin things you love on this board!'))
		return redirect('boards')
	return direct_to_template(request, "pins/rooms/form.html", locals())

def single_board(request, board_pk, slug):
	"""Shows all pins for certain board"""
	board = get_object_or_404(Board.objects.all().select_related('category'), is_active=True, pk=board_pk,
	category__is_active=True)
	pins = board.pin_set.filter(is_active=True).select_related('source_pin', 'domain','repinned_pin')

	extra = {'board': board}
	return process_pin_list_request(request, pins, "pins/rooms/single_board.html", extra)

@login_required
def edit_board(request, board_pk):
	board = get_object_or_404(Board, is_active=True, pk=board_pk, user=request.user,
	category__is_active=True)
	form = BoardForm(request.POST or None, instance=board)
	form_type = 'edit'#used in template
	if form.is_valid():
		form.save()
		messages.success(request, _('Board edited successfully.'))
		return redirect(board.get_absolute_url())
	return direct_to_template(request, "pins/rooms/form.html", locals())

@login_required
def delete_board(request, board_pk):
	board = get_object_or_404(Board, is_active=True, pk=board_pk, user=request.user,
	category__is_active=True)
	if request.method=='POST' and 'ok' in request.POST:
		board.is_active = False
		board.save()
		messages.success(request, _('Board deleted successfully!'))
		return redirect("home")
	return direct_to_template(request, "pins/rooms/delete_board.html", locals())
