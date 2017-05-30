from django.http import HttpResponse
from django.template import Context
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage
from django.conf import settings
from django.core.exceptions import ValidationError
from ledger.accounts.models import EmailUser
from applications.models import Referral
from confy import env

"""
Email Delivery will only work when EMAIL_DELIVERY is switched on.  To accidently stop invalid emails going out to end users.
If your local developement area doesn't have a email catch all setup you can use the override flag 'OVERRIDE_EMAIL' to send all email generated to a specfic address.

To enable the variable please add them to your .env

eg.

EMAIL_DELIVERY=on
OVERRIDE_EMAIL=jason.moore@dpaw.wa.gov.au

"""


def sendHtmlEmail(to,subject,context,template,cc,bcc,from_email):

    email_delivery = env('EMAIL_DELIVERY', 'off')
    override_email = env('OVERRIDE_EMAIL', None)
    context['default_url'] = env('DEFAULT_URL', '')

    if email_delivery != 'on':
        print ("EMAIL DELIVERY IS OFF NO EMAIL SENT -- applications/email.py ")
        return False

    if template is None:
        raise ValidationError('Invalid Template')
    if to is None:
        raise ValidationError('Invalid Email')
    if subject is None:
        raise ValidationError('Invalid Subject')

    if from_email is None:
        if settings.DEFAULT_FROM_EMAIL:
            from_email = settings.DEFAULT_FROM_EMAIL
        else:
            from_email = 'jason.moore@dpaw.wa.gov.au'

    context['version'] = settings.APPLICATION_VERSION_NO
    # Custom Email Body Template
    context['body'] = get_template(template).render(Context(context))
    # Main Email Template Style ( body template is populated in the center
    main_template = get_template('email-dpaw-template.html').render(Context(context))

    if override_email is not None:
        to = [override_email]
        if cc:
            cc = [override_email]
        if bcc:
            bcc = [override_email]

    msg = EmailMessage(subject, main_template, to=to,cc=cc, from_email=from_email)
    msg.content_subtype = 'html'
    msg.send()
    return True

def emailGroup(subject,context,template,cc,bcc,from_email,group):

    UsersInGroup = EmailUser.objects.filter(groups__name=group)
    for person in UsersInGroup:
        context['person'] = person
        sendHtmlEmail([person.email],subject,context,template,cc,bcc,from_email)


def emailApplicationReferrals(application_id,subject,context,template,cc,bcc,from_email):

    context['default_url'] = env('DEFAULT_URL', '')
    ApplicationReferrals = Referral.objects.filter(application=application_id)
    for Referee in ApplicationReferrals:
        context['person'] = Referee.referee
        context['application_id'] = application_id
        sendHtmlEmail([Referee.referee.email],subject,context,template,cc,bcc,from_email)


