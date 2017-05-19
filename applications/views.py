from __future__ import unicode_literals
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from extra_views import ModelFormSetView
import pdfkit
from accounts.utils import get_query
from actions.models import Action
from applications import forms as apps_forms
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from .models import Application, Referral, Condition, Compliance, Vessel, Location, Document, PublicationNewspaper, PublicationWebsite, PublicationFeedback, Communication
from django.utils.safestring import SafeText
from datetime import datetime, date
from applications.workflow import Flow 
from django.db.models import Q
from applications.views_sub import Application_Part5, Application_Emergency, Application_Permit, Application_Licence, Referrals_Next_Action_Check 
from applications.email import sendHtmlEmail,emailGroup,emailApplicationReferrals
from applications.validationchecks import Attachment_Extension_Check

class HomePage(LoginRequiredMixin, TemplateView):
    # TODO: rename this view to something like UserDashboard.
    template_name = 'applications/home_page.html'

    def get_context_data(self, **kwargs):
        context = super(HomePage, self).get_context_data(**kwargs)
        if Application.objects.filter(assignee=self.request.user).exclude(state__in=[Application.APP_STATE_CHOICES.issued, Application.APP_STATE_CHOICES.declined]).exists():
            applications_wip = Application.objects.filter(
                assignee=self.request.user).exclude(state__in=[Application.APP_STATE_CHOICES.issued, Application.APP_STATE_CHOICES.declined])
            context['applications_wip'] = self.create_applist(applications_wip)
			#context['applications_wip']
        if Application.objects.filter(assignee=self.request.user).exclude(state__in=[Application.APP_STATE_CHOICES.issued, Application.APP_STATE_CHOICES.declined]).exists():
            #            userGroups = self.request.user.groups.all() 
            userGroups = []
            for g in self.request.user.groups.all():
                userGroups.append(g.name)
            applications_groups = Application.objects.filter(group__name__in=userGroups).exclude(state__in=[Application.APP_STATE_CHOICES.issued, Application.APP_STATE_CHOICES.declined])
            context['applications_groups'] = self.create_applist(applications_groups)

        if Application.objects.filter(applicant=self.request.user).exists():
            applications_submitted = Application.objects.filter(
                    applicant=self.request.user).exclude(assignee=self.request.user)
            context['applications_submitted'] = self.create_applist(applications_submitted)
        if Referral.objects.filter(referee=self.request.user).exists():
            context['referrals'] = Referral.objects.filter(
                referee=self.request.user, status=Referral.REFERRAL_STATUS_CHOICES.referred)

        # TODO: any restrictions on who can create new applications?
        context['may_create'] = True
        # Processor users only: show unassigned applications.
        processor = Group.objects.get(name='Processor')
        if processor in self.request.user.groups.all() or self.request.user.is_superuser:
            if Application.objects.filter(assignee__isnull=True, state=Application.APP_STATE_CHOICES.with_admin).exists():
                applications_unassigned = Application.objects.filter(
                    assignee__isnull=True, state=Application.APP_STATE_CHOICES.with_admin)
                context['applications_unassigned'] = self.create_applist(applications_unassigned)
            # Rule: admin officers may self-assign applications.
            context['may_assign_processor'] = True
        return context

    def create_applist(self,applications):
        usergroups = self.request.user.groups.all()
        app_list = []
        for app in applications:
            row = {}
            row['may_assign_to_person'] = 'False'
            row['app'] = app
            if app.group in usergroups:
               if app.group is not None:
                    row['may_assign_to_person'] = 'True'
            app_list.append(row)
        return app_list





class ApplicationList(ListView):
    model = Application

    def get_queryset(self):
        qs = super(ApplicationList, self).get_queryset()

        # Did we pass in a search string? If so, filter the queryset and return
        # it.
        if 'q' in self.request.GET and self.request.GET['q']:
            query_str = self.request.GET['q']
            # Replace single-quotes with double-quotes
            query_str = query_str.replace("'", r'"')
            # Filter by pk, title, applicant__email, organisation__name,
            # assignee__email
            query = get_query(
                query_str, ['pk', 'title', 'applicant__email', 'organisation__name', 'assignee__email'])
            qs = qs.filter(query).distinct()
        return qs

    def get_context_data(self, **kwargs):
        context = super(ApplicationList, self).get_context_data(**kwargs)
        if 'q' in self.request.GET and self.request.GET['q']:
            query_str = self.request.GET['q']
            applications = Application.objects.filter(Q(pk__contains=query_str) | Q(title__icontains=query_str) | Q(applicant__email__icontains=query_str)| Q(organisation__name__icontains=query_str)| Q(assignee__email__icontains=query_str))
        else: 
            applications = Application.objects.all()

        usergroups = self.request.user.groups.all()
        context['app_list'] = [] 
        for app in applications:
            row = {}
            row['may_assign_to_person'] = 'False'
            row['app'] = app
            if app.group is not None:
                if app.group in usergroups:
                    row['may_assign_to_person'] = 'True'
            context['app_list'].append(row)
            
        # TODO: any restrictions on who can create new applications?
        context['may_create'] = True
        processor = Group.objects.get(name='Processor')
        # Rule: admin officers may self-assign applications.
        if processor in self.request.user.groups.all() or self.request.user.is_superuser:
            context['may_assign_processor'] = True

        return context


