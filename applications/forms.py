from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.forms import ModelForm
from .models import Application, Task


class ApplicationForm(ModelForm):

    class Meta:
        model = Application
        fields = ['app_type', 'title', 'description', 'submit_date']

    def __init__(self, *args, **kwargs):
        super(ApplicationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'id_form_create_application'
        self.helper.form_method = 'POST'  # This is default.
        self.helper.form_action = 'application_create'  # Calls reverse().
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-1 col-md-2'
        self.helper.field_class = 'col-lg-11 col-md-10'
        self.helper.add_input(Submit('save', 'Save', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel'))


class TaskReassignForm(ModelForm):

    class Meta:
        model = Task
        fields = ['assignee', ]

    def __init__(self, *args, **kwargs):
        super(TaskReassignForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.add_input(Submit('reassign', 'Reassign', css_class='btn-lg'))
        self.helper.add_input(Submit('cancel', 'Cancel'))
        self.fields['assignee'].required = True
        # TODO: business logic to limit the assignee queryset.
