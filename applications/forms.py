from __future__ import unicode_literals
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, HTML
from crispy_forms.bootstrap import FormActions
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.forms import ModelForm, ChoiceField, FileField

from accounts.models import Organisation
from .models import Application, Referral, Condition, Compliance


User = get_user_model()


class BaseFormHelper(FormHelper):
    form_class = 'form-horizontal'
    label_class = 'col-xs-12 col-sm-4 col-md-3 col-lg-2'
    field_class = 'col-xs-12 col-sm-8 col-md-6 col-lg-4'


class ApplicationCreateForm(ModelForm):
    class Meta:
        model = Application
        fields = ['app_type', 'organisation']

    def __init__(self, *args, **kwargs):
        # User must be passed in as a kwarg.
        user = kwargs.pop('user')
        super(ApplicationCreateForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper()
        self.helper.form_id = 'id_form_create_application'
        self.helper.attrs = {'novalidate': ''}
        self.helper.add_input(Submit('save', 'Save', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel'))
        # Limit the organisation queryset.
        self.fields['organisation'].queryset = Organisation.objects.filter(delegates__in=[user.emailuserprofile])
        self.fields['organisation'].help_text = '''The company or organisation
            on whose behalf you are applying (leave blank if not applicable).'''


class ApplicationLicencePermitForm(ModelForm):
    class Meta:
        model = Application
        fields = ['title', 'description',
            'proposed_commence', 'proposed_end', 'cost', 'project_no', 'related_permits', 'over_water',
            'purpose', 'max_participants', 'proposed_location', 'address',
            'jetties', 'jetty_dot_approval', 'jetty_dot_approval_expiry',
            'drop_off_pick_up', 'food', 'beverage', 'byo_alcohol', 'sullage_disposal', 'waste_disposal',
            'refuel_location_method', 'berth_location', 'anchorage', 'operating_details']

    def __init__(self, *args, **kwargs):
        super(ApplicationLicencePermitForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper()
        self.helper.form_id = 'id_form_update_licence_permit'
        self.helper.attrs = {'novalidate': ''}
        self.helper.add_input(Submit('save', 'Save', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel'))
        # TODO: all document fields.


class ApplicationPermitForm(ModelForm):
    class Meta:
        model = Application
        fields = ['title', 'description',
            'proposed_commence', 'proposed_end', 'cost', 'project_no', 'related_permits', 'over_water',
            'documents', 'land_owner_consent', 'deed']

    def __init__(self, *args, **kwargs):
        super(ApplicationPermitForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper()
        self.helper.form_id = 'id_form_update_permit'
        self.helper.attrs = {'novalidate': ''}
        self.helper.add_input(Submit('save', 'Save', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel'))


class ApplicationPart5Form(ModelForm):
    class Meta:
        model = Application
        fields = ['title', 'description',
            'cost', 'project_no', 'documents', 'other_supporting_docs', 'land_owner_consent', 'deed',
            'river_reserve_lease', 'current_land_use','proposed_development_current_use_of_land',
			'proposed_development_description','proposed_development_plans','document_draft','document_final',
			'document_determination','document_completion']

    def __init__(self, *args, **kwargs):
        super(ApplicationPart5Form, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper()
        self.helper.form_id = 'id_form_update_part_5'
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
        # Application must be passed in as a kwarg.
        app = kwargs.pop('application')
        super(ReferralForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper(self)
        self.helper.form_id = 'id_form_referral_create'
        self.helper.attrs = {'novalidate': ''}
        # Limit the referee queryset.
        referee = Group.objects.get_or_create(name='Referee')[0]
        existing_referees = app.referral_set.all().values_list('referee__email', flat=True)
        self.fields['referee'].queryset = User.objects.filter(groups__in=[referee]).exclude(email__in=existing_referees)
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


class ReferralRecallForm(ModelForm):
    class Meta:
        model = Referral
        exclude = ['effective_to', 'application', 'referee', 'details', 'sent_date', 'period', 'response_date', 'feedback', 'documents', 'status']

    def __init__(self, *args, **kwargs):
        super(ReferralRecallForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper(self)
        self.helper.form_id = 'id_form_referral_recall'
        self.helper.add_input(Submit('recall', 'Recall', css_class='btn-lg'))
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


class AssignProcessorForm(ModelForm):
    """A form for assigning a processor (admin officer) to an application.
    """
    class Meta:
        model = Application
        fields = ['app_type', 'title', 'description', 'submit_date', 'assignee']

    def __init__(self, *args, **kwargs):
        super(AssignProcessorForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper(self)
        self.helper.form_id = 'id_form_assign_application'
        self.helper.attrs = {'novalidate': ''}
        # Limit the assignee queryset.
        processor = Group.objects.get_or_create(name='Processor')[0]
        self.fields['assignee'].queryset = User.objects.filter(groups__in=[processor])
        self.fields['assignee'].required = True
        # Disable all form fields.
        for k, v in self.fields.items():
            self.fields[k].disabled = True
        # Re-enable the assignee field.
        self.fields['assignee'].disabled = False
        # Define the form layout.
        self.helper.layout = Layout(
            HTML('<p>Assign this application for processing:</p>'),
            'app_type', 'title', 'description', 'submit_date', 'assignee',
            FormActions(
                Submit('assign', 'Assign', css_class='btn-lg'),
                Submit('cancel', 'Cancel')
            )
        )


class AssignAssessorForm(ModelForm):
    """A form for assigning an assessor to an application.
    """
    class Meta:
        model = Application
        fields = ['app_type', 'title', 'description', 'submit_date', 'assignee']

    def __init__(self, *args, **kwargs):
        super(AssignAssessorForm, self).__init__(*args, **kwargs)
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


class AssignApproverForm(ModelForm):
    """A form for assigning a manager to approve an application.
    """
    class Meta:
        model = Application
        fields = ['app_type', 'title', 'description', 'submit_date', 'assignee']

    def __init__(self, *args, **kwargs):
        super(AssignApproverForm, self).__init__(*args, **kwargs)
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


class ComplianceCreateForm(ModelForm):
    supporting_document = FileField(required=False, max_length=128)

    class Meta:
        model = Compliance
        fields = ['condition', 'compliance', 'supporting_document']

    def __init__(self, *args, **kwargs):
        # Application must be passed in as a kwarg.
        application = kwargs.pop('application')
        super(ComplianceCreateForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper(self)
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.fields['condition'].queryset = Condition.objects.filter(application=application)
