from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, UpdateView

from .models import EmailUserProfile, Organisation


class UserProfile(LoginRequiredMixin, DetailView):
    model = EmailUserProfile
    template_name = 'accounts/user_profile.html'

    def get_object(self, queryset=None):
        """Override get_object to always return the request user profile.
        """
        return self.request.user.emailuserprofile

    def get_context_data(self, **kwargs):
        context = super(UserProfile, self).get_context_data(**kwargs)
        context['organisations'] = Organisation.objects.filter(delegates__in=[self.get_object()])
        return context


class UserProfileUpdate(LoginRequiredMixin, UpdateView):
    model = EmailUserProfile
    fields = ['dob', 'home_phone', 'work_phone', 'mobile', 'identification']

    def get_object(self, queryset=None):
        return self.request.user.emailuserprofile
