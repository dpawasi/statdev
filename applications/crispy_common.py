from __future__ import unicode_literals
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, HTML, Fieldset, MultiField, Div
from crispy_forms.bootstrap import FormActions
from django.conf import settings
from django.forms import Form, ModelForm, ChoiceField, FileField, CharField, Textarea, ClearableFileInput, HiddenInput, Field


def crispy_heading(collapse_id, header_id , heading_label):
    #    return Div(id=header_id, css_class='panel-heading')
     return Div(HTML('<h3 class="panel-title" ><a role="button" data-toggle="collapse" href="#'+collapse_id+'" aria-expanded="false" aria-controls="application_collapse"><span class="glyphicon glyphicon-plus"></span>'+heading_label+' </a></h3>'), id=header_id, css_class='panel-heading')

def crispy_box(collapse_id, header_id , heading_label,*field_set):
     print field_set[0]
 #    fieldsets = {} 
#     for f in field_set:
         #       print f
 #        fieldsets.append(f)
#         print fieldsets

     return Div(crispy_heading(collapse_id, header_id, heading_label),
                            Div(Div(
                              Fieldset('',
                                   *field_set
                            ), css_class='panel-body',
                          ), css_class="panel-collapse collapse in",id=collapse_id,
                    ), css_class='panel panel-default'
             )


def crispy_empty_box():
    return Div()
