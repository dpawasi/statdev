from __future__ import unicode_literals
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, HTML
from crispy_forms.bootstrap import FormActions
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.forms import ModelForm, ChoiceField

from .models import Application, Referral, Condition


User = get_user_model()


class BaseFormHelper(FormHelper):
    form_class = 'form-horizontal'
    label_class = 'col-xs-12 col-sm-4 col-md-3 col-lg-2'
    field_class = 'col-xs-12 col-sm-8 col-md-6 col-lg-4'


class ApplicationForm(ModelForm):

    class Meta:
        model = Application
        fields = ['app_type', 'title', 'description']

    def __init__(self, *args, **kwargs):
        super(ApplicationForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper()
        self.helper.form_id = 'id_form_create_application'
        self.helper.attrs = {'novalidate': ''}
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
        for k, v in self.fields.items():
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
        self.helper.form_id = 'id_form_referral_create'
        self.helper.attrs = {'novalidate': ''}
        # Limit the referee queryset.
        referee = Group.objects.get_or_create(name='Referee')[0]
        self.fields['referee'].queryset = User.objects.filter(groups__in=[referee])
        # TODO: business logic to limit the document queryset.
        self.helper.form_id = 'id_form_refer_application'
        self.helper.add_input(Submit('save', 'Save', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel'))


class ReferralCompleteForm(ModelForm):
    class Meta:
        model = Referral
        fields = ['feedback']

    def __init__(self, *args, **kwargs):
        super(ReferralCompleteForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper(self)
        self.helper.form_id = 'id_form_referral_complete'
        self.helper.add_input(Submit('complete', 'Complete', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel'))


class ConditionCreateForm(ModelForm):
    class Meta:
        model = Condition
        fields = ['condition', ]

    def __init__(self, *args, **kwargs):
        super(ConditionCreateForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper(self)
        self.helper.attrs = {'novalidate': ''}
        self.fields['condition'].required = True
        self.helper.add_input(Submit('save', 'Save', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel'))


class ApplicationAssignForm(ModelForm):
    class Meta:
        model = Application
        fields = ['app_type', 'title', 'description', 'submit_date', 'assignee']

    def __init__(self, *args, **kwargs):
        super(ApplicationAssignForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper(self)
        self.helper.form_id = 'id_form_assign_application'
        self.helper.attrs = {'novalidate': ''}
        # Limit the assignee queryset.
        assessor = Group.objects.get_or_create(name='Assessor')[0]
        self.fields['assignee'].queryset = User.objects.filter(groups__in=[assessor])
        self.fields['assignee'].required = True
        # Disable all form fields.
        for k, v in self.fields.items():
            self.fields[k].disabled = True
        # Re-enable the assignee field.
        self.fields['assignee'].disabled = False
        # Define the form layout.
        self.helper.layout = Layout(
            HTML('<p>Assign this application for assessment:</p>'),
            'app_type', 'title', 'description', 'submit_date', 'assignee',
            FormActions(
                Submit('assign', 'Assign', css_class='btn-lg'),
                Submit('cancel', 'Cancel')
            )
        )


class ApplicationApproveForm(ModelForm):
    class Meta:
        model = Application
        fields = ['app_type', 'title', 'description', 'submit_date', 'assignee']

    def __init__(self, *args, **kwargs):
        super(ApplicationApproveForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper(self)
        self.helper.form_id = 'id_form_approve_application'
        self.helper.attrs = {'novalidate': ''}
        # Limit the assignee queryset.
        approver = Group.objects.get_or_create(name='Approver')[0]
        self.fields['assignee'].queryset = User.objects.filter(groups__in=[approver])
        self.fields['assignee'].required = True
        self.fields['assignee'].label = 'Manager'
        # Disable all form fields.
        for k, v in self.fields.items():
            self.fields[k].disabled = True
        # Re-enable the assignee field.
        self.fields['assignee'].disabled = False
        # Define the form layout.
        self.helper.layout = Layout(
            HTML('<p>Assign this application to a manager for approval/issue:</p>'),
            'app_type', 'title', 'description', 'submit_date', 'assignee',
            FormActions(
                Submit('assign', 'Assign', css_class='btn-lg'),
                Submit('cancel', 'Cancel')
            )
        )


class ApplicationIssueForm(ModelForm):
    assessment = ChoiceField(choices=[
        (None, '---------'),
        ('issue', 'Issue'),
        ('decline', 'Decline'),
        # TODO: Return to assessor option.
        #('return', 'Return to assessor'),
    ])

    class Meta:
        model = Application
        fields = ['app_type', 'title', 'description', 'submit_date']

    def __init__(self, *args, **kwargs):
        super(ApplicationIssueForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper(self)
        self.helper.form_id = 'id_form_application_issue'
        self.helper.attrs = {'novalidate': ''}
        # Disable all form fields.
        for k, v in self.fields.items():
            self.fields[k].disabled = True
        # Re-enable the assessment field.
        self.fields['assessment'].disabled = False
        # Define the form layout.
        self.helper.layout = Layout(
            HTML('<p>Issue or decline this completed application:</p>'),
            'app_type', 'title', 'description', 'submit_date', 'assessment',
            FormActions(
                Submit('save', 'Save', css_class='btn-lg'),
                Submit('cancel', 'Cancel')
            )
        )

'''
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
'''
