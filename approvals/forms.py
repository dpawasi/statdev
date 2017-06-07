from __future__ import unicode_literals
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, HTML
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
        fields = ['status']

    def __init__(self, *args, **kwargs):

        # User must be passed in as a kwarg.
        super(ApprovalChangeStatus, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper()
        self.helper.form_id = 'id_form_create_application'
        self.helper.attrs = {'novalidate': ''}
        self.fields['status'].widget.attrs['disabled'] = True
        self.fields['status'].required = False
        self.helper.add_input(Submit('changestatus', 'Change Status', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel'))
        # Limit the organisation queryset unless the user is a superuser.



