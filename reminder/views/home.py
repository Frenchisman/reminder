from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages

from reminder.forms.login import LoginForm


class HomeView(View):

    template_name = 'reminder/home.html'
    form_class = LoginForm

    def get(self, request, *args, **kwargs):
        context = {}

        if not request.user.is_authenticated:
            form = self.form_class(initial={'username': '', 'password': ''})
            context = {
                'form': form
            }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # Get post infos
        form = self.form_class(request, request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # After login, redirect to dashboard.
                return HttpResponseRedirect(reverse('dashboard'))

        # Form not valid.
        return render(request, self.template_name, {'form': form})


class LogoutView(View):

    def get(self, request):
        connected = False
        if not request.user.is_anonymous:
            connected = True
        logout(request)
        if connected:
            messages.add_message(request, messages.INFO,
                                 "Successfully Logged Off.")
        return HttpResponseRedirect(reverse('home'))


class ForbiddenView(View):

    template_name = 'reminder/forbidden.html'

    def get(self, request):
        messages.add_message(
            request,
            messages.ERROR,
            'You do not have access to this page.')
        return render(request, self.template_name)


class Error404View(View):
    template_name = 'reminder/404.html'

    def get(self, request):
        messages.add_message(
            request,
            messages.ERROR,
            'Error 404 : Page not found')
        return render(request, self.template_name)
