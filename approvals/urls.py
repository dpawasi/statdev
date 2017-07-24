from django.conf.urls import url
from approvals import views

urlpatterns = [
                  url(r'^approvals/$', views.ApprovalList.as_view(), name='approval_list'),
                  url(r'^approvals/(?P<pk>\d+)/$', views.ApprovalDetails.as_view(), name='approval_detail'),
                  url(r'^approvals/(?P<pk>\d+)/change/(?P<status>\w+)/$', views.ApprovalStatusChange.as_view(), name='approval_status_change'),
                  url(r'^approvals/(?P<pk>\d+)/actions/$', views.ApprovalActions.as_view(), name='approval_actions'),
              ]
