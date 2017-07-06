from __future__ import unicode_literals
from django.core.urlresolvers import reverse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, HTML, Fieldset, MultiField, Div
from crispy_forms.bootstrap import FormActions, InlineRadios
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.forms import Form, ModelForm, ChoiceField, FileField, CharField, Textarea, ClearableFileInput, HiddenInput, Field, RadioSelect
from applications.widgets import ClearableMultipleFileInput
from multiupload.fields import MultiFileField
from .crispy_common import crispy_heading, crispy_box, crispy_empty_box, crispy_para, check_fields_exist, crispy_button_link, crispy_button
from ledger.accounts.models import EmailUser, Address, Organisation
from .models import (
    Application, Referral, Condition, Compliance, Vessel, Record, PublicationNewspaper,
    PublicationWebsite, PublicationFeedback, Delegate, Communication)

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
            user_orgs = [d.pk for d in Delegate.objects.filter(email_user=user)]
            self.fields['organisation'].queryset = Organisation.objects.filter(pk__in=user_orgs)
        self.fields['organisation'].help_text = '''The company or organisation
            on whose behalf you are applying (leave blank if not applicable).'''

        # Add labels for fields
        self.fields['app_type'].label = "Application Type"

class CommunicationCreateForm(ModelForm):
    records = Field(required=False, widget=ClearableMultipleFileInput(attrs={'multiple':'multiple'}),  label='Documents')

    class Meta:
        model = Communication 
        fields = ['comms_to','comms_from','subject','comms_type','details','records','details']

    def __init__(self, *args, **kwargs):
        # User must be passed in as a kwarg.
        user = kwargs.pop('user')
        #application = kwargs.pop('application')
        super(CommunicationCreateForm, self).__init__(*args, **kwargs)

        self.fields['comms_to'].required = True
        self.fields['comms_from'].required = True
        self.fields['subject'].required = True
        self.fields['comms_type'].required = True

        self.helper = BaseFormHelper()
        self.helper.form_id = 'id_form_create_communication'
        self.helper.attrs = {'novalidate': ''}
        self.helper.add_input(Submit('save', 'Create', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel'))
        # Add labels for fields
        #self.fields['app_type'].label = "Application Type"

class ApplicationWebPublishForm(ModelForm):

    class Meta:
        model = Application
        fields = ['publish_documents', 'publish_draft_report', 'publish_final_report', 'publish_determination_report']

    def __init__(self, *args, **kwargs):
        super(ApplicationWebPublishForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper()
        self.helper.form_id = 'id_form_web_publish_application'
        self.helper.attrs = {'novalidate': ''}

        # Delete publish fields not required for update.
        if kwargs['initial']['publish_type'] in 'records':
            del self.fields['publish_draft_report']
            del self.fields['publish_final_report']
            del self.fields['publish_determination_report']
            self.fields['publish_documents'].label = "Published Date"
            self.fields['publish_documents'].widget.attrs['disabled'] = True
        elif kwargs['initial']['publish_type'] in 'draft':
            del self.fields['publish_final_report']
            del self.fields['publish_documents']
            del self.fields['publish_determination_report']
            self.fields['publish_draft_report'].label = "Published Date"
            self.fields['publish_draft_report'].widget.attrs['disabled'] = True
        elif kwargs['initial']['publish_type'] in 'final':
            del self.fields['publish_draft_report']
            del self.fields['publish_documents']
            del self.fields['publish_determination_report']
            self.fields['publish_final_report'].label = "Published Date"
            self.fields['publish_final_report'].widget.attrs['disabled'] = True
        elif kwargs['initial']['publish_type'] in 'determination':
            del self.fields['publish_draft_report']
            del self.fields['publish_documents']
            del self.fields['publish_final_report']
            self.fields['publish_determination_report'].label = "Published Date"
            self.fields['publish_determination_report'].widget.attrs['disabled'] = True
        else:
            del self.fields['publish_draft_report']
            del self.fields['publish_final_report']
            del self.fields['publish_documents']
            del self.fields['publish_determination_report']

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
    deed = FileField(required=False, max_length=128, widget=ClearableFileInput)
    brochures_itineries_adverts = Field(required=False, widget=ClearableMultipleFileInput(attrs={'multiple':'multiple'}))
    #MultiFileField(
    #    required=False, label='Brochures, itineraries or advertisements',
    #    help_text='Choose multiple files to upload (if required). NOTE: this will replace any existing uploads.')
    #    land_owner_consent = MultiFileField(
            #        required=False, label='Landowner consent statement(s)',
        #        help_text='Choose multiple files to upload (if required). NOTE: this will replace any existing uploads.')
    land_owner_consent = Field(required=False, widget=ClearableMultipleFileInput(attrs={'multiple':'multiple'}),  label='Landowner consent statement(s)',
            help_text='Choose multiple files to upload (if required). NOTE: this will replace any existing uploads.'
            )

    location_route_access = FileField(required=False, max_length=128, widget=ClearableFileInput)
    document_final = FileField(required=False, max_length=128, widget=ClearableFileInput)
    other_relevant_documents = FileField(required=False, max_length=128, widget=ClearableMultipleFileInput(attrs={'multiple':'multiple'})) 
    vessel_or_craft_details = ChoiceField(choices=Application.APP_VESSEL_CRAFT ,widget=RadioSelect(attrs={'class':'radio-inline'}))
    jetty_dot_approval = ChoiceField(choices=Application.APP_YESNO ,widget=RadioSelect())
    food = ChoiceField(choices=Application.APP_YESNO ,widget=RadioSelect())
    beverage = ChoiceField(choices=Application.APP_YESNO ,widget=RadioSelect())
    byo_alcohol = ChoiceField(choices=Application.APP_YESNO ,widget=RadioSelect())


    class Meta:
        model = Application
        fields = [
            'applicant','title', 'description', 'proposed_commence', 'proposed_end',
            'purpose', 'max_participants', 'proposed_location', 'address',
            'jetties', 'jetty_dot_approval','type_of_crafts','number_of_crafts',
            'drop_off_pick_up', 'food', 'beverage', 'byo_alcohol', 'sullage_disposal', 'waste_disposal',
            'refuel_location_method', 'berth_location', 'anchorage', 'operating_details','assessment_start_date','expire_date','vessel_or_craft_details'
        ]

    def __init__(self, *args, **kwargs):
        super(ApplicationLicencePermitForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper()
        self.helper.form_id = 'id_form_update_licence_permit'
        self.helper.attrs = {'novalidate': ''}
        #self.helper.add_input(Submit('save', 'Save', css_class='btn-lg'))
        #self.helper.add_input(Submit('cancel', 'Cancel'))

        # Add labels for fields
        self.fields['description'].label = "Summary"
#       self.fields['project_no'].label = "Riverbank Project Number"
        self.fields['purpose'].label = "Purpose of Approval"
        self.fields['proposed_commence'].label = "Proposed Commencement Date"
        self.fields['proposed_end'].label = "Proposed End Date"
        self.fields['max_participants'].label = "Maximum Number of Participants"
        self.fields['address'].label = "Address of any landbased component of the commercial activity"
        self.fields['proposed_location'].label = "Proposed Location"
        self.fields['location_route_access'].label = "Location / Route and Access Points (mark clearly on map)"
        # self.fields['proposed_location'].label = "Location / Route and Access Points"
        self.fields['jetties'].label = "List all jetties to be used"
        self.fields['jetty_dot_approval'].label = "Do you have approval to use Department of Transport service jetties?"
        self.fields['drop_off_pick_up'].label = "List all drop off and pick up points"
        self.fields['food'].label = "Food to be served?"
        self.fields['beverage'].label = "Beverage to be served?"
        self.fields['byo_alcohol'].label = "Do you allow BYO alcohol?"
        self.fields['sullage_disposal'].label = "Details of sullage disposal method"
        self.fields['waste_disposal'].label = "Details of waste disposal method"
        self.fields['refuel_location_method'].label = "Location and method of refueling"
        self.fields['anchorage'].label = "List all anchorage areas"
        self.fields['operating_details'].label = "Hours and days of operation including length of tours / lessons"
        self.fields['vessel_or_craft_details'].label = "Are there any vessels or crafts to be noted in this application?"

        vesselandcraftdetails = crispy_para("Any vessel or craft to be used by a commercial operator in the river reserve must be noted in this application with the relevent Department of Transport certificate of survery or hire and driver registration.")
        deeddesc = crispy_para("Print <a href=''>the deed</a>, sign it and attach it to this application")
        landownerconsentdesc = crispy_para("Print <A href=''>this document</A> and have it signed by each landowner (or body responsible for management)")
        landownerconsentdesc2 = crispy_para("Then attach all signed documents to this application.")


        for fielditem in self.initial["fieldstatus"]:
            if fielditem in self.fields:
                del self.fields[fielditem]

        for fielditem in self.initial["fieldrequired"]:
            if fielditem in self.fields:
                self.fields[fielditem].required = True

        crispy_boxes = crispy_empty_box()


        if check_fields_exist(self.fields,['applicant']) is True:
            self.fields['applicant'].disabled = True
    #        print self.initial["workflow"]["hidden"]['vessels']
            if self.initial["may_change_application_applicant"] == "True":
                changeapplicantbutton = crispy_button_link('Add / Change Applicant',reverse('applicant_change', args=(self.initial['application_id'],)))
            else: 
                changeapplicantbutton = HTML('')
            crispy_boxes.append(crispy_box('applicant_collapse','form_applicant','Applicant','applicant', changeapplicantbutton,HTML('{% include "applications/applicant_update_snippet.html" %}')))


        if check_fields_exist(self.fields,['title']) is True:
             self.fields['title'].widget.attrs['placeholder'] = "Enter Title, ( Director of Corporate Services )"
             crispy_boxes.append(crispy_box('title_collapse', 'form_title' , 'Title','title',))

        if check_fields_exist(self.fields,['description']) is True:
             
             crispy_boxes.append(crispy_box('summary_collapse', 'form_summary' , 'Proposed Commercial Acts or Activities','description'))

        if check_fields_exist(self.fields,['description']) is True:
             crispy_boxes.append(crispy_box('vessel_or_crafts_view_collapse', 'form_vessel_or_crafts_view' , 'Vessel or Craft Details',vesselandcraftdetails,InlineRadios('vessel_or_craft_details'))) 

        if self.initial["workflow"]["hidden"]['vessels'] == "False":
            if self.initial['vessel_or_craft_details'] == 1:
                crispy_boxes.append(crispy_box('vessel_or_crafts_collapse', 'form_vessel_or_crafts' , 'Vessel Details',HTML('{% include "applications/application_vessels.html" %}')))
        if 'crafts' in self.initial["workflow"]["hidden"]:    
            if self.initial["workflow"]["hidden"]['crafts'] == "False":
                if self.initial['vessel_or_craft_details'] == 2:
                    crispy_boxes.append(crispy_box('crafts_collapse', 'form_crafts' , 'Craft Details','type_of_crafts','number_of_crafts'))
                else: 
                    del self.fields['type_of_crafts']
                    del self.fields['number_of_crafts']
                    

        if check_fields_exist(self.fields,['purpose']) is True:
             crispy_boxes.append(crispy_box('proposal_details_collapse', 'form_proposal_details' , 'Proposal Details ','purpose','proposed_commence','proposed_end','max_participants','proposed_location','address','location_route_access','jetties',InlineRadios('jetty_dot_approval'),'drop_off_pick_up',InlineRadios('food'),InlineRadios('beverage'),InlineRadios('byo_alcohol'),'sullage_disposal','waste_disposal','refuel_location_method','berth_location','anchorage','operating_details'))

        if check_fields_exist(self.fields,['cert_survey','cert_public_liability_insurance','risk_mgmt_plan','safety_mgmt_procedures','brochures_itineries_adverts','other_relevant_documents']) is True:
             crispy_boxes.append(crispy_box('other_documents_collapse', 'form_other_documents' , 'Other Documents','cert_survey','cert_public_liability_insurance','risk_mgmt_plan','safety_mgmt_procedures','brochures_itineries_adverts','other_relevant_documents'))

        # Landowner Consent
        if check_fields_exist(self.fields,['land_owner_consent']) is True:
            crispy_boxes.append(crispy_box('land_owner_consent_collapse', 'form_land_owner_consent' , 'Landowner Consent',landownerconsentdesc,landownerconsentdesc2,'land_owner_consent',))

        # Deed
        if check_fields_exist(self.fields,['deed']) is True:
            crispy_boxes.append(crispy_box('deed_collapse', 'form_deed' , 'Deed',deeddesc,'deed'))

        self.helper.layout = Layout(crispy_boxes,
  #                FormActions(
  #                            Submit('lodge', 'Lodge', css_class='btn-lg'),
  #                              Submit('cancel', 'Cancel')
                              #                            )
        )
        if 'condactions' in self.initial['workflow']:
             if  self.initial['workflow']['condactions'] is not None:
                 for ca in self.initial['workflow']['condactions']: 
                     if 'steplabel' in self.initial['workflow']['condactions'][ca]: 
                 # for ro in self.initial['workflow']['condactions'][ca]['routeoptions']:
                  #    print ro
                          self.helper = crispy_button(self.helper,ca,self.initial['workflow']['condactions'][ca]['steplabel'])
 
  #           self.helper = crispy_button(self.helper,'step1','Step 1')
#             self.helper.add_input(Submit('prevstep', 'Prev Step', css_class='btn-lg'))
 #            self.helper.add_input(Submit('nextstep', 'Next Step', css_class='btn-lg'))

             else:
                 self.helper.add_input(Submit('save', 'Save', css_class='btn-lg'))
                 self.helper.add_input(Submit('cancel', 'Cancel'))
                             


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

    document_final = FileField(required=False, max_length=128, widget=ClearableFileInput)
    records = Field(required=False, widget=ClearableMultipleFileInput(attrs={'multiple':'multiple'}),  label='Attach more detailed descripton, maps or plans')
    land_owner_consent = Field(required=False, widget=ClearableMultipleFileInput(attrs={'multiple':'multiple'}),  label='Land Owner Consent')
    deed = FileField(required=False, max_length=128, widget=ClearableFileInput) 
    over_water = ChoiceField(choices=Application.APP_YESNO ,widget=RadioSelect(attrs={'class':'radio-inline'}))

    lot = CharField(required=False)
    reserve_number = CharField(required=False)
    town_suburb = CharField(required=False)
    nearest_road_intersection = CharField(required=False)
    local_government_authority = CharField(required=False)

    proposed_development_plans = FileField(required=False, max_length=128, widget=ClearableMultipleFileInput(attrs={'multiple':'multiple'}))
    supporting_info_demonstrate_compliance_trust_policies = FileField(required=False, max_length=128, widget=ClearableFileInput) 

    class Meta:
        model = Application
        fields = [
            'applicant','title', 'description', 'proposed_commence', 'proposed_end',
            'cost', 'project_no', 'related_permits', 'over_water', 'assessment_start_date','expire_date']

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

#       self.fields['records'].label = "Attach more detailed descripton, maps or plans"
      
        for fielditem in self.initial["fieldstatus"]:
            if fielditem in self.fields:
                del self.fields[fielditem]

        for fielditem in self.initial["fieldrequired"]:
            if fielditem in self.fields:
                self.fields[fielditem].required = True

        deeddesc = crispy_para("Print <a href=''>the deed</a>, sign it and attach it to this application")
        landownerconsentdesc = crispy_para("Print <A href=''>this document</A> and have it signed by each landowner (or body responsible for management)")
        landownerconsentdesc2 = crispy_para("Then attach all signed documents to this application.")
      
        crispy_boxes = crispy_empty_box()
        self.fields['applicant'].disabled = True

        if self.initial["may_change_application_applicant"] == "True":
            changeapplicantbutton = crispy_button_link('Add / Change Applicant',reverse('applicant_change', args=(self.initial['application_id'],)))
        else:
            changeapplicantbutton = HTML('')
        crispy_boxes.append(crispy_box('applicant_collapse','form_applicant','Applicant','applicant', changeapplicantbutton))


        if check_fields_exist(self.fields,['title']) is True:
            self.fields['title'].widget.attrs['placeholder'] = "Enter Title, ( Director of Corporate Services )"
            crispy_boxes.append(crispy_box('title_collapse', 'form_title' , 'Title','title'))

        # Location 
        if check_fields_exist(self.fields,['lot','reserve_number','town_suburb','nearest_road_intersection','local_government_authority','over_water']) is True:
            crispy_boxes.append(crispy_box('location_collapse', 'form_location' , 'Location','lot','reserve_number','town_suburb','nearest_road_intersection','local_government_authority',InlineRadios('over_water')) )

        if check_fields_exist(self.fields,['proposed_commence','proposed_end','cost','project_no','related_permits']) is True:
            crispy_boxes.append(crispy_box('other_information_collapse', 'form_other_information' , 'Other Information','proposed_commence','proposed_end','cost','project_no','related_permits'))
        if check_fields_exist(self.fields,['description','proposed_development_plans']) is True:
            crispy_boxes.append(crispy_box('description_collapse', 'form_description' , 'Description','description','proposed_development_plans','supporting_info_demonstrate_compliance_trust_policies'))

        # Landowner Consent
        if check_fields_exist(self.fields,['land_owner_consent']) is True:
            crispy_boxes.append(crispy_box('land_owner_consent_collapse', 'form_land_owner_consent' , 'Landowner Consent',landownerconsentdesc,landownerconsentdesc2,'land_owner_consent',))

        # Deed
        if check_fields_exist(self.fields,['deed']) is True:
            crispy_boxes.append(crispy_box('deed_collapse', 'form_deed' , 'Deed',deeddesc,'deed'))

        self.helper.layout = Layout(crispy_boxes,)

        #self.fields['other_supporting_docs'].label = "Attach supporting information to demonstrate compliance with relevant Trust policies"

class ApplicationChange(ApplicationFormMixin, ModelForm):
     proposed_development_plans = Field(required=False, widget=ClearableMultipleFileInput(attrs={'multiple':'multiple'}),  label='Supporting Documents')

     class Meta:
        model = Application
        fields = ['title','app_type','proposed_development_plans','proposed_development_description']

     def __init__(self, *args, **kwargs):
        super(ApplicationChange, self).__init__(*args, **kwargs)

        self.helper = BaseFormHelper()
        self.fields['proposed_development_description'].label = "Details of proposed ammendment"
        self.fields['app_type'].disabled = True
        self.fields['title'].disabled = True
        self.helper.form_id = 'id_form_change_ammend'
        self.helper.attrs = {'novalidate': ''}
        self.helper.add_input(Submit('createform', 'Create Form', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel'))



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
    document_draft_signed = FileField(required=False, max_length=128 , widget=ClearableFileInput)
    document_final = FileField(required=False, max_length=128, widget=ClearableFileInput)
    document_final_signed = FileField(required=False, max_length=128 , widget=ClearableFileInput)
    document_determination = FileField(required=False, max_length=128, widget=ClearableFileInput)
    document_completion = FileField(required=False, max_length=128, widget=ClearableFileInput)
    river_lease_scan_of_application = FileField(required=False, max_length=128, widget=ClearableFileInput)
    deed = FileField(required=False, max_length=128, widget=ClearableFileInput)
    swan_river_trust_board_feedback = FileField(required=False, max_length=128, widget=ClearableFileInput)
    document_new_draft_v3 = FileField(required=False, max_length=128, widget=ClearableFileInput, label='Draft Version 3')
    document_memo = FileField(required=False, max_length=128, widget=ClearableFileInput, label='Memo')
    document_determination = FileField(required=False, max_length=128, widget=ClearableFileInput, label='Determination Report')
    document_briefing_note = FileField(required=False, max_length=128, widget=ClearableFileInput, label='Briefing Note')
    document_determination_approved = FileField(required=False, max_length=128, widget=ClearableFileInput, label='Determination Signed Approved')
    river_lease_require_river_lease = ChoiceField(choices=Application.APP_YESNO ,widget=RadioSelect(attrs={'class':'radio-inline'}))
    river_lease_reserve_licence = ChoiceField(choices=Application.APP_YESNO ,widget=RadioSelect(attrs={'class':'radio-inline'}))

    class Meta:
        model = Application
        fields = ['applicant','title', 'description','cost', 'river_lease_require_river_lease','river_lease_reserve_licence','river_lease_application_number','proposed_development_description','proposed_development_current_use_of_land','assessment_start_date']

    def __init__(self, *args, **kwargs):
        super(ApplicationPart5Form, self).__init__(*args, **kwargs)

        for fielditem in self.initial["fieldstatus"]:
            if fielditem in self.fields:
                del self.fields[fielditem]

        for fielditem in self.initial["fieldrequired"]:
            if fielditem in self.fields:
                self.fields[fielditem].required = True

        self.helper = BaseFormHelper()


        # Field helper Description text.
        fieldtext = crispy_para('Text Description') 
        attachpdf = crispy_para('Please attach application (PDF)')
        riverleasedesc = crispy_para("If you intend to apply for a lease in relation to this proposed develeopment, you will need to complete a seperate Form - Application for a River reserve lease - and lodge it concurrently with this application. Note "+'"'+" River reserve leases will not be granted for developments requiring approval under section 70 of the Act - to which the proposed lease relates - unless that approval has been granted. "+'"'+"")
        landownerconsentdesc = crispy_para("Print <A href=''>this document</A> and have it signed by each landowner (or body responsible for management)")
        landownerconsentdesc2 = crispy_para("Then attach all signed documents to this application.")
        deeddesc = crispy_para("Print <a href=''>the deed</a>, sign it and attach it to this application")


        # Field Groups & Collaspable Box Styling.

        # Create Empty Object to append to.
        crispy_boxes = crispy_empty_box()
#        changeapplicantbutton = crispy_button_link('Add / Change Applicant',reverse('applicant_change', args=(self.initial['application_id'],)))
#        crispy_boxes.append(crispy_box('applicant_collapse','form_applicant','Applicant','applicant', changeapplicantbutton))
        if self.initial["may_change_application_applicant"] == "True":
            changeapplicantbutton = crispy_button_link('Add / Change Applicant',reverse('applicant_change', args=(self.initial['application_id'],)))
        else:
            changeapplicantbutton = HTML('')
        crispy_boxes.append(crispy_box('applicant_collapse','form_applicant','Applicant','applicant', changeapplicantbutton))



        # Title Box
        if check_fields_exist(self.fields,['title']) is True:
             self.fields['title'].widget.attrs['placeholder'] = "Enter Title, ( Director of Corporate Services )"
             crispy_boxes.append(crispy_box('title_collapse', 'form_title' , 'Title','title'))

        # Certificate of Title Information
        if check_fields_exist(self.fields,['certificate_of_title_volume','folio','diagram_plan_deposit_number','location','reserve_number','street_number_and_name','town_suburb','lot','nearest_road_intersection']) is True:
             crispy_boxes.append(crispy_box('certificate_collapse', 'form_certificate' , 'Certificate of Title Information','certificate_of_title_volume','folio','diagram_plan_deposit_number','location','reserve_number','street_number_and_name','town_suburb','lot','nearest_road_intersection'))

        # River Reserve Lease (Swan and Cannning Management Act 2006 - section 29
        if check_fields_exist(self.fields,['river_lease_require_river_lease','river_lease_scan_of_application']) is True:
             crispy_boxes.append(crispy_box('riverleasesection29_collapse', 'form_riverleasesection29' , 'River Reserve Lease (Swan and Cannning Management Act 2006 - section 29',riverleasedesc,InlineRadios('river_lease_require_river_lease'),attachpdf,'river_lease_scan_of_application'))

        if check_fields_exist(self.fields,['river_lease_reserve_licence','river_lease_application_number']) is True:
        # River Reserve Lease (Swan and Cannning Management Act 2006 - section 32
             crispy_boxes.append(crispy_box('riverleasesection32_collapse', 'form_riverleasesection32' , 'River Reserve Lease (Swan and Cannning Management Act 2006 - section 32',InlineRadios('river_lease_reserve_licence'),'river_lease_application_number'))

        # Details of Proposed Developmen
        if check_fields_exist(self.fields,['cost','proposed_development_current_use_of_land','proposed_development_description','proposed_development_plans']) is True:
             crispy_boxes.append(crispy_box('proposed_development_collapse', 'form_proposed_development' , 'Details of Proposed Development','cost','proposed_development_current_use_of_land','proposed_development_description','proposed_development_plans'))

        # Landowner Consent
        if check_fields_exist(self.fields,['land_owner_consent']) is True:
            crispy_boxes.append(crispy_box('land_owner_consent_collapse', 'form_land_owner_consent' , 'Landowner Consent',landownerconsentdesc,landownerconsentdesc2,'land_owner_consent',))

        # Deed
        if check_fields_exist(self.fields,['deed']) is True:
            crispy_boxes.append(crispy_box('deed_collapse', 'form_deed' , 'Deed',deeddesc,'deed'))

        # Assessment Update Step
        if check_fields_exist(self.fields,['assessment_start_date']) is True:
            crispy_boxes.append(crispy_box('assessment_collapse', 'form_assessment' , 'Assessment','assessment_start_date','document_draft'))

        if check_fields_exist(self.fields,['swan_river_trust_board_feedback']) is True:
            crispy_boxes.append(crispy_box('boardfeedback_collapse', 'form_boardfeedback' , 'Attach Swan River Trust Board Feedback','swan_river_trust_board_feedback'))

        if check_fields_exist(self.fields,['document_draft_signed']) is True:
            crispy_boxes.append(crispy_box('boardfeedback_collapse', 'form_boardfeedback' , 'Attach Signed Draft','document_draft_signed'))
        if check_fields_exist(self.fields,["document_new_draft_v3","document_memo"]) is True:
            crispy_boxes.append(crispy_box('draft_new_collapse','form_draft_new','Attach new Draft & Memo','document_new_draft_v3','document_memo'))

        if check_fields_exist(self.fields,["document_final_signed"]) is True:
            crispy_boxes.append(crispy_box('final_signed_collapse','form_final_signed','Attach Final Signed Report','document_final_signed'))

        if check_fields_exist(self.fields,["document_briefing_note","document_determination"]) is True:
            crispy_boxes.append(crispy_box('determination_collapse','form_determination','Attached Deterimination & Breifing Notes','document_briefing_note','document_determination'))
 
        if check_fields_exist(self.fields,['document_determination_approved']) is True:
            crispy_boxes.append(crispy_box('determination_approved_collapse','form_determination_approved','Determination Approved','document_determination_approved'))




        self.helper.layout = Layout(
                                crispy_boxes,

#                            Div(crispy_heading('certificate_collapse', 'form_certificate' , 'Certificate of Title Information'),
#                                
#                         Div(Div(
#                             Fieldset(
#                              '',
 #                               'description',
 #                               'cost',
 #                               'project_no',
 #                               'river_lease_reserve_licence',
 #                               'river_lease_application_number',
 #                               'proposed_development_description',
 #                               'proposed_development_current_use_of_land',
 #                               'assessment_start_date'
 #                             ), css_class='panel-body',
 #                             ), css_class="panel-collapse collapse in",id="certificate_collapse",
 #                            ), css_class='panel panel-default'  
 #                           ),

#
#                          Fieldset('Documents',
#                                   'land_owner_consent',
#                                   'document_new_draft',
#                                   'document_draft',
#                                   'document_draft_signed',
#                                   'document_final',
#                                   'document_final_signed',
#                                   'document_determination',
#                                   'document_completion',
#                                   'river_lease_scan_of_application',
#                                   'deed',
#                                   'swan_river_trust_board_feedback',
#                                   'document_new_draft_v3',
#                                   'document_memo',
#                                   'document_determination',
#                                   'document_briefing_note',
#                                   'document_determination_approved'
#                          )
                        )
 
        self.fields['applicant'].disabled = True

        self.helper.form_id = 'id_form_update_part_5'
        self.helper.form_class = 'form-horizontal form_fields'
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

        self.fields['applicant'].disabled = True;
        self.fields['applicant'].required = True;
        # Add labels and help text for fields
        self.fields['proposed_commence'].label = "Start date"
        self.fields['proposed_end'].label = "Expiry date"
        changeapplicantbutton = crispy_button_link('Add / Change Applicant',reverse('applicant_change', args=(self.initial['application_id'],)))
        crispy_boxes = crispy_empty_box()
        crispy_boxes.append(crispy_box('emergency_collapse', 'form_emergency' , 'Emergency Works','applicant', changeapplicantbutton,'organisation', 'proposed_commence', 'proposed_end'))

        self.helper.layout = Layout(crispy_boxes,)



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

class VesselDeleteForm(Form):
    """Form is to allow a referral to be reminded about the outstanding feedback
    """
    def __init__(self, *args, **kwargs):
        kwargs.pop('instance')  # Don't need this because this isn't a ModelForm.
        super(VesselDeleteForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper(self)
        self.helper.form_id = 'id_form_vessel_delete'
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
    records = FileField(required=False, max_length=128, widget=ClearableFileInput)

    class Meta:
        model = Application
        fields = ['id','details','records']
    def __init__(self, *args, **kwargs):
        super(ApplicationAssignNextAction, self).__init__(*args, **kwargs)

        self.helper = BaseFormHelper(self)

        self.helper.form_id = 'id_form_assigngroup_application'
        self.helper.attrs = {'novalidate': ''}

        self.helper.layout = Layout(
            HTML('<p>Application Next Action</p>'),
            'details','records',
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
        #fields = ['app_type', 'title', 'description', 'submit_date', 'assignee']
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
            #'app_type', 'title', 'description', 'submit_date', 'assignee',
            'assignee',
            FormActions(
                Submit('assign', 'Assign', css_class='btn-lg'),
                Submit('cancel', 'Cancel')
            )
        )

class AssignApplicantForm(ModelForm):
    """A form for assigning or change the applicant on application.
    """

    class Meta:
        model = Application
        #fields = ['app_type', 'title', 'description', 'submit_date', 'assignee']
        fields = ['applicant']

    def __init__(self, *args, **kwargs):
        super(AssignApplicantForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper(self)
        self.helper.form_id = 'id_form_assign_person_application'
        self.helper.attrs = {'novalidate': ''}
        # Limit the assignee queryset.
        
        applicant = self.initial['applicant']
        self.fields['applicant'].queryset = User.objects.filter(pk=applicant)
        self.fields['applicant'].required = True
        self.fields['applicant'].disabled = True
        # Define the form layout.
        self.helper.layout = Layout(
            HTML('<p>Assign this application for processing:</p>'),
            #'app_type', 'title', 'description', 'submit_date', 'assignee',
            'applicant',
            FormActions(
                Submit('assign', 'Change Applicant', css_class='btn-lg'),
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
        #fields = ['app_type', 'title', 'description', 'submit_date', 'assignee']
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
            #'app_type', 'title', 'description', 'submit_date', 'assignee',
            'assignee',
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
        #fields = ['app_type', 'title', 'description', 'submit_date', 'assignee']
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
            #'app_type', 'title', 'description', 'submit_date', 'assignee',
            'assignee',
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
        #fields = ['app_type', 'title', 'description', 'submit_date', 'assignee']
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
            #'app_type', 'title', 'description', 'submit_date', 'assignee',
            'assignee',
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

        crispy_boxes = crispy_empty_box()
        crispy_boxes.append(crispy_box('emergency_collapse', 'form_emergency' , 'Emergency Works','holder', 'abn', 'issue_date', 'proposed_commence', 'proposed_end', 'assessment'))
 

        # Define the form layout.
        self.helper.layout = Layout(crispy_boxes,
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
    registration = Field(required=False, widget=ClearableMultipleFileInput(attrs={'multiple':'multiple'}))
#MultiFileField(
 #       required=False, label='Registration & licence documents',
#        help_text='Choose multiple files to upload (if required). NOTE: this will replace any existing uploads.')

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

    records = Field(required=False, widget=ClearableMultipleFileInput(attrs={'multiple':'multiple'}))
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

    records = FileField(required=False, max_length=128 , widget=ClearableMultipleFileInput(attrs={'multiple':'multiple'}))

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


class RecordCreateForm(ModelForm):
    class Meta:
        model = Record
        fields = ['upload', 'name', 'category', 'metadata']

    def __init__(self, *args, **kwargs):
        super(RecordCreateForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper()
        self.helper.form_id = 'id_form_create_document'
        self.helper.attrs = {'novalidate': ''}
        self.helper.add_input(Submit('save', 'Save', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel'))


class EmailUserForm(ModelForm):

    class Meta:
        model = EmailUser
        fields = ['first_name', 'last_name', 'title', 'dob', 'phone_number', 'mobile_number', 'fax_number']

    def __init__(self, *args, **kwargs):
        super(EmailUserForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper(self)
        self.helper.form_id = 'id_form_emailuser_account_update'
        self.helper.attrs = {'novalidate': ''}
        # Define the form layout.
        self.helper.layout = Layout(
            'first_name', 'last_name', 'title', 'dob', 'phone_number', 'mobile_number', 'fax_number',
            FormActions(
                Submit('save', 'Save', css_class='btn-lg'),
                Submit('cancel', 'Cancel')
            )
        )


class AddressForm(ModelForm):

    class Meta:
        model = Address
        fields = ['line1', 'line2', 'line3', 'locality', 'state', 'country', 'postcode']

    def __init__(self, *args, **kwargs):
        super(AddressForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper(self)
        self.helper.form_id = 'id_form_address'
        self.helper.attrs = {'novalidate': ''}
        self.helper.add_input(Submit('save', 'Save', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel'))


class OrganisationForm(ModelForm):

    class Meta:
        model = Organisation
        fields = ['name', 'abn']

    def __init__(self, *args, **kwargs):
        super(OrganisationForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = 'Company name'
        #self.fields['identification'].label = 'Certificate of incorporation'
        #self.fields['identification'].help_text = 'Electronic copy of current certificate (e.g. image/PDF)'
        self.helper = BaseFormHelper(self)
        self.helper.form_id = 'id_form_organisation'
        self.helper.attrs = {'novalidate': ''}
        self.helper.add_input(Submit('save', 'Save', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel'))


class DelegateAccessForm(Form):

    def __init__(self, *args, **kwargs):
        super(DelegateAccessForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper(self)
        self.helper.add_input(Submit('confirm', 'Confirm', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel'))


class UnlinkDelegateForm(Form):

    def __init__(self, *args, **kwargs):
        super(UnlinkDelegateForm, self).__init__(*args, **kwargs)
        self.helper = BaseFormHelper(self)
        self.helper.add_input(Submit('unlink', 'Unlink user', css_class='btn-lg btn-danger'))
        self.helper.add_input(Submit('cancel', 'Cancel'))
