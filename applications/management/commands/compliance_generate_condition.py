from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand
import logging
from actions.models import Action
from applications.models import Compliance,ComplianceGroup, Application, Condition
from approvals.models import Approval
logger = logging.getLogger('statdev')

class Command(BaseCommand):
    help = 'Iterates over current Conditions and creates a complaince which is due to for action'

    def handle(self, *args, **options):
	approvals = Approval.objects.filter(expiry_date__gt=date.today())
        
        for apps in approvals:
              #print apps.application.id
              #print apps.application

              end_date = apps.application.expire_date
              #print end_date

              conditions = Condition.objects.filter(application=apps.application.id)

              for c in conditions:
                   start_date = c.due_date
                   loop_start_date = start_date
                   print c.id
                   print c.due_date
                   if c.due_date is None:
                        print "MISSED"
                        # No due defined no business requirement to create condition.
                        continue;
                   if c.suspend is True:
                        print "Condition Suspended"
                        continue;

                   if c.recur_pattern == 1:
                        num_of_weeks = (end_date - start_date).days / 7.0
                        num_of_weeks_whole = str(num_of_weeks).split('.')
                        num_of_weeks_whole = num_of_weeks_whole[0]
                        week_freq = num_of_weeks / c.recur_freq
                        week_freq_whole = int(str(week_freq).split('.')[0])
                        loopcount = 1
                        loop_start_date = start_date

         #               while loopcount <= week_freq_whole:
         #                  loopcount = loopcount + 1
         #                  week_date_plus = timedelta(weeks = c.recur_freq)

#                      new_week_date = loop_start_date + week_date_plus
 #                     loop_start_date = new_week_date
                        
                        if Compliance.objects.filter(condition__id=c.id).exists():
                           compliance = Compliance.objects.filter(condition__id=c.id).order_by('-due_date')[0]
                           print "COMPL"

                           week_date_plus = timedelta(weeks = c.recur_freq)
                           new_week_date = loop_start_date + week_date_plus


                           if date.today() > compliance.due_date:
                                  print "WEEK CREATE NEXT"
                                  week_date_plus = timedelta(weeks = c.recur_freq)
                                  new_week_date = loop_start_date + week_date_plus
                                  print apps.expiry_date
                                  print new_week_date
                                  print "END"
                                  if apps.expiry_date >= new_week_date:
                                      compliance = Compliance.objects.create(
                                          app_type=apps.application.app_type,
                                          title=apps.application.title,
                                          condition=c,
                                          approval_id=apps.id,
                                          applicant=apps.applicant,
                                          organisation=apps.organisation,
                                          assignee=None,
                                          assessed_by=None,
                                          assessed_date=None,
                                          due_date=new_week_date,
                                         status=Compliance.COMPLIANCE_STATUS_CHOICES.due
                                      )
                                  else:
                                      compliance = Compliance.objects.create(
                                          app_type=apps.application.app_type,
                                          title=apps.application.title,
                                          condition=c,
                                          approval_id=apps.id,
                                          applicant=apps.applicant,
                                          assignee=None,
                                          assessed_by=None,
                                          assessed_date=None,
                                          due_date=apps.expiry_date,
                                         status=Compliance.COMPLIANCE_STATUS_CHOICES.due
                                      )
  
                        else:
                                  print "MONTH DOES NOT EXIST"
                                  compliance = Compliance.objects.create(
                                      app_type=apps.application.app_type,
                                      title=apps.application.title,
                                      condition=c,
                                      approval_id=apps.id,
                                      applicant=apps.applicant,
                                      organisation=apps.organisation,
                                      assignee=None,
                                      assessed_by=None,
                                      assessed_date=None,
                                      due_date=c.due_date,
                                      status=Compliance.COMPLIANCE_STATUS_CHOICES.due
                                  ) 


                   if c.recur_pattern == 2:

                        if Compliance.objects.filter(condition__id=c.id).exists():
                           compliance = Compliance.objects.filter(condition__id=c.id).order_by('-due_date')[0]
                           print "MONTH COMPL"
#                           months_date_plus = loop_start_date + relativedelta(months=c.recur_freq)
#                           new_month_date = loop_start_date + months_date_plus
                           print "MONTH START" 
                           print loop_start_date
 
