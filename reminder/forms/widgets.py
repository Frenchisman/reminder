from django.forms.widgets import DateInput, TimeInput
from django.forms import MultiWidget
from django.utils.html import mark_safe
from json import JSONEncoder
from datetime import datetime


class DatePickerWidget(DateInput):

    dateattrs = {
        'mode':'flipbox',
        'useFocus':'true',
        'useModal': 'true'
    }

    def render(self, name, value, attrs=None):

        html = '<input type="text"'
        for attr in attrs:
            html += ' '+str(attr)+'="'+str(attrs[attr])+'"'
        html+= ' data-role="datebox" data-options=\''
        options = JSONEncoder().encode(self.dateattrs)
        html += options
        html+= "'>"
        return mark_safe(html)


class TimePickerWidget(TimeInput):

    timeattrs = {
        'mode':'timeflipbox',
        'useFocus':'true',
        'useModal':'true'
    }

    def render(self, name, value, attrs=None):
        html = '<input type="text"'
        for attr in attrs:
            html += ' '+str(attr)+'="'+str(attrs[attr])+'"'
        html+= ' data-role="datebox" data-options=\''
        options = JSONEncoder().encode(self.timeattrs)
        html += options
        html+= "'>"
        return mark_safe(html)

class DateTimePickerWidget(MultiWidget):

    def __init__(self, attrs=None):
        _widgets = (
                DatePickerWidget(),
                TimePickerWidget()
            )
        super(DateTimePickerWidget, self).__init__(_widgets, attrs)

    def decompress(self, value):
        if value:
            return ['20170113', '124300']
        return ['20170113', '124300']

    def format_output(self, rendered_widgets):
        return '\n'.join(rendered_widgets)

    def value_from_datadict(self, data, files, name):
        valuelist = [
            widget.value_from_datadict(data, files, name + '_%s' % i)
            for i, widget in enumerate(self.widgets)
        ]

        # try:
        #     dt = datetime()
        return '20170113124300'
