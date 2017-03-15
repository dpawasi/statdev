from django.contrib import admin
from django.contrib.admin import register, ModelAdmin
from .models import Document, Vessel, ApplicationPurpose, Application, Location, Referral, Condition, Compliance, Task


@register(Document)
class DocumentAdmin(ModelAdmin):
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
    filter_horizontal = ('documents',)
    list_display = ('pk', 'app_type', 'applicant', 'organisation', 'state', 'title', 'submit_date', 'assignee')
    list_filter = ('app_type', 'state')
    search_fields = ('applicant__email', 'organisation__name', 'assignee__email', 'title')


@register(Location)
class LocationAdmin(ModelAdmin):
    filter_horizontal = ('documents',)
    search_fields = ('application__title', 'lot', 'reserve', 'suburb', 'intersection', 'lga')


@register(Referral)
class ReferralAdmin(ModelAdmin):
    date_hierarchy = 'sent_date'
    filter_horizontal = ('documents',)
    list_display = ('application', 'referee', 'sent_date', 'period', 'status', 'expire_date', 'response_date')
    list_filter = ('status',)
    search_fields = ('application__title', 'referee__email', 'details', 'feedback')


@register(Condition)
class ConditionAdmin(ModelAdmin):
    filter_horizontal = ('documents',)
    list_display = ('pk', 'application', 'referral', 'status')
    list_filter = ('status',)
    search_fields = ('application__title', 'condition')


@register(Compliance)
class ComplianceAdmin(ModelAdmin):
    date_hierarchy = 'submit_date'
    filter_horizontal = ('documents',)
    list_display = ('__str__', 'applicant', 'assignee', 'status', 'submit_date', 'approve_date')
    search_fields = ('applicant__email', 'assignee__email', 'compliance', 'comments')


@register(Task)
class TaskAdmin(ModelAdmin):
    filter_horizontal = ('documents',)
