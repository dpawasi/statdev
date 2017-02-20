from __future__ import unicode_literals

from accounts.models import EmailUser
from django.contrib.gis.db import models
from django.core.urlresolvers import reverse
from dpaw_utils.models import ActiveMixin
from model_utils import Choices


class Application(ActiveMixin):
    APP_TYPE_CHOICES = Choices(
        (1, 'permit', ('Permit')),
        (2, 'licence', ('Licence/permit')),
        (3, 'part5', ('Part 5')),
        (4, 'emergency', ('Emergency works')),
    )
    app_type = models.IntegerField(choices=APP_TYPE_CHOICES)
    state = models.CharField(max_length=64, default='draft', editable=False)
    title = models.CharField(max_length=256)
    description = models.TextField(null=True, blank=True)
    submit_date = models.DateField()
    proposed_commence = models.DateField(null=True, blank=True)
    proposed_end = models.DateField(null=True, blank=True)
    cost = models.CharField(max_length=256, null=True, blank=True)
    project_no = models.CharField(max_length=256, null=True, blank=True)
    related_permits = models.TextField(null=True, blank=True)
    over_water = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('application_detail', args=(self.pk,))


class Location(ActiveMixin):
    application = models.ForeignKey(Application)
    lot = models.CharField(max_length=256, null=True, blank=True)
    reserve = models.CharField(max_length=256, null=True, blank=True)
    suburb = models.CharField(max_length=256, null=True, blank=True)
    intersection = models.CharField(max_length=256, null=True, blank=True)
    lga = models.CharField(max_length=256, null=True, blank=True)
    poly = models.PolygonField(null=True, blank=True)


class Condition(ActiveMixin):
    CONDITION_STATUS_CHOICES = Choices(
        (1, 'proposed', ('Proposed')),
        (2, 'applied', ('Applied')),
        (3, 'cancelled', ('Cancelled')),
    )
    application = models.ForeignKey(Application)
    condition = models.TextField(blank=True, null=True)
    status = models.IntegerField(choices=CONDITION_STATUS_CHOICES, default=CONDITION_STATUS_CHOICES.proposed)


# TaskType


class Task(ActiveMixin):
    TASK_TYPE_CHOICES = Choices(
        (1, 'assess', ('Assess an application')),
        (2, 'refer', ('Refer an application for comment')),
    )
    TASK_STATUS_CHOICES = Choices(
        (1, 'ongoing', ('Ongoing')),
        (2, 'complete', ('Complete')),
    )
    application = models.ForeignKey(Application)
    task_type = models.IntegerField(choices=TASK_TYPE_CHOICES)
    status = models.IntegerField(choices=TASK_STATUS_CHOICES)
    assignee = models.ForeignKey(EmailUser, blank=True, null=True)
