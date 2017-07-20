from __future__ import unicode_literals
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, HTML, Hidden
from crispy_forms.bootstrap import FormActions
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.forms import Form, ModelForm, ChoiceField, FileField, CharField, Textarea, ClearableFileInput, HiddenInput, Field
from applications.widgets import ClearableMultipleFileInput
from multiupload.fields import MultiFileField

from ledger.accounts.models import EmailUser, Address, Organisation
from .models import Approval

User = get_user_model()

class BaseFormHelper(FormHelper):
    form_class = 'form-horizontal'
    label_class = 'col-xs-12 col-sm-4 col-md-3 col-lg-2'
    field_class = 'col-xs-12 col-sm-8 col-md-6 col-lg-4'

class ApprovalChangeStatus(ModelForm):

    class Meta:
        model = Approval
        fields = ['status','expiry_date','start_date','cancellation_date','surrender_date','suspend_from_date','suspend_to_date','reinstate_date','details']
#       fields = ['status']

    def __init__(self, *args, **kwargs):
        
        # User must be passed in as a kwarg.
        super(ApprovalChangeStatus, self).__init__(*args, **kwargs)

        # print self.initial['status']
        status = Approval.APPROVAL_STATE_CHOICES[self.initial['status']]

        print "FORM"
#        self.fields['status'].initial =3
#        print self.fields['status'].initial
        print self.initial['status']

        if status == "Expired":
            del self.fields['start_date']
            del self.fields['cancellation_date']
            del self.fields['surrender_date']
            del self.fields['suspend_from_date']
            del self.fields['suspend_to_date']
            del self.fields['reinstate_date']
            self.fields['expiry_date'].required = True
        elif status == "Suspended": 
            del self.fields['start_date']
            del self.fields['cancellation_date']
            del self.fields['surrender_date']
        #   del self.fields['suspend_from_date']
            del self.fields['expiry_date']
            del self.fields['reinstate_date']
            self.fields['suspend_from_date'].required = True
            self.fields['suspend_to_date'].required = True
        elif status == "Reinstate":
            del self.fields['start_date']
            del self.fields['cancellation_date']
            del self.fields['surrender_date']
            del self.fields['suspend_from_date']
            del self.fields['expiry_date']
            del self.fields['suspend_to_date']
            self.fields['reinstate_date'].required = True
        elif status == "Surrendered":
            del self.fields['start_date']
            del self.fields['cancellation_date']
            del self.fields['reinstate_date']
            del self.fields['suspend_from_date']
            del self.fields['expiry_date']
            del self.fields['suspend_to_date']
            self.fields['surrender_date'].required = True
        elif status == "Cancelled":
            del self.fields['start_date']
            del self.fields['surrender_date']
            del self.fields['reinstate_date']
            del self.fields['suspend_from_date']
            del self.fields['expiry_date']
            del self.fields['suspend_to_date']
            self.fields['cancellation_date'].required = True

        self.helper = BaseFormHelper()
        self.helper.form_id = 'id_form_create_application'
        self.helper.attrs = {'novalidate': ''}
        self.fields['status'].widget.attrs['disabled'] = True
        self.fields['status'].required = False

        # Purpose of the extra field (hidden) is to ensure the status dropdown is 
        # populated on form field error.  So the dropdown doesn't come through blank
        self.helper.add_input(Hidden('status',self.initial['status']))
        ###
        self.helper.add_input(Submit('changestatus', 'Change Status', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel'))

        # Limit the organisation queryset unless the user is a superuser.


