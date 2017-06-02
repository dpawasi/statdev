from django.shortcuts import render
from django.views.generic import ListView
from .models import Approval as ApprovalModel 
from django.db.models import Q
from django.contrib.auth.models import Group
from applications.utils import get_query

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
        for app in objlist:
            row = {}
            row['app'] = app
        #    if app.group is not None:
            context['app_list'].append(row)

        # TODO: any restrictions on who can create new applications?
        processor = Group.objects.get(name='Processor')
        # Rule: admin officers may self-assign applications.
        if processor in self.request.user.groups.all() or self.request.user.is_superuser:
            context['may_assign_processor'] = True

        return context




# Create your views here.
