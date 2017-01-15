from django.db import models
from django.contrib.auth.models import User


class Reminder(models.Model):
    sender = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=False, null=True)
    sender_email = models.EmailField()
    recipient_email = models.EmailField("recipient's email")
    # max_length of subject according to RFC 2822
    subject = models.CharField(
        'reminder subject', max_length=78, blank=False, null=False)
    # Slightly arbitrary max_length
    body = models.TextField(
        'reminder text', max_length=2674, blank=True, null=True)
    day_to_send = models.DateField(blank=False, null=False)
    time_to_send = models.TimeField(blank=False, null=False)
    is_sent = models.BooleanField(default=False)


class Question(models.Model):
    question = models.CharField(max_length=300)
    answer = models.TextField(max_length=1000)
    order = models.IntegerField(null=False)

    ordering = ['order']
