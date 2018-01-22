from datetime import date
from django.core.management.base import BaseCommand
import logging
from actions.models import Action
from applications.models import Referral

logger = logging.getLogger('statdev')


class Command(BaseCommand):
    help = 'Iterates over current referrals to resolve those past their expiry date'

    def handle(self, *args, **options):
        referrals = Referral.objects.filter(
            status=Referral.REFERRAL_STATUS_CHOICES.referred, expire_date__lt=date.today(),
            response_date__isnull=True)
        for r in referrals:
            self.stdout.write('Setting referral status to "expired": {}'.format(r))
            logger.info('Setting referral status to "expired": {}'.format(r))
            r.status = Referral.REFERRAL_STATUS_CHOICES.expired
            r.save()
            # Check the referral's application: if it is status 'with_referee'
            # but has no referral's that are status 'referred', then set the
            # application status to 'with admin'.
            app = r.application
            if not Referral.objects.filter(
                    application=app, status=Referral.REFERRAL_STATUS_CHOICES.referred).exists():
                self.stdout.write('Setting application status to "with admin": {}'.format(app))
                logger.info('Setting application status to "with admin": {}'.format(app))
                app.state = app.APP_STATE_CHOICES.with_admin
                app.save()
                # Record an action.
                action = Action(
                    content_object=app,
                    action='[SYSTEM] No outstanding referrals, application status set to {}'.format(app.get_state_display()))
                action.save()

        return 
