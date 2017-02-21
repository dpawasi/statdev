from django.http import HttpResponseRedirect
from django.views.generic import TemplateView, ListView, DetailView, CreateView
from .models import Application, Task
from .forms import ApplicationForm


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


class ApplicationDetail(DetailView):
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
