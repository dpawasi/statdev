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
        if 'q' in self.request.GET and self.request.GET['q']:
            query_str = self.request.GET['q']
            objlist = ApprovalModel.objects.filter(Q(pk__contains=query_str) | Q(title__icontains=query_str) | Q(applicant__email__icontains=query_str) )
        else:
            objlist = ApprovalModel.objects.all()
        usergroups = self.request.user.groups.all()
        context['app_list'] = []

        for app in objlist.order_by('title'):
            row = {}
            row['app'] = app
        #    if app.group is not None:
            context['app_list'].append(row)

#        context['app_list'] = context['app_list'].order_by('title')

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

        print "ACTION COMPLETED"
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


