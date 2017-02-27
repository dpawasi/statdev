from __future__ import unicode_literals
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, HTML
from crispy_forms.bootstrap import FormActions
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from .models import Application, Referral, Task


class BaseFormHelper(FormHelper):
    form_class = 'form-horizontal'
    label_class = 'col-xs-12 col-sm-4 col-md-3 col-lg-2'
    field_class = 'col-xs-12 col-sm-8 col-md-6 col-lg-4'
    help_text_inline = True


class ApplicationForm(ModelForm):

    class Meta:
        model = Application
        fields = ['app_type', 'title', 'description', 'submit_date']

    def __init__(self, *args, **kwargs):
        super(ApplicationForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper(self)
        self.helper.form_id = 'id_form_create_application'
        self.helper.form_action = 'application_create'  # Calls reverse().
        self.helper.add_input(Submit('save', 'Save', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel'))


class ApplicationLodgeForm(ModelForm):
    class Meta:
        model = Application
        fields = ['app_type', 'title', 'description', 'submit_date']

    def __init__(self, *args, **kwargs):
        super(ApplicationLodgeForm, self).__init__(*args, **kwargs)
        app = kwargs['instance']
        self.helper = BaseFormHelper(self)
        self.helper.form_id = 'id_form_lodge_application'
        self.helper.form_action = reverse('application_lodge', args=(app.pk,))
        # Disable all form fields.
        for k in self.fields.iterkeys():
            self.fields[k].disabled = True
        # Define the form layout.
        self.helper.layout = Layout(
            HTML('<p>Confirm that this application should be lodged for assessment:</p>'),
            'app_type', 'title', 'description', 'submit_date',
            FormActions(
                Submit('lodge', 'Lodge', css_class='btn-lg'),
                Submit('cancel', 'Cancel')
            )
        )


class ReferralForm(ModelForm):
    class Meta:
        model = Referral
        fields = ['referee', 'period', 'details', 'documents']

    def __init__(self, *args, **kwargs):
        super(ReferralForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper(self)
        # TODO: business logic to limit the referee queryset.
        # TODO: business logic to limit the document queryset.
        self.helper.form_id = 'id_form_refer_application'
        self.helper.add_input(Submit('save', 'Save', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel'))


class TaskReassignForm(ModelForm):

    class Meta:
        model = Task
        fields = ['assignee', ]

    def __init__(self, *args, **kwargs):
        super(TaskReassignForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper(self)
        self.helper.add_input(Submit('reassign', 'Reassign', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel'))
        self.fields['assignee'].required = True
        # TODO: business logic to limit the assignee queryset.
