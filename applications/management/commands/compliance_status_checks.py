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
        compliance_no_cid = Compliance.objects.filter(status__in=[1,2,3,8],compliance_group=None)
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


        import datetime 
        due_time_frame = datetime.timedelta(days=14)
        today = date.today()
        due_period = due_time_frame + today

        print 'PERIOD'
        print due_period

        # print date.today()
        # Look for Compliance that have expired and set them to expired.
        compliance = Compliance.objects.filter(due_date__lt=due_period,status__in=[1,2,3,8])
        for co in compliance:
            print co
            print Compliance.COMPLIANCE_STATUS_CHOICES[co.status]
            print co.due_date

            co.status = 2
            co.save()
            cgroup = ComplianceGroup.objects.get(id=co.compliance_group.id)
            cgroup.status = 2
            cgroup.save()

            # Update approvals and find next current Compliance Conditions
      
#        compliance = ComplianceGroup.objects.filter(due_date__gte=due_period,status__in=[1,2,3,8])
#        for co in compliance:
#            co.status = 3
#            co.save()
#            ci =  Compliance.objects.filter(compliance_group=co.id)
#            for ca in ci:
#                ca.status = 3
#                ca.save()
#                print ("Updated Condition: "+str(ca.id))
                  

        compliance = ComplianceGroup.objects.filter(due_date__lt=date.today(),status__in=[1,2,3,8])
        for co in compliance:
            co.status = 8
            co.save()
            ci =  Compliance.objects.filter(compliance_group=co.id)
            for ca in ci:
                ca.status = 8
                ca.save()
                print ("Updated Condition: "+str(ca.id))



         
        return
        # compliance = Compliance.objects.filter(due_date__gte=date.today(),status__in=[1,2,3])
        compliance = Compliance.objects.filter(due_date__gte=date.today(),status__in=[1,2,3,8]).values('approval_id').distinct()
        for co in compliance:
            compliance_approval = Compliance.objects.filter(status__in=[1,2,3],approval_id=co['approval_id']).order_by('due_date')[:1]
            for ca in compliance_approval:
                if ca.status == 1 or ca.status == 2:
                    print ("Approval ("+str(co['approval_id'])+") Skipping Condition: "+str(ca.id))
                elif ca.status == 3:
                    print ("Approval ("+str(co['approval_id'])+") Updated Condition: "+str(ca.id))
                    ca.status = 1
                    ca.save()
                    
                    cgroup = ComplianceGroup.objects.get(id=ca.compliance_group.id)
                    cgroup.status = 1
                    cgroup.save()
                    
        return
