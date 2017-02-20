from django.test import Client, TestCase
from django.core.urlresolvers import reverse
from datetime import date
from .models import Application


class ApplicationTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_get_absolute_url(self):
        """Test that Application.get_absolute_url works
        """
        app = Application.objects.create(app_type=1, title='foo', submit_date=date.today())
        self.assertTrue(app.get_absolute_url())

    def test_list_view_get(self):
        url = reverse('application_list')
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 200)

    def test_create_view_get(self):
        url = reverse('application_create')
        resp = self.client.get(url)
        self.assertEquals(resp.status_code, 200)

    def test_create_view_post(self):
        url = reverse('application_create')
        resp = self.client.post(url, {'app_type': 1, 'title': 'foo', 'submit_date': '2017/01/01'})
        self.assertEquals(resp.status_code, 200)
