from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView
from .models import Application, Task
from .forms import ApplicationForm, TaskReassignForm


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

    def form_valid(self, form):
        """Override form_valid to generate an "Assess" task on the new
        application, assigned to the request user.
        """
        self.object = form.save()
        Task.objects.create(
            application=self.object, task_type=Task.TASK_TYPE_CHOICES.assess,
            status=Task.TASK_STATUS_CHOICES.ongoing, assignee=self.request.user)
        return HttpResponseRedirect(self.get_success_url())


class ApplicationDetail(DetailView):
    model = Application


class ApplicationUpdate(UpdateView):
    model = Application
    form_class = ApplicationForm


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
