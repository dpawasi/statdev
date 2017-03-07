from __future__ import unicode_literals
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from itertools import chain

from .forms import EmailUserProfileForm, AddressForm, OrganisationForm
from .models import EmailUserProfile, Address, Organisation
from .utils import get_query


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
        context['principal'] = self.request.user.email
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
        update_address = False
        # Rule: only the address owner can change an address.
        if profile.postal_address == address or profile.billing_address == address:
            update_address = True
        # Organisational addresses: find which org uses this address, and if
        # the user is a delegate for that org then they can change it.
        org_list = list(chain(address.org_postal_address.all(), address.org_billing_address.all()))
        for org in org_list:
            if profile in org.delegates.all():
                update_address = True
        if update_address:
            return super(AddressUpdate, self).get(request, *args, **kwargs)
        else:
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
        delete_address = False
        # Rule: only the address owner can delete an address.
        if profile.postal_address == address or profile.billing_address == address:
            delete_address = True
        # Organisational addresses: find which org uses this address, and if
        # the user is a delegate for that org then they can delete it.
        org_list = list(chain(address.org_postal_address.all(), address.org_billing_address.all()))
        for org in org_list:
            if profile in org.delegates.all():
                delete_address = True
        if delete_address:
            return super(AddressDelete, self).get(request, *args, **kwargs)
        else:
            messages.error(self.request, 'You cannot delete this address!')
            return HttpResponseRedirect(reverse('user_profile'))

    def get_success_url(self):
        return reverse('user_profile')

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):
            return HttpResponseRedirect(self.get_success_url())
        return super(AddressDelete, self).post(request, *args, **kwargs)


class OrganisationList(ListView):
    model = Organisation

    def get_queryset(self):
        qs = super(OrganisationList, self).get_queryset()
        # Did we pass in a search string? If so, filter the queryset and return it.
        if 'q' in self.request.GET and self.request.GET['q']:
            query_str = self.request.GET['q']
            # Replace single-quotes with double-quotes
            query_str = query_str.replace("'", r'"')
            # Filter by name and ABN fields.
            query = get_query(query_str, ['name', 'abn'])
        return qs.filter(query).distinct()


class OrganisationCreate(LoginRequiredMixin, CreateView):
    """A view to create a new Organisation.
    """
    form_class = OrganisationForm
    template_name = 'accounts/organisation_form.html'

    def get_context_data(self, **kwargs):
        context = super(OrganisationCreate, self).get_context_data(**kwargs)
        context['action'] = 'Create'
        return context

    def get_success_url(self):
        return reverse('user_profile')

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):
            return HttpResponseRedirect(self.get_success_url())
        return super(OrganisationCreate, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        self.obj = form.save()
        # Attach the creating user as a delegate to the new organisation.
        self.obj.delegates.add(self.request.user.emailuserprofile)
        return HttpResponseRedirect(self.get_success_url())


class OrganisationUpdate(LoginRequiredMixin, UpdateView):
    """A view to update an Organisation object.
    """
    model = Organisation
    form_class = OrganisationForm

    def get(self, request, *args, **kwargs):
        org = self.get_object()
        profile = self.request.user.emailuserprofile
        # Rule: only a delegated user (or a superuser) can update an organisation.
        if profile in org.delegates.all() or request.user.is_superuser:
            return super(OrganisationUpdate, self).get(request, *args, **kwargs)
        messages.error(self.request, 'You cannot update this organisation!')
        return HttpResponseRedirect(reverse('user_profile'))

    def get_context_data(self, **kwargs):
        context = super(OrganisationUpdate, self).get_context_data(**kwargs)
        context['action'] = 'Update'
        return context

    def get_success_url(self):
        return reverse('user_profile')

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):
            return HttpResponseRedirect(self.get_success_url())
        return super(OrganisationUpdate, self).post(request, *args, **kwargs)


class OrganisationAddressCreate(UserAddressCreate):
    """A view to create a new address for an Organisation (subclasses the UserAddressCreate view).
    """
    def get_context_data(self, **kwargs):
        context = super(OrganisationAddressCreate, self).get_context_data(**kwargs)
        org = Organisation.objects.get(pk=self.kwargs['pk'])
        context['principal'] = org.name
        return context

    def form_valid(self, form):
        self.obj = form.save()
        # Attach the new address to the organisation.
        org = Organisation.objects.get(pk=self.kwargs['pk'])
        if self.kwargs['type'] == 'postal':
            org.postal_address = self.obj
        elif self.kwargs['type'] == 'billing':
            org.billing_address = self.obj
        org.save()
        return HttpResponseRedirect(reverse('user_profile'))