class ApplicationCreate(LoginRequiredMixin, CreateView):
    form_class = apps_forms.ApplicationCreateForm
    template_name = 'applications/application_form.html'

    def get_context_data(self, **kwargs):
        context = super(ApplicationCreate, self).get_context_data(**kwargs)
        context['page_heading'] = 'Create new application'
        return context

    def get_form_kwargs(self):
        kwargs = super(ApplicationCreate, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):
            return HttpResponseRedirect(reverse('home_page'))
        return super(ApplicationCreate, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        """Override form_valid to set the assignee as the object creator.
        """
        self.object = form.save(commit=False)
        # If this is not an Emergency Works set the applicant as current user
        if not (self.object.app_type == Application.APP_TYPE_CHOICES.emergency):
            self.object.applicant = self.request.user
        self.object.assignee = self.request.user
        self.object.submitted_by = self.request.user
        self.object.assignee = self.request.user
        self.object.submit_date = date.today()
        self.object.state = self.object.APP_STATE_CHOICES.new
        self.object.save()
        success_url = reverse('application_update', args=(self.object.pk,))
        return HttpResponseRedirect(success_url)


class ApplicationDetail(DetailView):
    model = Application

    def get_context_data(self, **kwargs):
        context = super(ApplicationDetail, self).get_context_data(**kwargs)
        app = self.get_object()
        context['may_update'] = "False"
#        print app.app_type
#        print Application.APP_TYPE_CHOICES[app.app_type]
#        print dict(Application.APP_TYPE_CHOICES).get('3')
        # May Assign to Person,  Business rules are restricted to the people in the group who can reassign amoung each other only within the same group.
#        usergroups = self.request.user.groups.all()
        
#        if app.routeid > 1:
#            context['may_assign_to_person'] = 'True'
#        else: 
#        context['may_assign_to_person'] = 'False'

        #if app.group is not None:
        emailcontext = {'user':'Jason'}

        #sendHtmlEmail(['jason.moore@dpaw.wa.gov.au'],'HTML TEST EMAIL',emailcontext,'email.html' ,None,None,None)
        #emailGroup('HTML TEST EMAIL',emailcontext,'email.html' ,None,None,None,'Processor')

        if app.assignee is not None:
            context['application_assignee_id'] = app.assignee.id

        context['may_assign_to_person'] = 'False'
        usergroups = self.request.user.groups.all()
        #print app.group
        if app.group in usergroups:
            if app.routeid > 1:
                context['may_assign_to_person'] = 'True'
        
        if app.app_type == app.APP_TYPE_CHOICES.part5:
            self.template_name = 'applications/application_details_part5_new_application.html'
            part5 = Application_Part5()
            context = part5.get(app,self,context)
        elif app.app_type == app.APP_TYPE_CHOICES.emergency:
            self.template_name = 'applications/application_detail_emergency.html'
            emergency = Application_Emergency()
            context = emergency.get(app,self,context)
   
        elif app.app_type == app.APP_TYPE_CHOICES.permit:
            permit = Application_Permit()
            context = permit.get(app,self,context)
        elif app.app_type == app.APP_TYPE_CHOICES.licence:
            licence = Application_Licence()
            context = licence.get(app,self,context)

        # context = flow.getAllGroupAccess(request,context,app.routeid,workflowtype)
        # may_update has extra business rules
        if app.routeid > 1:
            if app.assignee is None:
                context['may_update'] = "False"
                del context['workflow_actions']	
                context['workflow_actions'] = []
            if context['may_update'] == "True":
                if app.assignee != self.request.user:
                    context['may_update'] = "False"
                    del context['workflow_actions']
                    context['workflow_actions'] = []
            if app.assignee != self.request.user:
                del context['workflow_actions']
                context['workflow_actions'] = []

        #        print context['may_assign_to_person']
        #print context['may_assign_to_person']
#        print context['may_update']
#        print 'sfasdas'
#        print app.app_type
        #elif app.app_type == app.APP_TYPE_CHOICES.emergencyold:
        #    self.template_name = 'applications/application_detail_emergency.html'
        #    
        #    if app.organisation:
        #        context['address'] = app.organisation.postal_address
        #    elif app.applicant:
        #        context['address'] = app.applicant.emailuserprofile.postal_address

#        processor = Group.objects.get(name='Processor')
#        assessor = Group.objects.get(name='Assessor')
#        approver = Group.objects.get(name='Approver')
#        referee = Group.objects.get(name='Referee')
#        emergency = Group.objects.get(name='Emergency')
    

#        if app.state in [app.APP_STATE_CHOICES.new, app.APP_STATE_CHOICES.draft]:
            # Rule: if the application status is 'draft', it can be updated.
            # Rule: if the application status is 'draft', it can be lodged.
            # Rule: if the application is an Emergency Works and status is 'draft'
            #   conditions can be added
#            if app.app_type == app.APP_TYPE_CHOICES.emergency:
#                if app.assignee == self.request.user:
#                    context['may_update'] = True
#                    context['may_issue'] = True
#                    context['may_create_condition'] = True
#                    context['may_update_condition'] = True
#                    context['may_assign_emergency'] = True
#                elif emergency in self.request.user.groups.all() or self.request.user.is_superuser: 
#                    context['may_assign_emergency'] = True
#            elif app.applicant == self.request.user or self.request.user.is_superuser:
#                context['may_update'] = True
#                context['may_lodge'] = True
#        if processor in self.request.user.groups.all() or self.request.user.is_superuser:
#            # Rule: if the application status is 'with admin', it can be sent
#            # back to the customer.
#            if app.state == app.APP_STATE_CHOICES.with_admin:
#                context['may_assign_customer'] = True
            # Rule: if the application status is 'with admin' or 'with referee', it can
            # be referred, have conditions added, and referrals can be
            # recalled/resent.
#            if app.state in [app.APP_STATE_CHOICES.with_admin, app.APP_STATE_CHOICES.with_referee]:
#                context['may_refer'] = True
#                context['may_create_condition'] = True
#                context['may_recall_resend'] = True
#                context['may_assign_processor'] = True
#                # Rule: if there are no "outstanding" referrals, it can be
#                # assigned to an assessor.
#                if not Referral.objects.filter(application=app, status=Referral.REFERRAL_STATUS_CHOICES.referred).exists():
#                    context['may_assign_assessor'] = True
#        if assessor in self.request.user.groups.all() or self.request.user.is_superuser:
#            # Rule: if the application status is 'with assessor', it can have conditions added
#            # or updated, and can be sent for approval.
#            if app.state == app.APP_STATE_CHOICES.with_assessor:
#                context['may_create_condition'] = True
#                context['may_update_condition'] = True
#                context['may_accept_condition'] = True
#                context['may_submit_approval'] = True
##        if approver in self.request.user.groups.all() or self.request.user.is_superuser:
#            # Rule: if the application status is 'with manager', it can be issued or
#            # assigned back to an assessor.
#            if app.state == app.APP_STATE_CHOICES.with_manager:
#                context['may_assign_assessor'] = True
#                context['may_issue'] = True
##        if referee in self.request.user.groups.all():
#            # Rule: if the application has a current referral to the request
#            # user, they can create and update conditions.
#            if Referral.objects.filter(application=app, status=Referral.REFERRAL_STATUS_CHOICES.referred).exists():
#               context['may_create_condition'] = True
#                context['may_update_condition'] = True
#        if app.state == app.APP_STATE_CHOICES.issued:
#            context['may_generate_pdf'] = True
#        if app.state == app.APP_STATE_CHOICES.issued and app.condition_set.exists():
#            # Rule: only the delegate of the organisation (or submitter) can
#            # request compliance.
#            if app.organisation:
#                if self.request.user.emailuserprofile in app.organisation.delegates.all():
#                    context['may_request_compliance'] = True
#            elif self.request.user == app.applicant:
#                context['may_request_compliance'] = True
        return context


class ApplicationDetailPDF(ApplicationDetail):
    """This view is a proof of concept for synchronous, server-side PDF generation.
    Depending on performance and resource constraints, this might need to be
    refactored to use an asynchronous task.
    """
    template_name = 'applications/application_detail_pdf.html'

    def get(self, request, *args, **kwargs):
        response = super(ApplicationDetailPDF, self).get(request)
        options = {
            'page-size': 'A4',
            'encoding': 'UTF-8',
        }
        # Generate the PDF as a string, then use that as the response body.
        output = pdfkit.from_string(
            response.rendered_content, False, options=options)
        # TODO: store the generated PDF as a Document object.
        response = HttpResponse(output, content_type='application/pdf')
        obj = self.get_object()
        response['Content-Disposition'] = 'attachment; filename=application_{}.pdf'.format(
            obj.pk)
        return response


class ApplicationActions(DetailView):
    model = Application
    template_name = 'applications/application_actions.html'

    def get_context_data(self, **kwargs):
        context = super(ApplicationActions, self).get_context_data(**kwargs)
        app = self.get_object()
        # TODO: define a GenericRelation field on the Application model.
        context['actions'] = Action.objects.filter(
            content_type=ContentType.objects.get_for_model(app), object_id=app.pk).order_by('-timestamp')
        return context


class ApplicationUpdate(LoginRequiredMixin, UpdateView):
    """A view for updating a draft (non-lodged) application.
    """
    model = Application

    def get(self, request, *args, **kwargs):
        # TODO: business logic to check the application may be changed.
        app = self.get_object()

        # Rule: if the application status is 'draft', it can be updated.
        context = {}
        if app.assignee: 
            context['application_assignee_id'] = app.assignee.id
        else: 
            context['application_assignee_id'] = None
#        if app.app_type == app.APP_TYPE_CHOICES.part5:
        if app.routeid is None:
            app.routeid = 1

  #      processor = Group.objects.get(name='Processor')
  #          assessor = Group.objects.get(name='Assessor')
  #          approver = Group.objects.get(name='Approver')
  #          referee = Group.objects.get(name='Referee')

        flow = Flow()
        workflowtype = flow.getWorkFlowTypeFromApp(app)
        flow.get(workflowtype)
        context = flow.getAccessRights(request,context,app.routeid,workflowtype)

        if app.routeid > 1:
            if app.assignee is None:
                context['may_update'] = "False"
       
            if context['may_update'] == "True":
                if app.assignee != self.request.user: 
                    context['may_update'] = "False"

        if context['may_update'] != "True":
            messages.error(self.request, 'This application cannot be updated!')
            return HttpResponseRedirect(app.get_absolute_url())
 #       else: 
 #           if app.state != app.APP_STATE_CHOICES.draft and app.state != app.APP_STATE_CHOICES.new:
 #               messages.error(self.request, 'This application cannot be updated!')
 #               return HttpResponseRedirect(app.get_absolute_url())

        return super(ApplicationUpdate, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ApplicationUpdate, self).get_context_data(**kwargs)
        context['page_heading'] = 'Update application details'
        app = self.get_object()
        #if app.app_type == app.APP_TYPE_CHOICES.part5:
        if app.routeid is None:
            app.routeid = 1
        request = self.request
        flow = Flow()
        workflowtype = flow.getWorkFlowTypeFromApp(app)
        flow.get(workflowtype)
        context = flow.getAccessRights(request,context,app.routeid,workflowtype)
        return context

    def get_form_class(self):
        if self.object.app_type == self.object.APP_TYPE_CHOICES.licence:
            return apps_forms.ApplicationLicencePermitForm
        elif self.object.app_type == self.object.APP_TYPE_CHOICES.permit:
            return apps_forms.ApplicationPermitForm
        elif self.object.app_type == self.object.APP_TYPE_CHOICES.part5:
            return apps_forms.ApplicationPart5Form
        elif self.object.app_type == self.object.APP_TYPE_CHOICES.emergency:
            return apps_forms.ApplicationEmergencyForm
        else:
           # Add default forms.py and use json workflow to filter and hide fields
           return apps_forms.ApplicationPart5Form 

    def get_initial(self):
        initial = super(ApplicationUpdate, self).get_initial()
        app = self.get_object()
#        if app.app_type == app.APP_TYPE_CHOICES.part5:
        if app.routeid is None:
            app.routeid = 1
        request = self.request
        flow = Flow()
        workflowtype = flow.getWorkFlowTypeFromApp(app)
        flow.get(workflowtype)
        flowcontent = {}
        flowcontent = flow.getFields(flowcontent,app.routeid,workflowtype)
        flowcontent['formcomponent'] = flow.getFormComponent(app.routeid,workflowtype)
        initial['fieldstatus'] = []
          
        if "fields" in flowcontent:
            initial['fieldstatus'] = flowcontent['fields']
        initial['fieldrequired'] = []
        flowcontent = flow.getRequired(flowcontent,app.routeid,workflowtype)
        if "formcomponent" in flowcontent:
            if "update" in flowcontent['formcomponent']:
                if "required" in flowcontent['formcomponent']['update']:
                    initial['fieldrequired'] = flowcontent['formcomponent']['update']['required']

#       flow = Flow()
        #workflow = flow.get()
#        print (workflow)
#       initial['land_owner_consent'] = app.land_owner_consent.all()
        multifilelist = []
        a1 = app.land_owner_consent.all()
        for b1 in a1:
            fileitem = {}
            fileitem['fileid'] = b1.id
            fileitem['path'] = b1.upload.name
            multifilelist.append(fileitem)

        initial['land_owner_consent'] = multifilelist

        a1 = app.proposed_development_plans.all()
        multifilelist = []
        for b1 in a1:
            fileitem = {}
            fileitem['fileid'] = b1.id
            fileitem['path'] = b1.upload.name
            multifilelist.append(fileitem)
        initial['proposed_development_plans'] = multifilelist

        #initial['publication_newspaper'] = PublicationNewspaper.objects.get(application_id=self.object.id)
        if app.document_draft:
            initial['document_draft'] = app.document_draft.upload
#        if app.proposed_development_plans:
#           initial['proposed_development_plans'] = app.proposed_development_plans.upload

        if app.deed:
            initial['deed'] = app.deed.upload

        if app.document_final:
            initial['document_final'] = app.document_final.upload
        if app.document_determination:
            initial['document_determination'] = app.document_determination.upload
        if app.document_completion:
            initial['document_completion'] = app.document_completion.upload
        # Document FK fields:
        if app.cert_survey:
            initial['cert_survey'] = app.cert_survey.upload
        if app.cert_public_liability_insurance:
            initial['cert_public_liability_insurance'] = app.cert_public_liability_insurance.upload
        if app.risk_mgmt_plan:
            initial['risk_mgmt_plan'] = app.risk_mgmt_plan.upload
        if app.safety_mgmt_procedures:
            initial['safety_mgmt_procedures'] = app.safety_mgmt_procedures.upload
        if app.deed:
            initial['deed'] = app.deed.upload
        if app.river_lease_scan_of_application:
            initial['river_lease_scan_of_application'] = app.river_lease_scan_of_application.upload

        try:
            LocObj = Location.objects.get(application_id=self.object.id)
            if LocObj:
                initial['certificate_of_title_volume'] = LocObj.title_volume
                initial['folio'] = LocObj.folio
                initial['diagram_plan_deposit_number'] = LocObj.dpd_number
                initial['location'] = LocObj.location
                initial['reserve_number'] = LocObj.reserve
                initial['street_number_and_name'] = LocObj.street_number_name
                initial['town_suburb'] = LocObj.suburb
                initial['lot'] = LocObj.lot
                initial['nearest_road_intersection'] = LocObj.intersection
        except ObjectDoesNotExist:
            donothing = ''

        return initial

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):
            app = Application.objects.get(id=kwargs['pk'])
            if app.state == app.APP_STATE_CHOICES.new:
                app.delete()
                return HttpResponseRedirect(reverse('application_list'))
            return HttpResponseRedirect(self.get_object().get_absolute_url())
        return super(ApplicationUpdate, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        """Override form_valid to set the state to draft is this is a new application.
        """
        forms_data = form.cleaned_data
        self.object = form.save(commit=False)
        # ToDO remove dupes of this line below..   doesn't need to be called
        # multiple times
        application = Application.objects.get(id=self.object.id)

        try:
            new_loc = Location.objects.get(application_id=self.object.id)
        except:
            new_loc = Location()
            new_loc.application_id = self.object.id

        # TODO: Potentially refactor to separate process_documents method
        # Document upload fields.

        land_owner_consent = application.land_owner_consent.all()
        for la_co in land_owner_consent:
            if 'land_owner_consent-clear_multifileid-'+str(la_co.id) in form.data:
                application.land_owner_consent.remove(la_co)

        proposed_development_plans = application.proposed_development_plans.all()
        for filelist in proposed_development_plans:
            if 'proposed_development_plans-clear_multifileid-' + str(filelist.id) in form.data:
                application.proposed_development_plans.remove(filelist)

        # if 'land_owner_consent-clear_multifileid' in forms_data:
        # Check for clear checkbox (remove files)
        # Clear' was checked.
        if 'cert_survey-clear' in form.data and self.object.cert_survey:
            self.object.cert_survey = None
        if 'river_lease_scan_of_application-clear' in form.data:
            self.object.river_lease_scan_of_application = None
        if 'cert_public_liability_insurance-clear' in form.data and self.object.cert_public_liability_insurance:
            self.object.cert_public_liability_insurance = None
        if 'risk_mgmt_plan-clear' in form.data and self.object.risk_mgmt_plan:
            self.object.risk_mgmt_plan = None
        if 'safety_mgmt_procedures-clear' in form.data and self.object.safety_mgmt_procedures:
            self.object.safety_mgmt_procedures = None
        if 'deed-clear' in form.data and self.object.deed:
            self.object.deed = None

        # Upload New Files
        if self.request.FILES.get('cert_survey'):  # Uploaded new file.
            if self.object.cert_survey:
                doc = self.object.cert_survey
            else:
                doc = Document()

            if Attachment_Extension_Check('single',forms_data['cert_public_liability_insurance'],None) is False:
                raise ValidationError('Certficate Survey contains and unallowed attachment extension.')

            doc.upload = forms_data['cert_survey']
            doc.name = forms_data['cert_survey'].name
            doc.save()
            self.object.cert_survey = doc
        if self.request.FILES.get('cert_public_liability_insurance'):
            if self.object.cert_public_liability_insurance:
                doc = self.object.cert_public_liability_insurance
            else:
                doc = Document()

            if Attachment_Extension_Check('single',forms_data['cert_public_liability_insurance'],None) is False:
                raise ValidationError('Certficate of Public Liability Insurance contains and unallowed attachment extension.')

            doc.upload = forms_data['cert_public_liability_insurance']
            doc.name = forms_data['cert_public_liability_insurance'].name
            doc.save()
            self.object.cert_public_liability_insurance = doc
        if self.request.FILES.get('risk_mgmt_plan'):
            if self.object.risk_mgmt_plan:
                doc = self.object.risk_mgmt_plan
            else:
                doc = Document()

            if Attachment_Extension_Check('single',forms_data['risk_mgmt_plan'],None) is False:
                raise ValidationError('Risk Management Plan contains and unallowed attachment extension.')

            doc.upload = forms_data['risk_mgmt_plan']
            doc.name = forms_data['risk_mgmt_plan'].name
            doc.save()
            self.object.risk_mgmt_plan = doc
        if self.request.FILES.get('safety_mgmt_procedures'):
            if self.object.safety_mgmt_procedures:
                doc = self.object.safety_mgmt_procedures
            else:
                doc = Document()
            if Attachment_Extension_Check('single',forms_data['safety_mgmt_procedures'],None) is False:
                raise ValidationError('Safety Procedures contains and unallowed attachment extension.')

            doc.upload = forms_data['safety_mgmt_procedures']
            doc.name = forms_data['safety_mgmt_procedures'].name
            doc.save()
            self.object.safety_mgmt_procedures = doc
        #if self.request.FILES.get('deed'):
        #    if self.object.deed:
        #        doc = self.object.deed
        #    else:
        #        doc = Document()
#
#            if Attachment_Extension_Check('single',forms_data['deed'],None) is False:
 #               raise ValidationError('Deed contains and unallowed attachment extension.')
#
 #           doc.upload = forms_data['deed']
  #          doc.name = forms_data['deed'].name
   #         doc.save()
    #        self.object.deed = doc
#        if self.request.FILES.get('river_lease_scan_of_application'):
#            if self.object.river_lease_scan_of_application:
#                doc = self.object.river_lease_scan_of_application
#            else:
#                doc = Document()
#            if Attachment_Extension_Check('single',forms_data['river_lease_scan_of_application'],None) is False:
#                raise ValidationError('River Lease contains an unallowed attachment extension.')
#
#            doc.upload = forms_data['river_lease_scan_of_application']
#            doc.name = forms_data['river_lease_scan_of_application'].name
#            doc.save()
#            self.object.river_lease_scan_of_application = doc
        if self.request.FILES.get('brochures_itineries_adverts'):
            # Remove existing documents.
            for d in self.object.brochures_itineries_adverts.all():
                self.object.brochures_itineries_adverts.remove(d)
            # Add new uploads.
            if Attachment_Extension_Check('multi',self.request.FILES.getlist('brochures_itineries_adverts'),None) is False:
                raise ValidationError('Brochures Itineries contains and unallowed attachment extension.')

            for f in self.request.FILES.getlist('brochures_itineries_adverts'):
                doc = Document()
                doc.upload = f
                doc.name = f.name
                doc.save()
                self.object.brochures_itineries_adverts.add(doc)
        if self.request.FILES.get('land_owner_consent'):
            # Remove existing documents.
            # for d in self.object.land_owner_consent.all():
            #    self.object.land_owner_consent.remove(d)
            # Add new uploads.
            if Attachment_Extension_Check('multi',self.request.FILES.getlist('land_owner_consent'),None) is False:
                raise ValidationError('Land Owner Consent contains and unallowed attachment extension.')

            for f in self.request.FILES.getlist('land_owner_consent'):
                doc = Document()
                doc.upload = f
       #         doc.name = f.name
                doc.save()
                self.object.land_owner_consent.add(doc)

        if self.request.FILES.get('proposed_development_plans'):
            if Attachment_Extension_Check('multi',self.request.FILES.getlist('proposed_development_plans'),None) is False:
                raise ValidationError('Proposed Development Plans contains and unallowed attachment extension.')

            for f in self.request.FILES.getlist('proposed_development_plans'):
                doc = Document()
                doc.upload = f
                doc.save()
                self.object.proposed_development_plans.add(doc)
        if self.request.POST.get('document_draft-clear'):
            application = Application.objects.get(id=self.object.id)
            #document = Document.objects.get(pk=application.document_draft.id)
            #document.delete() // protect error occurs
            self.object.document_draft = None

        if self.request.FILES.get('document_draft'):
            if Attachment_Extension_Check('single',forms_data['document_draft'],None) is False:
                raise ValidationError('Draft contains and unallowed attachment extension.')

            new_doc = Document()
            new_doc.upload = self.request.FILES['document_draft']
            new_doc.save()
            self.object.document_draft = new_doc

        if self.request.FILES.get('document_final'):
            if Attachment_Extension_Check('single',forms_data['document_final'],None) is False:
                raise ValidationError('Final contains and unallowed attachment extension.')

            new_doc = Document()
            new_doc.upload = self.request.FILES['document_final']
            new_doc.save()
            self.object.document_final = new_doc

        if self.request.FILES.get('deed'):
            if Attachment_Extension_Check('single',forms_data['deed'],None) is False:
                raise ValidationError('Deed contains and unallowed attachment extension.')

            new_doc = Document()
            new_doc.upload = self.request.FILES['deed']
            new_doc.save()
            self.object.deed = new_doc
        if self.request.FILES.get('river_lease_scan_of_application'):
            if Attachment_Extension_Check('single',forms_data['river_lease_scan_of_application'],None) is False:
                raise ValidationError('River Lease Scan of Application contains and unallowed attachment extension.')

            new_doc = Document()
            new_doc.upload = self.request.FILES['river_lease_scan_of_application']
            new_doc.save()
            self.object.river_lease_scan_of_application = new_doc
        if self.request.FILES.get('document_determination'):
            if Attachment_Extension_Check('single',forms_data['document_determination'],None) is False:
                raise ValidationError('Determination contains and unallowed attachment extension.')

            new_doc = Document()
            new_doc.upload = self.request.FILES['document_determination']
            new_doc.save()
            self.object.document_determination = new_doc

        if self.request.FILES.get('document_completion'):
            if Attachment_Extension_Check('single',forms_data['document_completion'],None) is False:
                raise ValidationError('Completion Docuemnt contains and unallowed attachment extension.')

            new_doc = Document()
            new_doc.upload = self.request.FILES['document_completion']
            new_doc.save()
            self.object.document_completion = new_doc

        #new_loc.title_volume = forms_data['certificate_of_title_volume']
        if 'certificate_of_title_volume' in forms_data:
            new_loc.title_volume = forms_data['certificate_of_title_volume']
        if 'folio' in forms_data:
            new_loc.folio = forms_data['folio']
        if 'diagram_plan_deposit_number' in forms_data:
            new_loc.dpd_number = forms_data['diagram_plan_deposit_number']
        if 'location' in forms_data:
            new_loc.location = forms_data['location']
        if 'reserve_number' in forms_data:
            new_loc.reserve = forms_data['reserve_number']
        if 'street_number_and_name' in forms_data:
            new_loc.street_number_name = forms_data['street_number_and_name']
        if 'town_suburb' in forms_data:
            new_loc.suburb = forms_data['town_suburb']
        if 'lot' in forms_data:
            new_loc.lot = forms_data['lot']
        if 'lot' in forms_data:
            new_loc.intersection = forms_data['nearest_road_intersection']

        if self.object.state == Application.APP_STATE_CHOICES.new:
            self.object.state = Application.APP_STATE_CHOICES.draft

        self.object.save()
        new_loc.save()
        if self.object.app_type == self.object.APP_TYPE_CHOICES.licence:
            form.save_m2m()
        return HttpResponseRedirect(self.get_success_url())


class ApplicationLodge(LoginRequiredMixin, UpdateView):
    model = Application
    form_class = apps_forms.ApplicationLodgeForm
    template_name = 'applications/application_lodge.html'

    def get_context_data(self, **kwargs):
        context = super(ApplicationLodge, self).get_context_data(**kwargs)
        app = self.get_object()

        if app.app_type == app.APP_TYPE_CHOICES.part5:
            self.template_name = 'applications/application_lodge_part5.html'
        if app.routeid is None:
           app.routeid = 1
        return context

    def get(self, request, *args, **kwargs):
        # TODO: business logic to check the application may be lodged.
        # Rule: application state must be 'draft'.
        app = self.get_object()
        flowcontext = {}
        flowcontext['application_assignee_id'] = app.assignee.id

        workflowtype = ''

        if app.routeid is None:
            app.routeid = 1
        request = self.request
        flow = Flow()
        workflowtype = flow.getWorkFlowTypeFromApp(app)
        flow.get(workflowtype)
        flowcontext = flow.getAccessRights(request,flowcontext,app.routeid,workflowtype)

        if flowcontext['may_lodge'] == "True": 
            route = flow.getNextRouteObj('lodge',app.routeid,workflowtype)
            flowcontext = flow.getRequired(flowcontext,app.routeid,workflowtype)
            if "required" in route:
                for fielditem in route["required"]:
                    if hasattr(app, fielditem):
                        if getattr(app, fielditem) is None:
                            messages.error(self.request, 'Required Field '+fielditem+' is empty,  Please Complete' )
                            return HttpResponseRedirect(app.get_absolute_url())
                        appattr = getattr(app, fielditem)
                        if  isinstance(appattr, unicode) or isinstance(appattr, str):
                            if len(appattr) == 0:
                                messages.error(self.request, 'Required Field '+fielditem+' is empty,  Please Complete' )
                                return HttpResponseRedirect(app.get_absolute_url())

            donothing = ""
        else:
            messages.error(self.request, 'This application cannot be lodged!')
            return HttpResponseRedirect(app.get_absolute_url())

  #      else:
   #         if app.state != app.APP_STATE_CHOICES.draft:
                # TODO: better/explicit error response.
    #            messages.error(self.request, 'This application cannot be lodged!')
     #           return HttpResponseRedirect(app.get_absolute_url())
        return super(ApplicationLodge, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):
            return HttpResponseRedirect(self.get_object().get_absolute_url())
        return super(ApplicationLodge, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        """Override form_valid to set the submit_date and status of the new application.
        """
        app = self.get_object()
        flowcontext = {}
        #if app.app_type == app.APP_TYPE_CHOICES.part5:
        if app.routeid is None:
            app.routeid = 1
        flow = Flow()
        workflowtype = flow.getWorkFlowTypeFromApp(app)
        flow.get(workflowtype)

        DefaultGroups = flow.groupList()
        nextroute = flow.getNextRoute('lodge',app.routeid,workflowtype)
        route = flow.getNextRouteObj('lodge',app.routeid,workflowtype)
        app.routeid = nextroute
        flowcontext = flow.getRequired(flowcontext,app.routeid,workflowtype)
        if "required" in route:
            for fielditem in route["required"]:
                if hasattr(app, fielditem):
                    if getattr(app, fielditem) is None:
                        messages.error(self.request, 'Required Field '+fielditem+' is empty,  Please Complete' )
                        return HttpResponseRedirect(app.get_absolute_url())
                    appattr = getattr(app, fielditem)
                    if  isinstance(appattr, unicode) or isinstance(appattr, str):
                       if len(appattr) == 0:
                           messages.error(self.request, 'Required Field '+fielditem+' is empty,  Please Complete' )
                           return HttpResponseRedirect(app.get_absolute_url())




        groupassignment = Group.objects.get(name=DefaultGroups['grouplink']['admin'])
        app.group = groupassignment


        app.state = app.APP_STATE_CHOICES.with_admin
        self.object.submit_date = date.today()
        app.assignee = None
        app.save()

        # Generate a 'lodge' action:
        action = Action(
            content_object=app, category=Action.ACTION_CATEGORY_CHOICES.lodge,
            user=self.request.user, action='Application lodgement')
        action.save()
        # Success message.
        msg = """Your {0} application has been successfully submitted. The application
        number is: <strong>{1}</strong>.<br>
        Please note that routine applications take approximately 4-6 weeks to process.<br>
        If any information is unclear or missing, Parks and Wildlife may return your
        application to you to amend or complete.<br>
        The assessment process includes a 21-day external referral period. During this time
        your application may be referred to external departments, local government
        agencies or other stakeholders. Following this period, an internal report will be
        produced by an officer for approval by the Manager, Rivers and Estuaries Division,
        to determine the outcome of your application.<br>
        You will be notified by email once your {0} application has been determined and/or
        further action is required.""".format(app.get_app_type_display(), app.pk)
        messages.success(self.request, msg)
        return HttpResponseRedirect(self.get_success_url())


class ApplicationRefer(LoginRequiredMixin, CreateView):
    """A view to create a Referral object on an Application (if allowed).
    """
    model = Referral
    form_class = apps_forms.ReferralForm

    def get(self, request, *args, **kwargs):
        # TODO: business logic to check the application may be referred.
        # Rule: application state must be 'with admin' or 'with referee'
        app = Application.objects.get(pk=self.kwargs['pk'])

        flowcontext = {}
      #  if app.app_type == app.APP_TYPE_CHOICES.part5:
        if app.routeid is None:
            app.routeid = 1

        flow = Flow()
        workflowtype = flow.getWorkFlowTypeFromApp(app)
        flow.get(workflowtype)
        flowcontext = flow.getAccessRights(request,flowcontext,app.routeid,workflowtype)

        if flowcontext['may_refer'] != "True":
                messages.error(self.request, 'Can not modify referrals on this application!')
                return HttpResponseRedirect(app.get_absolute_url())


#        else:
#            if app.state not in [app.APP_STATE_CHOICES.with_admin, app.APP_STATE_CHOICES.with_referee]:
#               # TODO: better/explicit error response.
#                messages.error(
#                    self.request, 'This application cannot be referred!')
#                return HttpResponseRedirect(app.get_absolute_url())
        return super(ApplicationRefer, self).get(request, *args, **kwargs)

    def get_success_url(self):
        """Override to redirect to the referral's parent application detail view.
        """
        messages.success(self.request, 'Referral has been added! ')
        return reverse('application_refer', args=(self.object.application.pk,))

    def get_context_data(self, **kwargs):
        context = super(ApplicationRefer, self).get_context_data(**kwargs)
        context['application'] = Application.objects.get(pk=self.kwargs['pk'])
        context['application_referrals'] = Referral.objects.filter(application=self.kwargs['pk'])
        app = Application.objects.get(pk=self.kwargs['pk'])
        flow = Flow()
        workflowtype = flow.getWorkFlowTypeFromApp(app)
        flow.get(workflowtype)
        context = flow.getAccessRights(self.request,context,app.routeid,workflowtype)
        return context

    def get_initial(self):
        initial = super(ApplicationRefer, self).get_initial()
        # TODO: set the default period value based on application type.
        initial['period'] = 21
        return initial

    def get_form_kwargs(self):
        kwargs = super(ApplicationRefer, self).get_form_kwargs()
        kwargs['application'] = Application.objects.get(pk=self.kwargs['pk'])
        return kwargs

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):
            app = Application.objects.get(pk=self.kwargs['pk'])
            return HttpResponseRedirect(app.get_absolute_url())
        return super(ApplicationRefer, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        app = Application.objects.get(pk=self.kwargs['pk'])

#        if app.app_type == app.APP_TYPE_CHOICES.part5:
#            flow = Flow()
#            flow.get('part5')
#            nextroute = flow.getNextRoute('referral',app.routeid,"part5")
#            app.routeid = nextroute

        self.object = form.save(commit=False)
        self.object.application = app
        self.object.sent_date = date.today()
        self.object.save()
        # Set the application status to 'with referee'.
#        app.state = app.APP_STATE_CHOICES.with_referee
#        app.save()
        # TODO: the process of sending the application to the referee.
        # Generate a 'refer' action on the application:
        action = Action(
            content_object=app, category=Action.ACTION_CATEGORY_CHOICES.refer,
            user=self.request.user, action='Referred for conditions/feedback to {}'.format(self.object.referee))
        action.save()
        return super(ApplicationRefer, self).form_valid(form)

class ApplicationAssignNextAction(LoginRequiredMixin, UpdateView):
    """A view to allow an application to be assigned to an internal user or back to the customer.
    The ``action`` kwarg is used to define the new state of the application.
    """

    model = Application

    def get(self, request, *args, **kwargs):
        app = self.get_object()

#        DefaultGroups = {}
#        DefaultGroups['admin'] = 'Processor'
#        DefaultGroups['assess'] = 'Assessor'
#        DefaultGroups['manager'] = 'Approver'
#        DefaultGroups['director'] = 'Director'
#        DefaultGroups['exec'] = 'Executive'
#        appt = "app_type1"
#        print hasattr(app, appt)
#        print getattr(app, appt)
#        print app.routeid 
        if app.assignee is None: 
            messages.error(self.request, 'Please Allocate an Assigned Person First')
            return HttpResponseRedirect(app.get_absolute_url())

        action = self.kwargs['action']
      
        flow = Flow()
        workflowtype = flow.getWorkFlowTypeFromApp(app)
        flow.get(workflowtype)
        DefaultGroups = flow.groupList()
        flowcontext = {}
        flowcontext = flow.getAccessRights(request,flowcontext,app.routeid,workflowtype)
        flowcontext = flow.getRequired(flowcontext,app.routeid,workflowtype)
        route = flow.getNextRouteObj(action,app.routeid,workflowtype)
        
        if action is "creator":
            if flowcontext['may_assign_to_creator'] != "True":
                messages.error(self.request, 'This application cannot be reassign, Unknown Error')
                return HttpResponseRedirect(app.get_absolute_url())
        else:
            # nextroute = flow.getNextRoute(action,app.routeid,"part5")
            assign_action = flow.checkAssignedAction(action,flowcontext)
            if assign_action != True:
                if action in DefaultGroups['grouplink']:
                    messages.error(self.request, 'This application cannot be reassign to '+ DefaultGroups['grouplink'][action])
                    return HttpResponseRedirect(app.get_absolute_url())
                else:
                    messages.error(self.request, 'This application cannot be reassign, Unknown Error') 
                    return HttpResponseRedirect(app.get_absolute_url())

        if action == 'referral':
            app_refs = Referral.objects.filter(application=app).count()
            if app_refs == 0:
                messages.error(self.request, 'Unable to complete action as you have no referrals! ')
                return HttpResponseRedirect(app.get_absolute_url())
        if "required" in route:
            for fielditem in route["required"]:
                if hasattr(app, fielditem):
                    if getattr(app, fielditem) is None:
                        messages.error(self.request, 'Required Field '+fielditem+' is empty,  Please Complete' )
                        return HttpResponseRedirect(app.get_absolute_url())
                    appattr = getattr(app, fielditem)
                    if  isinstance(appattr, unicode) or isinstance(appattr, str): 
                       if len(appattr) == 0:
                           messages.error(self.request, 'Required Field '+fielditem+' is empty,  Please Complete' )
                           return HttpResponseRedirect(app.get_absolute_url())

        return super(ApplicationAssignNextAction, self).get(request, *args, **kwargs)

    def get_form_class(self):
        return apps_forms.ApplicationAssignNextAction

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):
            return HttpResponseRedirect(self.get_object().get_absolute_url())
        return super(ApplicationAssignNextAction, self).post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('application_list')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        forms_data = form.cleaned_data
        app = self.get_object()
        action = self.kwargs['action']

        # Upload New Files
        doc = None
        if self.request.FILES.get('document'):  # Uploaded new file.
            doc = Document()
            doc.upload = forms_data['document']
            doc.name = forms_data['document'].name
            doc.save()
           
        flow = Flow()
        workflowtype = flow.getWorkFlowTypeFromApp(app)
        DefaultGroups = flow.groupList()
        flow.get(workflowtype)

        if action == "creator":
            groupassignment = None
            assignee = app.submitted_by
        elif action == 'referral':
            groupassignment = None
            assignee = None
        else:
            assignee = None
            groupassignment = Group.objects.get(name=DefaultGroups['grouplink'][action])

        route = flow.getNextRouteObj(action,app.routeid,workflowtype)
        if route is None:
            messages.error(self.request, 'Error In Assigning Next Route, No routes Found')
            return HttpResponseRedirect(app.get_absolute_url())
        if route["route"] is None:
            messages.error(self.request, 'Error In Assigning Next Route, No routes Found')
            return HttpResponseRedirect(app.get_absolute_url())

        self.object.routeid = route["route"]
        self.object.state = route["state"]
        self.object.group = groupassignment
        self.object.assignee = assignee
        self.object.save()
        
        comms =  Communication()
        comms.application = app
        comms.details = forms_data['details']
        comms.state = route["state"]
        comms.save()
        if doc:
            comms.documents.add(doc)

        emailcontext = {}
        emailcontext['app'] = self.object

        if action != "creator" and action != 'referral':
            emailcontext['groupname'] = DefaultGroups['grouplink'][action]
            emailcontext['application_name'] = Application.APP_TYPE_CHOICES[app.app_type]
            emailGroup('Application Assignment to Group '+DefaultGroups['grouplink'][action],emailcontext,'application-assigned-to-group.html' ,None,None,None,DefaultGroups['grouplink'][action])
        elif action == "creator": 
            emailcontext['application_name'] = Application.APP_TYPE_CHOICES[app.app_type]
            emailcontext['person'] = assignee
            sendHtmlEmail([assignee.email],emailcontext['application_name']+' application assigned to you ',emailcontext,'application-assigned-to-person.html',None,None,None)
        elif action == "referral":
            emailcontext['application_name'] = Application.APP_TYPE_CHOICES[app.app_type]
            emailApplicationReferrals(app.id,'Application for Feedback ',emailcontext,'application-assigned-to-referee.html' ,None,None,None)

        # Record an action on the application:
        action = Action(
        content_object=self.object, category=Action.ACTION_CATEGORY_CHOICES.action, user=self.request.user,
            action='Next Step Application Assigned to group ({}) with action title ({}) and route id ({}) '.format(groupassignment,route['title'],self.object.routeid))
        action.save()
        return HttpResponseRedirect(self.get_success_url())


class ApplicationAssignPerson(LoginRequiredMixin, UpdateView):
    """A view to allow an application to be assigned to an internal user or back to the customer.
    The ``action`` kwarg is used to define the new state of the application.
    """
    model = Application

    def get(self, request, *args, **kwargs):
        app = self.get_object()
        if app.group is None:
            messages.error(self.request, 'Unable to set Person Assignments as No Group Assignments Set!')
            return HttpResponseRedirect(app.get_absolute_url())
        return super(ApplicationAssignPerson, self).get(request, *args, **kwargs)

    def get_form_class(self):
        # Return the specified form class
        return apps_forms.AssignPersonForm

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):
            return HttpResponseRedirect(self.get_object().get_absolute_url())
        return super(ApplicationAssignPerson, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=True)
        app = self.object

        flow = Flow()
        workflowtype = flow.getWorkFlowTypeFromApp(app)
        DefaultGroups = flow.groupList()
        flow.get(workflowtype)
        emailcontext = {'person': app.assignee }
        emailcontext['application_name'] = Application.APP_TYPE_CHOICES[app.app_type]
        if self.request.user != app.assignee:
            sendHtmlEmail([app.assignee.email],emailcontext['application_name']+' application assigned to you ',emailcontext,'application-assigned-to-person.html',None,None,None)

        # Record an action on the application:
        action = Action(
            content_object=self.object, category=Action.ACTION_CATEGORY_CHOICES.assign, user=self.request.user,
            action='Assigned application to {} (status: {})'.format(self.object.assignee.get_full_name(), self.object.get_state_display()))
        action.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_initial(self):
        initial = super(ApplicationAssignPerson, self).get_initial()
        app = self.get_object()
        if app.routeid is None:
            app.routeid = 1
        initial['assigngroup'] = app.group
        return initial


