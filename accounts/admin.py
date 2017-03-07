from django.contrib import admin
from django.contrib.admin import register
from .forms import OrganisationAdminForm
from .models import Address, EmailUser, EmailUserProfile, Organisation


@register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_filter = ('state', )
    search_fields = ('line1', 'line2', 'locality', 'postcode')


@register(EmailUser)
class EmailUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')


@register(EmailUserProfile)
class EmailUserProfileAdmin(admin.ModelAdmin):
    list_display = ('emailuser', 'dob', 'id_verified', 'home_phone', 'work_phone', 'mobile')
    search_fields = ('emailuser__email', 'emailuser__first_name', 'emailuser__last_name')


@register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    filter_horizontal = ('delegates', )
    form = OrganisationAdminForm
    list_display = ('name', 'abn')
    search_fields = ('name', 'abn')
