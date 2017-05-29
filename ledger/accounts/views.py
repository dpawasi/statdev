from __future__ import unicode_literals
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView

from .models import EmailUser


class UserProfile(LoginRequiredMixin, DetailView):
    model = EmailUser
    template_name = 'accounts/user_profile.html'

    def get_object(self, queryset=None):
        """Override get_object to always return the request user.
        """
        return self.request.user