class ApplicationAssign(LoginRequiredMixin, UpdateView):
    """A view to allow an application to be assigned to an internal user or back to the customer.
    The ``action`` kwarg is used to define the new state of the application.
    """
    model = Application

    def get(self, request, *args, **kwargs):
        app = self.get_object()
        if self.kwargs['action'] == 'customer':
            # Rule: application can go back to customer when only status is
            # 'with admin'.
            if app.state != app.APP_STATE_CHOICES.with_admin:
                messages.error(
                    self.request, 'This application cannot be returned to the customer!')
                return HttpResponseRedirect(app.get_absolute_url())
        if self.kwargs['action'] == 'assess':
            # Rule: application can be assessed when status is 'with admin',
            # 'with referee' or 'with manager'.
            if app.app_type == app.APP_TYPE_CHOICES.part5:
                flow = Flow()
                flow.get('part5')
                flowcontext = {}
                flowcontext = flow.getAccessRights(request,flowcontext,app.routeid,'part5')
                if flowcontext["may_assign_assessor"] != "True":
                    messages.error(self.request, 'This application cannot be assigned to an assessor!')
                    return HttpResponseRedirect(app.get_absolute_url())
            else:
                if app.state not in [app.APP_STATE_CHOICES.with_admin, app.APP_STATE_CHOICES.with_referee, app.APP_STATE_CHOICES.with_manager]:
                    messages.error(self.request, 'This application cannot be assigned to an assessor!')
                    return HttpResponseRedirect(app.get_absolute_url())
        # Rule: only the assignee (or a superuser) can assign for approval.
        if self.kwargs['action'] == 'approve':
            if app.app_type == app.APP_TYPE_CHOICES.part5:
                flow = Flow()
                flow.get('part5')
                flowcontext = {}
                flowcontext = flow.getAccessRights(request,flowcontext,app.routeid,'part5')
                
                if flowcontext["may_submit_approval"] != "True":
                    messages.error(self.request, 'This application cannot be assigned to an assessor!')
                    return HttpResponseRedirect(app.get_absolute_url())
            else:
                if app.state != app.APP_STATE_CHOICES.with_assessor:
                    messages.error(self.request, 'You are unable to assign this application for approval/issue!')
                    return HttpResponseRedirect(app.get_absolute_url())
                if app.assignee != request.user and not request.user.is_superuser:
                    messages.error(self.request, 'You are unable to assign this application for approval/issue!')
                    return HttpResponseRedirect(app.get_absolute_url())
        return super(ApplicationAssign, self).get(request, *args, **kwargs)

    def get_form_class(self):
        # Return the specified form class
        if self.kwargs['action'] == 'customer':
            return apps_forms.AssignCustomerForm
        elif self.kwargs['action'] == 'process':
            return apps_forms.AssignProcessorForm
        elif self.kwargs['action'] == 'assess':
            return apps_forms.AssignAssessorForm
        elif self.kwargs['action'] == 'approve':
            return apps_forms.AssignApproverForm
        elif self.kwargs['action'] == 'assign_emergency':
            return apps_forms.AssignEmergencyForm

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):
            return HttpResponseRedirect(self.get_object().get_absolute_url())
        return super(ApplicationAssign, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        app = self.object 
        if self.kwargs['action'] == 'customer':
            messages.success(self.request, 'Application {} has been assigned back to customer'.format(self.object.pk))
        else:
            messages.success(self.request, 'Application {} has been assigned to {}'.format(self.object.pk, self.object.assignee.get_full_name()))
        if self.kwargs['action'] == 'customer':
            # Assign the application back to the applicant and make it 'draft'
            # status.
            self.object.assignee = self.object.applicant
            self.object.state = self.object.APP_STATE_CHOICES.draft
            # TODO: email the feedback back to the customer.
        if self.kwargs['action'] == 'assess':
            if app.app_type == app.APP_TYPE_CHOICES.part5:
                flow = Flow()
                flow.get('part5')
                nextroute = flow.getNextRoute('assess',app.routeid,"part5")
                self.object.routeid = nextroute
            self.object.state = self.object.APP_STATE_CHOICES.with_assessor
        if self.kwargs['action'] == 'approve':
            if app.app_type == app.APP_TYPE_CHOICES.part5:
                flow = Flow()
                flow.get('part5')
                nextroute = flow.getNextRoute('manager',app.routeid,"part5")
                self.object.routeid = nextroute
            self.object.state = self.object.APP_STATE_CHOICES.with_manager
        if self.kwargs['action'] == 'process': 
            if app.app_type == app.APP_TYPE_CHOICES.part5:
                flow = Flow()
                flow.get('part5')
                nextroute = flow.getNextRoute('admin',app.routeid,"part5")
                self.object.routeid = nextroute

            self.object.state = self.object.APP_STATE_CHOICES.with_manager
        self.object.save()
        if self.kwargs['action'] == 'customer':
            # Record the feedback on the application:
            d = form.cleaned_data
            action = Action(
                content_object=self.object, category=Action.ACTION_CATEGORY_CHOICES.communicate, user=self.request.user,
                action='Feedback provided to applicant: {}'.format(d['feedback']))
            action.save()
        # Record an action on the application:
        action = Action(
            content_object=self.object, category=Action.ACTION_CATEGORY_CHOICES.assign, user=self.request.user,
            action='Assigned application to {} (status: {})'.format(self.object.assignee.get_full_name(), self.object.get_state_display()))
        action.save()
        return HttpResponseRedirect(self.get_success_url())

class ApplicationIssue(LoginRequiredMixin, UpdateView):
    """A view to allow a manager to issue an assessed application.
    """
    model = Application

    def get(self, request, *args, **kwargs):
        # Rule: only the assignee (or a superuser) can perform this action.
        app = self.get_object()
        if app.assignee == request.user or request.user.is_superuser:
            return super(ApplicationIssue, self).get(request, *args, **kwargs)
        messages.error(
            self.request, 'You are unable to issue this application!')
        return HttpResponseRedirect(app.get_absolute_url())

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):
            return HttpResponseRedirect(self.get_object().get_absolute_url())
        return super(ApplicationIssue, self).post(request, *args, **kwargs)

    def get_form_class(self):
        app = self.get_object()

        if app.app_type == app.APP_TYPE_CHOICES.emergency:
            return apps_forms.ApplicationEmergencyIssueForm
        else:
            return apps_forms.ApplicationIssueForm

    def get_initial(self):
        initial = super(ApplicationIssue, self).get_initial()
        app = self.get_object()

        if app.app_type == app.APP_TYPE_CHOICES.emergency:
            if app.organisation:
                initial['holder'] = app.organisation.name
                initial['abn'] = app.organisation.abn
            elif app.applicant:
                initial['holder'] = app.applicant.get_full_name()

        return initial

    def form_valid(self, form):
        self.object = form.save(commit=False)
        d = form.cleaned_data
        if d['assessment'] == 'issue':
            self.object.state = self.object.APP_STATE_CHOICES.issued
            self.object.assignee = None
            # Record an action on the application:
            action = Action(
                content_object=self.object, category=Action.ACTION_CATEGORY_CHOICES.issue,
                user=self.request.user, action='Application issued')
            action.save()
            if self.object.app_type == self.object.APP_TYPE_CHOICES.emergency:
                self.object.issue_date = date.today()

                msg = """<strong>The emergency works has been successfully issued.</strong><br />
                <br />
                <strong>Emergency Works:</strong> \t{0}<br />
                <strong>Date / Time:</strong> \t{1}<br />
                <br />
                <a href="{2}">{3}</a>
                <br />
                """
                if self.object.applicant:
                    msg = msg + """The Emergency Works has been emailed."""
                else:
                    msg = msg + """The Emergency Works needs to be printed and posted."""
                messages.success(self.request, msg.format(self.object.pk, self.object.issue_date, 
                        self.get_success_url() + "pdf", 'EmergencyWorks.pdf'))
            else:
                messages.success(
                    self.request, 'Application {} has been issued'.format(self.object.pk))
        elif d['assessment'] == 'decline':
            self.object.state = self.object.APP_STATE_CHOICES.declined
            self.object.assignee = None
            # Record an action on the application:
            action = Action(
                content_object=self.object, category=Action.ACTION_CATEGORY_CHOICES.decline,
                user=self.request.user, action='Application declined')
            action.save()
            messages.warning(
                self.request, 'Application {} has been declined'.format(self.object.pk))
        self.object.save()
        # TODO: logic around emailing/posting the application to the customer.
        return HttpResponseRedirect(self.get_success_url())


