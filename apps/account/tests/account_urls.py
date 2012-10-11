from django.conf.urls.defaults import *


urlpatterns = patterns("",
    url(r"^account/", include("account.urls")),
    url(r"^$", "account.views.login", name="home") #need a home to correctly render the template..
)
