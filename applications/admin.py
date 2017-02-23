from django.contrib import admin
from django.contrib.admin import register
from .models import Document, Application, Location, Condition, Task


@register(Document)
class DocumentAdmin(admin.ModelAdmin):
    pass


@register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    filter_horizontal = ('documents',)


@register(Location)
class LocationAdmin(admin.ModelAdmin):
    filter_horizontal = ('documents',)


@register(Condition)
class ConditionAdmin(admin.ModelAdmin):
    filter_horizontal = ('documents',)


@register(Task)
class TaskAdmin(admin.ModelAdmin):
    filter_horizontal = ('documents',)
