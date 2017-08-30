from __future__ import unicode_literals
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from django.contrib import messages
from .models import EmailUser


class UserProfile(LoginRequiredMixin, DetailView):
    model = EmailUser
    template_name = 'accounts/user_profile.html'

    def get_object(self, queryset=None):
        """Override get_object to always return the request user.
        """
        return self.request.user

def done(request):
    return render(request, 'customers/done.html')

def bounce(request):
    if ('HTTP_REFERER' in request.META) and (request.META['HTTP_REFERER']):
        return redirect(request.META['HTTP_REFERER'])
    return redirect('/')

def validation_sent(request):
    messages.success(request,
                     "An email has been sent to you. "
                     "Check your mailbox and click on the link to complete the sign-in process.")
    return bounce(request)

def logout(request, *args, **kwargs):
    user = request.user
    auth_logout(request)
    if bool(request.GET.get('link_account')) and not user.profiles.all():
        user.delete()
    messages.success(request,
                     "You have successfully logged out.")
    if 'next' in request.GET:
        return redirect(request.GET['next'])
    return bounce(request)

# The user will get an email with a link pointing to this view, this view just
# redirects the user to PSA complete process for the email backend. The mail
# link could point directly to PSA view but it's handy to proxy it and do
# additional computation if needed.
def token_login(request, token, email):
    redirect_url = '{}?{}'.format(
        reverse('social:complete', args=('email',)),
        urlencode({'verification_code': token, 'email': email})
    )
    return redirect(redirect_url)
