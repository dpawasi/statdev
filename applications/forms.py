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

from accounts.models import Organisation
from .models import Application, Referral, Condition, Compliance, Vessel, Document, PublicationNewspaper, PublicationWebsite, PublicationFeedback

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
        # Limit the organisation queryset unless the user is a superuser.
        if not user.is_superuser:
            self.fields['organisation'].queryset = Organisation.objects.filter(delegates__in=[user.emailuserprofile])
        self.fields['organisation'].help_text = '''The company or organisation
            on whose behalf you are applying (leave blank if not applicable).'''

        # Add labels for fields
        self.fields['app_type'].label = "Application Type"


class ApplicationWebPublishForm(ModelForm):

    class Meta:
        model = Application
        fields = ['publish_documents', 'publish_draft_report','publish_final_report']

    def __init__(self, *args, **kwargs):
        # User must be passed in as a kwarg.
        #user = kwargs.pop('user')
        super(ApplicationWebPublishForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper()
        self.helper.form_id = 'id_form_web_publish_application'
        self.helper.attrs = {'novalidate': ''}

        # Delete publish fields not required for update.
        if kwargs['initial']['publish_type'] in 'documents':
            del self.fields['publish_draft_report']
            del self.fields['publish_final_report']
            self.fields['publish_documents'].label = "Published Date"
            self.fields['publish_documents'].widget.attrs['disabled'] = True
        elif kwargs['initial']['publish_type'] in 'draft':
            del self.fields['publish_final_report']
            del self.fields['publish_documents']
            self.fields['publish_draft_report'].label = "Published Date"
            self.fields['publish_draft_report'].widget.attrs['disabled'] = True
        elif kwargs['initial']['publish_type'] in 'final':
            del self.fields['publish_draft_report']
            del self.fields['publish_documents']
            self.fields['publish_final_report'].label = "Published Date"
            self.fields['publish_final_report'].widget.attrs['disabled'] = True

        else:

            del self.fields['publish_draft_report']
            del self.fields['publish_final_report']
            del self.fields['publish_documents']

        self.helper.add_input(Submit('save', 'Publish to Website', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel'))


class ApplicationFormMixin(object):
    """Form mixin containing validation rules common to all application types.
    """
    def clean(self):
        cleaned_data = super(ApplicationFormMixin, self).clean()
        # Rule: proposed commence date cannot be later then proposed end date.
        if cleaned_data.get('proposed_commence') and cleaned_data.get('proposed_end'):
            if cleaned_data['proposed_commence'] > cleaned_data['proposed_end']:
                msg = 'Commence date cannot be later than the end date'
                self._errors['proposed_commence'] = self.error_class([msg])
                self._errors['proposed_end'] = self.error_class([msg])
        return cleaned_data


class ApplicationLicencePermitForm(ApplicationFormMixin, ModelForm):
    cert_survey = FileField(
        label='Certificate of survey', required=False, max_length=128)
    cert_public_liability_insurance = FileField(
        label='Public liability insurance certificate', required=False, max_length=128)
    risk_mgmt_plan = FileField(
        label='Risk managment plan', required=False, max_length=128)
    safety_mgmt_procedures = FileField(
        label='Safety management procedures', required=False, max_length=128)
    deed = FileField(required=False, max_length=128)
    brochures_itineries_adverts = MultiFileField(
        required=False, label='Brochures, itineraries or advertisements',
        help_text='Choose multiple files to upload (if required). NOTE: this will replace any existing uploads.')
    land_owner_consent = MultiFileField(
        required=False, label='Landowner consent statement(s)',
        help_text='Choose multiple files to upload (if required). NOTE: this will replace any existing uploads.')

    class Meta:
        model = Application
        fields = [
            'title', 'description', 'proposed_commence', 'proposed_end',
            'cost', 'project_no', 'related_permits', 'over_water',
            'purpose', 'max_participants', 'proposed_location', 'address',
            'jetties', 'jetty_dot_approval', 'jetty_dot_approval_expiry',
            'drop_off_pick_up', 'food', 'beverage', 'byo_alcohol', 'sullage_disposal', 'waste_disposal',
            'refuel_location_method', 'berth_location', 'anchorage', 'operating_details',
        ]

    def __init__(self, *args, **kwargs):
        super(ApplicationLicencePermitForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper()
        self.helper.form_id = 'id_form_update_licence_permit'
        self.helper.attrs = {'novalidate': ''}
        self.helper.add_input(Submit('save', 'Save', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel'))

        # Add labels for fields
        self.fields['description'].label = "Proposed Commercial Acts or Activities"
        self.fields['project_no'].label = "Riverbank Project Number"
        self.fields['purpose'].label = "Purpose of Approval"
        self.fields['proposed_commence'].label = "Proposed Commencement Date"
        self.fields['proposed_end'].label = "Proposed End Date"
        self.fields['max_participants'].label = "Maximum Number of Participants"
        self.fields['address'].label = "Address of any landbased component of the commercial activity"
        self.fields['proposed_location'].label = "Location / Route and Access Points"
        self.fields['jetties'].label = "List all jetties to be used"
        self.fields['jetty_dot_approval'].label = "Do you have approval to use Departmen of Transport service jetties?"
        self.fields['drop_off_pick_up'].label = "List all drop off and pick up points"
        self.fields['food'].label = "Food to be served?"
        self.fields['beverage'].label = "Beverage to be served?"
        self.fields['byo_alcohol'].label = "Do you allow BYO alcohol?"
        self.fields['sullage_disposal'].label = "Details of sullage disposal method"
        self.fields['waste_disposal'].label = "Details of waste disposal method"
        self.fields['refuel_location_method'].label = "Location and method of refueling"
        self.fields['anchorage'].label = "List all anchorage areas"
        self.fields['operating_details'].label = "Hours and days of operation including length of tours / lessons"

    def clean(self):
        cleaned_data = super(ApplicationLicencePermitForm, self).clean()
        # Clean the uploaded file fields (acceptable file types).
        for field in [
                'cert_survey', 'cert_public_liability_insurance', 'risk_mgmt_plan',
                'safety_mgmt_procedures', 'deed']:
            up = cleaned_data.get(field)
            if up and hasattr(up, 'content_type') and up.content_type not in settings.ALLOWED_UPLOAD_TYPES:
                self._errors[field] = self.error_class(['{}: this file type is not permitted'.format(up.name)])
        # Clean multi-upload fields:
        for field in ['brochures_itineries_adverts', 'land_owner_consent']:
            up = cleaned_data.get(field)
            errors = []
            if up:
                for f in up:
                    if hasattr(f, 'content_type') and f.content_type not in settings.ALLOWED_UPLOAD_TYPES:
                        errors.append('{}: this file type is not permitted'.format(f.name))
                if errors:
                    self._errors[field] = self.error_class(errors)
        return cleaned_data


class ApplicationPermitForm(ApplicationFormMixin, ModelForm):
    class Meta:
        model = Application
        fields = [
            'title', 'description', 'proposed_commence', 'proposed_end',
            'cost', 'project_no', 'related_permits', 'over_water', 'documents',
            'land_owner_consent', 'deed']

    def __init__(self, *args, **kwargs):
        super(ApplicationPermitForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper()
        self.helper.form_id = 'id_form_update_permit'
        self.helper.attrs = {'novalidate': ''}
        self.helper.add_input(Submit('save', 'Save', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel'))

        # Add labels and help text for fields
        self.fields['proposed_commence'].label = "Proposed commencement date"
        self.fields['proposed_commence'].help_text = "(Please that consider routine assessment takes approximately 4 - 6 weeks, and set your commencement date accordingly)"
        self.fields['proposed_end'].label = "Proposed end date"
        self.fields['cost'].label = "Approximate cost"
        self.fields['project_no'].label = "Riverbank project number (if applicable)"
        self.fields['related_permits'].label = "Details of related permits"
        self.fields['description'].label = "Description of works, acts or activities"
        self.fields['documents'].label = "Attach more detailed descripton, maps or plans"
        #self.fields['other_supporting_docs'].label = "Attach supporting information to demonstrate compliance with relevant Trust policies"


class ApplicationPart5Form(ApplicationFormMixin, ModelForm):

    certificate_of_title_volume = CharField(required=False)
    folio = CharField(required=False)
    diagram_plan_deposit_number = CharField(required=False)
    location = CharField(required=False)
    reserve_number = CharField(required=False)
    street_number_and_name = CharField(required=False)
    town_suburb = CharField(required=False)
    lot = CharField(required=False)
    nearest_road_intersection = CharField(required=False)

    land_owner_consent = Field(required=False, widget=ClearableMultipleFileInput(attrs={'multiple':'multiple'}),  label='Land Owner Consent')
    proposed_development_plans = FileField(required=False, max_length=128, widget=ClearableMultipleFileInput(attrs={'multiple':'multiple'}))
    document_new_draft = FileField(required=False, max_length=128 , widget=ClearableFileInput)
    document_draft = FileField(required=False, max_length=128 , widget=ClearableFileInput)
    document_final = FileField(required=False, max_length=128, widget=ClearableFileInput)
    document_determination = FileField(required=False, max_length=128, widget=ClearableFileInput)
    document_completion = FileField(required=False, max_length=128, widget=ClearableFileInput)
    river_lease_scan_of_application = FileField(required=False, max_length=128, widget=ClearableFileInput)
    deed = FileField(required=False, max_length=128, widget=ClearableFileInput)
    swan_river_trust_board_feedback = FileField(required=False, max_length=128, widget=ClearableFileInput)

    class Meta:
        model = Application
        fields = ['title', 'description','cost','project_no', 'river_lease_require_river_lease','river_lease_reserve_licence','river_lease_application_number','proposed_development_description','proposed_development_current_use_of_land','assessment_start_date']

    def __init__(self, *args, **kwargs):
        super(ApplicationPart5Form, self).__init__(*args, **kwargs)

        for fielditem in self.initial["fieldstatus"]:
            del self.fields[fielditem]

        for fielditem in self.initial["fieldrequired"]:
            self.fields[fielditem].required = True

        self.helper = BaseFormHelper()
        self.helper.form_id = 'id_form_update_part_5'
        self.helper.attrs = {'novalidate': ''}
        self.helper.add_input(Submit('save', 'Save', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel'))


class ApplicationEmergencyForm(ModelForm):
    class Meta:
        model = Application
        fields = ['applicant', 'organisation', 'proposed_commence', 'proposed_end']

    def __init__(self, *args, **kwargs):
        super(ApplicationEmergencyForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper()
        self.helper.form_id = 'id_form_update_emergency'
        self.helper.attrs = {'novalidate': ''}
        self.helper.add_input(Submit('save', 'Save', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel'))

        # Add labels and help text for fields
        self.fields['proposed_commence'].label = "Start date"
        self.fields['proposed_end'].label = "Expiry date"


class ApplicationLodgeForm(Form):
    """A basic form to submit a request to lodge an application.
    """
    def __init__(self, *args, **kwargs):
        kwargs.pop('instance')  # Don't need this because this isn't a ModelForm.
        super(ApplicationLodgeForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper(self)
        self.helper.form_id = 'id_form_lodge_application'
        self.helper.layout = Layout(
            HTML('<p>Confirm that this application should be lodged for assessment:</p>'),
            FormActions(
                Submit('lodge', 'Lodge', css_class='btn-lg'),
                Submit('cancel', 'Cancel')
            )
        )


class ReferralForm(ModelForm):
    class Meta:
        model = Referral
        fields = ['referee', 'period', 'details']

    def __init__(self, *args, **kwargs):
        # Application must be passed in as a kwarg.
        app = kwargs.pop('application')
        super(ReferralForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper(self)
        self.helper.form_id = 'id_form_referral_create'
        self.helper.attrs = {'novalidate': ''}
        # Limit the referee queryset.
        referee = Group.objects.get(name='Referee')
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


class ReferralRecallForm(Form):
    """A basic form to submit a request to lodge an application.
    """
    def __init__(self, *args, **kwargs):
        kwargs.pop('instance')  # Don't need this because this isn't a ModelForm.
        super(ReferralRecallForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper(self)
        self.helper.form_id = 'id_form_referral_recall'
        self.helper.add_input(Submit('recall', 'Recall', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel'))


class ReferralRemindForm(Form):
    """Form is to allow a referral to be reminded about the outstanding feedback 
    """
    def __init__(self, *args, **kwargs):
        kwargs.pop('instance')  # Don't need this because this isn't a ModelForm.
        super(ReferralRemindForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper(self)
        self.helper.form_id = 'id_form_referral_remind'
        self.helper.add_input(Submit('remind', 'Remind', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel'))


class ReferralResendForm(Form):
    """Form is to allow a admin officer to resend the referral back to the referral for additional feedback
    """
    def __init__(self, *args, **kwargs):
        kwargs.pop('instance')  # Don't need this because this isn't a ModelForm.
        super(ReferralResendForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper(self)
        self.helper.form_id = 'id_form_referral_resend'
        self.helper.add_input(Submit('remind', 'Resend', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel'))


class ReferralDeleteForm(Form):
    """Form is to allow a referral to be reminded about the outstanding feedback
    """
    def __init__(self, *args, **kwargs):
        kwargs.pop('instance')  # Don't need this because this isn't a ModelForm.
        super(ReferralDeleteForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper(self)
        self.helper.form_id = 'id_form_referral_delete'
        self.helper.add_input(Submit('delete', 'Delete', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel'))


class ConditionCreateForm(ModelForm):
    class Meta:
        model = Condition
        fields = ['condition', 'due_date', 'recur_pattern', 'recur_freq']

    def __init__(self, *args, **kwargs):
        super(ConditionCreateForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper(self)
        self.helper.attrs = {'novalidate': ''}
        self.fields['condition'].required = True
        self.helper.add_input(Submit('save', 'Save', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel'))


class ConditionUpdateForm(ModelForm):
    class Meta:
        model = Condition
        fields = ['condition', 'due_date', 'recur_pattern', 'recur_freq']

    def __init__(self, *args, **kwargs):
        super(ConditionUpdateForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper(self)
        self.helper.form_id = 'id_form_condition_apply'
        self.helper.add_input(Submit('update', 'Update', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel'))


class ConditionActionForm(ModelForm):
    class Meta:
        model = Condition
        fields = ['condition', 'due_date', 'recur_pattern', 'recur_freq']

    def __init__(self, *args, **kwargs):
        super(ConditionActionForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper(self)
        self.helper.form_id = 'id_form_condition_action'
        self.fields['condition'].disabled = True
        self.fields['due_date'].disabled = True
        self.helper.add_input(Submit('update', 'Update', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel'))



class OldConditionActionForm(ConditionUpdateForm):
    """A extension of ConditionUpdateForm with the condition field disabled.
    """
    # broken for some reason end up copying ConditionUpdateForm and adjusting.  kept getting bool error on this one.
    class Meta:
        model = Condition
        fields = ['condition', 'due_date', 'recur_pattern', 'recur_freq']

    def __init__(self, *args, **kwargs):
        super(OldConditionActionForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper(self)
        self.helper.form_id = 'id_form_condition_action'
        self.fields['condition'].disabled = True
        self.fields['due_date'].disabled = True
 #       self.fields['recur_pattern'] = True
#        self.fields['recur_freq'] = True
        self.helper.add_input(Submit('update', 'Update', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel'))

class ApplicationAssignNextAction(ModelForm):
    """A form for assigning an application back to a group.
    """
    details = CharField(required=False, widget=Textarea, help_text='Detailed information for communication log.')
    documents = FileField(required=False, max_length=128, widget=ClearableFileInput) 

    class Meta:
        model = Application
        fields = ['id','details','documents']
    def __init__(self, *args, **kwargs):
        super(ApplicationAssignNextAction, self).__init__(*args, **kwargs)

        self.helper = BaseFormHelper(self)
		
        self.helper.form_id = 'id_form_assigngroup_application'
        self.helper.attrs = {'novalidate': ''}
		
		
        self.helper.layout = Layout(
            HTML('<p>Application Next Action</p>'),
            'details','documents',
            FormActions(
                Submit('assign', 'Assign', css_class='btn-lg'),
                Submit('cancel', 'Cancel')
            )
        )



#        self.fields['title'].disabled = True 
#        self.helper.add_input(Submit('assign', 'Assign', css_class='btn-lg'))
#        self.helper.add_input(Submit('cancel', 'Cancel'))

class AssignPersonForm(ModelForm):
    """A form for assigning an application to people with a specific group.
    """

    class Meta:
        model = Application
#        fields = ['app_type', 'title', 'description', 'submit_date', 'assignee']
        fields = ['assignee']

    def __init__(self, *args, **kwargs):
        super(AssignPersonForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper(self)
        self.helper.form_id = 'id_form_assign_person_application'
        self.helper.attrs = {'novalidate': ''}
        # Limit the assignee queryset.
        assigngroup = Group.objects.get(name=self.initial['assigngroup'])
        self.fields['assignee'].queryset = User.objects.filter(groups__in=[assigngroup])
        self.fields['assignee'].required = True
        # Disable all form fields.
        for k, v in self.fields.items():
            self.fields[k].disabled = True
        # Re-enable the assignee field.
        self.fields['assignee'].disabled = False
        #self.initial["fieldstatus"]:
        # Define the form layout.
        self.helper.layout = Layout(
            HTML('<p>Assign this application for processing:</p>'),
            'app_type', 'title', 'description', 'submit_date', 'assignee',
            FormActions(
                Submit('assign', 'Assign', css_class='btn-lg'),
                Submit('cancel', 'Cancel')
            )
        )


class AssignCustomerForm(ModelForm):
    """A form for assigning an application back to the customer.
    """
    feedback = CharField(
        required=False, widget=Textarea, help_text='Feedback to be provided to the customer.')

    class Meta:
        model = Application
        fields = ['app_type', 'title', 'description']

    def __init__(self, *args, **kwargs):
        super(AssignCustomerForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper(self)
        self.helper.form_id = 'id_form_assign_application'
        self.helper.attrs = {'novalidate': ''}
        # Disable all form fields.
        for k, v in self.fields.items():
            self.fields[k].disabled = True
        # Re-enable the feedback field.
        self.fields['feedback'].disabled = False
        self.fields['feedback'].required = True
        # Define the form layout.
        self.helper.layout = Layout(
            HTML('<p>Reassign this application back to the applicant, with feedback:</p>'),
            'app_type', 'title', 'description', 'feedback',
            FormActions(
                Submit('assign', 'Assign', css_class='btn-lg'),
                Submit('cancel', 'Cancel')
            )
        )


class AssignProcessorForm(ModelForm):
    """A form for assigning a processor (admin officer) to an application.
    """

    class Meta:
        model = Application
#        fields = ['app_type', 'title', 'description', 'submit_date', 'assignee']
        fields = ['assignee']

    def __init__(self, *args, **kwargs):
        super(AssignProcessorForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper(self)
        self.helper.form_id = 'id_form_assign_application'
        self.helper.attrs = {'novalidate': ''}
        # Limit the assignee queryset.
        processor = Group.objects.get(name='Processor')
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
#        fields = ['app_type', 'title', 'description', 'submit_date', 'assignee']
        fields = ['assignee']
    def __init__(self, *args, **kwargs):
        super(AssignAssessorForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper(self)
        self.helper.form_id = 'id_form_assign_application'
        self.helper.attrs = {'novalidate': ''}
        # Limit the assignee queryset.
        assessor = Group.objects.get(name='Assessor')
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
#        fields = ['app_type', 'title', 'description', 'submit_date', 'assignee']
        fields = ['assignee']

    def __init__(self, *args, **kwargs):
        super(AssignApproverForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper(self)
        self.helper.form_id = 'id_form_approve_application'
        self.helper.attrs = {'novalidate': ''}
        # Limit the assignee queryset.
        approver = Group.objects.get(name='Approver')
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


class AssignEmergencyForm(ModelForm):
    """A form for assigning an emergency works to a user with the Emergency group.
    """
    class Meta:
        model = Application
        fields = ['assignee']

    def __init__(self, *args, **kwargs):
        super(AssignEmergencyForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper(self)
        self.helper.form_id = 'id_form_assign_emergency_application'
        self.helper.attrs = {'novalidate': ''}
        # Limit the assignee queryset.
        emergency = Group.objects.get(name='Emergency')
        self.fields['assignee'].queryset = User.objects.filter(groups__in=[emergency])
        self.fields['assignee'].required = True
        # Disable all form fields.
        for k, v in self.fields.items():
            self.fields[k].disabled = True
        # Re-enable the assignee field.
        self.fields['assignee'].disabled = False
        # Define the form layout.
        self.helper.layout = Layout(
            HTML('<p>Assign this Emergency Works to a new Admin officer:</p>'),
            'assignee',
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


class ApplicationEmergencyIssueForm(ModelForm):
    assessment = ChoiceField(choices=[
        (None, '---------'),
        ('issue', 'Issue'),
        ('decline', 'Decline'),
    ])

    holder = CharField(required=False)
    abn = CharField(required=False)

    class Meta:
        model = Application
        fields = ['app_type', 'issue_date', 'proposed_commence', 'proposed_end']

    def __init__(self, *args, **kwargs):
        super(ApplicationEmergencyIssueForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper(self)
        self.helper.form_id = 'id_form_application_issue'
        self.helper.attrs = {'novalidate': ''}
        self.fields['app_type'].required = False
        # Disable all form fields.
        for k, v in self.fields.items():
            self.fields[k].disabled = True
        # Re-enable the assessment field.
        self.fields['assessment'].disabled = False
        # Define the form layout.
        self.helper.layout = Layout(
            HTML('<p>Issue or decline this completed Emergency Works application:</p>'),
            'app_type', 'holder', 'abn', 'issue_date', 'proposed_commence', 'proposed_end', 'assessment',
            FormActions(
                Submit('save', 'Issue', css_class='btn-lg'),
                Submit('cancel', 'Cancel')
            )
        )

        self.fields['proposed_commence'].label = "Start Date"
        self.fields['proposed_end'].label = "Expiry Date"

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


class VesselForm(ModelForm):
    registration = MultiFileField(
        required=False, label='Registration & licence documents',
        help_text='Choose multiple files to upload (if required). NOTE: this will replace any existing uploads.')

    class Meta:
        model = Vessel
        fields = ['vessel_type', 'name', 'vessel_id', 'size', 'engine', 'passenger_capacity']

    def __init__(self, *args, **kwargs):
        # User must be passed in as a kwarg.
        super(VesselForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper()
        self.helper.form_id = 'id_form_create_vessel'
        self.helper.attrs = {'novalidate': ''}
        self.helper.add_input(Submit('save', 'Save', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel'))


class NewsPaperPublicationCreateForm(ModelForm):

    documents = Field(required=False, widget=ClearableMultipleFileInput(attrs={'multiple':'multiple'}))
    class Meta:
        model = PublicationNewspaper
        fields = ['application','date','newspaper']

    def __init__(self, *args, **kwargs):
        super(NewsPaperPublicationCreateForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper()
        self.helper.form_id = 'id_form_create_newspaperpublication'
        self.helper.attrs = {'novalidate': ''}
        self.fields['application'].widget = HiddenInput()
        self.helper.add_input(Submit('save', 'Save', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel'))


class WebsitePublicationCreateForm(ModelForm):

    original_document = FileField(required=False, max_length=128 , widget=ClearableFileInput(attrs={'multiple':'multiple'})) 
    published_document = FileField(required=False, max_length=128 , widget=ClearableMultipleFileInput(attrs={'multiple':'multiple'}))

    class Meta:
        model = PublicationWebsite
#        fields = ['application','original_document','published_document']
        fields = ['application']
    def __init__(self, *args, **kwargs):
        super(WebsitePublicationCreateForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper()
        self.helper.form_id = 'id_form_create_websitepublication'
        self.helper.attrs = {'novalidate': ''}
        self.fields['application'].widget = HiddenInput()
        self.helper.add_input(Submit('save', 'Save', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel'))

class WebsitePublicationForm(ModelForm):

    original_document = FileField(required=False, max_length=128 , widget=ClearableFileInput)
    published_document = FileField(required=False, max_length=128 , widget=ClearableMultipleFileInput)

    #    original_document = IntegerField()
    class Meta:
        model = PublicationWebsite
        fields = ['application','original_document']
    def __init__(self, *args, **kwargs):
        super(WebsitePublicationForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper()
        self.helper.form_id = 'id_form_create_websitepublication'
        self.helper.attrs = {'novalidate': ''}
        self.fields['application'].widget = HiddenInput()
        self.fields['original_document'].widget = HiddenInput()
        self.helper.add_input(Submit('save', 'Save', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel'))

class FeedbackPublicationCreateForm(ModelForm):

    documents = FileField(required=False, max_length=128 , widget=ClearableMultipleFileInput(attrs={'multiple':'multiple'}))

    class Meta:
        model = PublicationFeedback
        fields = ['application','name','address','suburb','state','postcode','phone','email','comments','status']

    def __init__(self, *args, **kwargs):
        super(FeedbackPublicationCreateForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper()
        self.helper.form_id = 'id_form_create_websitepublication'
        self.helper.attrs = {'novalidate': ''}
        self.fields['application'].widget = HiddenInput()
        self.fields['status'].widget = HiddenInput()
        self.helper.add_input(Submit('save', 'Save', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel'))

class DocumentCreateForm(ModelForm):
    class Meta:
        model = Document
        fields = ['upload', 'name', 'category', 'metadata']

    def __init__(self, *args, **kwargs):
        super(DocumentCreateForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper()
        self.helper.form_id = 'id_form_create_document'
        self.helper.attrs = {'novalidate': ''}
        self.helper.add_input(Submit('save', 'Save', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel'))
