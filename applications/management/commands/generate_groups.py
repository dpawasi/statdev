from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
import logging

logger = logging.getLogger('statdev')


class Command(BaseCommand):
    help = 'Checks and (if required) creates required groups.'

    def handle(self, *args, **options):
        groups = ['Processor', 'Assessor', 'Approver', 'Referee']
        for group in groups:
            if not Group.objects.filter(name=group).exists():
                new_group = Group.objects.create(name=group)
                self.stdout.write('Group created: {}'.format(group))
                logger.info('Group created: {}'.format(group))

        return
