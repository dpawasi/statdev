"""
HTML Widget classes
"""

from __future__ import unicode_literals

from django.forms.utils import flatatt, to_current_timezone
from django.utils.html import conditional_escape, format_html, html_safe
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy
from django.forms import Media, MediaDefiningClass, Widget, CheckboxInput
from django.utils.safestring import SafeText

__all__ = (
    'ClearableMultipleFileInput', 'FileInput',
)

MEDIA_TYPES = ('css', 'js')

class InputMultiFile(Widget):
    """
    Base class for all <input> widgets (except type='checkbox' and
    type='radio', which are special).
    """
    input_type = None  # Subclasses must define this.

    def format_value(self, value):
        if self.is_localized:
            return formats.localize_input(value)
        return value

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name, )
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            final_attrs['value'] = force_text(self.format_value(value))
        return format_html('<input{} />', flatatt(final_attrs))

class FileInput(InputMultiFile):
    input_type = 'file'
    needs_multipart_form = True

    def render(self, name, value, attrs=None):
        return super(FileInput, self).render(name, None, attrs=attrs)

    def value_from_datadict(self, data, files, name):
        "File widgets take data from FILES, not POST"
        return files.get(name)

    def value_omitted_from_data(self, data, files, name):
        return name not in files

class ClearableMultipleFileInput(FileInput):
    initial_text = ugettext_lazy('Currently testing')
    input_text = ugettext_lazy('Change')
    clear_checkbox_label = ugettext_lazy('Clear')

    template_with_initial = (
        '%(initial_text)s: <a href="%(initial_url)s">%(initial)s</a> '
        '%(clear_template)s<br />%(input_text)s: %(input)s'
    )

    template_with_clear = '%(clear)s <label for="%(clear_checkbox_id)s">%(clear_checkbox_label)s</label>'

    def clear_checkbox_name(self, name):
        """
        Given the name of the file input, return the name of the clear checkbox
        input.
        """
        return name + '-clear'

    def clear_checkbox_id(self, name):
        """
        Given the name of the clear checkbox input, return the HTML id for it.
        """
        return name + '_id'

    def is_initial(self, value):
        """
        Return whether value is considered to be initial value.
        """
        return bool(value and getattr(value, 'url', False))

    def get_template_substitution_values(self, value):
        """
        Return value-related substitutions.
        """
        #return {
        #    'initial': conditional_escape(value),
        #    'initial_url': conditional_escape(value.url),
        #}

    def render(self, name, value, attrs=None):
        substitutions = {
            'initial_text': self.initial_text,
            'input_text': self.input_text,
            'clear_template': '',
            'clear_checkbox_label': self.clear_checkbox_label,
        }

        template = '%(input)s %(clearfiles)s'
        substitutions['input'] = super(ClearableMultipleFileInput, self).render(name, value, attrs)
        substitutions['clearfiles'] = ''
        if type(value) is list:
           substitutions['clearfiles'] = "<div class='col-sm-12'><Label>Files:</Label></div>"
           if value:
              for fi in value:
                  if fi:
                      substitutions['clearfiles'] += "<div class='col-sm-8'><A HREF='/media/"+fi['path']+"'>"+SafeText(fi['path'])[19:]+"</A>"+"</div>"
                      substitutions['clearfiles'] += "<div class='col-sm-4'><input type='checkbox' "
                      substitutions['clearfiles'] += " name='"+name+"-clear_multifileid-"+str(fi['fileid'])+"'"
                      substitutions['clearfiles'] += " id='"+name+"-clear_multifileid-"+str(fi['fileid'])+"'"
                      substitutions['clearfiles'] += " > Clear</div>"

        if self.is_initial(value):
            template = self.template_with_initial
            substitutions.update(self.get_template_substitution_values(value))
            if not self.is_required:
                checkbox_name = self.clear_checkbox_name(name)
                checkbox_id = self.clear_checkbox_id(checkbox_name)
                substitutions['clear_checkbox_name'] = conditional_escape(checkbox_name)
                substitutions['clear_checkbox_id'] = conditional_escape(checkbox_id)
                substitutions['clear'] = CheckboxInput().render(checkbox_name, False, attrs={'id': checkbox_id})
                substitutions['clear_template'] = self.template_with_clear % substitutions

        return mark_safe(template % substitutions)

    def value_from_datadict(self, data, files, name):
        upload = super(ClearableMultipleFileInput, self).value_from_datadict(data, files, name)
        if not self.is_required and CheckboxInput().value_from_datadict(
                data, files, self.clear_checkbox_name(name)):

            if upload:
                # If the user contradicts themselves (uploads a new file AND
                # checks the "clear" checkbox), we return a unique marker
                # object that FileField will turn into a ValidationError.
                return FILE_INPUT_CONTRADICTION
            # False signals to clear any existing value, as opposed to just None
            return False
        return upload

    def use_required_attribute(self, initial):
        return super(ClearableMultipleFileInput, self).use_required_attribute(initial) and not initial

    def value_omitted_from_data(self, data, files, name):
        return (
            super(ClearableMultipleFileInput, self).value_omitted_from_data(data, files, name) and
            self.clear_checkbox_name(name) not in data
        )

