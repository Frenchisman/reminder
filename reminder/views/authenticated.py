from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import render
from reminder.forms.reminder import ReminderForm
from reminder.models import Reminder
from django.http import HttpResponseRedirect
from django.urls import reverse

def dashboard():
    '''Return a redirect to dashboard'''
    return HttpResponseRedirect(reverse('dashboard'))

class DashboardView(LoginRequiredMixin, View):
    ''' Display the reminder Dashboard'''

    login_url = reverse_lazy('auth_login')
    template_name = 'reminder/dashboard.html'

    def get(self, request, *args, **kwargs):
        context = {}
        reminder_list = Reminder.objects.filter(sender_id=request.user.id)
        context['reminder_list'] = reminder_list
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
            messages.add_message(request, messages.INFO, 'Reminder Created Successfully.')
            return dashboard()

        return render(request, self.template_name, {'form':form})


class ReminderEditView(LoginRequiredMixin, View):
    '''Display the reminder edit form'''
    form_class = ReminderForm
    login_url = reverse_lazy('auth_login')
    template_name = 'reminder/reminder_edition.html'


    def get(self, request, *args, **kwargs):
        '''Get request for reminder edit form.'''
        #Get id from url
        rem_id = kwargs['rem_id']
        try:
            reminder = Reminder.objects.get(id=rem_id)
        except Reminder.DoesNotExist:
            reminder = None

        # Warn user if reminder does not exist anymore.
        if reminder is None:
            messages.add_message(request, messages.INFO,'This reminder does not exist anymore.')
            return dashboard()

        #Redirect user if trying to edit someone else's reminder.
        if reminder.sender_id != request.user.id:
            return HttpResponseRedirect(reverse('forbidden'))

        if reminder.is_sent:
            messages.add_message(request, messages.INFO, 'This reminder has already been sent. It can not be edited.')
            return dashboard()

        form = self.form_class(initial={
                'recipient_email':reminder.recipient_email,
                'subject':reminder.subject,
                'day_to_send':reminder.day_to_send,
                'time_to_send':reminder.time_to_send,
                'body':reminder.body
            })

        context = { 'form' : form }

        return render(request, self.template_name, context)


    def post(self, request, *args, **kwargs):
        '''Post request for reminder edit form.'''
        #Get id from url
        rem_id = kwargs['rem_id']
        try:
            reminder = Reminder.objects.get(id=rem_id)
        except Reminder.DoesNotExist:
            reminder = None

        # Warn user if reminder does not exist anymore.
        if reminder is None:
            messages.add_message(request, messages.INFO,'This reminder does not exist anymore.')
            return dashboard()

        #Redirect user if trying to edit someone else's reminder.
        if reminder.sender_id != request.user.id:
            return HttpResponseRedirect(reverse('forbidden'))

        if reminder.is_sent:
            messages.add_message(request, messages.INFO, 'This reminder has already been sent. It can not be edited.')
            return dashboard()

        form = self.form_class(request.POST)

        if form.is_valid():
            if form.has_changed():
                reminder.recipient_email=form.cleaned_data['recipient_email']
                reminder.subject=form.cleaned_data['subject']
                reminder.body=form.cleaned_data['body']
                reminder.day_to_send=form.cleaned_data['day_to_send']
                reminder.time_to_send=form.cleaned_data['time_to_send']
            reminder.save()
            messages.add_message(request, messages.INFO, 'Reminder edited successfully.')
            return dashboard()
        context = { 'form' : form }
        return render(request, self.template_name, context)


# reminder.update(recipient_email=form.cleaned_data['recipient_email'], subject=form.cleaned_data['subject'], body=form.cleaned_data['body'], day_to_send=form.cleaned_data['day_to_send'], time_to_send=form.cleaned_data['time_to_send'])


class ReminderDeleteView(LoginRequiredMixin, View):
    ''' Display the reminder infos and ask for confirmation.'''
    login_url = reverse_lazy('auth_login')

    def get(self, request, *args, **kwargs):

        #Get id from url
        rem_id = kwargs['rem_id']
        try:
            reminder = Reminder.objects.get(id=rem_id)
        except Reminder.DoesNotExist:
            reminder = None

        # Warn user if reminder does not exist anymore.
        if reminder is None:
            messages.add_message(request, messages.INFO,'This reminder does not exist anymore.')
            return dashboard()

        #Redirect user if trying to delete someone else's reminder.
        if reminder.sender_id != request.user.id:
            return HttpResponseRedirect(reverse('forbidden'))

        if reminder.is_sent:
            messages.add_message(request, messages.INFO, 'This reminder has already been sent. It can not be deleted.')
            return dashboard()

        #No problems, we delete the reminder and notify the user.
            reminder.delete()
            messages.add_message(request, messages.INFO,'Reminder Deleted '+str(kwargs['rem_id']))
        return dashboard()
