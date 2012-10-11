from django.conf import settings

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q


class AuthenticationBackend(ModelBackend):
    
    def authenticate(self, **credentials):
        if 'email' in credentials:
            lookup_params = {'email__iexact': credentials.get("email")}
        elif 'username' in credentials:
            lookup_params = {'username__iexact': credentials.get("username")}
        else:
            return None
        try:
            user = User.objects.get(**lookup_params)
        except User.DoesNotExist:
            return None
        else:
            if user.check_password(credentials["password"]):
                return user


EmailModelBackend = AuthenticationBackend