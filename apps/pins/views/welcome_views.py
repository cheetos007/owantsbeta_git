from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.db.models import Count
from django.contrib.auth.models import User
from django.forms.formsets import formset_factory

from actstream.actions import follow


from pins.models import Category, DefaultBoard, Board
from pins.forms.welcome_forms import CategorySelectForm
from pins.forms.board_forms import OptionalBoardForm

@login_required
def welcome_wizard(request):
	"""
	Step 1 of welcome wizard- interested category selection
	"""
	categories = Category.objects.get_list_for_welcome_screen()
	if request.method=="POST":
		selected_categories = request.POST['selected_categories'].split(',')
		if len(selected_categories)>0 and selected_categories[0]:
			request.session['selected_categories'] = selected_categories
			return redirect('choose_people_to_follow')
		else:
			error = True
	return direct_to_template(request,"pins/welcome/step_1.html", locals())



@login_required
def choose_people_to_follow(request):
	"""
	Step 2 of welcome wizard- presents newly registered user some suggested people to follow.
	Users to follow are selected either from:
		1) Category model's recommended_users_to_follow field
		2) At random from users with at least 40 pins 
		3) At random from all users with pins in selected categories
	"""
	#how many users should we show per category
	USERS_PER_CATEGORY = 4
	USER_PREFERRED_NUMBER_OF_PINS = 40

	selected_categories = Category.objects.filter(pk__in=request.session['selected_categories'])

	for c in selected_categories:
		c.users_to_follow = c.suggest_users_to_follow(USERS_PER_CATEGORY, USER_PREFERRED_NUMBER_OF_PINS)

	if request.method=="POST":
		if len(request.POST['selected_users'])>0:
			users_list = request.POST['selected_users'].split(',')
			users_qs = User.objects.filter(pk__in=users_list)
			for u in users_qs:
				follow(request.user, u)

		return redirect('create_initial_boards')
	return direct_to_template(request, "pins/welcome/step_2.html", locals())

@login_required
def create_initial_boards(request):
	default_boards = DefaultBoard.objects.filter(is_active=True)
	BoardFormset = formset_factory(OptionalBoardForm)
	initial = []
	for b in default_boards:
		initial.append({'name': b.name, 'category': b.category})
	formset = BoardFormset(data=request.POST or None, initial=initial)
	if formset.is_valid():
		for form in formset:
			if form.cleaned_data['name']:
				Board.objects.create(name=form.cleaned_data['name'], category=form.cleaned_data['category'], user=request.user)

		messages.success(request, _('You can now start pinning!'))
		return redirect("home")
	return direct_to_template(request, "pins/welcome/create_boards.html", locals())




