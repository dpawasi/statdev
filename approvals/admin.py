from django.contrib.admin import register, ModelAdmin
from django.contrib import admin
from .models import Approval

@register(Approval)
class ApprovalsAdmin(ModelAdmin):
    date_hierarchy = 'start_date'
#    filter_horizontal = ('records',)
    list_display = ('id', 'title','app_type', 'applicant', 'start_date', 'expiry_date', 'status', 'approval_document')
    list_filter = ('app_type','status')
    search_fields = ('applicant__email', 'organisation__name', 'title')


# Register your models here.
