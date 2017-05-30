from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from mixer.backend.django import mixer
import logging

logger = logging.getLogger('statdev')
User = get_user_model()


class Command(BaseCommand):
    help = 'Create Test users accounts and assign groups'

    def handle(self, *args, **options):
        processor = Group.objects.get(name='Processor')
        assessor = Group.objects.get(name='Assessor')
        approver = Group.objects.get(name='Approver')
        referee = Group.objects.get(name='Referee')
        emergency = Group.objects.get(name='Emergency')
        director = Group.objects.get(name='Director')
        executive = Group.objects.get(name='Executive')
        referee = Group.objects.get(name='Referee')
        
        if not User.objects.filter(email="admin@dpaw.gov.wa.au").exists():

            self.user1 = mixer.blend(User, email="admin@dpaw.gov.wa.au", first_name="Admin", last_name="1", is_superuser=False, is_staff=False)
            self.user1.set_password('pass')
            self.user1.save()
            self.user1.groups.add(processor)

        if not User.objects.filter(email="asessor@dpaw.gov.wa.au").exists(): 
            self.user1 = mixer.blend(User, email="asessor@dpaw.gov.wa.au", first_name="Assessor", last_name="1", is_superuser=False, is_staff=False)
            self.user1.set_password('pass')
            self.user1.save()
            self.user1.groups.add(assessor)

        if not User.objects.filter(email="manager@dpaw.gov.wa.au").exists():
            self.user1 = mixer.blend(User, email="manager@dpaw.gov.wa.au", first_name="Manager", last_name="1", is_superuser=False, is_staff=False)
            self.user1.set_password('pass')
            self.user1.save()
            self.user1.groups.add(approver)

        if not User.objects.filter(email="director@dpaw.gov.wa.au").exists():
            self.user1 = mixer.blend(User, email="director@dpaw.gov.wa.au", first_name="Manager", last_name="1", is_superuser=False, is_staff=False)
            self.user1.set_password('pass')
            self.user1.save()
            self.user1.groups.add(director)

        if not User.objects.filter(email="exec@dpaw.gov.wa.au").exists():
            self.user1 = mixer.blend(User, email="exec@dpaw.gov.wa.au", first_name="Manager", last_name="1", is_superuser=False, is_staff=False)
            self.user1.set_password('pass')
            self.user1.save()
            self.user1.groups.add(executive)

        if not User.objects.filter(email="emergency@dpaw.gov.wa.au").exists():
            self.user1 = mixer.blend(User, email="emergency@dpaw.gov.wa.au", first_name="Emergency", last_name="1", is_superuser=False, is_staff=False)
            self.user1.set_password('pass')
            self.user1.save()
            self.user1.groups.add(emergency)


        if not User.objects.filter(email="referee1@dpaw.gov.wa.au").exists():
            self.user1 = mixer.blend(User, email="referee1@dpaw.gov.wa.au", first_name="Referee", last_name="1", is_superuser=False, is_staff=False)
            self.user1.set_password('pass')
            self.user1.save()
            self.user1.groups.add(referee)

        if not User.objects.filter(email="referee2@dpaw.gov.wa.au").exists():
            self.user1 = mixer.blend(User, email="referee2@dpaw.gov.wa.au", first_name="Referee", last_name="1", is_superuser=False, is_staff=False)
            self.user1.set_password('pass')
            self.user1.save()
            self.user1.groups.add(referee)

        if not User.objects.filter(email="referee3@dpaw.gov.wa.au").exists():
            self.user1 = mixer.blend(User, email="referee3@dpaw.gov.wa.au", first_name="Referee", last_name="1", is_superuser=False, is_staff=False)
            self.user1.set_password('pass')
            self.user1.save()
            self.user1.groups.add(referee)

        if not User.objects.filter(email="referee4@dpaw.gov.wa.au").exists():
            self.user1 = mixer.blend(User, email="referee4@dpaw.gov.wa.au", first_name="Referee", last_name="1", is_superuser=False, is_staff=False)
            self.user1.set_password('pass')
            self.user1.save()
            self.user1.groups.add(referee)

        if not User.objects.filter(email="referee5@dpaw.gov.wa.au").exists():
            self.user1 = mixer.blend(User, email="referee5@dpaw.gov.wa.au", first_name="Referee", last_name="1", is_superuser=False, is_staff=False)
            self.user1.set_password('pass')
            self.user1.save()
            self.user1.groups.add(referee)

        if not User.objects.filter(email="referee6@dpaw.gov.wa.au").exists():
            self.user1 = mixer.blend(User, email="referee6@dpaw.gov.wa.au", first_name="Referee", last_name="1", is_superuser=False, is_staff=False)
            self.user1.set_password('pass')
            self.user1.save()
            self.user1.groups.add(referee)

        print ("Test Account Creation Completed") 
        return
