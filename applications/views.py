from __future__ import unicode_literals
from datetime import date
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView
from .models import Application, Referral, Task
from .forms import ApplicationForm, ApplicationLodgeForm, ReferralForm, TaskReassignForm


class HomePage(TemplateView):
    # TODO: rename this view to something like UserDashboard.
    template_name = 'applications/home_page.html'

    def get_context_data(self, **kwargs):
        context = super(HomePage, self).get_context_data(**kwargs)
        context['page_heading'] = 'Home Page'
        context['tasks'] = Task.objects.filter(
            status=Task.TASK_STATUS_CHOICES.ongoing, assignee=self.request.user)
        return context


class ApplicationList(ListView):
    model = Application


class ApplicationCreate(CreateView):
    form_class = ApplicationForm
    template_name = 'applications/application_form.html'


class ApplicationDetail(DetailView):
    model = Application

    def get_context_data(self, **kwargs):
        context = super(ApplicationDetail, self).get_context_data(**kwargs)
        app = self.get_object()
        # Rule: if the application status is 'draft', it can be lodged.
        if app.state == app.APP_STATE_CHOICES.draft:
            context['may_lodge'] = True
        # Rule: if the application status is 'with admin' or 'with referee', it can be referred.
        app = Application.objects.get(pk=self.kwargs['pk'])
        if app.state in [app.APP_STATE_CHOICES.with_admin, app.APP_STATE_CHOICES.with_referee]:
            context['may_refer'] = True
        return context


class ApplicationUpdate(UpdateView):
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


class ApplicationLodge(UpdateView):
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
        app.save()
        Task.objects.create(
            application=self.object, task_type=Task.TASK_TYPE_CHOICES.assess,
            status=Task.TASK_STATUS_CHOICES.ongoing)
        return HttpResponseRedirect(self.get_success_url())


class ApplicationRefer(CreateView):
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


class TaskReassign(UpdateView):
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
