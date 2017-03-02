from __future__ import unicode_literals
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.views.generic import DetailView, UpdateView

from .forms import EmailUserProfileForm
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
    form_class = EmailUserProfileForm

    def get_object(self, queryset=None):
        return self.request.user.emailuserprofile

    def get_initial(self):
        initial = super(UserProfileUpdate, self).get_initial()
        user = self.get_object().emailuser
        initial['first_name'] = user.first_name
        initial['last_name'] = user.last_name
        return initial

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):
            return HttpResponseRedirect(self.get_object().get_absolute_url())
        return super(UserProfileUpdate, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        """Override to set first_name and last_name on the EmailUser object.
        """
        self.obj = form.save()
        user = self.obj.emailuser
        data = form.cleaned_data
        name_changed = False
        if 'first_name' in data and data['first_name']:
            user.first_name = data['first_name']
            name_changed = True
        if 'last_name' in data and data['last_name']:
            user.last_name = data['last_name']
            name_changed = True
        if name_changed:
            user.save()
        return HttpResponseRedirect(self.get_success_url())
