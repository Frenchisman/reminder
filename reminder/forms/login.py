from django.contrib.auth.forms import AuthenticationForm
from django import forms


class LoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email address')
    password = forms.CharField(widget=forms.PasswordInput(), label="Password")
