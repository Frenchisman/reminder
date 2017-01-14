from django import forms
from registration.forms import RegistrationFormUniqueEmail
from django.contrib.auth import password_validation
from django.contrib.auth.models import User


class UserRegistrationForm(RegistrationFormUniqueEmail):
    # Set username as an email field.
    username = forms.EmailField(
        label="Email address",
        required=True
    )
    email = forms.EmailField(
        label="Confirm your email",
        required=True,
        help_text='Enter your email address a second time, for confirmation.'
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput,
        label='Password',
        strip=False,
        help_text=password_validation.password_validators_help_text_html())

    class Meta(RegistrationFormUniqueEmail.Meta):
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'password1',
            'password2'
        ]

    def clean_email(self):
        '''
        Validate that the two email adresses are the same
        '''

        email1 = self.cleaned_data['username']
        email2 = self.cleaned_data['email']

        if email1 and email1 and email1 != email2:
            raise forms.ValidationError('Email adresses do not match.')

        return super(UserRegistrationForm, self).clean_email()


class ResendEmailActivationForm(forms.Form):
    email = forms.EmailField(required=True)


class ProfileEditForm(forms.Form):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)


class ProfileDeleteForm(forms.Form):
    check = forms.BooleanField(
        label='I understand the consequences of my actions.', required=True)
