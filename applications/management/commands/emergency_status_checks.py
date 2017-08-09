from datetime import date
from django.core.management.base import BaseCommand
import logging
from actions.models import Action
from applications.models import Application 

logger = logging.getLogger('statdev')

class Command(BaseCommand):
    help = 'Iterates over current Emergency Works list to correct the status on EW that have expired'

    def handle(self, *args, **options):

        # Look for Emergency Works that have expired and set them to expired.
        applications = Application.objects.filter(proposed_end__lte=date.today(),app_type__in=[16],state=6)
        for ap in applications:
            print ap
            print ap.state
            print ap.proposed_end
            ap.state = 11
            ap.save()

        return
