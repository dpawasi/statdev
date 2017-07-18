from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, UpdateView, DetailView
from django.core.urlresolvers import reverse
from .models import Approval as ApprovalModel 
from django.db.models import Q
from django.contrib.auth.models import Group
from applications.utils import get_query
from . import forms as apps_forms
from actions.models import Action
from django.contrib.contenttypes.models import ContentType
from applications.models import Application

class ApprovalList(ListView):
    model = ApprovalModel

    def get_queryset(self):
        qs = super(ApprovalList, self).get_queryset()

        # Did we pass in a search string? If so, filter the queryset and return
        # it.
        if 'q' in self.request.GET and self.request.GET['q']:
            query_str = self.request.GET['q']
            # Replace single-quotes with double-quotes
            query_str = query_str.replace("'", r'"')
            # Filter by pk, title, applicant__email, organisation__name,
            # assignee__email
            query = get_query(
                query_str, ['pk', 'title', 'applicant__email'])
            qs = qs.filter(query).distinct()
        return qs

    def get_context_data(self, **kwargs):
        context = super(ApprovalList, self).get_context_data(**kwargs)

        APP_TYPE_CHOICES = []
        APP_TYPE_CHOICES_IDS = []
        for i in Application.APP_TYPE_CHOICES:
            if i[0] in [4,5,6,7,8,9,10,11]:
               skip = 'yes'
            else:
               APP_TYPE_CHOICES.append(i)
               APP_TYPE_CHOICES_IDS.append(i[0])
        context['app_apptypes']= APP_TYPE_CHOICES


        if 'action' in self.request.GET and self.request.GET['action']:
            query_str = self.request.GET['q']
            query_obj = Q(pk__contains=query_str) | Q(title__icontains=query_str) | Q(applicant__email__icontains=query_str)

            if self.request.GET['apptype'] != '':
                query_obj &= Q(app_type=int(self.request.GET['apptype']))
            else:
                query_obj &= Q(app_type__in=APP_TYPE_CHOICES_IDS)

            if self.request.GET['applicant'] != '':
                query_obj &= Q(applicant=int(self.request.GET['applicant']))
            if self.request.GET['appstatus'] != '':
                query_obj &= Q(status=int(self.request.GET['appstatus']))

            objlist = ApprovalModel.objects.filter(query_obj)
            context['query_string'] = self.request.GET['q']

            if self.request.GET['apptype'] != '':
                 context['apptype'] = int(self.request.GET['apptype'])
            if self.request.GET['applicant'] != '':
                 context['applicant'] = int(self.request.GET['applicant'])
            if 'appstatus' in self.request.GET:
                if self.request.GET['appstatus'] != '':
                    context['appstatus'] = int(self.request.GET['appstatus'])



#        if 'q' in self.request.GET and self.request.GET['q']:
 #           query_str = self.request.GET['q']
  #          objlist = ApprovalModel.objects.filter(Q(pk__contains=query_str) | Q(title__icontains=query_str) | Q(applicant__email__icontains=query_str))
        else:
            objlist = ApprovalModel.objects.all()
        usergroups = self.request.user.groups.all()

        context['app_list'] = []
        context['app_applicants'] = {}
        context['app_applicants_list'] = []
        context['app_appstatus'] = list(ApprovalModel.APPROVAL_STATE_CHOICES)

        for app in objlist.order_by('title'):
            row = {}
            row['app'] = app
        #    if app.group is not None:

            if app.applicant:
                if app.applicant.id in context['app_applicants']:
                    donothing = ''
                else:
                    context['app_applicants'][app.applicant.id] = app.applicant.first_name + ' ' + app.applicant.last_name
                    context['app_applicants_list'].append({"id": app.applicant.id, "name": app.applicant.first_name + ' ' + app.applicant.last_name})


            context['app_list'].append(row)


#       context['app_list'] = context['app_list'].order_by('title')

        # TODO: any restrictions on who can create new applications?
        processor = Group.objects.get(name='Processor')

        # Rule: admin officers may self-assign applications.
        if processor in self.request.user.groups.all() or self.request.user.is_superuser:
            context['may_assign_processor'] = True

        return context

class ApprovalStatusChange(LoginRequiredMixin,UpdateView):
    model = ApprovalModel
    form_class = apps_forms.ApprovalChangeStatus
    template_name = 'applications/application_form.html'

    def get(self, request, *args, **kwargs):
        modelobject = self.get_object()
        return super(ApprovalStatusChange, self).get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('approval_list', args=())

    def get_context_data(self, **kwargs):
        context = super(ApprovalStatusChange,self).get_context_data(**kwargs)
        self.object = self.get_object()
        context['title'] = self.object.title
        return context

    def get_initial(self):
        initial = super(ApprovalStatusChange, self).get_initial()
        approval = self.get_object()
        status = self.kwargs['status']
        initial['status'] = ApprovalModel.APPROVAL_STATE_CHOICES.__getattr__(status)
        return initial

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel'):
            app = Application.objects.get(pk=self.kwargs['application'])
            return HttpResponseRedirect(app.get_absolute_url())
        return super(ApprovalStatusChange, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        
        self.object = form.save(commit=False)
        app = self.get_object()
        status = self.kwargs['status']
        self.object.status = ApprovalModel.APPROVAL_STATE_CHOICES.__getattr__(status)
        self.object.save()

        action = Action(
            content_object=app, category=Action.ACTION_CATEGORY_CHOICES.change,
            user=self.request.user, action='Approval Change')
        action.save()

        return super(ApprovalStatusChange, self).form_valid(form)


class ApprovalActions(DetailView):
    model = ApprovalModel
    template_name = 'applications/application_actions.html'

    def get_context_data(self, **kwargs):
        context = super(ApprovalActions, self).get_context_data(**kwargs)
        app = self.get_object()
        # TODO: define a GenericRelation field on the Application model.
        context['actions'] = Action.objects.filter(
            content_type=ContentType.objects.get_for_model(app), object_id=app.pk).order_by('-timestamp')
        return context


