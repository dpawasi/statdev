from __future__ import unicode_literals
from datetime import timedelta
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from itertools import chain
import logging

from actions.models import Action
from .forms import EmailUserForm, AddressForm, OrganisationForm, DelegateAccessForm, UnlinkDelegateForm
from .models import EmailUser, Address, Organisation
from .utils import get_query


def log_task_result(task):
    """A function to act as a hook for logging any errors in async tasks.
    """
    logger = logging.getLogger('statdev')
    if not task.success:
        logger.error(task.result)


class UserProfile(LoginRequiredMixin, DetailView):
    model = EmailUser
    template_name = 'accounts/user_profile.html'

    def get_object(self, queryset=None):
        """Override get_object to always return the request user profile.
        """
        return self.request.user.emailuserprofile

    def get_context_data(self, **kwargs):
        context = super(UserProfile, self).get_context_data(**kwargs)
        context['organisations'] = Organisation.objects.filter(delegates__in=[self.get_object()])
        return context


class EmailUserUpdate(LoginRequiredMixin, UpdateView):
    form_class = EmailUserForm

    def get_object(self, queryset=None):
        return self.request.user.emailuserprofile

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):
            return HttpResponseRedirect(self.get_object().get_absolute_url())
        return super(EmailUserUpdate, self).post(request, *args, **kwargs)


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


class OrganisationList(LoginRequiredMixin, ListView):
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
            qs = qs.filter(query).distinct()
        return qs


