from __future__ import unicode_literals
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from mixer.backend.django import mixer

from accounts.utils import random_dpaw_email
from .models import Address

User = get_user_model()


class AccountTest(TestCase):

    def setUp(self):
        self.client = Client()
        # Set up an internal user.
        self.user1 = mixer.blend(User, email=random_dpaw_email, is_superuser=False, is_staff=True)
        self.user1.set_password('pass')
        self.user1.save()
        self.address1 = mixer.blend(Address)

    def test_address_save(self):
        self.assertTrue(self.address1.search_text)

    def test_address_summary(self):
        self.assertTrue(self.address1.summary)

    def test_address_active_fields(self):
        self.assertTrue(self.address1.line1 in self.address1.active_address_fields())
