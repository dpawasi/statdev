from django.contrib import admin
from django.contrib.admin import register
from .models import Document, Vessel, ApplicationPurpose, Application, Location, Referral, Condition, Task


@register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'upload')
    list_filter = ('category',)
    search_fields = ('name',)


@register(Vessel)
class VesselAdmin(admin.ModelAdmin):
    filter_horizontal = ('registration',)
    list_display = ('name', 'vessel_type', 'vessel_id')
    list_filter = ('vessel_type',)
    search_fields = ('name', 'vessel_id')


@register(ApplicationPurpose)
class ApplicationPurposeAdmin(admin.ModelAdmin):
    search_fields = ('purpose',)


@register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    date_hierarchy = 'submit_date'
    filter_horizontal = ('documents',)
    list_display = ('app_type', 'applicant', 'organisation', 'state', 'title', 'submit_date', 'assignee')
    list_filter = ('app_type', 'state')
    search_fields = ('applicant__email', 'organisation__name', 'assignee__email', 'title')


@register(Location)
class LocationAdmin(admin.ModelAdmin):
    filter_horizontal = ('documents',)
    search_fields = ('application__title', 'lot', 'reserve', 'suburb', 'intersection', 'lga')


@register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    date_hierarchy = 'sent_date'
    filter_horizontal = ('documents',)
    list_display = ('application', 'referee', 'sent_date', 'period', 'status', 'expire_date', 'response_date')
    list_filter = ('status',)
    search_fields = ('application__title', 'referee__email', 'details', 'feedback')


@register(Condition)
class ConditionAdmin(admin.ModelAdmin):
    filter_horizontal = ('documents',)
    list_display = ('application', 'referral', 'status')
    list_filter = ('status',)
    search_fields = ('application__title', 'condition')


@register(Task)
class TaskAdmin(admin.ModelAdmin):
    filter_horizontal = ('documents',)
