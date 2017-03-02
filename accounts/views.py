from __future__ import unicode_literals
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView

from .forms import EmailUserProfileForm, AddressForm
from .models import EmailUserProfile, Address, Organisation


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


class UserAddressCreate(LoginRequiredMixin, CreateView):
    """A view to create a new address for a User.
    """
    form_class = AddressForm
    template_name = 'accounts/address_form.html'

    def dispatch(self, request, *args, **kwargs):
        # Rule: the ``type`` kwarg must be 'postal' or 'billing'
        if self.kwargs['type'] not in ['postal', 'billing']:
            messages.error(self.request, 'Invalid address type!')
            return HttpResponseRedirect(reverse('user_profile'))
        return super(UserAddressCreate, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UserAddressCreate, self).get_context_data(**kwargs)
        context['address_type'] = self.kwargs['type']
        context['action'] = 'Create'
        return context

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):
            return HttpResponseRedirect(reverse('user_profile'))
        return super(UserAddressCreate, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        self.obj = form.save()
        # Attach the new address to the user's profile.
        profile = self.request.user.emailuserprofile
        if self.kwargs['type'] == 'postal':
            profile.postal_address = self.obj
        elif self.kwargs['type'] == 'billing':
            profile.billing_address = self.obj
        profile.save()
        return HttpResponseRedirect(reverse('user_profile'))


class AddressUpdate(LoginRequiredMixin, UpdateView):
    model = Address
    form_class = AddressForm

    def get(self, request, *args, **kwargs):
        address = self.get_object()
        profile = self.request.user.emailuserprofile
        # Rule: only the address owner can change an address.
        # TODO: Organisational addresses.
        if profile.postal_address == address or profile.billing_address == address:
            return super(AddressUpdate, self).get(request, *args, **kwargs)
        messages.error(self.request, 'You cannot update this address!')
        return HttpResponseRedirect(reverse('user_profile'))

    def get_context_data(self, **kwargs):
        context = super(AddressUpdate, self).get_context_data(**kwargs)
        context['action'] = 'Update'
        return context

    def get_success_url(self):
        return reverse('user_profile')

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):
            return HttpResponseRedirect(self.get_success_url())
        return super(AddressUpdate, self).post(request, *args, **kwargs)


class AddressDelete(LoginRequiredMixin, DeleteView):
    model = Address

    def get(self, request, *args, **kwargs):
        address = self.get_object()
        profile = self.request.user.emailuserprofile
        # Rule: only the address owner can delete an address.
        if profile.postal_address == address or profile.billing_address == address:
            return super(AddressDelete, self).get(request, *args, **kwargs)
        messages.error(self.request, 'You cannot delete this address!')
        return HttpResponseRedirect(reverse('user_profile'))

    def get_success_url(self):
        return reverse('user_profile')

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):
            return HttpResponseRedirect(self.get_success_url())
        return super(AddressDelete, self).post(request, *args, **kwargs)
