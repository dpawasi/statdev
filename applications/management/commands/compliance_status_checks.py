from datetime import date
from django.core.management.base import BaseCommand
import logging
from actions.models import Action
from applications.models import Compliance 

logger = logging.getLogger('statdev')

class Command(BaseCommand):
    help = 'Iterates over current Compliance (Clearance of Conditions) to correct status that have expired or current'

    def handle(self, *args, **options):

        # print date.today()
        # Look for Compliance that have expired and set them to expired.
        compliance = Compliance.objects.filter(due_date__lte=date.today(),status__in=[1,2,3])
        for co in compliance:
            print co
            print Compliance.COMPLIANCE_STATUS_CHOICES[co.status]
            print co.due_date
            co.status = 8
            co.save()
            # Update approvals and find next current Compliance Conditions

        # compliance = Compliance.objects.filter(due_date__gte=date.today(),status__in=[1,2,3])
        compliance = Compliance.objects.filter(due_date__gte=date.today(),status__in=[1,2,3]).values('approval_id').distinct()
        for co in compliance:
            compliance_approval = Compliance.objects.filter(status__in=[1,2,3],approval_id=co['approval_id']).order_by('due_date')[:1]
            for ca in compliance_approval:
                if ca.status == 1 or ca.status == 2:
                    print ("Approval ("+str(co['approval_id'])+") Skipping Condition: "+str(ca.id))
                elif ca.status == 3:
                    print ("Approcal ("+str(co['approval_id'])+") Updated Condition: "+str(ca.id))
                    ca.status = 1
                    ca.save()
        return
