from reminder.forms.account_forms import UserRegistrationForm

from registration.backends.hmac.views import RegistrationView
from registration.forms import RegistrationForm

from registration import signals

# @IMPORTANT Comment dat shit
class EmailRegistrationView(RegistrationView):

    form_class = UserRegistrationForm

    def register(self, form):
        data = {
            'username' : form.fields['email'],
            'email' : form.fields['email'],
            'first_name'
            'password1' : form.fields['password1'],
            'password2' : form.fields['password2']
        }

        new_form = RegistrationForm(data)
        new_user = self.create_inactive_user(form)

        signals.user_registered.send(
            sender=self.__class__,
            user=new_user,
            request=self.request
        )
        return new_user