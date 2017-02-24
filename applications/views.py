from __future__ import unicode_literals
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView
from .models import Application, Task
from .forms import ApplicationForm, ApplicationLodgeForm, TaskReassignForm


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
        # Business rule: if the application status is 'draft', it can be lodged.
        if app.state == 'draft':
            context['may_lodge'] = True
        return context


class ApplicationUpdate(UpdateView):
    model = Application
    form_class = ApplicationForm


class ApplicationLodge(UpdateView):
    model = Application
    form_class = ApplicationLodgeForm

    def get(self, request, *args, **kwargs):
        # TODO: business logic to check the application may be lodged.
        # Business rules: application state must be 'draft'.
        app = self.get_object()
        if app.state != 'draft':
            messages.error(self.request, 'This application cannot be lodged!')
            return HttpResponseRedirect(app.get_absolute_url())
        return super(ApplicationLodge, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        """Override form_valid to generate an "Assess" task on the new
        application (no assignee) and change its status.
        """
        app = self.get_object()
        app.state = 'with admin'
        app.save()
        Task.objects.create(
            application=self.object, task_type=Task.TASK_TYPE_CHOICES.assess,
            status=Task.TASK_STATUS_CHOICES.ongoing)
        return HttpResponseRedirect(self.get_success_url())


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
