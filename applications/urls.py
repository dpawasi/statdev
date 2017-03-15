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
    url(r'^applications/(?P<pk>\d+)/create-condition/$', views.ConditionCreate.as_view(), name='condition_create'),
    url(r'^applications/(?P<pk>\d+)/assign/(?P<action>\w+)/$', views.ApplicationAssign.as_view(), name='application_assign'),
    url(r'^applications/(?P<pk>\d+)/issue/$', views.ApplicationIssue.as_view(), name='application_issue'),
    url(r'^applications/(?P<pk>\d+)/create-compliance/$', views.ComplianceCreate.as_view(), name='compliance_create'),
    url(r'^applications/(?P<pk>\d+)/vessel/$', views.VesselCreate.as_view(), name='application_add_vessel'),
    url(r'^referrals/(?P<pk>\d+)/complete/$', views.ReferralComplete.as_view(), name='referral_complete'),
    url(r'^referrals/(?P<pk>\d+)/recall/$', views.ReferralRecall.as_view(), name='referral_recall'),
    url(r'^condition/(?P<pk>\d+)/apply/$', views.ConditionApply.as_view(), name='condition_apply'),
    # TODO: condition update view.
    url(r'^compliances/$', views.ComplianceList.as_view(), name='compliance_list'),
    url(r'^documents/create/$', views.DocumentCreate.as_view(), name='document_create'),
    url(r'^documents/$', views.DocumentList.as_view(), name='document_list'),
]
