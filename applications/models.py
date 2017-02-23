from __future__ import unicode_literals

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField
from django.core.urlresolvers import reverse
from django.utils.encoding import python_2_unicode_compatible
from dpaw_utils.models import ActiveMixin
from model_utils import Choices

from accounts.models import Organisation

@python_2_unicode_compatible
class Document(ActiveMixin):
    """This model represents a document or record that needs to be saved for
    future reference. It also records metadata and optional text content to be
    indexed for search.
    """
    DOC_CATEGORY_CHOICES = Choices(
        (1, 'consent', ('Landowner consent')),
        (2, 'deed', ('Deed')),
        (3, 'assessment', ('Assessment report')),
        (4, 'referee_response', ('Referee response')),
        (5, 'lodgement', ('Lodgement document')),
    )
    upload = models.FileField(max_length=512, upload_to='uploads/%Y/%m/%d')
    name = models.CharField(max_length=256)
    category = models.IntegerField(choices=DOC_CATEGORY_CHOICES, null=True, blank=True)
    metadata = JSONField(null=True, blank=True)
    text_content = models.TextField(null=True, blank=True, editable=False)  # Text for indexing

    def __str__(self):
        if self.category:
            return '{} ({})'.format(self.name, self.get_category_display())
        return self.name


@python_2_unicode_compatible
class Application(ActiveMixin):
    """This model represents an application by a customer to P&W for a single
    permit, licence/permit, part 5, etc.
    """
    APP_TYPE_CHOICES = Choices(
        (1, 'permit', ('Permit')),
        (2, 'licence', ('Licence/permit')),
        (3, 'part5', ('Part 5')),
        (4, 'emergency', ('Emergency works')),
    )
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.PROTECT)
    organisation = models.ForeignKey(Organisation, blank=True, null=True, on_delete=models.PROTECT)
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
    documents = models.ManyToManyField(Document, blank=True)
    # TODO: Vessel details

    def __str__(self):
        return '{}: {} - {} ({})'.format(self.pk, self.get_app_type_display(), self.title, self.state)

    def get_absolute_url(self):
        return reverse('application_detail', args=(self.pk,))


@python_2_unicode_compatible
class Location(ActiveMixin):
    """This model represents a single spatial location associated with an
    application.
    """
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    lot = models.CharField(max_length=256, null=True, blank=True)
    reserve = models.CharField(max_length=256, null=True, blank=True)
    suburb = models.CharField(max_length=256, null=True, blank=True)
    intersection = models.CharField(max_length=256, null=True, blank=True)
    # TODO: validation related to LGA name (possible FK).
    lga = models.CharField(max_length=256, null=True, blank=True)
    poly = models.PolygonField(null=True, blank=True)
    documents = models.ManyToManyField(Document, blank=True)

    def __str__(self):
        return 'Location {} ({})'.format(self.pk, self.application)


@python_2_unicode_compatible
class Condition(ActiveMixin):
    """This model represents a condition of approval for an application
    (either proposed by a referee or applied by P&W).
    """
    CONDITION_STATUS_CHOICES = Choices(
        (1, 'proposed', ('Proposed')),
        (2, 'applied', ('Applied')),
        (3, 'cancelled', ('Cancelled')),
    )
    application = models.ForeignKey(Application, on_delete=models.PROTECT)
    condition = models.TextField(blank=True, null=True)
    status = models.IntegerField(choices=CONDITION_STATUS_CHOICES, default=CONDITION_STATUS_CHOICES.proposed)
    documents = models.ManyToManyField(Document, blank=True)
    # TODO: Parent condition (self-reference from proposed condition)
    # TODO: Due date
    # TODO: Recurrence
    # TODO: Start date
    # TODO: Expiry date

    def __str__(self):
        return 'Condition {} ({})'.format(self.pk, self.application)


@python_2_unicode_compatible
class Task(ActiveMixin):
    """This model represents a job that an internal user needs to undertake
    with an application.
    """
    TASK_TYPE_CHOICES = Choices(
        (1, 'assess', ('Assess an application')),
        (2, 'refer', ('Refer an application for comment')),
        (3, 'compliance', ('Assess compliance with a condition')),
    )
    TASK_STATUS_CHOICES = Choices(
        (1, 'ongoing', ('Ongoing')),
        (2, 'complete', ('Complete')),
        (3, 'cancelled', ('Cancelled')),
    )
    application = models.ForeignKey(Application, on_delete=models.PROTECT)
    task_type = models.IntegerField(choices=TASK_TYPE_CHOICES)
    status = models.IntegerField(choices=TASK_STATUS_CHOICES)
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.PROTECT)
    description = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    completed_date = models.DateField(blank=True, null=True)
    documents = models.ManyToManyField(Document, blank=True)

    def __str__(self):
        return 'Task {}: {} ({})'.format(self.pk, self.get_task_type_display(), self.get_status_display())
