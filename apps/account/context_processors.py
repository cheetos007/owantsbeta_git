from django.conf import settings

from account.models import Account, AnonymousAccount

from account.forms import LoginForm

def account(request):
    data = {}
    if request.user.is_authenticated():
        try:
            account = Account.objects.get_for_user(request.user)
        except Account.DoesNotExist:
            account = AnonymousAccount(request)
    else:
        account = AnonymousAccount(request)
        data['login_form'] = LoginForm()
    data.update({
        "account": account,
        "CONTACT_EMAIL": getattr(settings, "CONTACT_EMAIL", "support@example.com")
    })

    return data
