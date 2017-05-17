from __future__ import unicode_literals
from datetime import timedelta
from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField
from django.core.urlresolvers import reverse
from django.utils.encoding import python_2_unicode_compatible
from model_utils import Choices
from accounts.models import Organisation
from datetime import datetime
from django.contrib.auth.models import Group

@python_2_unicode_compatible
class Document(models.Model):
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
        (6, 'draft', ('Draft document')),
        (7, 'final', ('Final document')),
        (8, 'determination', ('Determination document')),
        (9, 'completion', ('Completed document')),
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
class Vessel(models.Model):
    """This model represents a vessel/craft that will be used
    in relation to the application
    """
    VESSEL_TYPE_CHOICES = Choices(
        (0, 'vessel', ('Vessel')),
        (1, 'craft', ('Craft')),
    )

    vessel_type = models.SmallIntegerField(choices=VESSEL_TYPE_CHOICES, null=True, blank=True)
    name = models.CharField(max_length=256)
    vessel_id = models.CharField(max_length=256, null=True, blank=True, verbose_name='Vessel identification')
    registration = models.ManyToManyField(Document, blank=True)
    size = models.PositiveIntegerField(null=True, blank=True, verbose_name='size (m)')
    engine = models.PositiveIntegerField(null=True, blank=True, verbose_name='engine (kW)')
    passenger_capacity = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class ApplicationPurpose(models.Model):
    purpose = models.CharField(max_length=256)

    def __str__(self):
        return self.purpose


@python_2_unicode_compatible
class Application(models.Model):
    """This model represents an application by a customer to P&W for a single
    permit, licence/permit, part 5, etc.
    """
    APP_TYPE_CHOICES = Choices(
        (1, 'permit', ('Permit')),
        (2, 'licence', ('Licence/permit')),
        (3, 'part5', ('Part 5 - New Application')),
        (4, 'emergency', ('Emergency works')),
        (5, 'part5cr', ('Part 5 - Ammendment Request')),
        (6, 'part5amend', ('Part 5 - Amendment Application'))
    )
    APP_STATE_CHOICES = Choices(
        (1, 'draft', ('Draft')),
        (2, 'with_admin', ('With Admin Officer')),
        (3, 'with_referee', ('With Referrals')),
        (4, 'with_assessor', ('With Assessor')),
        (5, 'with_manager', ('With Manager')),
        (6, 'issued', ('Issued')),
        (7, 'issued_with_admin', ('Issued (with admin)')),
        (8, 'declined', ('Declined')),
        (9, 'new', ('New')),
        (10,'approved',('Approved')),
        (11 ,'expird', ('Expired')),
        (12 ,'with_director',('With Director')),
        (13 ,'with_exec', ('With Executive')),
        (14 ,'completed', ('Completed'))
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
    expire_date = models.DateField(blank=True, null=True)
    proposed_commence = models.DateField(null=True, blank=True)
    proposed_end = models.DateField(null=True, blank=True)
    issue_date = models.DateField(null=True, blank=True)
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
    land_owner_consent = models.ManyToManyField(Document, blank=True, related_name='land_owner_consent')
    deed = models.ForeignKey(Document, blank=True, null=True, related_name='deed')
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.PROTECT, related_name='Submitted_by')
    river_lease_require_river_lease = models.NullBooleanField(default=None, null=True, blank=True)
    river_lease_scan_of_application = models.ForeignKey(Document, null=True, blank=True, related_name='river_lease_scan_of_application')
    river_lease_reserve_licence = models.NullBooleanField(default=None, null=True, blank=True)
    river_lease_application_number = models.CharField(max_length=30, null=True, blank=True)
    proposed_development_current_use_of_land = models.TextField(null=True, blank=True)
    proposed_development_plans = models.ManyToManyField(Document, blank=True, related_name='proposed_development_plans')
    proposed_development_description = models.TextField(null=True, blank=True)
    document_draft = models.ForeignKey(Document, null=True, blank=True, related_name='document_draft')
    document_final = models.ForeignKey(Document, null=True, blank=True, related_name='document_final')
    document_determination = models.ForeignKey(Document, null=True, blank=True, related_name='document_determination')
    document_completion = models.ForeignKey(Document, null=True, blank=True, related_name='document_completion')
    publish_documents = models.DateField(null=True, blank=True)
    publish_draft_report = models.DateField(null=True, blank=True)
    publish_final_report = models.DateField(null=True, blank=True)
    routeid = models.IntegerField(null=True, blank=True, default=1) 
    assessment_start_date = models.DateField(null=True, blank=True)
    group = models.ForeignKey(Group, null=True, blank=True, related_name='application_group_assignment')

    def __str__(self):
        return 'Application {}: {} - {} ({})'.format(
            self.pk, self.get_app_type_display(), self.title, self.get_state_display())

    def get_absolute_url(self):
        return reverse('application_detail', args=(self.pk,))


