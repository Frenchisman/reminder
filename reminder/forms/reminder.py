from django.forms import ModelForm, Form
from reminder.models import Reminder
from django.forms.widgets import DateInput, TimeInput
from json import JSONEncoder
from django import forms
import datetime


class ReminderForm(ModelForm):

    class Meta:
        model = Reminder

        dateattrs = {
            'mode': 'flipbox',
            'useFocus': 'true',
            'useModal': 'true',
            'afterToday': 'true',
            'maxDays': 365
        }

        timeattrs = {
            'mode': 'timeflipbox',
            'useFocus': 'true',
            'useModal': 'true',
            'minuteStep': 5
        }

        fields = [
            'recipient_email',
            'subject',
            'day_to_send',
            'time_to_send',
            'body'
        ]

        widgets = {
            'day_to_send': DateInput(attrs={
                "data-role": "datebox",
                "data-options": JSONEncoder().encode(dateattrs)
            }),
            'time_to_send': TimeInput(attrs={
                "data-role": "datebox",
                "data-options": JSONEncoder().encode(timeattrs)
            })
        }

    def clean_day_to_send(self):
        data = self.cleaned_data['day_to_send']
        if data < datetime.date.today():
            raise forms.ValidationError("The date must be today or later.")
        return data

    def clean(self):
        cleaned_data = super(ReminderForm, self).clean()

        day = cleaned_data.get('day_to_send')
        ti = cleaned_data.get('time_to_send')

        if day == datetime.date.today() and ti < datetime.datetime.now().time():
            raise forms.ValidationError('The time must be after now.')
