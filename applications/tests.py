from __future__ import unicode_literals
from datetime import date
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.test import Client, TestCase
from mixer.backend.django import mixer

from accounts.utils import random_dpaw_email
from .models import Application, Referral, Condition, Vessel

User = get_user_model()


class ApplicationTest(TestCase):

    def setUp(self):
        self.client = Client()
        # Set up some non-superuser internal users.
        self.user1 = mixer.blend(User, email=random_dpaw_email, is_superuser=False, is_staff=True)
        self.user1.set_password('pass')
        self.user1.save()
        self.user2 = mixer.blend(User, email=random_dpaw_email, is_superuser=False, is_staff=True)
        self.user2.set_password('pass')
        self.user2.save()
        self.user3 = mixer.blend(User, email=random_dpaw_email, is_superuser=False, is_staff=True)
        self.user3.set_password('pass')
        self.user3.save()

        for i in ['Processor', 'Assessor', 'Approver', 'Referee', 'Emergency']:
            Group.objects.create(name=i)
        processor = Group.objects.get(name='Processor')
        assessor = Group.objects.get(name='Assessor')
        approver = Group.objects.get(name='Approver')
        referee = Group.objects.get(name='Referee')
        emergency = Group.objects.get(name='Emergency')
        self.user1.groups.add(processor)
        self.user1.groups.add(assessor)
        self.user1.groups.add(approver)
        self.user1.groups.add(emergency)
        self.user2.groups.add(processor)
        self.user2.groups.add(assessor)
        self.user2.groups.add(approver)
        self.user2.groups.add(emergency)

        self.superuser = mixer.blend(User, email=random_dpaw_email, is_superuser=True, is_staff=True)
        self.superuser.set_password('pass')
        self.superuser.save()
        self.customer = mixer.blend(User, is_superuser=False, is_staff=False)
        self.customer.set_password('pass')
        self.customer.save()
        self.referee = mixer.blend(User, is_superuser=False, is_staff=True)
        self.referee.set_password('pass')
        self.referee.save()
        self.referee.groups.add(referee)
        self.app_type = "licence"

        # Log in user1, by default.
        self.client.login(email=self.user1.email, password='pass')
        # Generate test fixtures.
        self.app1 = mixer.blend(
            Application, app_type=Application.APP_TYPE_CHOICES.licence,
            state=Application.APP_STATE_CHOICES.draft, assignee=self.user1,routeid=1)
        self.app2 = mixer.blend(
            Application, app_type=Application.APP_TYPE_CHOICES.licence,
            state=Application.APP_STATE_CHOICES.draft, assignee=self.user3,routeid=2)
        self.ref1 = mixer.blend(Referral, application=self.app1, referee=self.referee, period=21)

    def test_get_absolute_url(self):
        self.assertTrue(self.app1.get_absolute_url())

    def test_home_page_get(self):
        url = reverse('home_page')
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 200)

    def test_list_application_get(self):
        url = reverse('application_list')
        resp = self.client.get(url, {'q': 'foo'})
        self.assertEquals(resp.status_code, 200)

    def test_create_application_view_get(self):
        url = reverse('application_create')
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 200)

    def test_create_application_view_post(self):
        count = Application.objects.count()
        url = reverse('application_create')
        self.client.post(url, {'app_type': Application.APP_TYPE_CHOICES.licence})
        # Test that a new object has been created.
        self.assertTrue(Application.objects.count() > count)

    def test_detail_application_view_get(self):
        url = reverse('application_detail', args=(self.app1.pk,))
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 200)
        # Render different application states, for coverage.
        self.app1.state = Application.APP_STATE_CHOICES.with_admin
        self.app1.save()
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 200)
        self.app1.state = Application.APP_STATE_CHOICES.with_assessor
        self.app1.save()
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 200)
        self.app1.state = Application.APP_STATE_CHOICES.with_manager
        self.app1.save()
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 200)

    def test_update_application_get(self):
        self.app1.state = Application.APP_STATE_CHOICES.draft
        self.app1.save()
        url = reverse('application_update', args=(self.app1.pk,))
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 200)

    def test_update_application_get_redirect(self):
        self.app1.state = Application.APP_STATE_CHOICES.with_admin
        self.app1.routeid = 2
        self.app1.assignee = None
        self.app1.save()
        url = reverse('application_update', args=(self.app1.pk,))
        resp = self.client.get(url)
        self.assertRedirects(resp, self.app1.get_absolute_url())

    def test_update_application_post(self):
        self.app1.state = Application.APP_STATE_CHOICES.draft
        self.app1.save()
        url = reverse('application_update', args=(self.app1.pk,))
        resp = self.client.post(url, {'title': 'foo'})
        # Create view will redirect to the detail view.
        self.assertRedirects(resp, self.app1.get_absolute_url())
        a = Application.objects.get(pk=self.app1.pk)
        self.assertEquals(a.title, 'foo')

    def test_lodge_application_get(self):
        self.app1.state = Application.APP_STATE_CHOICES.draft
        self.app1.routeid = 1
        self.app1.save()
        url = reverse('application_lodge', args=(self.app1.pk,))
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 200)

    def test_lodge_application_get_redirect(self):
        self.app1.state = Application.APP_STATE_CHOICES.with_admin
        self.app1.routeid = 2
        self.app1.save()
        url = reverse('application_lodge', args=(self.app1.pk,))
        resp = self.client.get(url)
        self.assertRedirects(resp, self.app1.get_absolute_url())

    def test_lodge_application_post(self):
        url = reverse('application_lodge', args=(self.app1.pk,))
        resp = self.client.post(url)
        self.assertRedirects(resp, self.app1.get_absolute_url())

    def test_refer_application_get(self):
        self.app1.state = Application.APP_STATE_CHOICES.with_admin
        self.app1.routeid = 2
        self.app1.save()
        url = reverse('application_refer', args=(self.app1.pk,))
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 200)

    def test_refer_application_get_redirect(self):
        self.app1.routeid = 2
        url = reverse('application_refer', args=(self.app1.pk,))
        resp = self.client.get(url)
        self.assertRedirects(resp, self.app1.get_absolute_url())

    def test_refer_application_post(self):
        referee = Group.objects.get(name='Referee')
        self.user1.groups.add(referee)  # Make user1 a referee.
        count = Referral.objects.count()
        self.app1.state = Application.APP_STATE_CHOICES.with_admin
        self.app1.routeid = 2
        self.app1.save()
        url = reverse('application_refer', args=(self.app1.pk,))
        resp = self.client.post(url, {'referee': self.user1.pk, 'period': 21})
        self.assertRedirects(resp, self.app1.get_absolute_url()+'refer/')
        #self.assertRedirects(resp, self.app1.get_success_url())
        self.assertEquals(resp.status_code, 302)
        # Test that a new object has been created.
        self.assertTrue(Referral.objects.count() > count)
        new_ref = Referral.objects.get(referee=self.user1.pk)
        self.assertTrue(new_ref.expire_date)  # Check that expire_date is set.

    def test_condition_create_get(self):
        self.app1.state = Application.APP_STATE_CHOICES.with_admin
        self.app1.save()
        url = reverse('condition_create', args=(self.app1.pk,))
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 200)

    def test_condition_create_get_redirect(self):
        url = reverse('condition_create', args=(self.app1.pk,))
        resp = self.client.get(url)
        self.assertRedirects(resp, self.app1.get_absolute_url())

    def test_condition_create_post(self):
        self.assertFalse(Condition.objects.exists())
        url = reverse('condition_create', args=(self.app1.pk,))
        resp = self.client.post(url, {'condition': 'foobar'})
        self.assertRedirects(resp, self.app1.get_absolute_url())
        self.assertTrue(Condition.objects.exists())

    def test_condition_update_get(self):
        self.app1.state = Application.APP_STATE_CHOICES.with_assessor
        self.app1.save()
        condition = mixer.blend(Condition, application=self.app1, referral=self.ref1)
        url = reverse('condition_update', args=(condition.pk,))
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 200)

    def test_condition_update_get_redirect(self):
        # Redirect on application status (Draft).
        condition = mixer.blend(Condition, application=self.app1, referral=self.ref1)
        url = reverse('condition_update', args=(condition.pk,))
        resp = self.client.get(url)
        self.assertRedirects(resp, self.app1.get_absolute_url())
        # Redirect on user permission (not an Assessor).
        self.app1.state = Application.APP_STATE_CHOICES.with_assessor
        self.app1.save()
        assessor = Group.objects.get(name='Assessor')
        self.user1.groups.remove(assessor)
        resp = self.client.get(url)
        self.assertRedirects(resp, self.app1.get_absolute_url())

    def test_condition_update_post(self):
        self.app1.state = Application.APP_STATE_CHOICES.with_assessor
        self.app1.save()
        condition = mixer.blend(Condition, application=self.app1, referral=self.ref1)
        url = reverse('condition_update', args=(condition.pk,))
        resp = self.client.post(url, {'condition': 'foobar'})
        self.assertRedirects(resp, self.app1.get_absolute_url())
        c = Condition.objects.get(pk=condition.pk)
        self.assertEquals(c.condition, 'foobar')

    def test_condition_delete_get(self):
        self.app1.state = Application.APP_STATE_CHOICES.with_assessor
        self.app1.save()
        condition = mixer.blend(Condition, application=self.app1, referral=self.ref1)
        url = reverse('condition_delete', args=(condition.pk,))
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 200)

    def test_condition_delete_get_redirect(self):
        # Redirect on application status (Draft).
        condition = mixer.blend(Condition, application=self.app1, referral=self.ref1)
        url = reverse('condition_delete', args=(condition.pk,))
        resp = self.client.get(url)
        self.assertRedirects(resp, self.app1.get_absolute_url())
        # Redirect on user permission (not an Assessor).
        self.app1.state = Application.APP_STATE_CHOICES.with_assessor
        self.app1.save()
        assessor = Group.objects.get(name='Assessor')
        self.user1.groups.remove(assessor)
        resp = self.client.get(url)
        self.assertRedirects(resp, self.app1.get_absolute_url())

    def test_condition_delete_post(self):
        self.app1.state = Application.APP_STATE_CHOICES.with_assessor
        self.app1.save()
        condition = mixer.blend(Condition, application=self.app1, referral=self.ref1)
        url = reverse('condition_delete', args=(condition.pk,))
        resp = self.client.post(url)
        self.assertRedirects(resp, self.app1.get_absolute_url())
        self.assertFalse(Condition.objects.exists())

    def test_application_assign_processor_get(self):
        self.app1.state = Application.APP_STATE_CHOICES.with_admin
        self.app1.save()
        url = reverse('application_assign', args=(self.app1.pk, 'process'))
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 200)

    def test_application_assign_processor_post(self):
        self.app1.state = Application.APP_STATE_CHOICES.with_admin
        self.app1.assignee = None
        self.app1.save()
        url = reverse('application_assign', args=(self.app1.pk, 'process'))
        resp = self.client.post(url, {'assignee': self.user1.pk})
        self.assertRedirects(resp, self.app1.get_absolute_url())
        a = Application.objects.get(pk=self.app1.pk)
        self.assertEquals(a.assignee, self.user1)

    def test_application_assign_assessor_get(self):
        self.app1.state = Application.APP_STATE_CHOICES.with_admin
        self.app1.save()
        url = reverse('application_assign', args=(self.app1.pk, 'assess'))
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 200)

    def test_application_assign_assessor_get_redirect(self):
        url = reverse('application_assign', args=(self.app1.pk, 'assess'))
        resp = self.client.get(url)
        self.assertRedirects(resp, self.app1.get_absolute_url())

    def test_application_assign_assessor_post(self):
        self.app1.state = Application.APP_STATE_CHOICES.with_admin
        self.app1.assignee = None
        self.app1.save()
        url = reverse('application_assign', args=(self.app1.pk, 'assess'))
        resp = self.client.post(url, {'assignee': self.user1.pk})
        self.assertRedirects(resp, self.app1.get_absolute_url())
        a = Application.objects.get(pk=self.app1.pk)
        self.assertEquals(a.assignee, self.user1)

    def test_application_assign_approver_get(self):
        self.app1.state = Application.APP_STATE_CHOICES.with_assessor
        self.app1.save()
        url = reverse('application_assign', args=(self.app1.pk, 'approve'))
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 200)

    def test_application_assign_approver_get_redirect(self):
        self.app1.assignee = self.user2
        self.app1.save()
        url = reverse('application_assign', args=(self.app1.pk, 'approve'))
        resp = self.client.get(url)
        self.assertRedirects(resp, self.app1.get_absolute_url())

    def test_application_assign_approver_post(self):
        self.app1.state = Application.APP_STATE_CHOICES.with_assessor
        self.app1.save()
        url = reverse('application_assign', args=(self.app1.pk, 'approve'))
        resp = self.client.post(url, {'assignee': self.user2.pk})
        self.assertRedirects(resp, self.app1.get_absolute_url())
        a = Application.objects.get(pk=self.app1.pk)
        self.assertEquals(a.assignee, self.user2)
        self.assertEquals(a.state, Application.APP_STATE_CHOICES.with_manager)

    def test_application_issue_get(self):
        self.app1.state = Application.APP_STATE_CHOICES.with_manager
        self.app1.assignee = self.user2
        self.app1.save()
        # Log in as user2
        self.client.logout()
        self.client.login(email=self.user2.email, password='pass')
        url = reverse('application_issue', args=(self.app1.pk,))
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 200)

    def test_application_issue_get_redirect(self):
        self.app1.state = Application.APP_STATE_CHOICES.with_manager
        self.app1.assignee = self.user2
        self.app1.save()
        url = reverse('application_issue', args=(self.app1.pk,))
        resp = self.client.get(url)
        # Will redirect when logged in as user1
        self.assertRedirects(resp, self.app1.get_absolute_url())

    def test_application_issue_post(self):
        self.app1.state = Application.APP_STATE_CHOICES.with_manager
        self.app1.assignee = self.user2
        self.app1.save()
        # Log in as user2
        self.client.logout()
        self.client.login(email=self.user2.email, password='pass')
        url = reverse('application_issue', args=(self.app1.pk,))
        resp = self.client.post(url, {'assessment': 'issue'})
        self.assertRedirects(resp, self.app1.get_absolute_url())
        a = Application.objects.get(pk=self.app1.pk)
        self.assertEquals(a.assignee, None)
        self.assertEquals(a.state, Application.APP_STATE_CHOICES.issued)

    def test_referral_complete_get(self):
        self.client.logout()
        self.client.login(email=self.referee.email, password='pass')
        url = reverse('referral_complete', args=(self.ref1.pk,))
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 200)

    def test_referral_complete_get_redirect(self):
        url = reverse('referral_complete', args=(self.ref1.pk,))
        resp = self.client.get(url)
        self.assertRedirects(resp, self.app1.get_absolute_url())

    def test_referral_complete_post(self):
        self.client.logout()
        self.client.login(email=self.referee.email, password='pass')
        self.app1.routeid = 2
        self.app1.assignee = None

        url = reverse('referral_complete', args=(self.ref1.pk,))
        resp = self.client.post(url, {'feedback': 'foo'})
        self.assertRedirects(resp, self.app1.get_absolute_url())
        r = Referral.objects.get(pk=self.ref1.pk)
        self.assertEquals(r.response_date, date.today())

    def test_referral_recall_get(self):
        url = reverse('referral_recall', args=(self.ref1.pk,))
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 200)

    def test_referral_recall_get_redirect(self):
        self.ref1.status = Referral.REFERRAL_STATUS_CHOICES.responded
        self.ref1.save()
        url = reverse('referral_recall', args=(self.ref1.pk,))
        resp = self.client.get(url)
        self.assertRedirects(resp, self.app1.get_absolute_url())

    def test_referral_recall_post(self):
        url = reverse('referral_recall', args=(self.ref1.pk,))
        resp = self.client.post(url)
        self.assertRedirects(resp, self.app1.get_absolute_url())
        r = Referral.objects.get(pk=self.ref1.pk)
        self.assertEquals(r.status, Referral.REFERRAL_STATUS_CHOICES.recalled)

    def test_application_add_vessel_get(self):
        url = reverse('application_add_vessel', args=(self.app1.pk,))
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 200)

    def test_application_add_vessel_get_redirect(self):
        self.app1.state = Application.APP_STATE_CHOICES.with_admin
        self.app1.save()
        url = reverse('application_add_vessel', args=(self.app1.pk,))
        resp = self.client.get(url)
        self.assertRedirects(resp, self.app1.get_absolute_url())

    def test_application_add_vessel_post(self):
        self.assertFalse(Vessel.objects.exists())
        url = reverse('application_add_vessel', args=(self.app1.pk,))
        resp = self.client.post(url, {'name': 'foo'})
        self.assertRedirects(resp, self.app1.get_absolute_url())
        self.assertTrue(Vessel.objects.exists())

    def test_vessel_update_get(self):
        vessel = mixer.blend(Vessel)
        self.app1.vessels.add(vessel)
        url = reverse('vessel_update', args=(vessel.pk,))
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 200)

    def test_vessel_update_get_redirect(self):
        vessel = mixer.blend(Vessel)
        self.app1.vessels.add(vessel)
        self.app1.state = Application.APP_STATE_CHOICES.with_admin
        self.app1.save()
        url = reverse('vessel_update', args=(vessel.pk,))
        resp = self.client.get(url)
        self.assertRedirects(resp, self.app1.get_absolute_url())

    def test_vessel_update_post(self):
        vessel = mixer.blend(Vessel)
        self.app1.vessels.add(vessel)
        url = reverse('vessel_update', args=(vessel.pk,))
        resp = self.client.post(url, {'name': 'foo'})
        self.assertRedirects(resp, self.app1.get_absolute_url())
        v = Vessel.objects.get(pk=vessel.pk)
        self.assertEquals(v.name, 'foo')
