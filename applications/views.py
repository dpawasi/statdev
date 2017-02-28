from __future__ import unicode_literals
from datetime import date
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView
from .models import Application, Referral, Condition, Task
from .forms import (
    ApplicationForm, ApplicationLodgeForm, ReferralForm, ReferralCompleteForm,
    ConditionCreateForm, ApplicationAssignForm, ApplicationApproveForm, ApplicationIssueForm)


class HomePage(LoginRequiredMixin, TemplateView):
    # TODO: rename this view to something like UserDashboard.
    template_name = 'applications/home_page.html'

    def get_context_data(self, **kwargs):
        context = super(HomePage, self).get_context_data(**kwargs)
        context['page_heading'] = 'Home Page'
        context['tasks'] = Task.objects.filter(
            status=Task.TASK_STATUS_CHOICES.ongoing, assignee=self.request.user)
        processor = Group.objects.get_or_create(name='Processor')[0]
        if processor in self.request.user.groups.all() or self.request.user.is_superuser:
            context['may_create'] = True
        if Referral.objects.filter(referee=self.request.user).exists():
            context['referrals'] = Referral.objects.filter(referee=self.request.user)
        return context


class ApplicationList(ListView):
    model = Application


class ApplicationCreate(LoginRequiredMixin, CreateView):
    form_class = ApplicationForm
    template_name = 'applications/application_form.html'

    def get(self, request, *args, **kwargs):
        # TODO: business logic to check user is authorised to create applications.
        processor = Group.objects.get_or_create(name='Processor')[0]
        if processor in request.user.groups.all() or request.user.is_superuser:
            return super(ApplicationCreate, self).get(request, *args, **kwargs)
        else:
            messages.error(self.request, 'You are not authorised to create applications!')
            return HttpResponseRedirect(reverse('home_page'))

    def get_context_data(self, **kwargs):
        context = super(ApplicationCreate, self).get_context_data(**kwargs)
        context['page_heading'] = 'Create new application'
        return context

    def form_valid(self, form):
        """Override form_valid to set the assignee as the object creator.
        """
        self.object = form.save(commit=False)
        self.object.assignee = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class ApplicationDetail(DetailView):
    model = Application

    def get_context_data(self, **kwargs):
        context = super(ApplicationDetail, self).get_context_data(**kwargs)
        app = self.get_object()
        processor = Group.objects.get_or_create(name='Processor')[0]
        assessor = Group.objects.get_or_create(name='Assessor')[0]
        approver = Group.objects.get_or_create(name='Approver')[0]
        if processor in self.request.user.groups.all() or self.request.user.is_superuser:
            # Rule: if the application status is 'draft', it can be updated.
            # Rule: if the application status is 'draft', it can be lodged.
            if app.state == app.APP_STATE_CHOICES.draft:
                context['may_update'] = True
                context['may_lodge'] = True
            # Rule: if the application status is 'with admin' or 'with referee', it can be referred.
            # Rule: if the application status is 'with admin' or 'with referee', it can be assigned.
            # TODO: review the rule above.
            if app.state in [app.APP_STATE_CHOICES.with_admin, app.APP_STATE_CHOICES.with_referee]:
                context['may_refer'] = True
                context['may_assign'] = True
        if assessor in self.request.user.groups.all() or self.request.user.is_superuser:
            # Rule: if the application status is 'with assessor', it can have conditions added.
            # Rule: if the application status is 'with assessor', it can be sent for approval.
            if app.state == app.APP_STATE_CHOICES.with_assessor:
                context['may_create_condition'] = True
                context['may_submit_approval'] = True
        if approver in self.request.user.groups.all() or self.request.user.is_superuser:
            # Rule: if the application status is 'with manager', it can be issued.
            # TODO: function to reassign back to assessor.
            # TODO: function to reassign back to assessor.
            if app.state == app.APP_STATE_CHOICES.with_manager:
                context['may_issue'] = True
        return context


