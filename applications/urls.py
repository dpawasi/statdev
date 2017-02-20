from django.conf.urls import url
from .views import HomePage, ApplicationList, ApplicationDetail, ApplicationCreate


urlpatterns = [
    url(r'^$', HomePage.as_view(), name='home_page'),
    url(r'^applications/$', ApplicationList.as_view(), name='application_list'),
    url(r'^applications/create/$', ApplicationCreate.as_view(), name='application_create'),
    url(r'^applications/(?P<pk>\d+)/$', ApplicationDetail.as_view(), name='application_detail'),
]
