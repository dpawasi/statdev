from __future__ import unicode_literals
from datetime import timedelta
from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField
from django.core.urlresolvers import reverse
from django.utils.encoding import python_2_unicode_compatible
from dpaw_utils.models import ActiveMixin
from model_utils import Choices
from datetime import datetime
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
class Vessel(ActiveMixin):
    """This model represents a vessel/craft that will be used
    in relation to the application
    """
    VESSEL_TYPE_CHOICES = Choices(
        (0, 'vessel', ('Vessel')),
        (1, 'craft', ('Craft')),
    )

    vessel_type = models.SmallIntegerField(choices=VESSEL_TYPE_CHOICES)
    name = models.CharField(max_length=256)
    vessel_id = models.CharField(max_length=256)
    registration = models.ManyToManyField(Document)
    size = models.IntegerField()
    engine = models.IntegerField()
    passenger_capacity = models.IntegerField()

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class ApplicationPurpose(ActiveMixin):
    purpose = models.CharField(max_length=256)

    def __str__(self):
        return self.purpose


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
    APP_STATE_CHOICES = Choices(
        (1, 'draft', ('Draft')),
        (2, 'with_admin', ('With admin')),
        (3, 'with_referee', ('With referee')),
        (4, 'with_assessor', ('With assessor')),
        (5, 'with_manager', ('With manager')),
        (6, 'issued', ('Issued')),
        (7, 'issued_with_admin', ('Issued (with admin)')),
        (8, 'declined', ('Declined')),
        (9, 'new', ('New')),
    )
    APP_LOCATION_CHOICES = Choices(
        (0, 'onland', ('On Land')),
        (1, 'onwater', ('On Water')),
        (2, 'both', ('Both')),
    )

    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.PROTECT, related_name='applicant')
    organisation = models.ForeignKey(Organisation, blank=True, null=True, on_delete=models.PROTECT)
    app_type = models.IntegerField(choices=APP_TYPE_CHOICES)
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.PROTECT, related_name='assignee')
    state = models.IntegerField(choices=APP_STATE_CHOICES, default=APP_STATE_CHOICES.draft, editable=False)
    title = models.CharField(max_length=256)
    description = models.TextField(null=True, blank=True)
    submit_date = models.DateField()
    proposed_commence = models.DateField(null=True, blank=True)
    proposed_end = models.DateField(null=True, blank=True)
    cost = models.CharField(max_length=256, null=True, blank=True)
    project_no = models.CharField(max_length=256, null=True, blank=True)
    related_permits = models.TextField(null=True, blank=True)
    over_water = models.BooleanField(default=False)
    documents = models.ManyToManyField(Document, blank=True, related_name='documents')
    vessels = models.ManyToManyField(Vessel, blank=True)
    purpose = models.ForeignKey(ApplicationPurpose, null=True, blank=True)
    max_participants = models.IntegerField(null=True, blank=True)
    proposed_location = models.SmallIntegerField(choices=APP_LOCATION_CHOICES, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    location_route_access = models.ForeignKey(Document, null=True, blank=True, related_name='location_route_access')
    jetties = models.TextField(null=True, blank=True)
    jetty_dot_approval = models.NullBooleanField(default=None)
    jetty_dot_approval_expiry = models.DateField(null=True, blank=True)
    drop_off_pick_up = models.TextField(null=True, blank=True)
    food = models.NullBooleanField(default=None)
    beverage = models.NullBooleanField(default=None)
    byo_alcohol = models.NullBooleanField(default=None)
    sullage_disposal = models.TextField(null=True, blank=True)
    waste_disposal = models.TextField(null=True, blank=True)
    refuel_location_method = models.TextField(null=True, blank=True)
    berth_location = models.TextField(null=True, blank=True)
    anchorage = models.TextField(null=True, blank=True)
    operating_details = models.TextField(null=True, blank=True)
    cert_survey = models.ForeignKey(Document, blank=True, null=True, related_name='cert_survey')
    cert_public_liability_insurance = models.ForeignKey(Document, blank=True, null=True, related_name='cert_public_liability_insurace')
    risk_mgmt_plan = models.ForeignKey(Document, blank=True, null=True, related_name='risk_mgmt_plan')
    safety_mgmt_procedures = models.ForeignKey(Document, blank=True, null=True, related_name='safety_mgmt_plan')
    brochures_itineries_adverts = models.ManyToManyField(Document, blank=True, related_name='brochures_itineries_adverts')
    other_supporting_docs = models.ManyToManyField(Document, blank=True, related_name='other_supporting_docs')
    land_owner_consent = models.ManyToManyField(Document, blank=True, related_name='land_owner_consent')
    deed = models.ForeignKey(Document, blank=True, null=True, related_name='deed')
    river_reserve_lease = models.NullBooleanField(default=None)
    current_land_use = models.TextField(null=True, blank=True)
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.PROTECT, related_name='Submitted_by')


    # Added for part 5 form.
    certificate_of_title_volume = models.CharField(max_length=256,null=True, blank=True)
    certificate_folio =  models.CharField(max_length=30,null=True, blank=True)
    certificate_dpd_number = models.CharField(max_length=30, null=True, blank=True)
    certificate_subject_lot_lot_number = models.CharField(max_length=30,null=True, blank=True)
    certificate_location = models.CharField(max_length=256,null=True, blank=True)
    certificate_reserve_number = models.CharField(max_length=30,null=True, blank=True)
    certificate_street_number_name = models.CharField(max_length=256,null=True, blank=True)
    certificate_town_suburb = models.CharField(max_length=100,null=True, blank=True)
    certificate_nearest_road_intersection = models.CharField(max_length=256,null=True, blank=True)
    river_lease_require_river_lease = models.NullBooleanField(default=None,null=True, blank=True)
    river_lease_scan_of_application = models.FileField(null=True, blank=True)
    river_lease_proposed_development = models.NullBooleanField(default=None,null=True, blank=True)
    river_lease_application_number = models.CharField(max_length=30,null=True, blank=True)
    proposed_development_cost = models.CharField(max_length=256, null=True, blank=True)
    proposed_development_current_use_of_land = models.TextField(null=True, blank=True)
    proposed_development_description = models.TextField(null=True, blank=True)
    proposed_development_plans = models.FileField(null=True, blank=True) 
    landowner_consent_signed = models.FileField(null=True, blank=True)
    deed_signed = models.FileField(null=True, blank=True)


    def __str__(self):
        return '{}: {} - {} ({})'.format(self.pk, self.get_app_type_display(), self.title, self.get_state_display())

    def get_absolute_url(self):
        return reverse('application_detail', args=(self.pk,))