class OrganisationCreate(LoginRequiredMixin, CreateView):
    """A view to create a new Organisation.
    """
    form_class = OrganisationForm
    template_name = 'accounts/organisation_form.html'

    def get_context_data(self, **kwargs):
        context = super(OrganisationCreate, self).get_context_data(**kwargs)
        context['action'] = 'Create'
        return context

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):
            return HttpResponseRedirect(self.get_success_url())
        return super(OrganisationCreate, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        self.obj = form.save()
        # Attach the creating user as a delegate to the new organisation.
        self.obj.delegates.add(self.request.user.emailuserprofile)
        return HttpResponseRedirect(self.obj.get_absolute_url())


class OrganisationDetail(LoginRequiredMixin, DetailView):
    model = Organisation

    def get_context_data(self, **kwargs):
        context = super(OrganisationDetail, self).get_context_data(**kwargs)
        org = self.get_object()
        context['user_is_delegate'] = self.request.user.emailuserprofile in org.delegates.all()
        return context


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


class RequestDelegateAccess(LoginRequiredMixin, FormView):
    """A view to allow a user to request to be added to an organisation as a delegate.
    This view sends an email to all current delegate, any of whom may confirm the request.
    """
    form_class = DelegateAccessForm
    template_name = 'accounts/request_delegate_access.html'

    def get_organisation(self):
        return Organisation.objects.get(pk=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        # Rule: redirect if the user is already a delegate.
        org = self.get_organisation()
        if request.user.emailuserprofile in org.delegates.all():
            messages.error(self.request, 'You are already a delegate for this organisation!')
            return HttpResponseRedirect(reverse('user_profile'))
        return super(RequestDelegateAccess, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(RequestDelegateAccess, self).get_context_data(**kwargs)
        context['organisation'] = self.get_organisation()
        return context

    def get_success_url(self):
        return reverse('user_profile')

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):
            return HttpResponseRedirect(self.get_success_url())
        # For each existing organisation delegate user, send an email that
        # contains a unique URL to confirm the request. The URL consists of the
        # requesting user PK (base 64-encoded) plus a unique token for that user.
        org = self.get_organisation()
        if not org.delegates.exists():
            # In the event that an organisation has no delegates, the request
            # will be sent to all users in the "Processor" group.
            processor = Group.objects.get(name='Processor')
            recipients = [i.email for i in EmailUser.objects.filter(groups__in=[processor])]
        else:
            recipients = [i.emailuser.email for i in org.delegates.all()]
        user = self.request.user
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        # Note that the token generator uses the requesting user object to generate a hash.
        # This means that if the user object changes (e.g. they log out and in again),
        # the hash will be invalid. Therefore, this request/response needs to occur
        # fairly promptly to work.
        token = default_token_generator.make_token(user)
        url = reverse('organisation_confirm_delegate_access', args=(org.pk, uid, token))
        url = request.build_absolute_uri(url)
        subject = 'Delegate access request for {}'.format(org.name)
        message = '''The following user has requested delegate access for {}: {}\n
        Click here to confirm and grant this access request:\n{}'''.format(org.name, user, url)
        html_message = '''<p>The following user has requested delegate access for {}: {}</p>
        <p><a href="{}">Click here</a> to confirm and grant this access request.</p>'''.format(org.name, user, url)
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipients, fail_silently=False, html_message=html_message)
        # Send a request email to the recipients asynchronously.
        # NOTE: the lines below should remain commented until (if) async tasking is implemented in prod.
        #from django_q.tasks import async
        #async(
        #    'django.core.mail.send_mail', subject, message,
        #    settings.DEFAULT_FROM_EMAIL, recipients, fail_silently=True, html_message=html_message,
        #    hook='log_task_result')
        #messages.success(self.request, 'An email requesting delegate access for {} has been sent to existing delegates.'.format(org.name))
        # Generate an action record:
        action = Action(content_object=org, user=user, action='Requested delegate access')
        action.save()
        return super(RequestDelegateAccess, self).post(request, *args, **kwargs)


class ConfirmDelegateAccess(LoginRequiredMixin, FormView):
    form_class = DelegateAccessForm
    template_name = 'accounts/confirm_delegate_access.html'

    def get_organisation(self):
        return Organisation.objects.get(pk=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        # Rule: request user must be a delegate (or superuser).
        org = self.get_organisation()
        if request.user.emailuserprofile in org.delegates.all() or request.user.is_superuser:
            uid = urlsafe_base64_decode(self.kwargs['uid'])
            user = EmailUser.objects.get(pk=uid)
            token = default_token_generator.check_token(user, self.kwargs['token'])
            if token:
                return super(ConfirmDelegateAccess, self).get(request, *args, **kwargs)
            else:
                messages.warning(self.request, 'The request delegate token is no longer valid.')
        else:
            messages.error(self.request, 'You are not authorised to confirm this request!')
        return HttpResponseRedirect(reverse('user_profile'))

    def get_context_data(self, **kwargs):
        context = super(ConfirmDelegateAccess, self).get_context_data(**kwargs)
        context['organisation'] = self.get_organisation()
        uid = urlsafe_base64_decode(self.kwargs['uid'])
        context['requester'] = EmailUser.objects.get(pk=uid)
        return context

    def get_success_url(self):
        return reverse('user_profile')

    def post(self, request, *args, **kwargs):
        uid = urlsafe_base64_decode(self.kwargs['uid'])
        user = EmailUser.objects.get(pk=uid)
        token = default_token_generator.check_token(user, self.kwargs['token'])
        # Change the user state to expire the token.
        user.last_login = user.last_login + timedelta(seconds=1)
        user.save()  # Prevent token re-use by changing user state.
        if request.POST.get('cancel'):
            return HttpResponseRedirect(self.get_success_url())
        if token:
            org = self.get_organisation()
            org.delegates.add(user.emailuserprofile)
            messages.success(self.request, '{} has been added as a delegate for {}.'.format(user, org.name))
        else:
            messages.warning(self.request, 'The request delegate token is no longer valid.')
        return HttpResponseRedirect(self.get_success_url())


class OrganisationUnlinkDelegate(LoginRequiredMixin, UpdateView):
    model = Organisation
    form_class = UnlinkDelegateForm
    template_name = 'accounts/confirm_unlink_delegate.html'

    def get(self, request, *args, **kwargs):
        # Rule: request user must be a delegate (or superuser).
        obj = self.get_object()
        if request.user.emailuserprofile not in obj.delegates.all() and not request.user.is_superuser:
            messages.error(self.request, 'You are not authorised to unlink a delegated user!')
            return HttpResponseRedirect(self.get_object().get_absolute_url())
        return super(OrganisationUnlinkDelegate, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(OrganisationUnlinkDelegate, self).get_context_data(**kwargs)
        context['delegate'] = EmailUser.objects.get(pk=self.kwargs['user_id'])
        return context

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):
            return HttpResponseRedirect(self.get_object().get_absolute_url())
        return super(OrganisationUnlinkDelegate, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        # Unlink the specified user from the organisation.
        org = self.get_object()
        user = EmailUser.objects.get(pk=self.kwargs['user_id'])
        org.delegates.remove(user.emailuserprofile)
        messages.success(self.request, '{} has been removed as a delegate for {}.'.format(user, org.name))
        # Generate an action record:
        action = Action(content_object=org, user=self.request.user,
            action='Unlinked delegate access for {}'.format(user.get_full_name()))
        action.save()
        return HttpResponseRedirect(self.get_success_url())
