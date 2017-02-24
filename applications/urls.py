from django.conf.urls import url
from applications import views


urlpatterns = [
    url(r'^$', views.HomePage.as_view(), name='home_page'),
    url(r'^applications/$', views.ApplicationList.as_view(), name='application_list'),
    url(r'^applications/create/$', views.ApplicationCreate.as_view(), name='application_create'),
    url(r'^applications/(?P<pk>\d+)/$', views.ApplicationDetail.as_view(), name='application_detail'),
    url(r'^applications/(?P<pk>\d+)/update/$', views.ApplicationUpdate.as_view(), name='application_update'),
    url(r'^applications/(?P<pk>\d+)/lodge/$', views.ApplicationLodge.as_view(), name='application_lodge'),
    url(r'^applications/(?P<pk>\d+)/refer/$', views.ApplicationRefer.as_view(), name='application_refer'),
    #url(r'^applications/(?P<pk>\d+)/assign/$', views.ApplicationUpdate.as_view(), name='application_update'),
    url(r'^tasks/(?P<pk>\d+)/reassign/$', views.TaskReassign.as_view(), name='task_reassign'),
]
