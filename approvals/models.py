from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from applications.models import Application, Record
from django.conf import settings
from django.db import models
from model_utils import Choices

@python_2_unicode_compatible
class Approvals(models.Model):
     """This model represents an approvals by a customer to P&W for a single
     permit, licence/permit, part 5, etc.
     """

     APPROVAL_STATE_CHOICES = Choices(
        (1, 'current', ('Current')),
        (2, 'expired', ('Expired')),
        (3, 'cancelled', ('Cancelled')),
        (4, 'surrendered', ('Surrendered')),
        (5, 'suspended', ('Suspended'))
     )

     app_type = models.IntegerField(choices=Application.APP_TYPE_CHOICES)
     title = models.CharField(max_length=254)
     applicant = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.PROTECT, related_name='applicant_holder') 
     start_date = models.DateField(null=True, blank=True)
     expiry_date = models.DateField(null=True, blank=True)
     status = models.IntegerField(choices=APPROVAL_STATE_CHOICES) 
     approval_document = models.ForeignKey(Record, null=True, blank=True, related_name='approval_document')

     def __str__(self):
        if self.id:
            return '{} ({})'.format(self.title, self.get_category_display())
        return self.name