class ReferralComplete(LoginRequiredMixin, UpdateView):
    """A view to allow a referral to be marked as 'completed'.
    """
    model = Referral
    form_class = apps_forms.ReferralCompleteForm

    def get(self, request, *args, **kwargs):
        referral = self.get_object()
        # Rule: can't mark a referral completed more than once.
#        if referral.response_date:
        if referral.status != Referral.REFERRAL_STATUS_CHOICES.referred:
            messages.error(self.request, 'This referral is already completed!')
            return HttpResponseRedirect(referral.application.get_absolute_url())
        # Rule: only the referee (or a superuser) can mark a referral
        # "complete".
        if referral.referee == request.user or request.user.is_superuser:
            return super(ReferralComplete, self).get(request, *args, **kwargs)
        messages.error(
            self.request, 'You are unable to mark this referral as complete!')
        return HttpResponseRedirect(referral.application.get_absolute_url())

    def get_context_data(self, **kwargs):
        context = super(ReferralComplete, self).get_context_data(**kwargs)
        self.template_name = 'applications/referral_complete_form.html'
        context['application'] = self.get_object().application
        return context

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):
            return HttpResponseRedirect(self.get_object().application.get_absolute_url())
        return super(ReferralComplete, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.response_date = date.today()
        self.object.status = Referral.REFERRAL_STATUS_CHOICES.responded
        self.object.save()
        app = self.object.application
        # Record an action on the referral's application:
        action = Action(
            content_object=app, user=self.request.user,
            action='Referral to {} marked as completed'.format(self.object.referee))
        action.save()
        # If there are no further outstanding referrals, then set the
        # application status to "with admin".
#        if not Referral.objects.filter(
#                application=app, status=Referral.REFERRAL_STATUS_CHOICES.referred).exists():
#            app.state = Application.APP_STATE_CHOICES.with_admin
#            app.save()
        refnextaction = Referrals_Next_Action_Check()
        refactionresp = refnextaction.get(app)
        if refactionresp == True:
            refnextaction.go_next_action(app)
            # Record an action.
            action = Action(
                content_object=app,
                action='No outstanding referrals, application status set to "{}"'.format(app.get_state_display()))
            action.save()

        return HttpResponseRedirect(app.get_absolute_url())


class ReferralRecall(LoginRequiredMixin, UpdateView):
    model = Referral
    form_class = apps_forms.ReferralRecallForm
    template_name = 'applications/referral_recall.html'

    def get(self, request, *args, **kwargs):
        referral = self.get_object()
        # Rule: can't recall a referral that is any other status than
        # 'referred'.
        if referral.status != Referral.REFERRAL_STATUS_CHOICES.referred:
            messages.error(self.request, 'This referral is already completed!')
            return HttpResponseRedirect(referral.application.get_absolute_url())
        return super(ReferralRecall, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ReferralRecall, self).get_context_data(**kwargs)
        context['referral'] = self.get_object()
        return context

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):
            return HttpResponseRedirect(self.get_object().application.get_absolute_url())
        return super(ReferralRecall, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        ref = self.get_object()
        ref.status = Referral.REFERRAL_STATUS_CHOICES.recalled
        ref.save()
        # Record an action on the referral's application:
        action = Action(
            content_object=ref.application, user=self.request.user,
            action='Referral to {} recalled'.format(ref.referee))
        action.save()

        #  check to see if there is any uncompleted/unrecalled referrals
        #  If no more pending referrals than more to next step in workflow
        refnextaction = Referrals_Next_Action_Check()
        refactionresp = refnextaction.get(ref.application)

        if refactionresp == True:
            refnextaction.go_next_action(ref.application)
            action = Action(
              content_object=ref.application, user=self.request.user,
              action='All Referrals Completed, Progress to next Workflow Action {} '.format(ref.referee))
            action.save()
            
        return HttpResponseRedirect(ref.application.get_absolute_url())

class ReferralResend(LoginRequiredMixin, UpdateView):
    model = Referral
    form_class = apps_forms.ReferralResendForm
    template_name = 'applications/referral_resend.html'

    def get(self, request, *args, **kwargs):
        referral = self.get_object()
        # Rule: can't recall a referral that is any other status than
        # 'referred'.
        if referral.status != Referral.REFERRAL_STATUS_CHOICES.recalled & referral.status != Referral.REFERRAL_STATUS_CHOICES.responded:
            messages.error(self.request, 'This referral is already completed!'+ str(referral.status)+str(Referral.REFERRAL_STATUS_CHOICES.responded))
            return HttpResponseRedirect(referral.application.get_absolute_url())
        return super(ReferralResend, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ReferralResend, self).get_context_data(**kwargs)
        context['referral'] = self.get_object()
        return context

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):
            return HttpResponseRedirect(self.get_object().application.get_absolute_url())
        return super(ReferralResend, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        ref = self.get_object()
        ref.status = Referral.REFERRAL_STATUS_CHOICES.referred
        ref.save()
        # Record an action on the referral's application:
        action = Action(
            content_object=ref.application, user=self.request.user,
            action='Referral to {} resend '.format(ref.referee))
        action.save()

        return HttpResponseRedirect(ref.application.get_absolute_url())

class ReferralRemind(LoginRequiredMixin, UpdateView):
    model = Referral
    form_class = apps_forms.ReferralRemindForm
    template_name = 'applications/referral_remind.html'

    def get(self, request, *args, **kwargs):
        referral = self.get_object()
      
        if referral.status != Referral.REFERRAL_STATUS_CHOICES.referred:
            messages.error(self.request, 'This referral is already completed!')
            return HttpResponseRedirect(referral.application.get_absolute_url())
        return super(ReferralRemind, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ReferralRemind, self).get_context_data(**kwargs)
        context['referral'] = self.get_object()
        return context

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):
            return HttpResponseRedirect(self.get_object().application.get_absolute_url())
        return super(ReferralRemind, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        ref = self.get_object()
        emailcontext = {}
        emailcontext['person'] = ref.referee
        emailcontext['application_id'] = ref.application.id
        emailcontext['application_name'] = Application.APP_TYPE_CHOICES[ref.application.app_type] 

        sendHtmlEmail([ref.referee.email],'Application for Feedback Reminder',emailcontext,'application-assigned-to-referee.html',None,None,None)

        action = Action(
            content_object=ref.application, user=self.request.user,
            action='Referral to {} reminded'.format(ref.referee))
        action.save()
        return HttpResponseRedirect(ref.application.get_absolute_url())

class ReferralDelete(LoginRequiredMixin, UpdateView):
    model = Referral
    form_class = apps_forms.ReferralDeleteForm
    template_name = 'applications/referral_delete.html'

    def get(self, request, *args, **kwargs):
        referral = self.get_object()
        if referral.status != Referral.REFERRAL_STATUS_CHOICES.referred:
            messages.error(self.request, 'This referral is already completed!')
            return HttpResponseRedirect(referral.application.get_absolute_url())
        return super(ReferralDelete, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ReferralDelete, self).get_context_data(**kwargs)
        context['referral'] = self.get_object()
        return context
    def get_success_url(self,application_id):
        return reverse('application_refer', args=(application_id,))

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):
            return HttpResponseRedirect(self.get_object().application.get_absolute_url())
        return super(ReferralDelete, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        ref = self.get_object()
        application_id = ref.application.id
        ref.delete()
        # Record an action on the referral's application:
        action = Action(
            content_object=ref.application, user=self.request.user,
            action='Referral to {} delete'.format(ref.referee))
        action.save()
        return HttpResponseRedirect(self.get_success_url(application_id))



class ComplianceList(ListView):
    model = Compliance

    def get_queryset(self):
        qs = super(ComplianceList, self).get_queryset()
        # Did we pass in a search string? If so, filter the queryset and return
        # it.
        if 'q' in self.request.GET and self.request.GET['q']:
            query_str = self.request.GET['q']
            # Replace single-quotes with double-quotes
            query_str = query_str.replace("'", r'"')
            # Filter by applicant__email, assignee__email, compliance
            query = get_query(
                query_str, ['applicant__email', 'assignee__email', 'compliance'])
            qs = qs.filter(query).distinct()
        return qs


class ComplianceCreate(LoginRequiredMixin, ModelFormSetView):
    model = Compliance
    form_class = apps_forms.ComplianceCreateForm
    template_name = 'applications/compliance_formset.html'
    fields = ['condition', 'compliance']

    def get_application(self):
        return Application.objects.get(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super(ComplianceCreate, self).get_context_data(**kwargs)
        app = self.get_application()
        context['application'] = app
        return context

    def get_initial(self):
        # Return a list of dicts, each containing a reference to one condition.
        app = self.get_application()
        conditions = app.condition_set.all()
        return [{'condition': c} for c in conditions]

    def get_factory_kwargs(self):
        kwargs = super(ComplianceCreate, self).get_factory_kwargs()
        app = self.get_application()
        conditions = app.condition_set.all()
        # Set the number of forms in the set to equal the number of conditions.
        kwargs['extra'] = len(conditions)
        return kwargs

    def get_extra_form_kwargs(self):
        kwargs = super(ComplianceCreate, self).get_extra_form_kwargs()
        kwargs['application'] = self.get_application()
        return kwargs

    def formset_valid(self, formset):
        for form in formset:
            data = form.cleaned_data
            # If text has been input to the compliance field, create a new
            # compliance object.
            if 'compliance' in data and data.get('compliance', None):
                new_comp = form.save(commit=False)
                new_comp.applicant = self.request.user
                new_comp.application = self.get_application()
                new_comp.submit_date = date.today()
                # TODO: handle the uploaded file.
                new_comp.save()
                # Record an action on the compliance request's application:
                action = Action(
                    content_object=new_comp.application, user=self.request.user,
                    action='Request for compliance created')
                action.save()
        messages.success(
            self.request, 'New requests for compliance have been submitted.')
        return super(ComplianceCreate, self).formset_valid(formset)

    def get_success_url(self):
        return reverse('application_detail', args=(self.get_application().pk,))

class WebPublish(LoginRequiredMixin, UpdateView):
    model = Application
    form_class = apps_forms.ApplicationWebPublishForm

    def get(self, request, *args, **kwargs):
        app = Application.objects.get(pk=self.kwargs['pk'])
        return super(WebPublish, self).get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('application_detail', args=(self.kwargs['pk'],))

    def get_context_data(self, **kwargs):
        context = super(WebPublish,
                        self).get_context_data(**kwargs)
        context['application'] = Application.objects.get(pk=self.kwargs['pk'])
        return context

    def get_initial(self):
        initial = super(WebPublish, self).get_initial()
        initial['application'] = self.kwargs['pk']

        current_date = datetime.now().strftime('%d/%m/%Y')

        publish_type = self.kwargs['publish_type']
        if publish_type in 'documents':
            initial['publish_documents'] = current_date 
        elif publish_type in 'draft':
            initial['publish_draft_report'] = current_date
        elif publish_type in 'final':
            initial['publish_final_report'] = current_date

        initial['publish_type'] = self.kwargs['publish_type']
        #try:
        #    pub_news = PublicationNewspaper.objects.get(
        #    application=self.kwargs['pk'])
        #except:
        #    pub_news = None
        return initial

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):
            app = Application.objects.get(pk=self.kwargs['pk'])
            return HttpResponseRedirect(app.get_absolute_url())
        return super(WebPublish, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        forms_data = form.cleaned_data
        self.object = form.save(commit=True)
        publish_type = self.kwargs['publish_type']

        current_date = datetime.now().strftime('%Y-%m-%d')

        if publish_type in 'documents':
            self.object.publish_documents = current_date
        elif publish_type in 'draft':
            self.object.publish_draft_report = current_date
        elif publish_type in 'final':
            self.object.publish_final_report = current_date

        return super(WebPublish, self).form_valid(form)


class NewsPaperPublicationCreate(LoginRequiredMixin, CreateView):
    model = PublicationNewspaper
    form_class = apps_forms.NewsPaperPublicationCreateForm

    def get(self, request, *args, **kwargs):
        app = Application.objects.get(pk=self.kwargs['pk'])
        flow = Flow()
        workflowtype = flow.getWorkFlowTypeFromApp(app)
        flow.get(workflowtype)
        DefaultGroups = flow.groupList()
        flowcontext = {}
        flowcontext = flow.getAccessRights(request,flowcontext,app.routeid,workflowtype)


#       if flowcontext.state != app.APP_STATE_CHOICES.draft:
        if flowcontext["may_update_publication_newspaper"] != "True":
            messages.error(
                self.request, "Can't add new newspaper publication to this application")
            return HttpResponseRedirect(app.get_absolute_url())
        return super(NewsPaperPublicationCreate, self).get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('application_detail', args=(self.kwargs['pk'],))

    def get_context_data(self, **kwargs):
        context = super(NewsPaperPublicationCreate,
                        self).get_context_data(**kwargs)
        context['application'] = Application.objects.get(pk=self.kwargs['pk'])
        return context

    def get_initial(self):
        initial = super(NewsPaperPublicationCreate, self).get_initial()
        initial['application'] = self.kwargs['pk']

        #try:
        #    pub_news = PublicationNewspaper.objects.get(
        #    application=self.kwargs['pk'])
        #except:
        #    pub_news = None
        return initial

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):
            app = Application.objects.get(pk=self.kwargs['pk'])
            return HttpResponseRedirect(app.get_absolute_url())
        return super(NewsPaperPublicationCreate, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        forms_data = form.cleaned_data
        self.object = form.save(commit=True)

        if self.request.FILES.get('documents'):
            for f in self.request.FILES.getlist('documents'):
                doc = Document()
                doc.upload = f
                doc.save()
                self.object.documents.add(doc)
 
        return super(NewsPaperPublicationCreate, self).form_valid(form)

class NewsPaperPublicationUpdate(LoginRequiredMixin, UpdateView):
    model = PublicationNewspaper
    form_class = apps_forms.NewsPaperPublicationCreateForm

    def get(self, request, *args, **kwargs):
		#app = self.get_object().application_set.first()
        PubNew = PublicationNewspaper.objects.get(pk=self.kwargs['pk'])
        app = Application.objects.get(pk=PubNew.application.id)
        flow = Flow()
        workflowtype = flow.getWorkFlowTypeFromApp(app)
        flow.get(workflowtype)
        DefaultGroups = flow.groupList()
        flowcontext = {}
        flowcontext = flow.getAccessRights(request,flowcontext,app.routeid,workflowtype)
        if flowcontext["may_update_publication_newspaper"] != "True":
            messages.error(
                self.request, "Can't update newspaper publication to this application")
            return HttpResponseRedirect(app.get_absolute_url())
        # Rule: can only change a vessel if the parent application is status
        # 'draft'.
		#if app.state != Application.APP_STATE_CHOICES.draft:
		#    messages.error(
		#        self.request, 'You can only change a publication details when the application is "draft" status')
#        return HttpResponseRedirect(app.get_absolute_url())
        return super(NewsPaperPublicationUpdate, self).get(request, *args, **kwargs)

    def get_initial(self):
        initial = super(NewsPaperPublicationUpdate, self).get_initial()
#       initial['application'] = self.kwargs['pk']

        try:
            pub_news = PublicationNewspaper.objects.get(
            pk=self.kwargs['pk'])
        except:
            pub_news = None

        multifilelist = []
        if pub_news:
            documents = pub_news.documents.all()
            for b1 in documents:
                fileitem = {}
                fileitem['fileid'] = b1.id
                fileitem['path'] = b1.upload.name
                multifilelist.append(fileitem)
        initial['documents'] = multifilelist
        return initial
    def get_context_data(self, **kwargs):
        context = super(NewsPaperPublicationUpdate, self).get_context_data(**kwargs)
        context['page_heading'] = 'Update Newspaper Publication details'
        return context

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):
            app = self.get_object().application_set.first()
            return HttpResponseRedirect(app.get_absolute_url())
        return super(NewsPaperPublicationUpdate, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()
        app = Application.objects.get(pk=self.object.application.id)

        pub_news = PublicationNewspaper.objects.get(pk=self.kwargs['pk'])

        documents = pub_news.documents.all()
        for filelist in documents:
            if 'documents-clear_multifileid-'+str(filelist.id) in form.data:
                pub_news.documents.remove(filelist)


        if self.request.FILES.get('documents'):
            for f in self.request.FILES.getlist('documents'):
                doc = Document()
                doc.upload = f
                doc.save()
                self.object.documents.add(doc)

        return HttpResponseRedirect(app.get_absolute_url())

class NewsPaperPublicationDelete(LoginRequiredMixin, DeleteView):
    model = PublicationNewspaper

    def get(self, request, *args, **kwargs):
        modelobject = self.get_object()

        PubNew = PublicationNewspaper.objects.get(pk=self.kwargs['pk'])
        app = Application.objects.get(pk=PubNew.application.id)
        flow = Flow()
        workflowtype = flow.getWorkFlowTypeFromApp(app)
        flow.get(workflowtype)
        DefaultGroups = flow.groupList()
        flowcontext = {}
        flowcontext = flow.getAccessRights(request,flowcontext,app.routeid,workflowtype)
        if flowcontext["may_update_publication_newspaper"] != "True":
            messages.error(
                self.request, "Can't delete newspaper publication to this application")
            return HttpResponseRedirect(app.get_absolute_url())

        # Rule: can only delete a condition if the parent application is status
        # 'with referral' or 'with assessor'.
#        if modelobject.application.state not in [Application.APP_STATE_CHOICES.with_assessor, Application.APP_STATE_CHOICES.with_referee]:
 #           messages.warning(self.request, 'You cannot delete this condition')
  #          return HttpResponseRedirect(modelobject.application.get_absolute_url())
        # Rule: can only delete a condition if the request user is an Assessor
        # or they are assigned the referral to which the condition is attached
        # and that referral is not completed.
  #      assessor = Group.objects.get(name='Assessor')
   #     ref = condition.referral
	#    if assessor in self.request.user.groups.all() or (ref and ref.referee == request.user and ref.status == Referral.REFERRAL_STATUS_CHOICES.referred):
        return super(NewsPaperPublicationDelete, self).get(request, *args, **kwargs)
	#    else:
	 #       messages.warning(self.request, 'You cannot delete this condition')
	  #      return HttpResponseRedirect(condition.application.get_absolute_url())

    def get_success_url(self):
        return reverse('application_detail', args=(self.get_object().application.pk,))

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):
            return HttpResponseRedirect(self.get_success_url())
        # Generate an action.
        modelobject = self.get_object()
        action = Action(
            content_object=modelobject.application, user=self.request.user,
            action='Delete Newspaper Publication {} deleted (status: {})'.format(modelobject.pk,'delete'))
        action.save()
        messages.success(self.request, 'Newspaper Publication {} has been deleted'.format(modelobject.pk))
        return super(NewsPaperPublicationDelete, self).post(request, *args, **kwargs)

class WebsitePublicationChange(LoginRequiredMixin, CreateView):
    model = PublicationWebsite
    form_class = apps_forms.WebsitePublicationForm

    def get(self, request, *args, **kwargs):
        app = Application.objects.get(pk=self.kwargs['pk'])
        flow = Flow()
        workflowtype = flow.getWorkFlowTypeFromApp(app)
        flow.get(workflowtype)
        DefaultGroups = flow.groupList()
        flowcontext = {}
        flowcontext = flow.getAccessRights(request,flowcontext,app.routeid,workflowtype)
        if flowcontext["may_update_publication_website"] != "True":
            messages.error(
                self.request, "Can't update ebsite publication to this application")
            return HttpResponseRedirect(app.get_absolute_url())
        return super(WebsitePublicationChange, self).get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('application_detail', args=(self.kwargs['pk'],))

#    def get_success_url(self):
#        print self.kwargs['pk']
        #        return reverse('application_detail', args=(self.get_object().application.pk,))
#        return reverse('application_detail', args=(self.kwargs['pk']))

    def get_context_data(self, **kwargs):
		# self.object.original_document = self.kwargs['original_document']
        context = super(WebsitePublicationChange,
                        self).get_context_data(**kwargs)
        context['application'] = Application.objects.get(pk=self.kwargs['pk'])
        return context

    def get_initial(self):
        initial = super(WebsitePublicationChange, self).get_initial()
        initial['application'] = self.kwargs['pk']

        doc = Document.objects.get(pk=self.kwargs['docid'])
        try:
           pub_web = PublicationWebsite.objects.get(original_document_id=self.kwargs['docid'])
        except:
           pub_web = None

        filelist = []
        if pub_web:
           if pub_web.published_document:
           
        
#          documents = pub_news.documents.all()
              fileitem = {}
              fileitem['fileid'] = pub_web.published_document.id
              fileitem['path'] = pub_web.published_document.upload.name
              filelist.append(fileitem)
        if pub_web:
           if pub_web.id:
              initial['id'] = pub_web.id

        initial['published_document'] = filelist
        doc = Document.objects.get(pk=self.kwargs['docid'])
        initial['original_document'] = doc
        return initial

    def post(self, request, *args, **kwargs):

        if request.POST.get('cancel'):
            app = Application.objects.get(pk=self.kwargs['pk'])
            return HttpResponseRedirect(app.get_absolute_url())
        return super(WebsitePublicationChange, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        forms_data = form.cleaned_data
        self.object = form.save(commit=False)
        pub_web = None
        try:
           pub_web = PublicationWebsite.objects.get(original_document_id=self.kwargs['docid'])
        except:
           pub_web = None
        if pub_web:
           self.object.id = pub_web.id
           self.object.published_document = pub_web.published_document
           if pub_web.published_document:
              if 'published_document-clear_multifileid-'+str(pub_web.published_document.id) in self.request.POST:
                  self.object.published_document = None

        orig_doc = Document.objects.get(id=self.kwargs['docid'])
        self.object.original_document = orig_doc
        
        if self.request.FILES.get('published_document'):
             for f in self.request.FILES.getlist('published_document'):
                 doc = Document()
                 doc.upload = f
                 doc.save()
                 self.object.published_document = doc
        return super(WebsitePublicationChange, self).form_valid(form)


class FeedbackPublicationCreate(LoginRequiredMixin, CreateView):
    model = PublicationFeedback
    form_class = apps_forms.FeedbackPublicationCreateForm

    def get(self, request, *args, **kwargs):
        app = Application.objects.get(pk=self.kwargs['pk'])
#        if app.state != app.APP_STATE_CHOICES.draft:
 #           messages.errror(
  #              self.request, "Can't add new feedback publication to this application")
   #         return HttpResponseRedirect(app.get_absolute_url())
        return super(FeedbackPublicationCreate, self).get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('application_detail', args=(self.kwargs['pk'],))

    def get_context_data(self, **kwargs):
        context = super(FeedbackPublicationCreate,
                        self).get_context_data(**kwargs)
        context['application'] = Application.objects.get(pk=self.kwargs['pk'])
        return context

    def get_initial(self):
        initial = super(FeedbackPublicationCreate, self).get_initial()
        initial['application'] = self.kwargs['pk']

        if self.kwargs['status'] == 'final':
            initial['status'] = 'final'
        else:
            initial['status'] = 'draft'
        return initial

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):
            app = Application.objects.get(pk=self.kwargs['pk'])
            return HttpResponseRedirect(app.get_absolute_url())
        return super(FeedbackPublicationCreate, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=True)
        if self.request.FILES.get('documents'):
            for f in self.request.FILES.getlist('documents'):
                doc = Document()
                doc.upload = f
                doc.save()
                self.object.documents.add(doc)
 
        return super(FeedbackPublicationCreate, self).form_valid(form)


class FeedbackPublicationUpdate(LoginRequiredMixin, UpdateView):
    model = PublicationFeedback
    form_class = apps_forms.FeedbackPublicationCreateForm

    def get(self, request, *args, **kwargs):
        modelobject = self.get_object()
        # app = Application.objects.get(pk=self.kwargs['application'])
        # if app.state != app.APP_STATE_CHOICES.draft:
        #    messages.errror(
        #       self.request, "Can't add new newspaper publication to this application")
        #  return HttpResponseRedirect(app.get_absolute_url())
        return super(FeedbackPublicationUpdate, self).get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('application_detail', args=(self.kwargs['application'],))

    def get_context_data(self, **kwargs):
        context = super(FeedbackPublicationUpdate,
                        self).get_context_data(**kwargs)
        context['application'] = Application.objects.get(pk=self.kwargs['application'])
        return context

    def get_initial(self):
        initial = super(FeedbackPublicationUpdate, self).get_initial()
        initial['application'] = self.kwargs['application']
        try:
            pub_feed = PublicationFeedback.objects.get(
            pk=self.kwargs['pk'])
        except:
            pub_feed = None

        multifilelist = []
        if pub_feed:
            documents = pub_feed.documents.all()
            for b1 in documents:
                fileitem = {}
                fileitem['fileid'] = b1.id
                fileitem['path'] = b1.upload.name
                multifilelist.append(fileitem)
        initial['documents'] = multifilelist
        return initial

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):
            app = Application.objects.get(pk=self.kwargs['application'])
            return HttpResponseRedirect(app.get_absolute_url())
        return super(FeedbackPublicationUpdate, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()
        app = Application.objects.get(pk=self.object.application.id)

        pub_feed = PublicationFeedback.objects.get(pk=self.kwargs['pk'])

        documents = pub_feed.documents.all()
        for filelist in documents:
            if 'documents-clear_multifileid-'+str(filelist.id) in form.data:
                pub_feed.documents.remove(filelist)


        if self.request.FILES.get('documents'):
            for f in self.request.FILES.getlist('documents'):
                doc = Document()
                doc.upload = f
                doc.save()
                self.object.documents.add(doc)


        return super(FeedbackPublicationUpdate, self).form_valid(form)

class FeedbackPublicationDelete(LoginRequiredMixin, DeleteView):
    model = PublicationFeedback 

    def get(self, request, *args, **kwargs):
        modelobject = self.get_object()
        return super(FeedbackPublicationDelete, self).get(request, *args, **kwargs)
    def get_success_url(self):
        return reverse('application_detail', args=(self.get_object().application.pk,))

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):
            return HttpResponseRedirect(self.get_success_url())
        # Generate an action.
        modelobject = self.get_object()
        action = Action(
            content_object=modelobject.application, user=self.request.user,
            action='Delete Feedback Publication {} deleted (status: {})'.format(modelobject.pk,'delete'))
        action.save()
        messages.success(self.request, 'Newspaper Feedback {} has been deleted'.format(modelobject.pk))
        return super(FeedbackPublicationDelete, self).post(request, *args, **kwargs)

