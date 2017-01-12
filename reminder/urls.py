from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from reminder.views.registration import EmailRegistrationView
# from reminder.backends.registration import Backend
from reminder.forms.account_forms import UserRegistrationForm
# from registration import views as registration_views
from reminder.views.home import HomeView, LogoutView
from reminder.views.authenticated import DashboardView
from django.views.generic import RedirectView


urlpatterns = [
    url(r'^$',HomeView.as_view(), name='home'),
    url(r'^dashboard/$', DashboardView.as_view(), name='dashboard'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^accounts/register/$', 
        EmailRegistrationView.as_view(),
        name='registration_register'
    ),
    url(r'^accounts/', include('registration.backends.hmac.urls')),
    # @TODO https://docs.djangoproject.com/fr/1.10/topics/auth/default/#all-authentication-views
    # Create Templates for these.
    # https://github.com/ubernostrum/django-registration/blob/master/registration/auth_urls.py
    # Urls needed .
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + static(settings.STATIC_URL, docuùment_root=settings.STATIC_ROOT)