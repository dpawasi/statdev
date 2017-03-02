from django.contrib import admin
from django.contrib.admin import register
from .forms import OrganisationAdminForm
from .models import Address, EmailUser, EmailUserProfile, Organisation


@register(Address)
class AddressAdmin(admin.ModelAdmin):
    pass


@register(EmailUser)
class EmailUserAdmin(admin.ModelAdmin):
    pass


@register(EmailUserProfile)
class EmailUserProfileAdmin(admin.ModelAdmin):
    pass


@register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = ('name', 'abn')
    form = OrganisationAdminForm
