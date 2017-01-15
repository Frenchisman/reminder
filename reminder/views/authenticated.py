from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from django.views import View
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import render
from reminder.forms.reminder import ReminderForm
from reminder.forms.account_forms import ProfileEditForm, ProfileDeleteForm
from reminder.models import Reminder
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date


def dashboard():
    '''Return a redirect to dashboard'''
    return HttpResponseRedirect(reverse('dashboard'))


class DashboardView(LoginRequiredMixin, View):
    ''' Display the reminder Dashboard'''

    login_url = reverse_lazy('auth_login')
    template_name = 'reminder/dashboard.html'

    def get(self, request, *args, **kwargs):
        context = {}
        today = date.today()
        left_today = 5 - Reminder.objects.filter(day_to_send=today).count()
        current = Reminder.objects.filter(
            sender_id=request.user.id).filter(
            is_sent=0).order_by(
            'day_to_send', 'time_to_send')

        sent = Reminder.objects.filter(
            sender_id=request.user.id).filter(
            is_sent=1).order_by(
            '-day_to_send', '-time_to_send')[:5]

        context['current'] = current
        context['sent'] = sent
        context['left_today'] = left_today
        return render(request, self.template_name, context)


class ReminderCreationView(LoginRequiredMixin, View):
    '''Display the reminder creation form'''

    form_class = ReminderForm
    login_url = reverse_lazy('auth_login')
    template_name = 'reminder/reminder_creation.html'

    def get(self, request, *args, **kwargs):
        context = {
            'form': self.form_class()
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            # Check if user an create a reminder for the specified date
            if (Reminder.objects.filter(
                day_to_send=form.cleaned_data['day_to_send']
            ).count() < 5):

                r = Reminder(
                    sender=request.user,
                    sender_email=request.user.email,
                    recipient_email=form.cleaned_data['recipient_email'],
                    subject=form.cleaned_data['subject'],
                    body=form.cleaned_data['body'],
                    day_to_send=form.cleaned_data['day_to_send'],
                    time_to_send=form.cleaned_data['time_to_send']
                )
                r.save()
                messages.add_message(request, messages.SUCCESS,
                                     'Reminder Created.')
                return dashboard()
            else:
                # If all reminders are used, we need to notify the user.
                form.add_error(
                    'day_to_send',
                    "You have already used all your reminders for " +
                    form.cleaned_data['day_to_send'].strftime('%B %d, %Y'))

        return render(request, self.template_name, {'form': form})


class ReminderEditView(LoginRequiredMixin, View):
    '''Display the reminder edit form'''
    form_class = ReminderForm
    login_url = reverse_lazy('auth_login')
    template_name = 'reminder/reminder_edition.html'

    def get(self, request, *args, **kwargs):
        '''Get request for reminder edit form.'''
        # Get id from url
        rem_id = kwargs['rem_id']
        try:
            reminder = Reminder.objects.get(id=rem_id)
        except Reminder.DoesNotExist:
            reminder = None

        # Warn user if reminder does not exist anymore.
        if reminder is None:
            messages.add_message(request, messages.INFO,
                                 'This reminder does not exist anymore.')
            return dashboard()

        # Redirect user if trying to edit someone else's reminder.
        if reminder.sender_id != request.user.id:
            return HttpResponseRedirect(reverse('forbidden'))

        if reminder.is_sent:
            messages.add_message(
                request,
                messages.INFO,
                'This reminder has already been sent. It can not be edited.')
            return dashboard()

        form = self.form_class(initial={
            'recipient_email': reminder.recipient_email,
            'subject': reminder.subject,
            'day_to_send': reminder.day_to_send,
            'time_to_send': reminder.time_to_send,
            'body': reminder.body
        })

        context = {'form': form}

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        '''Post request for reminder edit form.'''
        # Get id from url
        rem_id = kwargs['rem_id']
        try:
            reminder = Reminder.objects.get(id=rem_id)
        except Reminder.DoesNotExist:
            reminder = None

        # Warn user if reminder does not exist anymore.
        if reminder is None:
            messages.add_message(request, messages.INFO,
                                 'This reminder does not exist anymore.')
            return dashboard()

        # Redirect user if trying to edit someone else's reminder.
        if reminder.sender_id != request.user.id:
            return HttpResponseRedirect(reverse('forbidden'))

        if reminder.is_sent:
            messages.add_message(
                request,
                messages.INFO,
                'This reminder has already been sent. It can not be edited.')
            return dashboard()

        form = self.form_class(request.POST)

        # If infos have changed, update the reminder object
        if form.is_valid():
            if form.has_changed():
                # We need to recheck the date
                # When editing a reminder with the same date it's ok !
                is_same_day = (reminder.day_to_send ==
                               form.cleaned_data['day_to_send'])
                if (Reminder.objects.filter(
                    day_to_send=form.cleaned_data['day_to_send']
                ).count() < 5 or is_same_day):

                    reminder.recipient_email = form.cleaned_data[
                        'recipient_email']
                    reminder.subject = form.cleaned_data['subject']
                    reminder.body = form.cleaned_data['body']
                    reminder.day_to_send = form.cleaned_data['day_to_send']
                    reminder.time_to_send = form.cleaned_data['time_to_send']
                    reminder.save()
                    messages.add_message(request, messages.SUCCESS,
                                         'Reminder edited.')
                    return dashboard()
                else:
                    # If all reminders are used, we need to notify the user.
                    form.add_error(
                        'day_to_send',
                        "You have already used all your reminders for " +
                        form.cleaned_data['day_to_send'].strftime('%B %d, %Y'))
            else:
                # If form has not changed, do nothing
                # notify the user all is ok
                messages.add_message(request, messages.SUCCESS,
                                     'Reminder edited.')
                return dashboard()
        # If we have errors, resend the form
        context = {'form': form}
        return render(request, self.template_name, context)


class ReminderDeleteView(LoginRequiredMixin, View):
    ''' Display the reminder infos and ask for confirmation.'''
    login_url = reverse_lazy('auth_login')

    def get(self, request, *args, **kwargs):

        # Get id from url
        rem_id = kwargs['rem_id']
        try:
            reminder = Reminder.objects.get(id=rem_id)
        except Reminder.DoesNotExist:
            reminder = None

        # Warn user if reminder does not exist anymore.
        if reminder is None:
            messages.add_message(request, messages.INFO,
                                 'This reminder does not exist anymore.')
            return dashboard()

        # Redirect user if trying to delete someone else's reminder.
        if reminder.sender_id != request.user.id:
            return HttpResponseRedirect(reverse('forbidden'))

        if reminder.is_sent:
            messages.add_message(
                request, messages.INFO, 'This reminder has already been sent. It can not be deleted.')
            return dashboard()

        # No problems, we delete the reminder and notify the user.
            reminder.delete()
            messages.add_message(request, messages.SUCCESS,
                                 'Reminder Deleted.')
        return dashboard()


class ProfileDisplayView(LoginRequiredMixin, View):
    login_url = reverse_lazy('auth_login')
    template_name = "reminder/profile.html"

    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        context = {
            'username': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }
        return render(request, self.template_name, context)


class ProfileEditView(LoginRequiredMixin, View):
    ''' Display the view for profile edition'''
    login_url = reverse_lazy('auth_login')
    template_name = "reminder/profile_edit.html"
    form_class = ProfileEditForm

    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)

        form = self.form_class(
            initial={
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        )

        context = {'form': form}

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        ''' Update user object if form has valid values'''
        user = User.objects.get(id=request.user.id)
        form = self.form_class(request.POST)

        if form.is_valid():
            # Update user whan form is valid.
            user.username = form.cleaned_data['email']
            user.email = form.cleaned_data['email']
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            messages.add_message(request, messages.INFO,
                                 'Profile Information Updated.')
            return HttpResponseRedirect(reverse('profile'))

        # When form is not valid return it for completion
        context = {'form': form}
        return render(request, self.template_name, context)


class ProfileDeleteView(LoginRequiredMixin, View):
    template_name = 'reminder/profile_delete.html'
    login_url = reverse_lazy('auth_login')
    form_class = ProfileDeleteForm

    def get(self, request, *args, **kwargs):
        messages.add_message(request, messages.WARNING,
                             'This action can not be undone, are you sure ?')
        form = self.form_class()
        context = {'form': form}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        form = self.form_class(request.POST)

        # Check if user has checked the checkbox.
        if form.is_valid():
            if form.cleaned_data['check']:
                logout(request)
                user.delete()
                messages.add_message(
                    request, messages.SUCCESS, 'Account Deleted.')
            return HttpResponseRedirect(reverse('home'))

            context = {'form': form}
        return render(request, self.template_name, context)
