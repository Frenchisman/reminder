from django.forms import ModelForm, Form
from reminder.models import Reminder
from django.forms.widgets import DateInput, TimeInput
from json import JSONEncoder
from django import forms

class ReminderForm(ModelForm):

    class Meta:
        model = Reminder

        dateattrs = {
            'mode':'flipbox',
            'useFocus':'true',
            'useModal': 'true'
        }

        timeattrs = {
        'mode':'timeflipbox',
        'useFocus':'true',
        'useModal':'true'
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
            "data-options":JSONEncoder().encode(dateattrs)
            }),
        'time_to_send': TimeInput(attrs={
            "data-role": "datebox",
            "data-options": JSONEncoder().encode(timeattrs)
            })
        }

