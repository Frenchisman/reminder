from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from reminder.views.registration import (
    EmailRegistrationView, ResendActivationEmailView,
    ResentActivationEmailView)
from reminder.views.home import HomeView, LogoutView, ForbiddenView
from reminder.views.authenticated import (DashboardView, ReminderCreationView,
                                          ReminderDeleteView, ReminderEditView,
                                          ProfileDisplayView, ProfileEditView,
                                          ProfileDeleteView)
from django.contrib.auth import views as auth_views
from reminder.forms.login import LoginForm

urlpatterns = [
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^dashboard/$', DashboardView.as_view(), name='dashboard'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^profile/$', ProfileDisplayView.as_view(), name='profile'),
    url(r'^profile/edit/$', ProfileEditView.as_view(), name='profile_edit'),
    url(r'^profile/delete/$',
        ProfileDeleteView.as_view(),
        name='profile_delete'),
    url(r'^create/$', ReminderCreationView.as_view(), name='rem_create'),
    url(r'^delete/reminder/(?P<rem_id>[0-9]+)/$',
        ReminderDeleteView.as_view(), name='delete_reminder'),
    url(r'^edit/(?P<rem_id>[0-9]+)/$',
        ReminderEditView.as_view(), name='edit_reminder'),
    url(r'forbidden/$', ForbiddenView.as_view(), name='forbidden'),
    # edit
    url(r'^accounts/register/$',
        EmailRegistrationView.as_view(),
        name='registration_register'
        ),
    url(r'accounts/login/$', auth_views.login,
        {'template_name': 'registration/login.html',
         'authentication_form': LoginForm},
        name='auth_login',
        ),
    url(r'^accounts/activate/resend/$',
        ResendActivationEmailView.as_view(), name='registration_resend'),
    url(r'^accounts/activate/resent/$',
        ResentActivationEmailView.as_view(),
        name='registration_resent'),
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