class ConditionCreate(LoginRequiredMixin, CreateView):
    """A view for a referee or an internal user to create a Condition object
    on an Application.
    """
    model = Condition
    form_class = apps_forms.ConditionCreateForm

    def get(self, request, *args, **kwargs):
        app = Application.objects.get(pk=self.kwargs['pk'])
        # Rule: conditions can be created when the app is with admin, with
        # referee or with assessor.
        if app.app_type == app.APP_TYPE_CHOICES.emergency:
            if app.state != app.APP_STATE_CHOICES.draft or app.assignee != self.request.user:
                messages.error(
                    self.request, 'New conditions cannot be created for this application!')
                return HttpResponseRedirect(app.get_absolute_url())
        elif app.state not in [app.APP_STATE_CHOICES.with_admin, app.APP_STATE_CHOICES.with_referee, app.APP_STATE_CHOICES.with_assessor]:
            messages.error(
                self.request, 'New conditions cannot be created for this application!')
            return HttpResponseRedirect(app.get_absolute_url())
        return super(ConditionCreate, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ConditionCreate, self).get_context_data(**kwargs)
        context['page_heading'] = 'Create a new condition'
        return context

    def get_success_url(self):
        """Override to redirect to the condition's parent application detail view.
        """
        return reverse('application_detail', args=(self.object.application.pk,))

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):
            app = Application.objects.get(pk=self.kwargs['pk'])
            return HttpResponseRedirect(app.get_absolute_url())
        return super(ConditionCreate, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        app = Application.objects.get(pk=self.kwargs['pk'])
        self.object = form.save(commit=False)
        self.object.application = app
        # If a referral exists for the parent application for this user,
        # link that to the new condition.
        if Referral.objects.filter(application=app, referee=self.request.user).exists():
            self.object.referral = Referral.objects.get(
                application=app, referee=self.request.user)
        # If the request user is not in the "Referee" group, then assume they're an internal user
        # and set the new condition to "applied" status (default = "proposed").
        referee = Group.objects.get(name='Referee')
        if referee not in self.request.user.groups.all():
            self.object.status = Condition.CONDITION_STATUS_CHOICES.applied
        self.object.save()
        # Record an action on the application:
        action = Action(
            content_object=app, user=self.request.user,
            action='Created condition {} (status: {})'.format(self.object.pk, self.object.get_status_display()))
        action.save()
        return super(ConditionCreate, self).form_valid(form)


class ConditionUpdate(LoginRequiredMixin, UpdateView):
    """A view to allow an assessor to update a condition that might have been
    proposed by a referee.
    The ``action`` kwarg is used to define the new state of the condition.
    """
    model = Condition

    def get(self, request, *args, **kwargs):
        condition = self.get_object()
        # Rule: can only change a condition if the parent application is status
        # 'with assessor' or 'with_referee' unless it is an emergency works.
        if condition.application.app_type == Application.APP_TYPE_CHOICES.emergency:
            if condition.application.state != Application.APP_STATE_CHOICES.draft:
                messages.error(
                    self.request, 'You can not change conditions when the application has been issued')
                return HttpResponseRedirect(condition.application.get_absolute_url())
            elif condition.application.assignee != self.request.user:
                messages.error(
                    self.request, 'You can not change conditions when the application is not assigned to you')
                return HttpResponseRedirect(condition.application.get_absolute_url())

            else:
                return super(ConditionUpdate, self).get(request, *args, **kwargs)
        elif condition.application.state not in [Application.APP_STATE_CHOICES.with_assessor, Application.APP_STATE_CHOICES.with_referee]:
            messages.error(
                self.request, 'You can only change conditions when the application is "with assessor" or "with referee" status')
            return HttpResponseRedirect(condition.application.get_absolute_url())
        # Rule: can only change a condition if the request user is an Assessor
        # or they are assigned the referral to which the condition is attached
        # and that referral is not completed.
        assessor = Group.objects.get(name='Assessor')
        ref = condition.referral
        if assessor in self.request.user.groups.all() or (ref and ref.referee == request.user and ref.status == Referral.REFERRAL_STATUS_CHOICES.referred):
            return super(ConditionUpdate, self).get(request, *args, **kwargs)
        else:
            messages.warning(self.request, 'You cannot update this condition')
            return HttpResponseRedirect(condition.application.get_absolute_url())

    def get_form_class(self):
        # Updating the condition as an 'action' should not allow the user to
        # change the condition text.
        if 'action' in self.kwargs:
            return apps_forms.ConditionActionForm
        return apps_forms.ConditionUpdateForm

    def get_context_data(self, **kwargs):
        context = super(ConditionUpdate, self).get_context_data(**kwargs)
        if 'action' in self.kwargs:
            if self.kwargs['action'] == 'apply':
                context['page_heading'] = 'Apply a proposed condition'
            elif self.kwargs['action'] == 'reject':
                context['page_heading'] = 'Reject a proposed condition'
        return context

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):
            return HttpResponseRedirect(self.get_object().application.get_absolute_url())
        return super(ConditionUpdate, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        if 'action' in self.kwargs:
            if self.kwargs['action'] == 'apply':
                self.object.status = Condition.CONDITION_STATUS_CHOICES.applied
            elif self.kwargs['action'] == 'reject':
                self.object.status = Condition.CONDITION_STATUS_CHOICES.rejected
            # Generate an action:
            action = Action(
                content_object=self.object.application, user=self.request.user,
                action='Condition {} updated (status: {})'.format(self.object.pk, self.object.get_status_display()))
            action.save()
        self.object.save()
        return HttpResponseRedirect(self.object.application.get_absolute_url())


class ConditionDelete(LoginRequiredMixin, DeleteView):
    model = Condition

    def get(self, request, *args, **kwargs):
        condition = self.get_object()
        # Rule: can only delete a condition if the parent application is status
        # 'with referral' or 'with assessor'. Can also delete if you are the user assigned
        # to an Emergency Works
        if condition.application.app_type != Application.APP_TYPE_CHOICES.emergency:
            if condition.application.state not in [Application.APP_STATE_CHOICES.with_assessor, Application.APP_STATE_CHOICES.with_referee]:
                messages.warning(self.request, 'You cannot delete this condition')
                return HttpResponseRedirect(condition.application.get_absolute_url())
            # Rule: can only delete a condition if the request user is an Assessor
            # or they are assigned the referral to which the condition is attached
            # and that referral is not completed.
            assessor = Group.objects.get(name='Assessor')
            ref = condition.referral
            if assessor in self.request.user.groups.all() or (ref and ref.referee == request.user and ref.status == Referral.REFERRAL_STATUS_CHOICES.referred):
                return super(ConditionDelete, self).get(request, *args, **kwargs)
            else:
                messages.warning(self.request, 'You cannot delete this condition')
                return HttpResponseRedirect(condition.application.get_absolute_url())
        else:
            # Rule: can only delete a condition if the request user is the assignee and the application 
            # has not been issued.
            if condition.application.assignee == request.user and condition.application.state != Application.APP_STATE_CHOICES.issued:
                return super(ConditionDelete, self).get(request, *args, **kwargs)
            else:
                messages.warning(self.request, 'You cannot delete this condition')
                return HttpResponseRedirect(condition.application.get_absolute_url())


    def get_success_url(self):
        return reverse('application_detail', args=(self.get_object().application.pk,))

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):
            return HttpResponseRedirect(self.get_success_url())
        # Generate an action.
        condition = self.get_object()
        action = Action(
            content_object=condition.application, user=self.request.user,
            action='Condition {} deleted (status: {})'.format(condition.pk, condition.get_status_display()))
        action.save()
        messages.success(self.request, 'Condition {} has been deleted'.format(condition.pk))
        return super(ConditionDelete, self).post(request, *args, **kwargs)


