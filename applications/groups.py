from __future__ import unicode_literals
from django.contrib.auth.models import Group


# TODO: the authorisation groups below are WiP.
PROCESSOR = Group.objects.get_or_create(name='Processor')[0]
ASSESSOR = Group.objects.get_or_create(name='Assessor')[0]
REFEREE = Group.objects.get_or_create(name='Referee')[0]
APPROVER = Group.objects.get_or_create(name='Approver')[0]
