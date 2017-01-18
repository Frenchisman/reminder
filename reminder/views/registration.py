from reminder.forms.account_forms import (
    UserRegistrationForm, ResendEmailActivationForm)
from django.conf import settings
from django.views import View
from django.core import signing
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from registration.backends.hmac.views import RegistrationView
from registration.forms import RegistrationForm

from registration import signals

# @IMPORTANT Comment dat shit


class EmailRegistrationView(RegistrationView):

    form_class = UserRegistrationForm

    def register(self, form):
        data = {
            'username': form.fields['email'],
            'email': form.fields['email'],
            'first_name'
            'password1': form.fields['password1'],
            'password2': form.fields['password2']
        }

        new_form = RegistrationForm(data)
        new_user = self.create_inactive_user(form)

        signals.user_registered.send(
            sender=self.__class__,
            user=new_user,
            request=self.request
        )
        return new_user


class ResendActivationEmailView(View):
    ''' logic for the ResendActivationEmail page '''

    email_body_template = 'registration/activation_email.txt'
    email_subject_template = 'registration/activation_email_subject.txt'
    form_class = ResendEmailActivationForm
    template_name = 'registration/resend_activation_email.html'

    def get(self, request, *args, **kwargs):
        ''' GET logic'''
        if not request.user.is_anonymous:
            messages.add_message(request, messages.INFO,
                                 'Your account is already active')
            return HttpResponseRedirect(reverse('dashboard'))

        # When user is not logged in, create the form
        context = {}
        form = self.form_class()
        context.update({'form': form})
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        ''' POST logic '''
        form = self.form_class(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
            # Get the user from the email adress if inactive.
            users = User.objects.filter(email=email, is_active=0)

            if not users.count():
                form._errors['email'] = [
                    """This email address is not registered,\
                     or already activated"""
                ]

            REGISTRATION_SALT = getattr(
                settings, 'REGISTRATION_SALT', 'registration')

            for user in users:
                # dumps returns a value with the format
                # <component1>:<component2>
                # where component1 is a base64 encoded representation
                # of argument 1 and component 2 is a base64 encoded hmac-sha1 
                # hash of arg1+arg2, signed using the timestamp
                activation_key = signing.dumps(
                    obj=getattr(user, user.USERNAME_FIELD),
                    salt=REGISTRATION_SALT,
                )

                # Load data for the email template.
                context = {}
                context['activation_key'] = activation_key
                context['expiration_days'] = settings.ACCOUNT_ACTIVATION_DAYS
                context['site'] = get_current_site(request)
                context['user'] = user.email

                subject = render_to_string(
                    self.email_subject_template, context)
                # Subject must be 1 line to avoid header injection issues
                subject = ''.join(subject.splitlines())
                message = render_to_string(self.email_body_template, context)

                # Send the email to the user.
                user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)
                return HttpResponseRedirect(reverse('registration_resent'))

        # when form does not have valid input, resend the form.
        context = {'form': form}
        return render(request, self.template_name, context)


class ResentActivationEmailView(View):

    template_name = 'registration/resend_activation_email_done.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_anonymous:
            messages.add_message(request, messages.INFO,
                                 'Your account is already active')
            return HttpResponseRedirect(reverse('dashboard'))

        return render(request, self.template_name)