#                           months_date_plus = loop_start_date + relativedelta(months=c.recur_freq)
#                           loop_start_date = months_date_plus
                           print "MONTH FINISH"
                           print c.recur_freq
                           print loop_start_date 

                           if date.today() > compliance.due_date:
                                  print "CREATE NEXT"
                                  months_date_plus = loop_start_date + relativedelta(months=c.recur_freq)
                                  new_month_date = months_date_plus

                                  #week_date_plus = timedelta(weeks = c.recur_freq)
                                  print loop_start_date
                                  if apps.expiry_date >= new_month_date: 
                                      compliance = Compliance.objects.create(
                                          app_type=apps.application.app_type,
                                          title=apps.application.title,
                                          condition=c,
                                          approval_id=apps.id,
                                          applicant=apps.applicant,
                                          organisation=apps.organisation,
                                          assignee=None,
                                          assessed_by=None,
                                          assessed_date=None,
                                          due_date=new_month_date,
                                          status=Compliance.COMPLIANCE_STATUS_CHOICES.due
                                      )
                                  else:
                                      compliance = Compliance.objects.create(
                                          app_type=apps.application.app_type,
                                          title=apps.application.title,
                                          condition=c,
                                          approval_id=apps.id,
                                          applicant=apps.applicant,
                                          organisation=apps.organisation,
                                          assignee=None,
                                          assessed_by=None,
                                          assessed_date=None,
                                          due_date=apps.expiry_date,
                                         status=Compliance.COMPLIANCE_STATUS_CHOICES.due
                                      )



                           else:
                                  print "NOT EXPIRED"

                        else:
                                  print "DOES NOT EXIST"
                                  compliance = Compliance.objects.create(
                                      app_type=apps.application.app_type,
                                      title=apps.application.title,
                                      condition=c,
                                      approval_id=apps.id,
                                      applicant=apps.applicant,
                                      organisation=apps.organisation,
                                      assignee=None,
                                      assessed_by=None,
                                      assessed_date=None,
                                      due_date=c.due_date,
                                      status=Compliance.COMPLIANCE_STATUS_CHOICES.due
                                  )





                   if c.recur_pattern == 3:
                              
                        if Compliance.objects.filter(condition__id=c.id).exists():
                           compliance = Compliance.objects.filter(condition__id=c.id).order_by('-due_date')[0]

                           if date.today() > compliance.due_date:
                                  print "CREATE NEXT"
                                  months_date_plus = loop_start_date + relativedelta(months=c.recur_freq)
                                  years_date_plus = loop_start_date + relativedelta(years=c.recur_freq)
                                  new_year_date = years_date_plus

                                  if apps.expiry_date >= new_year_date:
                                       compliance = Compliance.objects.create(
                                           app_type=apps.application.app_type,
                                           title=apps.application.title,
                                           condition=c,
                                           approval_id=apps.id,
                                           applicant=apps.applicant,
                                           organisation=apps.organisation,
                                           assignee=None,
                                           assessed_by=None,
                                           assessed_date=None,
                                           due_date=new_year_date,
                                           status=Compliance.COMPLIANCE_STATUS_CHOICES.due
                                       )
                                  else:
                                      compliance = Compliance.objects.create(
                                          app_type=apps.application.app_type,
                                          title=apps.application.title,
                                          condition=c,
                                          approval_id=apps.id,
                                          applicant=apps.applicant,
                                          organisation=apps.organisation,
                                          assignee=None,
                                          assessed_by=None,
                                          assessed_date=None,
                                          due_date=apps.expiry_date,
                                         status=Compliance.COMPLIANCE_STATUS_CHOICES.due
                                      )




                           else:
                                  print "NOT EXPIRED"

                        else:
                                  print "YEAR DOES NOT EXIST"
                                  compliance = Compliance.objects.create(
                                      app_type=apps.application.app_type,
                                      title=apps.application.title,
                                      condition=c,
                                      approval_id=apps.id,
                                      applicant=apps.applicant,
                                      organisation=apps.organisation,
                                      assignee=None,
                                      assessed_by=None,
                                      assessed_date=None,
                                      due_date=c.due_date,
                                      status=Compliance.COMPLIANCE_STATUS_CHOICES.due
                                  )

                   print "RECURE"
                   print c.recur_pattern
                   if c.recur_pattern is None:  
                           print "NONE" 
                           if Compliance.objects.filter(condition__id=c.id).exists():
                              pass
                           else:
                                 print "CREATE ONE RECORD" 
                                 compliance = Compliance.objects.create(
                                      app_type=apps.application.app_type,
                                      title=apps.application.title,
                                      condition=c,
                                      approval_id=apps.id,
                                      applicant=apps.applicant,
                                      organisation=apps.organisation,
                                      assignee=None,
                                      assessed_by=None,
                                      assessed_date=None,
                                      due_date=c.due_date,
                                      status=Compliance.COMPLIANCE_STATUS_CHOICES.due
                                 )



#      if compliance.count() > 0: 
#
#                            for co in compliance:
#                               print co.due_date 
#                               if week_freq > week_freq_whole:
#                                   print "EXPIRED"
#                               else:
#                                   print "STILL MORE"
                   print c




        return
