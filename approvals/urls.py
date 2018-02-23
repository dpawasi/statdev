from django.conf.urls import url
from approvals import views

urlpatterns = [
                  url(r'^approvals/$', views.ApprovalList.as_view(), name='approval_list'),
                  url(r'^approvals/(?P<pk>\d+)/$', views.ApprovalDetails.as_view(), name='approval_detail'),
                  url(r'^approvals/(?P<pk>\d+)/change/(?P<status>\w+)/$', views.ApprovalStatusChange.as_view(), name='approval_status_change'),
                  url(r'^approvals/(?P<pk>\d+)/actions/$', views.ApprovalActions.as_view(), name='approval_actions'),
                  url(r'^approvals/(?P<pk>\d+)/comms-create/$', views.ApprovalCommsCreate.as_view(), name='approvals_comms_create'),
                  url(r'^approvals/(?P<pk>\d+)/comms/$', views.ApprovalComms.as_view(), name='approvals_comms'),
                  url(r'^approvals/viewpdf-(?P<approval_id>\d+).pdf$', views.getPDF, name='approvals_view_pdf'),
              ]
