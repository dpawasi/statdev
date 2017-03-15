from django.contrib.admin import register, ModelAdmin
from .models import Action


@register(Action)
class ActionAdmin(ModelAdmin):
    list_display = ('content_object', 'category', 'action')
    list_filter = ('category',)
    search_fields = ('action',)
