from django.shortcuts import render
from applications.models import Application, PublicationFeedback, Record
from approvals.models import Approval 
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.db.models import Q
from public import forms as apps_forms
from django.core.urlresolvers import reverse
from django.utils.safestring import SafeText

class PublicApplicationsList(TemplateView):
    #model = appmodel.Application

    template_name = "public/home_page.html"
    def get_context_data(self, **kwargs):

        context = super(PublicApplicationsList, self).get_context_data(**kwargs)
        # app = self.get_object()
        # print self.req
        action =  self.kwargs['action']
        context['action'] = action
        search = None
        query_obj = None

        if action == 'draft':
            query_obj = Q(publish_documents__isnull=False,publish_draft_report__isnull=True) & Q(app_type__in=[3])
        elif action == 'final':
            query_obj = Q(publish_documents__isnull=False, publish_draft_report__isnull=False,publish_final_report__isnull=True) & Q(app_type__in=[3])
        elif action == 'determination':
            query_obj = Q(publish_documents__isnull=False, publish_draft_report__isnull=False, publish_final_report__isnull=False,publish_determination_report__isnull=True ) & Q(app_type__in=[3])
        else:
            query_obj = Q(publish_documents__isnull=False, publish_draft_report__isnull=False,publish_final_report__isnull=False) & Q(app_type__in=[3])
            #query_obj = Q(publish_documents__isnull=False) & Q(app_type__in=[3])

        if 'q' in self.request.GET and self.request.GET['q']:
            query_str = self.request.GET['q']
            query_obj = Q(Q(pk__contains=query_str) | Q(title__icontains=query_str) | Q(applicant__email__icontains=query_str) | Q(organisation__name__icontains=query_str) |  Q(assignee__email__icontains=query_str)) & query_obj
            

        if action is not None: 
            context['items'] = Application.objects.filter(query_obj)

        return context


class PublicApplicationFeedback(UpdateView):
    """A view for updating a draft (non-lodged) application.
    """
    model = Application
    form_class = apps_forms.ApplicationPart5
    template_name = 'public/application_form.html'

    def get(self, request, *args, **kwargs):
        # TODO: business logic to check the application may be changed.
        app = self.get_object()
        return super(PublicApplicationFeedback, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PublicApplicationFeedback, self).get_context_data(**kwargs)
        app_id = self.kwargs['pk']
        context['page_heading'] = 'Application for new Part 5 - '+app_id
        context['left_sidebar'] = 'yes'
        context['action'] = self.kwargs['action']
        app = self.get_object()

        doclist = app.proposed_development_plans.all()
        context['proposed_development_plans_list'] = []
        for doc in doclist:
            fileitem = {}
            fileitem['fileid'] = doc.id
            fileitem['path'] = doc.upload.name
            fileitem['path_short'] = SafeText(doc.upload.name)[19:]
            context['proposed_development_plans_list'].append(fileitem)


        return context
    def get_initial(self):
        initial = super(PublicApplicationFeedback, self).get_initial()
        app = self.get_object()
       
        initial['application_id'] = self.kwargs['pk']
        initial['organisation'] = app.organisation
        if app.river_lease_scan_of_application:
            initial['river_lease_scan_of_application'] = app.river_lease_scan_of_application.upload

        return initial

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):
            app = Application.objects.get(id=kwargs['pk'])
            if app.state == app.APP_STATE_CHOICES.new:
                app.delete()
                return HttpResponseRedirect(reverse('application_list'))
            return HttpResponseRedirect(self.get_object().get_absolute_url())
        return super(PublicApplicationFeedback, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        """Override form_valid to set the state to draft is this is a new application.
        """
        forms_data = form.cleaned_data
        self.object = form.save(commit=False)
        app_id = self.kwargs['pk']
        action = self.kwargs['action']
        status=None
        application = Application.objects.get(id=app_id)
      
        if action == 'draft':
             status='draft'
        elif action == 'final': 
             status='final' 
        elif action == 'determination':
             status=='determination'

        # ToDO remove dupes of this line below. doesn't need to be called
        # multiple times
        pfcreate = PublicationFeedback.objects.create(application=application,
						      name=forms_data['name'],
                                                      address=forms_data['address'],
                                                      suburb=forms_data['suburb'],
                                                      state=forms_data['state'],
                                                      postcode=forms_data['post_code'],
                                                      phone=forms_data['phone'],
                                                      email=forms_data['email'],
                                                      comments=forms_data['comments'],
                                                      status=status
 
	)


        if self.request.FILES.get('records'):
            for f in self.request.FILES.getlist('records'):
                doc = Record()
                doc.upload = f
                doc.save()
                pfcreate.records.add(doc)



#    name = CharField(required=False,max_length=255)
#    address = CharField(required=False,max_length=255)
#    suburb = CharField(required=False,max_length=255)
#    post_code = CharField(required=False,max_length=255)
#    phone = CharField(required=False,max_length=255)
#    email = EmailField(required=False,max_length=255)
#    email_confirm = EmailField(required=False,max_length=255)
#    comments = CharField(required=False,max_length=255, widget=Textarea)




#        application = Application.objects.get(id=self.object.id)
 #       self.object.save()
        return HttpResponseRedirect(reverse('public_application_list', args=(action,)))

