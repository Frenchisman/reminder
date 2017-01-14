from django import forms
from registration.forms import RegistrationFormUniqueEmail
from django.contrib.auth.models import User

# class Email(forms.EmailField):
#     def clean(self, value):
#         super(Email, self).clean(value)
#         try:
#             User.objects.get(email=value)
#             raise forms.ValidationError("This Email is already resistered. If you have forgotten your password, please use the 'Forgotten password ?' link on the login page.")
#         except User.DoesNotExist:
#             return value


# class UserRegistrationForm(forms.Form):
#     email = Email()
#     first_name  = forms.CharField(widget = forms.TextInput, label ="First Name")
#     last_name = forms.CharField(widget=forms.TextInput, label="Last Name")
#     password1 = forms.CharField(widget=forms.PasswordInput(), label="Password")
#     password2 = forms.CharField(widget=forms.PasswordInput(), label="Confirm your Password")

#     #Email will become username


#     def clean_password(self):
#         password1 = self.cleaned_data.get("password1")
#         password2 = self.cleaned_data.get("password2")
#         if password1 and password2 and password1 != password2:
#             raise forms.ValidationError("Passwords do not match.")
#         return password2

class UserRegistrationForm(RegistrationFormUniqueEmail):
    #Set username as an email field.
    username = forms.EmailField(
        label="Email address",
        required=True
    )
    email = forms.EmailField(
        label="Confirm your email",
        required=True,
        help_text='Enter your email address a second time, for confirmation.'
    )

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
