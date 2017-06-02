from django.conf.urls import url
from approvals import views

urlpatterns = [
                  url(r'^approvals/$', views.ApprovalList.as_view(), name='approval_list')
              ]