@python_2_unicode_compatible
class PublicationFeedback(ActiveMixin):
    PUB_STATES_CHOICES = Choices(
        (1, 'Western Australia', ('Western Australia')),
        (2, 'New South Wales', ('New South Wales')),
        (3, 'Victoria', ('Victoria')),
        (4, 'South Australia', ('South Australia')),
		(5, 'Northern Territory', ('Northern Territory')),
		(6, 'Queensland', ('Queensland')),
		(7, 'Australian Capital Territory', ('Australian Capital Territory')),
		(8, 'Tasmania',('Tasmania')),
    )

    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    address = models.CharField(max_length=256)
    suburb = models.CharField(max_length=100)
    state = models.IntegerField(choices=PUB_STATES_CHOICES)
    postcode = models.CharField(max_length=4)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    comments = models.TextField(null=True, blank=True)
    documents = models.FileField()
    status = models.CharField(max_length=20)

    def __str__(self):
       return 'PublicationFeedback {} ({})'.format(self.pk, self.application)

@python_2_unicode_compatible
class PublicationNewspaper(ActiveMixin):
    """This model represents Application Published in newspapert
    """

    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    newspaper = models.CharField(max_length=150)
    documents = models.FileField()

    def __str__(self):
        return 'PublicationNewspaper {} ({})'.format(self.pk, self.application)

@python_2_unicode_compatible
class PublicationWebsite(ActiveMixin):
    """This model represents Application Published in Website 
    """

    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    original_document = models.FileField()
    published_document = models.FileField()

    def __str__(self):
        return 'PublicationWebsite {} ({})'.format(self.pk, self.application)


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
    # TODO: certificate of title fields (ref. screen 30)

    def __str__(self):
        return 'Location {} ({})'.format(self.pk, self.application)


@python_2_unicode_compatible
class Referral(ActiveMixin):
    """This model represents a referral of an application to a referee
    (external or internal) for comment/conditions.
    """
    REFERRAL_STATUS_CHOICES = Choices(
        (1, 'referred', ('Referred')),
        (2, 'responded', ('Responded')),
        (3, 'recalled', ('Recalled')),
        (4, 'expired', ('Expired')),
    )
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    referee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    details = models.TextField(blank=True, null=True)
    sent_date = models.DateField()
    period = models.PositiveIntegerField(verbose_name='period (days)')
    expire_date = models.DateField(blank=True, null=True, editable=False)
    response_date = models.DateField(blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)
    documents = models.ManyToManyField(Document, blank=True)
    status = models.IntegerField(choices=REFERRAL_STATUS_CHOICES, default=REFERRAL_STATUS_CHOICES.referred)

    class Meta:
        unique_together = ('application', 'referee')

    def __str__(self):
        return 'Referral {} to {} ({})'.format(self.pk, self.referee, self.application)

    def save(self, *args, **kwargs):
        """Override save to set the expire_date field.
        """
        self.expire_date = self.sent_date + timedelta(days=self.period)
        super(Referral, self).save(*args, **kwargs)


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
    referral = models.ForeignKey(Referral, null=True, blank=True, on_delete=models.PROTECT)
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