@python_2_unicode_compatible
class PublicationFeedback(models.Model):
    PUB_STATES_CHOICES = Choices(
        (1, 'Western Australia', ('Western Australia')),
        (2, 'New South Wales', ('New South Wales')),
        (3, 'Victoria', ('Victoria')),
        (4, 'South Australia', ('South Australia')),
        (5, 'Northern Territory', ('Northern Territory')),
        (6, 'Queensland', ('Queensland')),
        (7, 'Australian Capital Territory', ('Australian Capital Territory')),
        (8, 'Tasmania', ('Tasmania')),
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
    documents = models.ManyToManyField(Document, blank=True, related_name='feedback')
    status = models.CharField(max_length=20)

    def __str__(self):
        return 'PublicationFeedback {} ({})'.format(self.pk, self.application)


@python_2_unicode_compatible
class PublicationNewspaper(models.Model):
    """This model represents Application Published in newspapert
    """

    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    newspaper = models.CharField(max_length=150)
    documents = models.ManyToManyField(Document, blank=True, related_name='newspaper')

    def __str__(self):
        return 'PublicationNewspaper {} ({})'.format(self.pk, self.application)


@python_2_unicode_compatible
class PublicationWebsite(models.Model):
    """This model represents Application Published in Website
    """

    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    original_document = models.ForeignKey(Document, blank=True, null=True, related_name='original_document')
    published_document = models.ForeignKey(Document, blank=True, null=True, related_name='published_document')

    def __str__(self):
        return 'PublicationWebsite {} ({})'.format(self.pk, self.application)


@python_2_unicode_compatible
class Location(models.Model):
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
    title_volume = models.CharField(max_length=256, null=True, blank=True)
    folio = models.CharField(max_length=30, null=True, blank=True)
    dpd_number = models.CharField(max_length=30, null=True, blank=True)
    location = models.CharField(max_length=256, null=True, blank=True)  # this seem like it different from street address based on the example form.
    street_number_name = models.CharField(max_length=256, null=True, blank=True)

    def __str__(self):
        return 'Location {} ({})'.format(self.pk, self.application)


@python_2_unicode_compatible
class Referral(models.Model):
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
class Condition(models.Model):
    """This model represents a condition of approval for an application
    (either proposed by a referee or applied by P&W).
    """
    CONDITION_STATUS_CHOICES = Choices(
        (1, 'proposed', ('Proposed')),
        (2, 'applied', ('Applied')),
        (3, 'rejected', ('Rejected')),
        (4, 'cancelled', ('Cancelled')),
    )
    CONDITION_RECUR_CHOICES = Choices(
        (1, 'weekly', ('Weekly')),
        (2, 'monthly', ('Monthly')),
        (3, 'annually', ('Annually')),
    )
    application = models.ForeignKey(Application, on_delete=models.PROTECT)
    condition = models.TextField(blank=True, null=True)
    referral = models.ForeignKey(Referral, null=True, blank=True, on_delete=models.PROTECT)
    status = models.IntegerField(choices=CONDITION_STATUS_CHOICES, default=CONDITION_STATUS_CHOICES.proposed)
    documents = models.ManyToManyField(Document, blank=True)
    due_date = models.DateField(blank=True, null=True)
    # Rule: recurrence patterns (if present) begin on the due date.
    recur_pattern = models.IntegerField(choices=CONDITION_RECUR_CHOICES, null=True, blank=True)
    recur_freq = models.PositiveIntegerField(
        null=True, blank=True, verbose_name='recurrence frequency',
        help_text='How frequently is the recurrence pattern applied (e.g. every 2 months)')

    def __str__(self):
        return 'Condition {}: {}'.format(self.pk, self.condition)


@python_2_unicode_compatible
class Compliance(models.Model):
    """This model represents a request for confirmation of fulfilment of the
    requirements for a single condition, based upon supplied evidence.
    """
    COMPLIANCE_STATUS_CHOICES = Choices(
        (1, 'requested', ('Requested')),
        (2, 'approved', ('Approved')),
        (3, 'returned', ('Returned')),
    )
    condition = models.ForeignKey(Condition, on_delete=models.PROTECT)
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.PROTECT, related_name='compliance_applicant')
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.PROTECT, related_name='compliance_assignee')
    status = models.IntegerField(choices=COMPLIANCE_STATUS_CHOICES, default=COMPLIANCE_STATUS_CHOICES.requested)
    submit_date = models.DateField()
    compliance = models.TextField(blank=True, null=True, help_text='Information to fulfil requirement of condition.')
    comments = models.TextField(blank=True, null=True)
    approve_date = models.DateField(blank=True, null=True)
    documents = models.ManyToManyField(Document, blank=True)

    def __str__(self):
        return 'Compliance {} ({})'.format(self.pk, self.condition)


class Communication(models.Model):
      """This model represents the communication model 
      """
      application = models.ForeignKey(Application, on_delete=models.PROTECT)
      details = models.TextField(blank=True, null=True)
      documents = models.ManyToManyField(Document, blank=True, related_name='communication_docs')
      state = models.IntegerField() # move to foreign key once APP_STATE_CHOICES becomes a model 
      created = models.DateTimeField(("Date"), default=datetime.now())




