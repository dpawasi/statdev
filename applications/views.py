from django.views.generic import TemplateView, ListView, DetailView, CreateView
from .models import Application


class HomePage(TemplateView):
    template_name = 'applications/home_page.html'

    def get_context_data(self, **kwargs):
        context = super(HomePage, self).get_context_data(**kwargs)
        context['page_heading'] = 'Home Page'
        context['page_content'] = 'This is the Statutory Development application.'
        return context


class ApplicationList(ListView):
    model = Application


class ApplicationDetail(DetailView):
    model = Application


class ApplicationCreate(CreateView):
    model = Application
    fields = ['app_type', 'title', 'description', 'submit_date']
