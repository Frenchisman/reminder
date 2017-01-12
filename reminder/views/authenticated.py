from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import render

class DashboardView(LoginRequiredMixin, View):
    login_url = reverse_lazy('auth_login')
    template_name = 'reminder/dashboard.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
