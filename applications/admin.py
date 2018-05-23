from django.contrib.admin import register, ModelAdmin
from .models import (
    Record, Vessel, ApplicationPurpose, Application, Location, Referral,
    Condition, Compliance, Delegate, ApplicationInvoice, Communication, Craft, 
    OrganisationContact, OrganisationPending, OrganisationExtras,PublicationFeedback, 
    PublicationWebsite,ComplianceGroup, StakeholderComms, ConditionPredefined)


@register(Record)
class RecordAdmin(ModelAdmin):
    list_display = ('name', 'category', 'upload')
    list_filter = ('category',)
    search_fields = ('name',)


@register(Vessel)
class VesselAdmin(ModelAdmin):
    filter_horizontal = ('registration',)
    list_display = ('name', 'vessel_type', 'vessel_id')
    list_filter = ('vessel_type',)
    search_fields = ('name', 'vessel_id')


@register(ApplicationPurpose)
class ApplicationPurposeAdmin(ModelAdmin):
    search_fields = ('purpose',)


@register(Application)
class ApplicationAdmin(ModelAdmin):
    date_hierarchy = 'submit_date'
    filter_horizontal = ('records',)
    list_display = ('id', 'app_type', 'applicant', 'organisation', 'state', 'title', 'submit_date', 'assignee', 'expire_date')
    list_filter = ('app_type', 'state')
    search_fields = ('applicant__email', 'organisation__name', 'assignee__email', 'title')


@register(Location)
class LocationAdmin(ModelAdmin):
    filter_horizontal = ('records',)
    search_fields = ('application__title', 'lot', 'reserve', 'suburb', 'intersection', 'lga')


@register(Referral)
class ReferralAdmin(ModelAdmin):
    date_hierarchy = 'sent_date'
    filter_horizontal = ('records',)
    list_display = ('id', 'application', 'referee', 'sent_date', 'period', 'status', 'expire_date', 'response_date')
    list_filter = ('status',)
    search_fields = ('application__title', 'referee__email', 'details', 'feedback')


@register(Condition)
class ConditionAdmin(ModelAdmin):
    filter_horizontal = ('records',)
    list_display = ('id', 'referral', 'status', 'due_date', 'recur_pattern')
    list_filter = ('status', 'recur_pattern')
    search_fields = ('application__title', 'condition')


@register(Compliance)
class ComplianceAdmin(ModelAdmin):
    date_hierarchy = 'submit_date'
    filter_horizontal = ('records',)
    list_display = ('__str__', 'applicant', 'approval_id','assignee', 'status', 'submit_date', 'approve_date','due_date','compliance_group')
    search_fields = ('applicant__email', 'assignee__email', 'compliance', 'comments')

@register(ComplianceGroup)
class ComplianceGroupAdmin(ModelAdmin):
    list_display = ('__str__', 'applicant', 'approval_id','assignee', 'status', 'due_date')
    search_fields = ('applicant__email', 'assignee__email', 'compliance', 'comments')

@register(Delegate)
class DelegateAdmin(ModelAdmin):
    pass

@register(ApplicationInvoice)
class ApplicationInvoiceAdmin(ModelAdmin):
    pass

@register(Communication)
class CommunicationAdmin(ModelAdmin):
    list_display = ('application', 'comms_to', 'comms_from','subject','comms_type','details','created')
    search_fields = ('comms_to','comms_from','subject','details')

@register(Craft)
class CraftAdmin(ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@register(OrganisationContact)
class CommunicationAdmin(ModelAdmin):
    list_display = ('email','first_name','last_name','phone_number','mobile_number','fax_number')
    search_fields = ('email','first_name','last_name','phone_number','mobile_number','fax_number')

@register(OrganisationPending)
class OrganisationPending(ModelAdmin):
    list_display = ('name','abn','identification','postal_address','billing_address')
    search_fields = ('name','abn','identification','postal_address','billing_address')

@register(OrganisationExtras)
class OrganisationExtras(ModelAdmin):
    list_display = ('organisation','pin1','pin2')
    search_fields = ('organisation','pin1','pin2')

@register(PublicationFeedback)
class OrganisationExtras(ModelAdmin):
    list_display = ('name','address','suburb')
    search_fields = ('name','address','suburb')

@register(PublicationWebsite)
class PublicationWebsite(ModelAdmin):
    list_display = ('application','original_document','published_document')
    search_fields = ('application','original_document','published_document')

@register(StakeholderComms)
class StakeholderComms(ModelAdmin):
    list_display = ('application','email','name','sent_date','role')
    search_fields = ('application','email','name','sent_date','role')


@register(ConditionPredefined)
class ConditionPredefined(ModelAdmin):
    list_display = ('title','condition','status')
    search_fields = ('title','condition','status')