class ApplicationUpdate(LoginRequiredMixin, UpdateView):
    model = Application
    form_class = ApplicationForm

    def get(self, request, *args, **kwargs):
        # TODO: business logic to check the application may be changed.
        app = self.get_object()
        # Rule: if the application status is 'draft', it can be updated.
        if app.state != app.APP_STATE_CHOICES.draft:
            messages.error(self.request, 'This application cannot be updated!')
            return HttpResponseRedirect(app.get_absolute_url())
        return super(ApplicationUpdate, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ApplicationUpdate, self).get_context_data(**kwargs)
        context['page_heading'] = 'Update application details'
        return context


class ApplicationLodge(LoginRequiredMixin, UpdateView):
    model = Application
    form_class = ApplicationLodgeForm

    def get(self, request, *args, **kwargs):
        # TODO: business logic to check the application may be lodged.
        # Rule: application state must be 'draft'.
        app = self.get_object()
        if app.state != app.APP_STATE_CHOICES.draft:
            # TODO: better/explicit error response.
            messages.error(self.request, 'This application cannot be lodged!')
            return HttpResponseRedirect(app.get_absolute_url())
        return super(ApplicationLodge, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        """Override form_valid to generate an "Assess" task on the new
        application (no assignee) and change its status.
        """
        app = self.get_object()
        app.state = app.APP_STATE_CHOICES.with_admin
        app.assignee = None
        app.save()
        Task.objects.create(
            application=self.object, task_type=Task.TASK_TYPE_CHOICES.assess,
            status=Task.TASK_STATUS_CHOICES.ongoing)
        return HttpResponseRedirect(self.get_success_url())


class ApplicationRefer(LoginRequiredMixin, CreateView):
    """A view to create a Referral object on an Application (if allowed).
    """
    model = Referral
    form_class = ReferralForm

    def get(self, request, *args, **kwargs):
        # TODO: business logic to check the application may be referred.
        # Rule: application state must be 'with admin' or 'with referee'
        app = Application.objects.get(pk=self.kwargs['pk'])
        if app.state not in [app.APP_STATE_CHOICES.with_admin, app.APP_STATE_CHOICES.with_referee]:
            # TODO: better/explicit error response.
            messages.error(self.request, 'This application cannot be referred!')
            return HttpResponseRedirect(app.get_absolute_url())
        return super(ApplicationRefer, self).get(request, *args, **kwargs)

    def get_success_url(self):
        """Override to redirect to the referral's parent application detail view.
        """
        return reverse('application_detail', args=(self.object.application.pk,))

    def get_context_data(self, **kwargs):
        context = super(ApplicationRefer, self).get_context_data(**kwargs)
        context['application'] = Application.objects.get(pk=self.kwargs['pk'])
        return context

    def get_initial(self):
        initial = super(ApplicationRefer, self).get_initial()
        # TODO: set the default period value based on application type.
        initial['period'] = 21
        return initial

    def form_valid(self, form):
        app = Application.objects.get(pk=self.kwargs['pk'])
        self.object = form.save(commit=False)
        self.object.application = app
        self.object.sent_date = date.today()
        self.object.save()
        # Set the application status to 'with referee'.
        app.state = app.APP_STATE_CHOICES.with_referee
        app.save()
        # TODO: the process of sending the application to the referee.
        # TODO: update the communication log.
        return super(ApplicationRefer, self).form_valid(form)


class ConditionCreate(LoginRequiredMixin, CreateView):
    """A view for a referee or an internal user to create a Condition object
    on an Application.
    """
    model = Condition
    form_class = ConditionCreateForm

    def get_context_data(self, **kwargs):
        context = super(ConditionCreate, self).get_context_data(**kwargs)
        context['application'] = Application.objects.get(pk=self.kwargs['pk'])
        return context

    def get_success_url(self):
        """Override to redirect to the condition's parent application detail view.
        """
        return reverse('application_detail', args=(self.object.application.pk,))

    def get(self, request, *args, **kwargs):
        # TODO: business logic to check that a condition can be created.
        return super(ConditionCreate, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        app = Application.objects.get(pk=self.kwargs['pk'])
        self.object = form.save(commit=False)
        self.object.application = app
        # If a referral exists for the parent application for this user,
        # link that to the new condition.
        if Referral.objects.filter(application=app, referee=self.request.user).exists():
            self.object.referral = Referral.objects.get(application=app, referee=self.request.user)
            # TODO: record some feedback on the referral.
        return super(ConditionCreate, self).form_valid(form)


class ApplicationAssign(LoginRequiredMixin, UpdateView):
    """A view to allow an application to be assigned to an assessor.
    """
    model = Application
    form_class = ApplicationAssignForm

    def get(self, request, *args, **kwargs):
        # TODO: business logic to check the application may be assigned.
        return super(ApplicationAssign, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.state = self.object.APP_STATE_CHOICES.with_assessor
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class ReferralComplete(LoginRequiredMixin, UpdateView):
    """A view to allow an application to be assigned to an assessor.
    """
    model = Referral
    form_class = ReferralCompleteForm

    def get(self, request, *args, **kwargs):
        # Business rule: only the referee can mark a referral "complete".
        referral = self.get_object()
        if referral.referee != request.user:
            messages.error(self.request, 'You are unable to mark this referral as complete!')
            return HttpResponseRedirect(referral.application.get_absolute_url())
        return super(ReferralComplete, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.response_date = date.today()
        self.object.save()
        return HttpResponseRedirect(self.object.application.get_absolute_url())


class ApplicationApprove(LoginRequiredMixin, UpdateView):
    """A view to allow an application to be assigned to an assessor.
    TODO: refactor this view to share the ApplicationAssign view logic.
    """
    model = Application
    form_class = ApplicationApproveForm

    def get(self, request, *args, **kwargs):
        # Rule: only the assignee can perform this action.
        # TODO: any other business rules.
        app = self.get_object()
        if app.assignee != request.user:
            messages.error(self.request, 'You are unable to assign this application for approval/issue!')
            return HttpResponseRedirect(app.get_absolute_url())
        return super(ApplicationApprove, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.state = self.object.APP_STATE_CHOICES.with_manager
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class ApplicationIssue(LoginRequiredMixin, UpdateView):
    """A view to allow a manager to issue an assessed application.
    """
    model = Application
    form_class = ApplicationIssueForm

    def get(self, request, *args, **kwargs):
        # Rule: only the assignee can perform this action.
        # TODO: any other business rules.
        app = self.get_object()
        if app.assignee != request.user:
            messages.error(self.request, 'You are unable to issue this application!')
            return HttpResponseRedirect(app.get_absolute_url())
        return super(ApplicationIssue, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        d = form.cleaned_data
        if d['assessment'] == 'issue':
            self.object.state = self.object.APP_STATE_CHOICES.issued
            self.object.assignee = None
        elif d['assessment'] == 'decline':
            self.object.state = self.object.APP_STATE_CHOICES.declined
            self.object.assignee = None
        # TODO: logic for the manager to select who to assign it back to.
        #elif d['assessment'] == 'return':
        #    self.object.state = self.object.APP_STATE_CHOICES.with_assessor
        # TODO: logic around emailing/posting the application to the customer.
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


'''
class TaskReassign(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskReassignForm
    template_name = 'applications/task_form.html'

    def get(self, request, *args, **kwargs):
        # TODO: business logic to check that task can be reassigned.
        return super(TaskReassign, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        # TODO: business logic to ensure valid assignee.
        return super(TaskReassign, self).form_valid(form)

    def get_success_url(self):
        """Override to redirect to the task's parent application detail view.
        """
        return reverse('application_detail', args=(self.object.application.pk,))
'''
