from django.contrib import admin
from django.contrib.admin import register
from .models import Application, Location, Condition, Task


@register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    pass


@register(Location)
class LocationAdmin(admin.ModelAdmin):
    pass


@register(Condition)
class ConditionAdmin(admin.ModelAdmin):
    pass


@register(Task)
class TaskAdmin(admin.ModelAdmin):
    pass
