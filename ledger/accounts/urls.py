from django.conf.urls import url
from ledger.accounts import views


urlpatterns = [
    url(r'^$', views.UserProfile.as_view(), name='user_profile'),
]