class VesselCreate(LoginRequiredMixin, CreateView):
    model = Vessel
    form_class = apps_forms.VesselForm

    def get(self, request, *args, **kwargs):
        app = Application.objects.get(pk=self.kwargs['pk'])
        if app.state != app.APP_STATE_CHOICES.draft:
            messages.error(
                self.request, "Can't add new vessels to this application")
            return HttpResponseRedirect(app.get_absolute_url())
        return super(VesselCreate, self).get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('application_detail', args=(self.kwargs['pk'],))

    def get_context_data(self, **kwargs):
        context = super(VesselCreate, self).get_context_data(**kwargs)
        context['page_heading'] = 'Create new vessel details'
        return context

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):
            app = Application.objects.get(pk=self.kwargs['pk'])
            return HttpResponseRedirect(app.get_absolute_url())
        return super(VesselCreate, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        app = Application.objects.get(pk=self.kwargs['pk'])
        self.object = form.save()
        app.vessels.add(self.object.id)
        app.save()
        # Registration document uploads.
        if self.request.FILES.get('registration'):
            # Remove any existing documents.
            for d in self.object.registration.all():
                self.object.registration.remove(d)
            # Add new uploads.
            for f in form.cleaned_data['registration']:
                doc = Document()
                doc.upload = f
                doc.name = f.name
                doc.save()
                self.object.registration.add(doc)

        return super(VesselCreate, self).form_valid(form)


class VesselUpdate(LoginRequiredMixin, UpdateView):
    model = Vessel
    form_class = apps_forms.VesselForm

    def get(self, request, *args, **kwargs):
        app = self.get_object().application_set.first()
        # Rule: can only change a vessel if the parent application is status
        # 'draft'.
        if app.state != Application.APP_STATE_CHOICES.draft:
            messages.error(
                self.request, 'You can only change a vessel details when the application is "draft" status')
            return HttpResponseRedirect(app.get_absolute_url())
        return super(VesselUpdate, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(VesselUpdate, self).get_context_data(**kwargs)
        context['page_heading'] = 'Update vessel details'
        return context

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):
            app = self.get_object().application_set.first()
            return HttpResponseRedirect(app.get_absolute_url())
        return super(VesselUpdate, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()
        # Registration document uploads.
        if self.request.FILES.get('registration'):
            # Remove any existing documents.
            for d in self.object.registration.all():
                self.object.registration.remove(d)
            # Add new uploads.
            for f in form.cleaned_data['registration']:
                doc = Document()
                doc.upload = f
                doc.name = f.name
                doc.save()
                self.object.registration.add(doc)
        app = self.object.application_set.first()
        return HttpResponseRedirect(app.get_absolute_url())


class DocumentCreate(LoginRequiredMixin, CreateView):
    form_class = apps_forms.DocumentCreateForm
    template_name = 'applications/document_form.html'

    def get_context_data(self, **kwargs):
        context = super(DocumentCreate, self).get_context_data(**kwargs)
        context['page_heading'] = 'Create new Document'
        return context

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):
            return HttpResponseRedirect(reverse('home_page'))
        return super(DocumentCreate, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        """Override form_valid to set the assignee as the object creator.
        """
        self.object = form.save(commit=False)
        self.object.save()
        success_url = reverse('document_list', args=(self.object.pk,))
        return HttpResponseRedirect(success_url)


class DocumentList(ListView):
    model = Document
