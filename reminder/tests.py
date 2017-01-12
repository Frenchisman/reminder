from django.test import TestCase

# Create your tests here.
from django.contrib import auth
from .models import ReminderUser

class AuthTestCase(TestCase):
    def setUp(self):
        self.u = ReminderUser.objects.create_superuser('test@dom.com', 'test', 'testl', 'pass')

        self.u.save()

    def testLogin(self):
        self.client.login(username='test@dom.com', password='pass')