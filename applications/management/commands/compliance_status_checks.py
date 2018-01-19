from datetime import date
from django.core.management.base import BaseCommand
import logging
from actions.models import Action
from applications.models import Compliance,ComplianceGroup

logger = logging.getLogger('statdev')

class Command(BaseCommand):
    help = 'Iterates over current Compliance (Clearance of Conditions) to correct status that have expired or current'

    def handle(self, *args, **options):

        # Create Compliance Group ID
        compliance_no_cid = Compliance.objects.filter(status__in=[1,2,3],compliance_group=None)
        # print compliance_no_cid

        for cid in compliance_no_cid:
              # print cid
              print cid.due_date

              if ComplianceGroup.objects.filter(due_date=cid.due_date,approval_id=cid.approval_id).exists():
                   cgroup = ComplianceGroup.objects.get(due_date=cid.due_date,approval_id=cid.approval_id)
                   
                   if cid.compliance_group is None:
                      co = Compliance.objects.get(pk=cid.id)
                      co.compliance_group = cgroup
                      co.save()
              else:

                   cgroup = ComplianceGroup.objects.create(
                        approval_id=cid.approval_id,
                        title=cid.title,
                        app_type=cid.app_type,
                        applicant=cid.applicant,
                        due_date=cid.due_date,
                        assignee=cid.assignee
                   )
                   co = Compliance.objects.get(pk=cid.id)
                   co.compliance_group = cgroup
                   co.save()




        # print date.today()
        # Look for Compliance that have expired and set them to expired.
        compliance = Compliance.objects.filter(due_date__lte=date.today(),status__in=[1,2,3])
        for co in compliance:
            print co
            print Compliance.COMPLIANCE_STATUS_CHOICES[co.status]
            print co.due_date
            co.status = 8
            co.save()
            cgroup = ComplianceGroup.objects.get(id=co.compliance_group)
            cgroup.status = 8
            cgroup.save()

            # Update approvals and find next current Compliance Conditions

        # compliance = Compliance.objects.filter(due_date__gte=date.today(),status__in=[1,2,3])
        compliance = Compliance.objects.filter(due_date__gte=date.today(),status__in=[1,2,3]).values('approval_id').distinct()
        for co in compliance:
            compliance_approval = Compliance.objects.filter(status__in=[1,2,3],approval_id=co['approval_id']).order_by('due_date')[:1]
            for ca in compliance_approval:
                if ca.status == 1 or ca.status == 2:
                    print ("Approval ("+str(co['approval_id'])+") Skipping Condition: "+str(ca.id))
                elif ca.status == 3:
                    print ("Approval ("+str(co['approval_id'])+") Updated Condition: "+str(ca.id))
                    ca.status = 1
                    ca.save()
                    
                    cgroup = ComplianceGroup.objects.get(id=ca.compliance_group)
                    cgroup.status = 1
                    cgroup.save()
                    
        return
